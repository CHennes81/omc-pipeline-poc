# Ask page: Audit Information cards — audit and layout recommendations

> **Status:** audit and recommendations only; nothing here is implemented except Part 1 (every field on the current card is populated, commit `6692f0d`). Written 2026-11-03.
> **Sources:** `apps/web/src/components/VersionAuditCard.tsx`, `apps/web/src/pages/Ask.tsx`, `apps/api/app/ask_templates.py`, the 112 seeded `omc_json` payloads, the `events` / `packages` / `creative_context` data, and `Documentation/OMC-Asset-Metadata-Matrix.md`.

## 1. Part 1 result: the current card is fully populated

The card shows nine fields: **Version Type, Created, Codec, FPS, Timecode In, Timecode Out, Reel, Version ID, Locator**. Before this change only some Ask answers filled them in; the lineage-chain answer filled none of codec / fps / timecodes / reel, and the relink answer left codec, created, locator and reel empty.

Now all five Ask templates that return version evidence select one shared column set (`VERSION_CARD_COLUMNS` in `ask_templates.py`), read from `omc_json`. The rule applied:

| Field                                                                             | Camera Original | Camera Master | Dailies Proxy | Edit Export (incl. rework) |
| --------------------------------------------------------------------------------- | --------------- | ------------- | ------------- | -------------------------- |
| Version Type, Created, Codec, FPS, Timecode In, Timecode Out, Locator, Version ID | always          | always        | always        | always                     |
| **Reel**                                                                          | **always**      | not carried   | not carried   | not carried                |

Reel is camera metadata (`cameraMetadata.reelName`); the payloads of the later stages do not carry it, so those cards correctly show "—". `tests/test_audit_card_fields.py` enforces this over every template, shot and package (it fails on the previous code). Checked in the UI for the lineage-chain and relink answers.

## 2. Findings in the current design

1. **One layout for four different kinds of asset.** The same three rows are used for a raw camera file, a debayered master, a review proxy and an editorial export. The Reel row is a permanent dash on three of the four types.
2. **Timecode frames are silently dropped.** `normalizeTimecode` turns `01:00:10:12` into `01:00:10.000`: the comment says the frame rate is unknown, but the card shows FPS right beside it. All seeded timecodes end in `:00`, which hides this today; any real clip with a non-zero frame count would be wrong. Editorial users expect SMPTE (`01:00:15:00`).
3. **"Latest versions by type" is in alphabetical order**, so Camera Master appears before Camera Original. Lifecycle order (Camera Original, Camera Master, Dailies Proxy, Edit Export) is what a reader expects; the lineage-chain answer already uses it.
4. **A rework looks identical to the original.** In the lineage answer for 011_001 the two Edit Export cards differ only by date and locator. The data has `version.versionNumber = 2`, `RevisionOf`, `provenance.reason` and `creative_context.rework_type`; none is shown.
5. **Rich data the payload holds is not shown at all:** container, resolution, colour space, file name, camera / lens, clip name, who or what made the version (events `actor` / `tool`, payload `software`), the parent version, and package membership.
6. **The card has no visual identity per type.** "Version Type: Camera Original" is a label and value like any other, and the Dashboard's per-stage colours (CAMERA_MASTER, DAILIES, EDIT_EXPORT, …) are not reused.
7. **Long lists become a very long scroll.** A package-members answer renders 12 or 20 full cards.
8. **Non-version evidence is inconsistent.** Shots use `ShotsAuditCard`; the `archive_status` answer (`{"archived": 8, "total": 28}`) falls to a generic key/value list.
9. **Version ID is a full 36-character UUID** here, while the Shot Detail page abbreviates to `...` plus the last 8 characters. Reasonable for an audit view, but a deliberate choice rather than an accident should be made.

## 3. What each version type can carry

From the seeded payloads, `events`, `creative_context` and package membership. **Bold** = shown on the card today.

| Attribute                                           | Camera Original (`capture.ocf`)        | Camera Master (`shot`)                                          | Dailies Proxy (`proxy.daily`)                          | Edit Export (`shot.editorial`)                                        |
| --------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------ | --------------------------------------------------------------------- |
| **Codec**                                           | ARRIRAW                                | ProRes 422 HQ                                                   | H.264                                                  | ProRes 422                                                            |
| Container                                           | MXF                                    | MOV                                                             | MP4                                                    | MOV                                                                   |
| Resolution                                          | 3840×2160                              | 3840×2160                                                       | 1920×1080                                              | 3840×2160                                                             |
| **FPS**                                             | 24                                     | 24                                                              | 24                                                     | 24                                                                    |
| Colour space                                        | ARRI LogC3                             | ARRI LogC3 (log, no look)                                       | Rec.709                                                | Rec.709                                                               |
| **Timecode In / Out** (+ duration)                  | `cameraMetadata.timecodeStart/End`     | `timing.sourceStart/End`, `duration`                            | same                                                   | same                                                                  |
| **Reel**                                            | `cameraMetadata.reelName`              | no                                                              | no                                                     | no                                                                    |
| Clip name                                           | `functionalProperties.clipName`        | no                                                              | no                                                     | no                                                                    |
| Camera (make, model, serial, EI)                    | ARRI ALEXA Mini LF, ALX-001234, EI 800 | no                                                              | no                                                     | no                                                                    |
| Lens (model, focal length, T-stop)                  | Signature Prime 35/T1.8, 35 mm, T2.8   | no                                                              | no                                                     | no                                                                    |
| File name / media type                              | `011_001.mxf`, application/mxf         | `.mov`, video/quicktime                                         | `.mp4`, video/mp4                                      | `.mov`, video/quicktime                                               |
| Made by (event actor / tool)                        | Camera Operator / ARRI ALEXA Mini LF   | Cloud Transcode Service / Cloud Auto-Debayer & Master Transcode | Cloud Transcode Service / Cloud Auto-Dailies Transcode | Editor / Avid Media Composer                                          |
| Derived from (parent)                               | none (root)                            | Camera Original                                                 | Camera Master                                          | Dailies Proxy (v1) or prior Edit Export (v2, `RevisionOf`)            |
| Revision (`versionNumber`, `reason`, `rework_type`) | no                                     | no                                                              | no                                                     | rework only: v2, e.g. "Director notes - creative rework", `editorial` |
| In packages                                         | no                                     | Archive (8)                                                     | no                                                     | Turnover (12), Archive (12)                                           |
| **Created**, **Locator**, **Version ID**            | yes                                    | yes                                                             | yes                                                    | yes                                                                   |

## 4. Recommendation: card families, not one card

The right layout depends on **two things**: the version type (what it carries) and the answer type (how many cards, and why the reader asked). Recommended:

### 4.1 By version type

**A. Capture card — Camera Original.** Answers "what did the camera record, and where is it". Sections: Format, Camera and lens, Timecode, Source.

```
┌──────────────────────────────────────────────────────────────┐
│ ▌CAMERA ORIGINAL                         15 Jan 2026 · 07:58 │
│ ▌011_001 · clip A001C001_011_001.mxf · Reel A001             │
│ Format    ARRIRAW · MXF · 3840×2160 · 24 fps · ARRI LogC3    │
│ Camera    ARRI ALEXA Mini LF · ALX-001234 · EI 800           │
│ Lens      Signature Prime 35/T1.8 · 35 mm · T2.8             │
│ Timecode  01:00:00:00 → 01:00:15:00   (15 s)                 │
│ Recorded by  Camera Operator                                 │
│ Locator   dam://camera_originals/011_001.mxf                 │
│                                    Version ID  …446655440201 │
└──────────────────────────────────────────────────────────────┘
```

**B. Derived-media card — Camera Master and Dailies Proxy.** One family, two variants. Answers "what was made from what, by which process, in what format". No camera or lens (they belong to the original). Reel is replaced by a labelled **Source** line (reel and clip of the root camera original), which is a lineage lookup, not a stored value.

```
┌──────────────────────────────────────────────────────────────┐
│ ▌CAMERA MASTER                           15 Jan 2026 · 08:08 │
│ ▌debayered, viewable master                                  │
│ Derived from  Camera Original …446655440201                 │
│ Made by       Cloud Auto-Debayer & Master Transcode          │
│ Format    ProRes 422 HQ · MOV · 3840×2160 · 24 fps · LogC3   │
│ Timecode  01:00:00:00 → 01:00:15:00   (15 s)                 │
│ Source    Reel A001 · A001C001_011_001.mxf                   │
│ Locator   dam://camera_masters/011_001.mov                   │
└──────────────────────────────────────────────────────────────┘
```

The Dailies Proxy variant is the same with `1920×1080`, `H.264 · MP4`, `Rec.709` and the dailies tool; its header line reads "review proxy". Emphasise the colour space on both: LogC3 (no look) versus Rec.709 (viewing transform) is the most useful thing to distinguish them.

**C. Editorial card — Edit Export.** Answers "who cut this, and is it the current one". Adds revision and delivery.

```
┌──────────────────────────────────────────────────────────────┐
│ ▌EDIT EXPORT  v2  ·  REWORK              20 Jan 2026 · 14:11 │
│ ▌Revision of Edit Export …446655440501                       │
│ Reason    Director notes - creative rework  (editorial)      │
│ Made by   Editor · Avid Media Composer                       │
│ Format    ProRes 422 · MOV · 3840×2160 · 24 fps · Rec.709    │
│ Timecode  01:00:00:00 → 01:00:15:00   (15 s)                 │
│ Delivered in   [Turnover: VFX Vendor Alpha] [Archive]        │
│ Locator   dam://edit_exports/011_001_v2.mov                  │
└──────────────────────────────────────────────────────────────┘
```

A first-cut Edit Export has no Revision band and reads "Derived from Dailies Proxy …". Package chips link to the package.

### 4.2 By answer type

| Answer (template)                      | Cards            | Recommended presentation                                                                                                                                                                                                    |
| -------------------------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Latest camera original / relink keys   | 1                | Full **Capture card**. For relink, put the relink keys (fps, timecode in/out, clip, reel) in a highlighted block at the top, since that is the question.                                                                    |
| Lineage chain to latest edit export    | 4 to 6           | A **vertical chain** of full cards (family A, B, B, C) joined by connectors, with a one-line **delta** on each connector, e.g. `ARRIRAW → ProRes 422 HQ · MXF → MOV · LogC3 unchanged`. Rework cards get the revision band. |
| Latest versions by type                | up to 4          | Full cards in **lifecycle order** (fix the alphabetical order, finding 3).                                                                                                                                                  |
| Package members                        | 12 to 20         | **Compact rows**, grouped by version type: type chip · shot · codec · resolution · timecode · locator, expandable to the full card. Show a count per group.                                                                 |
| Archive status (summary)               | stat, not a card | A small **stat card** ("8 of 28 shots archived", progress bar) instead of the generic key/value list.                                                                                                                       |
| Shot lists (existing `ShotsAuditCard`) | n                | Keep as is.                                                                                                                                                                                                                 |

### 4.3 Shared rules for every card

- **Type identity:** a left accent bar and header chip in the stage colour the Dashboard already uses; the type name becomes the header, not a "Version Type:" row.
- **Never show a field that cannot exist for that type.** Hide the Reel row on derived and editorial cards (replace with Source where useful) instead of a permanent "—". Keep "—" only for a field the type _can_ carry but this record lacks, so a dash always means "missing".
- **SMPTE timecode** (`HH:MM:SS:FF`, using the version's own FPS) with a duration. Fix `normalizeTimecode`, which drops frames today.
- **Timestamps** with the time zone, or a documented fixed zone.
- **Version ID:** keep the full UUID on the audit card (it is an audit view), de-emphasised as now, and make it copyable; the abbreviated form stays on Shot Detail.

## 5. What each recommendation needs

| Change                                                                       | New data needed                                                                                          | Size   |
| ---------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- | ------ |
| Per-type field sets; hide Reel on derived/editorial; SMPTE fix; stage accent | none (card only)                                                                                         | small  |
| Format line (container, resolution, colour space)                            | three more `omc_fields` SQL expressions; no schema change                                                | small  |
| Camera / lens block                                                          | `cameraMetadata` / `lensMetadata` paths                                                                  | small  |
| Made by (actor, tool)                                                        | join `events` on `version_id`                                                                            | small  |
| Derived from / revision band / reason                                        | parent id (already in lineage; join otherwise), `versionNumber`, `provenance.reason`, `creative_context` | medium |
| Package chips                                                                | join `package_members` / `packages`                                                                      | medium |
| Source reel for derived cards                                                | recursive lookup to the root camera original                                                             | medium |
| Compact rows; chain connectors with deltas; stat card; lifecycle ordering    | front-end layout work; ordering is a one-line `ORDER BY`                                                 | medium |

Keep the single-source rule from Phase B: every new value is read from `omc_json` (or events) through `omc_fields.py`, with a field added to the card-field test, so the card can never disagree with the data.

## 6. Suggested order

1. **Quick wins:** lifecycle ordering, SMPTE timecode, hide Reel where it cannot exist, stage-coloured headers.
2. **Per-type cards (A, B, C)** with the Format line, made-by and revision band.
3. **Answer-specific layouts:** compact package rows, lineage connectors with deltas, archive stat card.

## 7. Decisions needed

1. **Reel on derived cards:** hide it, or replace it with a "Source" reel and clip looked up from the root camera original?
2. **Timecode:** SMPTE with duration everywhere (recommended)?
3. **Package members:** compact rows (recommended) or keep full cards?
4. **Lineage chain:** connectors with change deltas, or plain stacked cards?
5. **Version ID:** keep the full UUID on audit cards?
