| Version | Build version | Installer type | Installer SHA256 | Application SHA256 | Release date |
| --- | --- | --- | --- | --- | --- |
| 6.0 | 3385 | `mac` | `113749a54abd6c537bf1838a91cf35a70b2fdf04cfc4880eb906448b3156053e` | Quarantined (see collection notes) | 2017-03-09 |

## EAP, RC, preview, and other non-release builds

| Version | Build version | Installer type | Installer SHA256 | Application SHA256 | Release date |
| --- | --- | --- | --- | --- | --- |

## Collection notes

Product: **Youtrack Workflow Editor** (`YTWE`). [Machine-readable history](../data/YTWE.json).

Installer hashes: **1/1**; application hashes: **0/1**; not advertised: **1**; quarantined: **1**. [All collection failures](COLLECTION_FAILURES.md).

Bold versions/builds have multiple observed build numbers for the same version and channel. `(repacked)` means multiple installer hashes were observed for the same version, build, channel, and installer type. History is retained even after entries disappear from the API.

Rows are sorted by version, build version, and installer type, descending, with numeric version/build components compared numerically rather than by release date.

`Pending` means collection has not completed. Rows without an advertised macOS installer are omitted. Missing hashes are not inferred. Application hashes cover the bundle's main `Contents/MacOS/` executable, not the bundle or signing CDHash.

### Quarantined after repeated failures

These records are excluded from automatic collection until their inputs change or an explicit retry is requested. Missing hashes are not treated as verified.

| Version | API build | Channel | Installer type | Installer SHA256 | State | Identical failures | Last result / attempt (UTC) | Stage and reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6.0 | 3385 | release | `mac` | `113749a54abd6c537bf1838a91cf35a70b2fdf04cfc4880eb906448b3156053e` | Quarantined | 5/5 | 2026-11-12T15:59:07.818152+00:00 | application: Invalid application metadata: Invalid file |
