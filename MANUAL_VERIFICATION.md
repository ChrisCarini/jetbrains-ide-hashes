# Manually verifying an installer and its application hash

Use **macOS**, Python 3.11+, and the repository checkout. `curl`, `shasum`,
`hdiutil`, `plutil`, and `/usr/libexec/PlistBuddy` are supplied by macOS. Do not
launch the downloaded application or change macOS security settings.

The [collection failure report](ides/COLLECTION_FAILURES.md) lists **all saved
failures**, including historical attempts. It is not a list of only the latest
run's attempts. A run's `ERROR CODE (version, build, channel, platform)` lines
identify the exact records it tried.

Work on one record at a time, starting from the latest `main` after any publishing
job finishes. Keep the API version, build, channel, platform, URLs, size, and
installer checksum unchanged. In particular, keep the API's `build` separate
from the executable bundle's actual `app_build`.

## Checklist from the completed 2026-11-09 run

The [15:43 UTC run](https://github.com/ChrisCarini/jetbrains-ide-hashes/actions/runs/42647467123)
finished at 16:19 UTC. Its logs contain **56 failed installer records across 12
products**: 43 bundle-build mismatches, 12 metadata parsing failures, and one
installer checksum mismatch. This is a fixed snapshot of that completed run,
not the newer in-progress run or the entire historical backlog.

`mac` and `macM1` are separate installers and must be verified separately. Rows
with both platforms below represent two failures. The observed bundle builds
come from CI diagnostics; independently confirm them on your machine.

| IDE | Version | API build | Channel | Platform | Observed bundle build / failure |
| --- | --- | --- | --- | --- | --- |
| `AC` | 3.1.8 | `139.1803` | release | mac | Bundle: `OC-139.1803.27` |
| `AC` | 3.2.1 | `141.3058` | release | mac | Bundle: `OC-141.3058.49` |
| `AC` | 3.3.4 | `143.2370` | release | mac | Bundle: `OC-143.2370.39` |
| `AC` | 2016.1.2 | `145.971` | release | mac | Bundle: `OC-145.971.26` |
| `AC` | 2016.1.2b | `145.972` | release | mac | Bundle: `OC-145.972.5` |
| `AC` | 2016.1.3 | `145.1617` | release | mac | Bundle: `OC-145.1617.5` |
| `AC` | 2016.1.4 | `145.2073` | release | mac | Bundle: `OC-145.2073.4` |
| `AC` | 2016.2 | `162.1236` | release | mac | Bundle: `OC-162.1236.19` |
| `CL` | 1.1.2 | `141.3058` | release | mac | Bundle: `CL-141.3058.48` |
| `CL` | 1.2.5 | `143.2370` | release | mac | Bundle: `CL-143.2370.46` |
| `CL` | 2016.1.3 | `145.1617` | release | mac | Bundle: `CL-145.1617.9` |
| `DG` | 1.0 | `143.1410` | release | mac | Bundle: `DB-143.1410.7` |
| `DG` | 1.0.1 | `143.1411` | release | mac | Bundle: `DB-143.1411.5` |
| `DG` | 1.0.4 | `143.2371` | release | mac | Bundle: `DB-143.2371.6` |
| `DG` | 1.0.5 | `143.2372` | release | mac | Bundle: `DB-143.2372.1` |
| `DG` | 2016.1 | `145.862` | release | mac | Bundle: `DB-145.862.4` |
| `DG` | 2016.1.1 | `145.863` | release | mac | Bundle: `DB-145.863.1` |
| `DG` | 2016.1.2 | `145.864` | release | mac | Bundle: `DB-145.864.1` |
| `DG` | 2016.3.1 | `163.9735.5` | release | mac | Bundle: `DB-163.9735.6` |
| `DG` | 2025.3.5.1 | `253.31033.213` | release | mac, macM1 | Bundle: `253.31033.21` |
| `DS` | 2025.2.4 | `252.28539.109` | release | mac, macM1 | Bundle: `252.28539.155` |
| `IIC` | 11.0.2 | `111.277` | release | mac | Invalid application metadata: unexpected key at line 10 |
| `IIC` | 14.0.5 | `139.1803` | release | mac | Bundle: `IC-139.1803.20` |
| `IIC` | 14.1.7 | `141.3058` | release | mac | Bundle: `IC-141.3058.30` |
| `IIU` | 14.0.5 | `139.1803` | release | mac | Bundle: `IU-139.1803.20` |
| `IIU` | 14.1.7 | `141.3058` | release | mac | Bundle: `IU-141.3058.30` |
| `MPS` | 2019.3.6 | `193.1617` | release | mac | Invalid application metadata: Invalid file |
| `MPS` | 2019.3.7 | `193.1623` | release | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.1.3 | `201.8538.1503` | release | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.1.4 | `201.8743.1536` | release | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.2 | `202.6397.948` | release | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.2-EAP3 | `202.6397.665` | eap | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.2-EAP4 | `202.6397.798` | eap | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.2-RC1 | `202.6397.898` | eap | mac | Invalid application metadata: Invalid file |
| `MPS` | 2020.3-EAP1 | `203.4818.451` | eap | mac | Invalid application metadata: Invalid file |
| `MPS` | 2026.2 | `262.11879.701` | release | macM1 | Invalid application metadata: Invalid file |
| `PCC` | 4.0.7 | `139.1803` | release | mac | Bundle: `PC-139.1803.14` |
| `PCC` | 4.5.5 | `141.3058` | release | mac | Bundle: `PC-141.3058.47` |
| `PCC` | 5.0.6 | `143.2371` | release | mac | Bundle: `PC-143.2371.1` |
| `PCP` | 1.5.4 | `107.756` | release | mac | Bundle: `PY-107.576` |
| `PCP` | 4.0.7 | `139.1803` | release | mac | Bundle: `PY-139.1803.14` |
| `PCP` | 4.5.5 | `141.3058` | release | mac | Bundle: `PY-141.3058.47` |
| `PCP` | 5.0.6 | `143.2371` | release | mac | Bundle: `PY-143.2371.1` |
| `PS` | 3.0.3 | `111.271` | release | mac | Bundle: `PS-111.344` |
| `PS` | 8.0.4 | `139.1803` | release | mac | Bundle: `PS-139.1803.25` |
| `PS` | 9.0.3 | `141.3058` | release | mac | Bundle: `PS-141.3058.33` |
| `PS` | 10.0.4 | `143.2370` | release | mac | Bundle: `PS-143.2370.33` |
| `PS` | 2016.1.2 | `145.1616` | release | mac | Bundle: `PS-145.1616.3` |
| `PS` | 2018.3.6 | `183.6156.29` | release | mac | **Installer SHA-256 mismatch; stop before hashing the app** |
| `WS` | 9.0.4 | `139.1803` | release | mac | Bundle: `WS-139.1803.34` |
| `WS` | 10.0.5 | `141.3058` | release | mac | Bundle: `WS-141.3058.28` |
| `WS` | 11.0.4 | `143.2370` | release | mac | Bundle: `WS-143.2370.35` |
| `WS` | 2016.1.3 | `145.1616` | release | mac | Bundle: `WS-145.1616.9` |
| `YTWE` | 6.0 | `3385` | release | mac | Invalid application metadata: Invalid file |

Product names and codes are listed in the [IDE index](ides/README.md).
The MPS rows above are only the ten attempted in this run; the full failure
report contains other outstanding MPS versions.

For PhpStorm 2018.3.6, the recorded installer digest is
`00764bd3f9fcb2694c3691292f4d323c3575e9057b33cd17cd36c532dc43a27c`, while CI
downloaded bytes with digest
`b2bfc36b835840f7cfec1071ad83da31dd6a199319425eb554808d2aa4ed02cc`.
Do not use the latter installer to fill the former record's application hash.

## 1. Select the exact record

Run the following sections in the **same Bash session** (`bash`). These example
values select the AppCode 2016.1.4 failure. Change them for each checklist entry.
If there are multiple payload revisions, also set `EXPECTED_INSTALLER_SHA256`
to the particular recorded digest you are investigating.

```bash
set -euo pipefail

export PRODUCT=AC
export VERSION=2016.1.4
export BUILD=145.2073
export CHANNEL=release
export PLATFORM=mac
export EXPECTED_INSTALLER_SHA256=7354ddf250cd56cb68be83017b31d92c301a80ec8794bddb05e735eea862121d
WORK="$(mktemp -d "${TMPDIR:-/tmp}/jetbrains-manual.XXXXXX")"
export WORK
printf 'Keep this workspace path: %s\n' "$WORK"

python3 - <<'PY'
import json
import os
from pathlib import Path

key = tuple(os.environ[name] for name in ("VERSION", "BUILD", "CHANNEL", "PLATFORM"))
expected = os.environ.get("EXPECTED_INSTALLER_SHA256", "")
path = Path("data") / f"{os.environ['PRODUCT']}.json"
rows = [
    row for row in json.loads(path.read_text())["records"]
    if tuple(row[name] for name in ("version", "build", "release_type", "platform")) == key
    and (not expected or row["installer_sha256"] == expected)
]
if len(rows) != 1:
    raise SystemExit(f"Expected exactly one record, found {len(rows)}; check the identity/digest")
row = rows[0]
if not row["installer_url"] or not row["installer_sha256"]:
    raise SystemExit("No recorded installer URL/checksum; establish provenance before proceeding")
Path(os.environ["WORK"], "record.json").write_text(json.dumps(row, indent=2) + "\n")
print(json.dumps(row, indent=2))
PY

record_field() {
  python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]])' \
    "$WORK/record.json" "$1"
}

INSTALLER_URL="$(record_field installer_url)"
CHECKSUM_URL="$(record_field checksum_url)"
EXPECTED="$(record_field installer_sha256)"
case "$INSTALLER_URL" in
  *.dmg) export INSTALLER="$WORK/installer.dmg" ;;
  *.zip) export INSTALLER="$WORK/installer.zip" ;;
  *) printf 'Unsupported installer format: %s\n' "$INSTALLER_URL"; exit 1 ;;
esac
```

For another record, change or unset `EXPECTED_INSTALLER_SHA256`; do not reuse the
AppCode digest. Keep separate workspaces for different installers.

## 2. Download and verify the installer before opening it

```bash
curl --fail --location --retry 3 --proto '=https' --proto-redir '=https' \
  --output "$INSTALLER" "$INSTALLER_URL"

shasum -a 256 "$INSTALLER"
printf '%s  %s\n' "$EXPECTED" "$INSTALLER" | shasum -a 256 -c -

python3 - <<'PY'
import json
import os
from pathlib import Path

row = json.loads(Path(os.environ["WORK"], "record.json").read_text())
actual = Path(os.environ["INSTALLER"]).stat().st_size
if actual != row["size_bytes"]:
    raise SystemExit(f"Size mismatch: expected {row['size_bytes']}, got {actual}")
print(f"Verified installer size: {actual} bytes")
PY

curl --fail --location --retry 3 --proto '=https' --proto-redir '=https' \
  --output "$WORK/published.sha256" "$CHECKSUM_URL"

python3 - <<'PY'
import json
import os
from pathlib import Path
from jetbrains_hashes.transfer import parse_checksum

work = Path(os.environ["WORK"])
row = json.loads((work / "record.json").read_text())
published = parse_checksum((work / "published.sha256").read_bytes(), row["installer_url"])
print(f"Current published SHA-256: {published}")
if published != row["installer_sha256"]:
    raise SystemExit("The published checksum changed; preserve the original history record")
PY
```

**Stop on a mismatch.** A URL may now serve a different installer. Do not replace
the old `installer_sha256` or attach the replacement's application hash to it.
Recover the original matching installer, or investigate and retain a separate,
independently verified revision. A checksum sidecar that still advertises the old
hash does not make different downloaded bytes acceptable.

If a sidecar is unavailable but the download matches the previously recorded
checksum, record the sidecar failure separately and review that provenance before
proceeding; do not silently treat an unavailable sidecar as a successful check.

## 3. Mount the DMG read-only, or inspect a verified ZIP

For a DMG:

```bash
export CONTENTS="$WORK/mount"
mkdir "$CONTENTS"
hdiutil attach "$INSTALLER" -readonly -nobrowse -noautoopen -mountpoint "$CONTENTS"
```

For a ZIP instead (for example YouTrack Workflow Editor):

```bash
unzip -l "$INSTALLER"
export CONTENTS="$WORK/extracted"
mkdir "$CONTENTS"
ditto -x -k "$INSTALLER" "$CONTENTS"
```

Locate the application. This command deliberately stops if there is not exactly
one top-level `.app`; inspect the contents rather than guessing between bundles.

```bash
APP="$(python3 - <<'PY'
import os
from pathlib import Path

apps = [
    path for path in Path(os.environ["CONTENTS"]).glob("*.app")
    if path.is_dir() and not path.is_symlink()
]
if len(apps) != 1:
    raise SystemExit(f"Expected one top-level application, found: {apps}")
print(apps[0])
PY
)"
export APP
test -n "$APP"
```

## 4. Inspect the original metadata and identify the launcher

```bash
plutil -lint "$APP/Contents/Info.plist"
plutil -p "$APP/Contents/Info.plist"
plutil -convert xml1 -o "$WORK/Info.normalized.plist" "$APP/Contents/Info.plist"
EXECUTABLE="$(/usr/libexec/PlistBuddy \
  -c 'Print :CFBundleExecutable' "$WORK/Info.normalized.plist")"
export EXECUTABLE

python3 - <<'PY'
import json
import os
import plistlib
from pathlib import Path

app = Path(os.environ["APP"])
info = plistlib.loads(Path(os.environ["WORK"], "Info.normalized.plist").read_bytes())
print("CFBundleExecutable:", info.get("CFBundleExecutable"))
print("CFBundleShortVersionString:", info.get("CFBundleShortVersionString"))
print("CFBundleVersion:", info.get("CFBundleVersion"))
for suffix in ("Contents/Resources/product-info.json",
               "Contents/Resources/build.txt", "Contents/build.txt"):
    path = app / suffix
    if path.is_file():
        if path.name == "product-info.json":
            product = json.loads(path.read_text())
            print(suffix, json.dumps({key: product.get(key) for key in
                                     ("name", "version", "buildNumber", "productCode")}))
        else:
            print(suffix, repr(path.read_text().strip()))
PY
```

The normalized plist is only a diagnostic copy outside the application. Native
`plutil` can sometimes read older plist formats that Python's parser rejects.
If it also rejects the file, stop and inspect the original metadata; do not
invent a launcher or edit the bundle to force the collector to accept it.

Record the actual bundle build, preferring `product-info.json`'s `buildNumber`,
then `Contents/Resources/build.txt` or `Contents/build.txt`, then a meaningful
`CFBundleVersion`. If those sources disagree or are absent, investigate rather
than guessing.

An API build such as `145.2073` and bundle build `OC-145.2073.4` are **not equal
under the collector's rules**. The product prefix is already ignored; the
additional numeric suffix is the mismatch. Verify the advertised version and
the bundle's product/version/build against trustworthy release information.
Matching installer bytes alone does not establish that the API's build label is
correct. Do not assume every differing build is just a harmless suffix.

## 5. Hash the raw main executable

```bash
python3 - <<'PY'
import os
from pathlib import Path

name = os.environ["EXECUTABLE"]
if not name or name in (".", "..") or Path(name).name != name:
    raise SystemExit("Invalid CFBundleExecutable")
root = Path(os.environ["CONTENTS"]).resolve()
launcher = (Path(os.environ["APP"]) / "Contents" / "MacOS" / name).resolve()
if not launcher.is_relative_to(root) or not launcher.is_file():
    raise SystemExit("Launcher is missing or resolves outside the inspected contents")
print(f"Launcher: {launcher}")
PY

file "$APP/Contents/MacOS/$EXECUTABLE"
APP_SHA256="$(shasum -a 256 "$APP/Contents/MacOS/$EXECUTABLE" | awk '{print $1}')"
APP_PATH="$(basename "$APP")/Contents/MacOS/$EXECUTABLE"
export APP_SHA256 APP_PATH
printf 'app_sha256: %s\napp_path: %s\n' "$APP_SHA256" "$APP_PATH"
```

This hashes the executable bytes, not the whole `.app`, the installer, a code
signing CDHash, or a notarization result.

## 6. Record only what you actually verified

After resolving the identity discrepancy, set the build to the value you observed
(this example is for the AppCode record above), then print the fields to copy into
that **existing** JSON record:

```bash
export APP_BUILD='OC-145.2073.4'
python3 - <<'PY'
import json
import os
from datetime import datetime, timezone

now = datetime.now(timezone.utc).isoformat()
print(json.dumps({
    "app_sha256": os.environ["APP_SHA256"],
    "app_path": os.environ["APP_PATH"],
    "app_build": os.environ["APP_BUILD"],
    "error_stage": "",
    "error": "",
    "consecutive_failures": 0,
    "failure_updated_at": now,
    "last_attempt": now,
}, indent=2))
PY

# After carefully editing the matching entry in data/<PRODUCT>.json:
python3 -m jetbrains_hashes render
git diff --check
git diff -- "data/$PRODUCT.json" ides/
```

Preserve the API `build`, installer provenance, other records, and catalog
timestamps. Keep a note in your commit/PR describing why the metadata discrepancy
was accepted and what evidence supported it. Commit the JSON and regenerated
tables/report together. Start a **new workflow run** after merging; rerunning an
old run uses its original source revision.

If you cannot establish provenance or the launcher identity, leave the hash
missing. Quarantine is the honest outcome for an unverified artifact.

## 7. Detach and clean up

For a DMG, detach **before** deleting anything:

```bash
hdiutil detach "$WORK/mount"
```

If detaching fails, stop and retain the workspace. Once detached (or after
finishing with a ZIP), remove only the specific workspace path printed in step
1, for example through Finder. Never recursively delete a still-mounted image
or a broad temporary directory.
