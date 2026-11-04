#!/usr/bin/env python3
"""Rebuild versions.omc_json inside db/seed.sql as OMC-JSON v2.8 payloads.

db/seed.sql is the source of truth for seed data (the old generator script was removed).
This script reads the seed rows (assets, shots, events, versions), builds one OMC-JSON `Asset`
per version row, and either emits them as a JSON array for the official OMC validator
(--emit PATH) or rewrites the omc_json column in place (--write). It touches nothing else in the file.

Version types: CAMERA_ORIGINAL (raw), CAMERA_MASTER (debayered), DAILIES_PROXY, EDIT_EXPORT. The OMC JSON describes
the pipeline Camera Raw -> Debayered Camera Master -> Dailies Proxy -> Edit Export.

Usage:
    python3 scripts/rewrite_seed_omc_json.py --emit /path/payloads.json
    python3 scripts/rewrite_seed_omc_json.py --write
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SEED = Path(__file__).resolve().parent.parent / "db" / "seed.sql"
SCHEMA_VERSION = "https://movielabs.com/omc/json/schema/v2.8"
SCOPE = "EXFTR"
CUSTOM_DOMAIN, CUSTOM_NAMESPACE = "poc", "plc"

# Mini LF "3.8K LF 16:9 - UHD" ARRIRAW mode: 3840 x 2160, up to 60 fps (ARRI recording formats sheet).
FULL_RES = ("3840", "2160")   # UHD, camera onward
DAILIES_RES = ("1920", "1080")  # Full HD, downrezzed for review
FPS = 24

# Controlled value (validator V3 clean). "video.debayered" appears in the OMC docs' examples but is NOT in the
# controlled list, which makes the official validator report "Needs Your Attention" on every master.
MASTER_FUNCTIONAL_TYPE = "shot"


# ---------------------------------------------------------------- SQL tuple parsing
def split_tuple(line):
    """Split '    (a, b, ...)[,;]' into [(start, end, raw_token)] with absolute offsets in `line`."""
    i = line.index("(")
    n = len(line)
    i += 1
    tokens = []
    while i < n:
        while i < n and line[i] == " ":
            i += 1
        start = i
        if line[i] == "'":
            i += 1
            while i < n:
                if line[i] == "'":
                    if i + 1 < n and line[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            # optional ::type cast
            m = re.match(r"::[a-z]+", line[i:])
            if m:
                i += m.end()
        else:
            while i < n and line[i] not in ",)":
                i += 1
        tokens.append((start, i, line[start:i]))
        while i < n and line[i] == " ":
            i += 1
        if i < n and line[i] == ",":
            i += 1
            continue
        break  # ')'
    return tokens


def unq(tok):
    """'abc'::type -> abc (with '' unescaped); other tokens returned stripped."""
    m = re.match(r"^'(.*)'(::[a-z]+)?$", tok, re.S)
    return m.group(1).replace("''", "'") if m else tok.strip()


def parse_seed(text):
    """Return dict of tables -> list of (line_no, columns, tokens) for rows we care about."""
    lines = text.split("\n")
    tables = {}
    cur_table, cur_cols = None, None
    for ln, line in enumerate(lines):
        m = re.match(r"^INSERT INTO (\w+) \(([^)]*)\)", line)
        if m:
            cur_table, cur_cols = m.group(1), [c.strip() for c in m.group(2).split(",")]
            continue
        if cur_table and re.match(r"^\s+\('", line):
            toks = split_tuple(line)
            if len(toks) == len(cur_cols):
                tables.setdefault(cur_table, []).append((ln, cur_cols, toks))
    return lines, tables


def rows_as_dicts(tables, name):
    out = []
    for ln, cols, toks in tables.get(name, []):
        out.append((ln, {c: unq(t[2]) for c, t in zip(cols, toks)}, cols, toks))
    return out


# ---------------------------------------------------------------- payload building
def iso(ts):
    # '2026-01-15 08:00:00+00' -> '2026-01-15T08:00:00Z' for `provenance.createdOn` (typed dateTime).
    # NOT used for `instanceInfo.createdOn`: that is oneOf(date, dateTime), and the schema's unanchored
    # date pattern also matches a full timestamp, so a timestamp there matches both and fails `oneOf`.
    return ts.replace(" ", "T").replace("+00", "Z")


def date_only(ts):
    # '2026-01-15 08:00:00+00' -> '2026-01-15': the UTC date of the same instant as provenance.createdOn.
    # `instanceInfo.createdOn` can ONLY hold a plain date and still validate (see note on iso()); it is kept
    # deliberately so the data shows the constraint, alongside the full timestamp in provenance.createdOn.
    return ts.split(" ")[0]


def ident(asset_id, version_id):
    return [{"identifierScope": SCOPE, "identifierValue": f"asset/{asset_id}/version/{version_id}"}]


def hhmmss_ff_duration(tc_in, tc_out):
    def secs(tc):
        h, m, s, f = (int(x) for x in tc.split(":"))
        return h * 3600 + m * 60 + s + f / FPS
    d = secs(tc_out) - secs(tc_in)
    whole, frames = int(d), round((d - int(d)) * FPS)
    return f"{whole // 3600:02d}:{(whole % 3600) // 60:02d}:{whole % 60:02d}:{frames:02d}"


MEDIA_TYPE = {"mxf": "application/mxf", "mov": "video/quicktime", "mp4": "video/mp4"}

# ---------------------------------------------------------------- timecode model
# On set the camera runs time-of-day timecode jam-synced to the production clock, so a clip's Timecode In is its
# record-start wall-clock time plus an arbitrary frame, and Timecode Out is In plus the take length (also any frame).
# The camera master and dailies proxy are transcodes of the same essence and carry the same timecode range. An edit
# export is the part of the take used in the cut, so it is a sub-range with its own In and Out (a rework differs from
# the first export). Everything is a deterministic function of the shot and the CAPTURE event time (idempotent).
SHOOT_TZ = ZoneInfo("America/Los_Angeles")


def _h(*parts):
    return int(hashlib.sha256("|".join(parts).encode()).hexdigest(), 16)


def tc_to_frames(tc):
    h, m, sec, f = (int(x) for x in tc.split(":"))
    return ((h * 3600 + m * 60 + sec) * FPS) + f


def frames_to_tc(n):
    n %= 24 * 3600 * FPS
    sec, f = divmod(n, FPS)
    return f"{sec // 3600:02d}:{(sec % 3600) // 60:02d}:{sec % 60:02d}:{f:02d}"


def camera_range(shot, capture_ts):
    """(In, Out) in frames for the camera original of this shot."""
    dt = datetime.fromisoformat(capture_ts.replace(" ", "T").replace("+00", "+00:00")).astimezone(SHOOT_TZ)
    start = (dt.hour * 3600 + dt.minute * 60 + dt.second) * FPS + _h(shot, "in") % FPS
    length = (12 + _h(shot, "len") % 37) * FPS + 1 + _h(shot, "lenf") % (FPS - 1)  # 12-48 s plus 1-23 frames
    end = start + length
    if end % FPS == 0:  # Timecode Out always ends on a non-zero frame
        end += 1
    return start, end


def timecodes(v, vt, asset_id, is_rework, ctx):
    """(tc_in, tc_out) SMPTE strings for this version."""
    cam = ctx["camera_by_asset"][asset_id]
    shot = ctx["shots"][ctx["assets"][asset_id]["shot_id"]]
    cin, cout = camera_range(shot, ctx["events"][cam["id"]]["created_at"])
    if vt == "EDIT_EXPORT":
        tag = "v2" if is_rework else "v1"
        cin += (1 + _h(shot, tag, "a") % 4) * FPS + _h(shot, tag, "af") % FPS      # trimmed in: +1 to 4 s plus frames
        cout -= (1 + _h(shot, tag, "b") % 3) * FPS + _h(shot, tag, "bf") % FPS    # trimmed out: -1 to 3 s plus frames
        if cout % FPS == 0:
            cout += 1
    return frames_to_tc(cin), frames_to_tc(cout)

# Edit Export codec follows the editing tool (events.tool of the EDIT_EXPORT_CREATED event): an Avid Media Composer
# export is DNxHR (DNxHD tops out at 1920x1080, these exports are UHD); other editors export ProRes 422. A mix like
# this is plausible on a real show where different cutting rooms use different systems. Convention, not a standard.
EDIT_CODEC_BY_TOOL = {"Avid Media Composer": "DNxHR HQX"}
EDIT_CODEC_DEFAULT = "ProRes 422"


def media_inputs(v, asset):
    """Values the payload needs that used to live in relational columns.

    Phase A seeds carried them as columns (versions.codec/container/timecode_in/timecode_out, assets.clip_name/
    reel_or_roll/camera_serial). Phase B dropped those columns: the OMC JSON is now the only home, so when the
    columns are absent the values are read back from the version's existing payload (idempotent rewrite).
    """
    if "codec" in v:
        return {
            "codec": v["codec"], "container": v["container"],
            "tc_in": v["timecode_in"], "tc_out": v["timecode_out"],
            "clip_name": asset["clip_name"], "reel": asset["reel_or_roll"], "serial": asset["camera_serial"],
        }
    old = json.loads(v["omc_json"])
    sc = old["AssetSC"]
    fprops = old["assetFC"]["functionalProperties"]
    custom = sc["customData"][0]["value"]
    cam = fprops.get("cameraMetadata") or {}
    timing = fprops.get("timing") or {}
    return {
        "codec": sc["structuralProperties"]["codec"], "container": custom["container"],
        "tc_in": cam.get("timecodeStart") or timing["sourceStart"],
        "tc_out": cam.get("timecodeEnd") or timing["sourceEnd"],
        "clip_name": fprops.get("clipName") or custom.get("clipName"),  # customData = payloads before the move
        "reel": cam.get("reelName"), "serial": cam.get("cameraSerialNumber"),
    }


def build(v, ctx):
    vt = v["version_type"]
    asset = ctx["assets"][v["asset_id"]]
    shot = ctx["shots"][asset["shot_id"]]
    uri = v["storage_uri"]
    fname = uri.rsplit("/", 1)[-1]
    ext = fname.rsplit(".", 1)[-1].lower()
    is_rework = bool(v.get("creative_context")) and vt == "EDIT_EXPORT" and fname.endswith("_v2.mov")
    ev = ctx["events"].get(v["id"], {})
    mi = media_inputs(v, asset)
    mi["tc_in"], mi["tc_out"] = timecodes(v, vt, v["asset_id"], is_rework, ctx)
    if vt == "EDIT_EXPORT":
        mi["codec"] = EDIT_CODEC_BY_TOOL.get(ev.get("tool"), EDIT_CODEC_DEFAULT)

    title = {
        "CAMERA_ORIGINAL": ("Camera Raw", "Camera-original raw capture (ARRIRAW) as recorded by the camera (POC example)."),
        "CAMERA_MASTER": ("Camera Master", "Full-resolution, debayered, viewable camera master derived from the camera raw (POC example)."),
        "DAILIES_PROXY": ("Dailies Proxy", "Downrezzed Full HD review proxy for dailies (POC example)."),
        "EDIT_EXPORT": ("Edit Export", "Editorial export of the shot from the edit (POC example)."),
    }[vt]
    name = f"{title[0]} {shot}" + (" v2" if is_rework else "")

    functional = {
        "CAMERA_ORIGINAL": "capture.ocf",
        "CAMERA_MASTER": MASTER_FUNCTIONAL_TYPE,
        "DAILIES_PROXY": "proxy.daily",
        "EDIT_EXPORT": "shot.editorial",
    }[vt]

    fprops = {}
    if vt == "CAMERA_ORIGINAL":
        fprops["cameraMetadata"] = {
            "cameraMake": "ARRI",
            "cameraModel": "ALEXA Mini LF",
            "cameraSerialNumber": mi["serial"],
            "exposureIndex": "800",
            "captureRate": str(FPS),
            "playbackRate": str(FPS),
            "frameWidth": FULL_RES[0],
            "frameHeight": FULL_RES[1],
            "reelName": mi["reel"],
            "timecodeStart": mi["tc_in"],
            "timecodeEnd": mi["tc_out"],
        }
        # Same place MovieLabs' own HSM examples put it (assetFC.functionalProperties.clipName). Not a schema-defined
        # property in v2.0/v2.6/v2.8; the validator does not check unknown keys here (see Matrix doc).
        fprops["clipName"] = mi["clip_name"]
        fprops["lensMetadata"] = {
            "lensMake": "ARRI",
            "lensModel": "Signature Prime 35/T1.8",
            "focalLength": "35",
            "tStop": "2.8",
        }
    else:
        fprops["timing"] = {
            "sourceStart": mi["tc_in"],
            "sourceEnd": mi["tc_out"],
            "duration": hhmmss_ff_duration(mi["tc_in"], mi["tc_out"]),
        }

    w, h = DAILIES_RES if vt == "DAILIES_PROXY" else FULL_RES
    # String, not number: a JSON `:24` in the SQL text is read by SQLAlchemy's text() as a bind parameter.
    sc_custom = {"frameRate": str(FPS), "container": mi["container"]}
    if vt == "CAMERA_ORIGINAL":
        sc_custom["colorSpace"] = "ARRI LogC3"
    elif vt == "CAMERA_MASTER":
        # Camera master stays in log (no look baked in); this is the debayered form of the raw.
        sc_custom["colorSpace"] = "ARRI LogC3"
        sc_custom["functionalTypeDetail"] = "video.debayered"  # OMC docs example term; not a controlled value
    elif vt in ("DAILIES_PROXY", "EDIT_EXPORT"):
        # Display-referred review/editorial colour (viewing transform applied). Convention, not a spec value.
        sc_custom["colorSpace"] = "Rec.709"

    asc = {
        "schemaVersion": SCHEMA_VERSION,
        "entityType": "AssetSC",
        "identifier": [{"identifierScope": SCOPE, "identifierValue": f"assetsc/{v['id']}"}],
        "structuralType": "digital.movingImage",
        "structuralProperties": {
            "codec": mi["codec"],
            "dimensions": {"width": f"{w}px", "height": f"{h}px"},
            "fileDetails": {
                "fileName": fname,
                "filePath": uri,
                "fileExtension": ext,
                "mediaType": MEDIA_TYPE[ext],
            },
        },
        "customData": [
            {"domain": CUSTOM_DOMAIN, "namespace": CUSTOM_NAMESPACE, "value": sc_custom}
        ],
    }
    if vt != "CAMERA_ORIGINAL" and ev.get("tool"):
        asc["software"] = [{"softwareName": ev["tool"]}]  # OMC `software` is an array

    payload = {
        "schemaVersion": SCHEMA_VERSION,
        "entityType": "Asset",
        "identifier": ident(v["asset_id"], v["id"]),
        "name": name,
        "description": title[1],
        "instanceInfo": {"createdOn": date_only(v["created_at"])},
        "provenance": {"createdOn": iso(v["created_at"])},
    }

    src = v.get("derived_from_version_id")
    if src and src != "NULL":
        parent = ctx["versions"][src]
        ref = {"identifier": ident(parent["asset_id"], parent["id"])}
        if is_rework:
            payload["version"] = {"versionNumber": "2", "RevisionOf": ref}
            reason = json.loads(v["creative_context"]).get("reason")
            if reason:
                payload["provenance"]["reason"] = reason
        else:
            payload["version"] = {"DerivationOf": ref}

    payload["assetFC"] = {"functionalType": functional, "functionalProperties": fprops}
    payload["AssetSC"] = asc
    return payload


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--emit", metavar="PATH", help="write payload array JSON for the OMC validator")
    g.add_argument("--write", action="store_true", help="rewrite omc_json in db/seed.sql in place")
    args = ap.parse_args()

    text = SEED.read_text()
    lines, tables = parse_seed(text)

    assets = {r["id"]: r for _, r, _, _ in rows_as_dicts(tables, "assets")}
    shots = {r["id"]: r["shot_code"] for _, r, _, _ in rows_as_dicts(tables, "shots")}
    events = {}
    for _, r, _, _ in rows_as_dicts(tables, "events"):
        if r.get("version_id") and r["version_id"] != "NULL":
            events[r["version_id"]] = r
    vrows = rows_as_dicts(tables, "versions")
    versions = {r["id"]: r for _, r, _, _ in vrows}
    camera_by_asset = {r["asset_id"]: r for _, r, _, _ in vrows if r["version_type"] == "CAMERA_ORIGINAL"}
    ctx = {"assets": assets, "shots": shots, "events": events, "versions": versions,
           "camera_by_asset": camera_by_asset}

    built = []
    for ln, r, cols, toks in vrows:
        built.append((ln, cols, toks, build(r, ctx)))

    if args.emit:
        Path(args.emit).write_text(json.dumps([b[3] for b in built], indent=1))
        print(f"wrote {len(built)} payloads to {args.emit}")
        return

    for ln, cols, toks, payload in built:
        idx = cols.index("omc_json")
        s, e, _ = toks[idx]
        js = json.dumps(payload, separators=(",", ":")).replace("'", "''")
        line = lines[ln]
        lines[ln] = line[:s] + f"'{js}'::jsonb" + line[e:]
    SEED.write_text("\n".join(lines))
    print(f"rewrote omc_json on {len(built)} version rows in {SEED}")


if __name__ == "__main__":
    sys.exit(main())
