#!/usr/bin/env python3
"""Rebuild versions.omc_json inside db/seed.sql as OMC-JSON v2.8 payloads.

db/seed.sql (not scripts/generate_seed.py, which is stale) is the source of truth for seed data.
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
import json
import re
import sys
from pathlib import Path

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


def build(v, ctx):
    vt = v["version_type"]
    asset = ctx["assets"][v["asset_id"]]
    shot = ctx["shots"][asset["shot_id"]]
    uri = v["storage_uri"]
    fname = uri.rsplit("/", 1)[-1]
    ext = fname.rsplit(".", 1)[-1].lower()
    is_rework = bool(v.get("creative_context")) and vt == "EDIT_EXPORT" and fname.endswith("_v2.mov")
    ev = ctx["events"].get(v["id"], {})

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
            "cameraSerialNumber": asset["camera_serial"],
            "exposureIndex": "800",
            "captureRate": str(FPS),
            "playbackRate": str(FPS),
            "frameWidth": FULL_RES[0],
            "frameHeight": FULL_RES[1],
            "reelName": asset["reel_or_roll"],
            "timecodeStart": v["timecode_in"],
            "timecodeEnd": v["timecode_out"],
        }
        fprops["lensMetadata"] = {
            "lensMake": "ARRI",
            "lensModel": "Signature Prime 35/T1.8",
            "focalLength": "35",
            "tStop": "2.8",
        }
    else:
        fprops["timing"] = {
            "sourceStart": v["timecode_in"],
            "sourceEnd": v["timecode_out"],
            "duration": hhmmss_ff_duration(v["timecode_in"], v["timecode_out"]),
        }

    w, h = DAILIES_RES if vt == "DAILIES_PROXY" else FULL_RES
    # String, not number: a JSON `:24` in the SQL text is read by SQLAlchemy's text() as a bind parameter.
    sc_custom = {"frameRate": str(FPS), "container": v["container"]}
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
            "codec": v["codec"],
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
    ctx = {"assets": assets, "shots": shots, "events": events, "versions": versions}

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
