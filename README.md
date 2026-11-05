# JetBrains IDE Hashes

Historical SHA-256 hashes of JetBrains macOS installers and the main application
executables inside them. Inspired by
[JetBrains IDE Release Dates](https://github.com/ChrisCarini/jetbrains-ide-release-dates).

**[Browse the IDE tables and current coverage](ides/README.md).**
Missing hashes are explicitly marked; the initial historical backfill is not complete.

Each product page starts directly with a table of **released versions**, followed by
a separate table of **EAP, RC, preview, and every other non-release channel**:

| Version | Build version | Installer type | Installer SHA256 | Application SHA256 | Release date |
| --- | --- | --- | --- | --- | --- |

Rows are sorted by **version**, then **build version**, then **installer type**, all
descending. Version and build components are compared numerically, so `2026.10`
comes before `2026.9`, regardless of release date.

The application hash is the raw main launcher, such as
`IntelliJ IDEA.app/Contents/MacOS/idea` or
`PyCharm.app/Contents/MacOS/pycharm`. It is **not** a hash of the entire `.app`
directory, a signing CDHash, or a notarization/signature verdict.

## Coverage

The source is JetBrains' public
[`/products` API](https://data.services.jetbrains.com/products), **without a
release-type or latest-version filter**. Discovery includes products classified
as `IDE`, plus Rider and Gateway, which the API classifies differently. Legacy
Community editions and discontinued products are retained under their stable
product codes rather than collapsed into renamed products.

Installer types are `mac` and `macM1`, plus the equivalent `macos_x64` and
`macos_aarch64` aliases used by Air. Tables retain the API's actual type names.
Alternate JBR distributions and Windows/Linux installers are outside this project's
scope. Ignored download types are recorded in each product's JSON history.

Some products classified as IDEs are plugins or hosted services, and some old
releases have empty download metadata. Only advertised macOS installer rows appear
in the main tables: a version with one architecture shows only that architecture.
Versions with an entirely empty `downloads` object are listed once per build and
channel under **Collection notes**. Missing architectures and nonempty downloads
containing only non-macOS artifacts are not listed in that subsection. Collection
errors remain visible in the notes.

The JSON history retains unadvertised installer entries and records empty-download
releases separately on catalog refresh; older histories without that information
are not assumed to have empty downloads. Neither omission nor empty metadata
proves that an installer never existed.

## Reissued versions and historical integrity

The canonical data lives in [`data/`](data/), one JSON file per product. The
collector never replaces a whole history with the latest API response:

- A different **build number** for an existing version creates another record.
  Advertised installers for both builds remain in the tables, with their
  versions/builds **bolded** within the same release channel.
- A different **installer checksum**, even at the same URL with the same version
  and build, preserves the old payload and creates a new revision. These rows
  are marked `(repacked)`.
- Completed hashes survive disappearing releases, renamed products, stale job
  artifacts, and later API responses. Conflicting application hashes for the
  same installer are rejected rather than overwritten.
- A queued historical installer is always checked against its **previously
  captured SHA-256**. If the URL now serves another payload, it is not attributed
  to the old build. Bundle build metadata is also compared with the API build
  when available.

If the API simultaneously advertises the same URL for different builds, that
ambiguity is reported rather than assigning one sidecar checksum to both builds.
An older saved catalog cannot rewind the current build identities.

History can only preserve observations the project has actually made. It cannot
recover an overwritten build that vanished before a poll, an unpublished checksum,
or an executable whose installer is no longer available. Catalog labels and
published checksums are upstream observations, not independent security endorsements.

## Scheduled collection

[Update JetBrains IDE hashes](.github/workflows/update-hashes.yml) runs daily at
**06:23 UTC**, and can also be started manually:

1. An Ubuntu job discovers the selected products and snapshots every release channel.
2. At most **two macOS jobs run concurrently**, each processing one IDE.
3. Each IDE gets at most **10 installer download attempts** and **40 minutes** by
   default. Successful work is checkpointed after each artifact. New/never-attempted
   builds take priority over retries, so one broken URL cannot stall the backfill.
4. Product checkpoints are uploaded even when individual artifacts fail. A final
   Ubuntu job merges the successful progress into the latest default branch,
   regenerates the Markdown, and commits only `data/` and `ides/`.

All current checksum sidecars for the selected IDEs are refreshed on each run to detect repacked
installers. The download limit applies to full installers; reaching a time/download
budget leaves explicit pending work for the next run. Actual collection failures
remain visible as failed jobs and in the product's collection notes.

Manual runs accept an optional `product` input with a JetBrains IDE product code,
such as `IIU` (IntelliJ IDEA), `PCP` (PyCharm), or `RD` (Rider). Find other codes in
the [IDE index](ides/README.md). Leave it blank to process all discovered IDEs,
as scheduled runs do. Selecting one IDE still includes every release channel;
unknown codes fail discovery rather than falling back to all IDEs.

```bash
gh workflow run update-hashes.yml -f product=IIU
```

Manual runs can also increase `max_installers` and `max_minutes` (up to 240 minutes).
The initial backfill can take many runs and substantial aggregate bandwidth; there
is no claim that every historical app hash is available immediately.

Installer downloads log their start, progress roughly every 10 seconds while data
arrives (downloaded/total MiB, percentage, and average speed), and completion after
SHA-256 verification. Messages are flushed immediately to stderr so progress is
visible in GitHub Actions logs. Each retry starts its progress from zero.

Only the publication job receives `contents: write`. Actions are pinned to commit
SHAs, updates cannot overlap, and publication is restricted to the default branch.
The branch must permit commits from `github-actions[bot]`; otherwise publication
fails without force-pushing. Per-product artifacts remain available for 30 days
for recovery:

```bash
# After downloading/extracting a run's hashes-* artifacts into incoming/:
python -m jetbrains_hashes merge --from-dir incoming
```

No hosted workflow runs until this repository is pushed to GitHub and Actions is
enabled. Nothing in this project creates a GitHub repository or changes its visibility.

## Run locally

Python **3.11+** is required. The collector uses only the standard library.
DMG application hashing requires **macOS and `hdiutil`**; catalog, checksum,
Markdown, and ZIP operations also work on Linux.

```bash
# Refresh IntelliJ IDEA, collect up to 10 installers, and update its tables.
python -m jetbrains_hashes sync --product IIU

# Fetch all published hashes for one IDE without downloading full installers.
python -m jetbrains_hashes sync --product PCP --checksums-only

# Use an external disk for the single temporary installer.
python -m jetbrains_hashes sync --product RD --work-dir /Volumes/External/scratch

# Choose a larger, still bounded backfill.
python -m jetbrains_hashes sync --product IIU --max-installers 50 --max-minutes 120

# Discover all IDEs and generate metadata-only tables without downloading installers.
python -m jetbrains_hashes discover --seed

# Prepare workflow snapshots for one IDE, including every release channel.
python -m jetbrains_hashes discover --product PCP

# Rebuild Markdown deterministically from the saved history; no network access.
python -m jetbrains_hashes render
```

`jetbrains_sha256.py` is an alternative entry point for these same subcommands.
The original release-only `idea-hashes/` output can be imported without losing the
hashes already collected:

```bash
python -m jetbrains_hashes import-legacy --source idea-hashes
```

The collector downloads **one installer at a time**, verifies its checksum, and
mounts DMGs read-only without copying or launching the application. ZIP launchers
are streamed directly from the archive. A workspace needs the compressed installer
plus **1 GiB of free-space reserve**; space is checked before and during downloads.
The image is detached and the download deleted before continuing.

Rerunning resumes missing hashes and refreshes the catalog. Normal interruptions
clean up the active installer. Forced termination or power loss can leave a
`jetbrains-sha256-*` workspace; detach any associated image before removing that
specific workspace. A failed detach stops collection and preserves the workspace
rather than risking recursive deletion of a mounted filesystem.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/pytest -q
```

Tests use local fixtures rather than JetBrains downloads. On macOS, a native test
also creates, mounts, hashes, and cleans up a small synthetic DMG. CI runs on
macOS 15 with Python 3.13 for relevant pull-request changes and pushes to `main`,
or manually. Feature-branch pushes do not trigger duplicate pull-request runs.
Generated history is merged semantically, not guarded by fragile Markdown
line-count comparisons.

## License

[Apache License 2.0](LICENSE). JetBrains product names and software remain the
property of their respective owners; this repository distributes metadata and
hashes, not JetBrains installers or applications.
