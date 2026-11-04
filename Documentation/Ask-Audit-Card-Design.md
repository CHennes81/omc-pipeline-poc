# Ask page: Audit Information cards

Status: implemented 2026-11-03 (card layouts as specified by Christopher Hennes). Recommendations not yet adopted are listed at the end.

Code: `apps/web/src/components/VersionAuditCard.tsx` and `.css`, `apps/api/app/audit_cards.py`, `apps/api/app/ask_templates.py`, `apps/api/app/omc_fields.py`. Test: `apps/api/tests/test_audit_card_fields.py`.

## The pattern (all card types)

1. **Version Type is always on top** (with Created on the right).
2. **Information lines follow, most significant first.**
3. **Who made it is always last** before the separator.
4. **A thin separator line, then the Locator.** The Version ID sits on the same line, right-justified.

Every label ends with a colon. The values start at the same x position on every card: the label column is as wide as the longest label ("Captured By:" / "Timecode In:", about 6.4em) plus a 12 px gap. A value that is legitimately absent shows **(n/a)** (for example no Reason on a first export, or an export that has not been delivered). A field that a version type cannot carry is not shown on that card.

## Camera Original

```
Version Type: Camera Original              Created: 15 Jan 2026 @ 07:58
Camera:       ARRI ALEXA Mini LF · ALX-001234 · EI 800
Format:       ARRIRAW · MXF · 3840×2160 · 24 fps · ARRI LogC3
Lens:         ARRI Signature Prime 35/T1.8 · 35 mm · T2.8
Reel:         A001   Timecode In: 07:55:21:09   Timecode Out: 07:55:39:08
Captured By:  Camera Operator
------------------------------------------------------------------------
Locator: dam://camera_originals/011_001.mxf        Version ID: 550e8400-…
```

## Derived media (Camera Master, Dailies Proxy)

```
Version Type: Camera Master                Created: 15 Jan 2026 @ 08:08
Format:       ProRes 422 HQ · MOV · 3840×2160 · 24 fps · ARRI LogC3
Source:       Reel A001 · Clip A001C001_011_001.mxf
Timecode In:  07:55:21:09   Timecode Out: 07:55:39:08
Created By:   Cloud Transcode Service · Cloud Auto-Debayer & Master Transcode
------------------------------------------------------------------------
Locator: dam://camera_masters/011_001.mov          Version ID: 550e8400-…
```

Source is the reel and clip of the camera original this version came from, found by walking up the lineage.

## Edit Export (including reworks)

```
Version Type: Edit Export                  Created: 20 Jan 2026 @ 14:11
Format:        DNxHR HQX · MOV · 3840×2160 · 24 fps · Rec.709
Timecode In:   07:55:24:09   Timecode Out: 07:55:36:14
Reason:        Editorial re-cut for pacing
Delivered in:  (n/a)
Created By:    Editor · Avid Media Composer
------------------------------------------------------------------------
Locator: dam://edit_exports/011_001_v2.mov         Version ID: 550e8400-…
```

Reason is filled for reworks only. Delivered in lists the packages the export is a member of.

## Locator and Version ID

If `Locator: <uri>` and `Version ID: <id>` fit on one line with at least 24 px of space between them, they share one line, with the Version ID flush right. Otherwise the Locator label and the Version ID share the first line and the URI moves to the line below. The card measures a hidden single-line copy and re-checks whenever its width changes, so it adapts to the window size.

## Where each value comes from

Single-source rule (Phase B): values come from the version's `omc_json` through `omc_fields.py`, or from events and packages. A key is always present in the Ask evidence and is empty when not applicable.

- **Format:** codec, container, width and height, frame rate and colour space, all in `omc_json` (`AssetSC`).
- **Camera, Lens, Reel:** `cameraMetadata` and `lensMetadata` in `omc_json` (camera originals only).
- **Timecode In / Out:** `cameraMetadata.timecodeStart/End` for camera originals, `timing.sourceStart/End` for the rest. Shown as SMPTE `HH:MM:SS:FF`, frames included.
- **Source:** `omc_json` of the root camera original (`audit_cards.py` walks `derived_from_version_id`).
- **Reason:** `provenance.reason` in `omc_json`.
- **Created By / Captured By:** the event that created the version (`events.actor`, `events.tool`). Camera originals show the actor only, because the tool is already on the Camera line.
- **Delivered in:** `package_members` joined to `packages`.
- **Locator, Version ID, Created:** `versions.storage_uri`, `versions.id`, `versions.created_at`.

## Seed data: Edit Export tool and codec

Different cutting rooms use different editing systems, as on a real show. The editing tool is set per scene on the `EDIT_EXPORT_CREATED` events, and the codec follows the tool (`scripts/rewrite_seed_omc_json.py`):

- **Avid Media Composer** (scenes 011, 013, 015, 017): **DNxHR HQX**. DNxHD tops out at 1920×1080 and these exports are UHD, so DNxHR is the correct family.
- **Adobe Premiere Pro** (scenes 012, 016) and **DaVinci Resolve** (scene 014): **ProRes 422**.

The camera master stays ProRes 422 HQ. These pairings are conventions, not verified against a real production.

## Seed data: timecode

Modelled as on a real set (`scripts/rewrite_seed_omc_json.py`, deterministic per shot):

- **Camera original:** time-of-day timecode jam-synced to the production clock. Timecode In is the record-start wall-clock time (Pacific) from the CAPTURE event plus an arbitrary frame, so it never begins on an even `01:00:00:00` and the frame can be non-zero. Timecode Out is In plus a 12 to 48 second take plus frames, and always ends on a non-zero frame.
- **Camera master and dailies proxy:** transcodes of the same essence, so the same In and Out as the camera original.
- **Edit export:** the part of the take used in the cut, so a sub-range (In 1 to 4 s later, Out 1 to 3 s earlier, both with frames). A rework has its own trim.

## Not adopted yet (earlier recommendations)

- Stage-coloured accent on each card header.
- "Latest versions by type" is in alphabetical order (Camera Master before Camera Original); lifecycle order would read better.
- Compact rows for package-member answers (12 to 20 full cards is a long scroll).
- Connectors between the cards of a lineage answer, with a one-line summary of what changed.
- A stat card for the archive-status answer, which currently uses a generic key/value list.
