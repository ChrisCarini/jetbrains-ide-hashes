"""Inspect one macOS installer and confirm the proposed JSON changes once."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shlex
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import urllib.parse
import zipfile
from pathlib import Path, PurePosixPath
from typing import Callable
from xml.parsers.expat import ExpatError

from . import history, transfer
from .cli import locked
from .transfer import ArtifactError, StopRun

ROOT = Path(__file__).resolve().parent.parent
FAILURES = (
    ArtifactError,
    StopRun,
    OSError,
    ValueError,
    ExpatError,
    plistlib.InvalidFileException,
    subprocess.SubprocessError,
    zipfile.BadZipFile,
)


class Aborted(RuntimeError):
    """The operator stopped the review."""


class Verification:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.work = Path(tempfile.mkdtemp(prefix="jetbrains-manual-", dir=args.work_dir)).resolve()
        self.history_path = ROOT / "data" / f"{args.product}.json"
        self.original = ""
        self.index = -1
        self.selected: history.Record | None = None
        self.app: Path | None = None
        self.info: dict = {}
        self.builds: dict[str, str] = {}
        self.executable = ""
        self.app_build = ""
        self.fields: dict | None = None
        self.mount_attempted = False
        self.opened = False
        self.written = False
        self.failed = False
        self.observed: dict = {}
        self.events: list[dict] = []
        self.report = {
            "product": args.product,
            "requested_identity": {
                name: getattr(args, name)
                for name in ("version", "build", "channel", "platform", "expected_installer_sha256")
            },
            "workspace": str(self.work),
            "observations": self.observed,
            "steps": self.events,
            "history_updated": False,
        }
        self.log(f"Keep this workspace path: {self.work}")
        self.checkpoint()

    def log(self, message: str) -> None:
        print(message, flush=True)
        with (self.work / "transcript.log").open("a", encoding="utf-8") as output:
            output.write(message + "\n")

    def checkpoint(self) -> None:
        self.report["updated_at"] = history.now()
        transfer.atomic_write(
            self.work / "verification.json", json.dumps(self.report, indent=2) + "\n"
        )

    def ask(self, prompt: str) -> str:
        answer = input(prompt).strip()
        self.log(prompt + answer)
        return answer

    def step(self, title: str, action: Callable[[], object]) -> bool:
        self.log(f"\n== {title} ==")
        event = {"step": title, "at": history.now()}
        self.events.append(event)
        try:
            action()
        except FAILURES as exc:
            event.update(result="failed", error=str(exc))
            self.failed = True
            self.log(f"FAILED: {exc}")
            self.checkpoint()
            return False
        event["result"] = "passed"
        self.checkpoint()
        return True

    def command(self, *args: str, timeout: int | None = 180) -> str:
        self.log("$ " + shlex.join(args))
        result = subprocess.run(
            args,
            cwd=ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            timeout=timeout,
            check=False,
        )
        if result.stdout:
            self.log(result.stdout.rstrip())
        if result.returncode:
            raise ArtifactError(f"Command exited {result.returncode}: {shlex.join(args)}")
        return result.stdout

    @property
    def record(self) -> history.Record:
        if self.selected is None:
            raise ArtifactError(
                "No exact history record selected; abort and correct the arguments."
            )
        return self.selected

    @property
    def image(self) -> Path:
        suffix = Path(urllib.parse.urlsplit(self.record.installer_url).path).suffix.lower()
        if suffix not in (".dmg", ".zip"):
            raise ArtifactError(f"Unsupported installer format: {self.record.installer_url}")
        return self.work / f"installer{suffix}"

    @property
    def contents(self) -> Path:
        return self.work / ("mount" if self.image.suffix == ".dmg" else "extracted")

    def contained(self, path: Path) -> Path:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.contents.resolve()):
            raise ArtifactError(f"Path resolves outside the inspected contents: {path}")
        return resolved

    def bundle_file(self, suffix: str) -> Path:
        if self.app is None:
            raise ArtifactError("No application bundle selected.")
        return self.contained(self.app / suffix)

    def digest(self, path: Path) -> str:
        with path.open("rb") as source:
            return transfer.hash_stream(source)

    def select_record(self) -> None:
        original = self.history_path.read_text(encoding="utf-8")
        saved = history.load(self.history_path)
        key = (self.args.version, self.args.build, self.args.channel, self.args.platform)
        matches = [
            (index, row)
            for index, row in enumerate(saved.records)
            if row.release_key() == key
            and (
                not self.args.expected_installer_sha256
                or row.installer_sha256 == self.args.expected_installer_sha256
            )
        ]
        if len(matches) != 1:
            raise ArtifactError(
                f"Expected exactly one record, found {len(matches)}; check identity and digest."
            )
        index, row = matches[0]
        if (
            not history.valid_url(row.installer_url)
            or not transfer.SHA256.fullmatch(row.installer_sha256)
            or row.size_bytes <= 0
        ):
            raise ArtifactError("No usable recorded HTTPS installer URL, SHA-256, or size.")
        if self.history_path.read_text(encoding="utf-8") != original:
            raise ArtifactError(
                "History changed during selection; retry after publication finishes."
            )
        self.original, self.index, self.selected = original, index, row
        snapshot = json.dumps(json.loads(original)["records"][index], indent=2) + "\n"
        transfer.atomic_write(self.work / "record.json", snapshot)
        self.log(snapshot.rstrip())
        self.log(f"Installer destination: {self.image}")

    def curl(self, url: str, destination: Path) -> None:
        if not history.valid_url(url):
            raise ArtifactError(f"Missing or invalid HTTPS URL: {url!r}")
        self.log("Downloading with curl's three retries and exponential backoff.")
        self.command(
            "curl",
            "--fail",
            "--location",
            "--retry",
            "3",
            "--proto",
            "=https",
            "--proto-redir",
            "=https",
            "--silent",
            "--show-error",
            "--output",
            str(destination),
            url,
            timeout=None,
        )

    def download(self) -> None:
        transfer.require_space(self.work, self.record.size_bytes + transfer.GIB)
        if self.args.installer is not None:
            self.log(f"Copying locally supplied installer: {self.args.installer}")
            shutil.copyfile(self.args.installer, self.image)
        else:
            self.curl(self.record.installer_url, self.image)

    def verify_digest(self) -> None:
        actual = self.digest(self.image)
        self.observed["installer_sha256"] = actual
        self.log(f"Recorded installer SHA-256: {self.record.installer_sha256}\nActual: {actual}")
        if actual != self.record.installer_sha256:
            raise ArtifactError(
                "Installer SHA-256 mismatch. This payload will not be opened or "
                "attributed to the selected record."
            )

    def verify_size(self) -> None:
        actual = self.image.stat().st_size
        self.observed["size_bytes"] = actual
        self.log(f"Recorded size: {self.record.size_bytes}; actual: {actual} bytes")
        if actual != self.record.size_bytes:
            raise ArtifactError("Installer size mismatch; preserve the recorded provenance.")

    def verify_sidecar(self) -> None:
        published = transfer.parse_checksum(
            (self.work / "published.sha256").read_bytes(), self.record.installer_url
        )
        self.observed["published_sha256"] = published
        self.log(f"Current published SHA-256: {published}")
        if published != self.record.installer_sha256:
            raise ArtifactError("Published checksum changed; do not rewrite the historical digest.")

    def open_installer(self) -> None:
        self.opened = False
        digest = self.digest(self.image)
        size = self.image.stat().st_size
        self.observed.update(inspected_installer_sha256=digest, inspected_size_bytes=size)
        if digest != self.observed.get("installer_sha256") or size != self.observed.get(
            "size_bytes"
        ):
            raise ArtifactError(
                "Installer changed or was not measured. Restart with this installer."
            )
        self.contents.mkdir(exist_ok=True)
        if self.image.suffix == ".dmg":
            self.mount_attempted = True
            devices = transfer.attached_devices(self.image)
            if not self.contents.is_mount():
                if devices:
                    raise ArtifactError(
                        f"Image already attached elsewhere ({devices}); detach it before retrying."
                    )
                self.command(
                    "hdiutil",
                    "attach",
                    str(self.image),
                    "-readonly",
                    "-nobrowse",
                    "-noautoopen",
                    "-mountpoint",
                    str(self.contents),
                )
            elif not devices:
                raise ArtifactError("The mountpoint belongs to an unexpected disk image.")
            if not self.contents.is_mount():
                raise ArtifactError("Installer did not mount at the requested mountpoint.")
        else:
            with zipfile.ZipFile(self.image) as archive:
                for entry in archive.infolist():
                    name = PurePosixPath(entry.filename)
                    if name.is_absolute() or ".." in name.parts:
                        raise ArtifactError(f"Unsafe ZIP member: {entry.filename}")
                    if stat.S_ISLNK(entry.external_attr >> 16):
                        if entry.file_size > 4096:
                            raise ArtifactError(f"Oversized ZIP symlink: {entry.filename}")
                        target = PurePosixPath(archive.read(entry).decode("utf-8"))
                        if target.is_absolute() or ".." in target.parts:
                            raise ArtifactError(f"Unsafe ZIP symlink: {entry.filename} -> {target}")
                transfer.require_space(
                    self.work, sum(entry.file_size for entry in archive.infolist()) + transfer.GIB
                )
            self.command("ditto", "-x", "-k", str(self.image), str(self.contents), timeout=None)
        self.opened = True

    def set_app(self, app: Path) -> None:
        self.contained(app)
        if app.suffix != ".app" or not app.is_dir() or app.is_symlink():
            raise ArtifactError(f"Not a nonsymlink application directory: {app}")
        self.app = app
        self.observed["app"] = str(app)
        self.log(f"Application: {app}")

    def locate_app(self) -> None:
        apps = [app for app in self.contents.glob("*.app") if app.is_dir() and not app.is_symlink()]
        if len(apps) != 1:
            raise ArtifactError(f"Expected one top-level application; found: {apps}")
        self.set_app(apps[0])

    def manual_app(self) -> None:
        name = self.args.app_path
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise ArtifactError("Supply a relative application path inside the inspected contents.")
        self.set_app(self.contents / name)

    def read_plist(self) -> None:
        info = plistlib.loads((self.work / "Info.normalized.plist").read_bytes())
        if not isinstance(info, dict):
            raise ArtifactError("Normalized Info.plist is not a dictionary.")
        summary = {
            key: info.get(key, "")
            for key in (
                "CFBundleExecutable",
                "CFBundleIdentifier",
                "CFBundleShortVersionString",
                "CFBundleVersion",
            )
        }
        for key, value in summary.items():
            if not isinstance(value, str):
                raise ArtifactError(f"{key} is not a string: {value!r}")
        self.info = info
        self.observed["plist"] = summary
        self.log(json.dumps(summary, indent=2))

    def read_executable(self) -> None:
        self.executable = self.command(
            "/usr/libexec/PlistBuddy",
            "-c",
            "Print :CFBundleExecutable",
            str(self.work / "Info.normalized.plist"),
        ).strip()
        self.launcher()

    def manual_executable(self) -> None:
        self.executable = self.args.executable
        self.launcher()
        self.observed["manual_executable"] = self.executable

    def read_build_source(self, suffix: str) -> None:
        path = self.bundle_file(suffix)
        if not path.exists():
            self.log(f"{suffix}: absent")
            return
        if path.stat().st_size > 4 * transfer.CHUNK:
            raise ArtifactError(f"Metadata exceeds 4 MiB: {path}")
        if path.name == "product-info.json":
            product = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(product, dict):
                raise ArtifactError("product-info.json is not an object.")
            summary = {
                key: product.get(key) for key in ("name", "version", "buildNumber", "productCode")
            }
            self.observed["product_info"] = summary
            self.log(f"{suffix}: {json.dumps(summary)}")
            build = product.get("buildNumber", "")
        else:
            build = path.read_text(encoding="utf-8").strip()
            self.log(f"{suffix}: {build!r}")
        if not isinstance(build, str):
            raise ArtifactError(f"Build is not a string: {suffix}")
        if build.strip():
            self.builds[suffix] = build.strip()

    def choose_build(self) -> None:
        version = self.info.get("CFBundleVersion")
        if version and version != self.info.get("CFBundleShortVersionString"):
            if not isinstance(version, str):
                raise ArtifactError("CFBundleVersion is not a string.")
            if version.strip():
                self.builds["CFBundleVersion"] = version.strip()
        self.observed["build_sources"] = self.builds
        if not self.builds:
            raise ArtifactError("No meaningful bundle build; inspect the original metadata.")
        if len({transfer.normalize_build(build) for build in self.builds.values()}) != 1:
            raise ArtifactError(
                f"Build sources disagree: {self.builds}; investigate, do not guess."
            )
        self.app_build = next(iter(self.builds.values()))
        self.observed["app_build"] = self.app_build
        self.log(f"Observed app_build: {self.app_build}")

    def manual_build(self) -> None:
        build = self.args.app_build.strip()
        if self.builds and build not in self.builds.values():
            raise ArtifactError(
                f"Choose an observed build from {self.builds}, not an invented value."
            )
        self.app_build = build
        self.observed["app_build"] = build

    def compare_build(self) -> None:
        if not self.app_build:
            raise ArtifactError("No observed application build.")
        if not transfer.build_matches(self.record.build, self.app_build):
            raise ArtifactError(
                f"API build {self.record.build!r} != bundle build {self.app_build!r}. "
                "This is NOT an allowed abbreviated build. DO NOT ACCEPT this proposal: "
                "type 'n' at confirmation, not Enter (which defaults to yes). "
                "Investigate the genuine build mismatch separately."
            )
        if transfer.is_abbreviated_build(self.record.build, self.app_build):
            self.log(
                f"Abbreviated API build {self.record.build}; "
                f"the hash will be attributed to exact bundle build {self.app_build}."
            )

    def launcher(self) -> Path:
        name = self.executable
        if not name or name in (".", "..") or Path(name).name != name:
            raise ArtifactError("Missing or invalid CFBundleExecutable.")
        path = self.bundle_file(f"Contents/MacOS/{name}")
        if not path.is_file():
            raise ArtifactError(f"Launcher is not a regular file: {path}")
        return path

    def hash_launcher(self) -> None:
        launcher = self.launcher()
        if self.app is None:
            raise ArtifactError("No application bundle selected.")
        app_path = (self.app / "Contents" / "MacOS" / self.executable).relative_to(self.contents)
        self.observed.update(app_sha256=self.digest(launcher), app_path=app_path.as_posix())
        self.log(
            f"Launcher: {launcher}\napp_sha256: {self.observed['app_sha256']}\napp_path: {app_path}"
        )

    def propose(self) -> None:
        if (
            not self.opened
            or self.observed.get("inspected_installer_sha256") != self.record.installer_sha256
            or self.observed.get("inspected_size_bytes") != self.record.size_bytes
        ):
            raise ArtifactError(
                "Inspected bytes do not have verified provenance for this record. "
                "No update will be generated; recover the original installer and start a new review."
            )
        if not self.observed.get("app_sha256") or not self.app_build:
            raise ArtifactError(
                "Launcher hash or actual bundle build is missing; leave history alone."
            )
        now = history.now()
        fields = {
            "app_sha256": self.observed["app_sha256"],
            "app_path": self.observed["app_path"],
            "app_build": self.app_build,
            "app_bundle_id": self.info.get("CFBundleIdentifier", ""),
            "app_version": self.info.get("CFBundleShortVersionString", ""),
            "error_stage": "",
            "error": "",
            "consecutive_failures": 0,
            "failure_updated_at": now,
            "last_attempt": now,
        }
        for key in ("app_sha256", "app_path", "app_build", "app_bundle_id", "app_version"):
            existing = getattr(self.record, key)
            if existing and existing != fields[key]:
                raise ArtifactError(f"Refusing to overwrite an existing conflicting {key}.")
        transfer.atomic_write(
            self.work / "proposed-fields.json", json.dumps(fields, indent=2) + "\n"
        )
        self.fields = fields
        original_record = json.loads(self.original)["records"][self.index]
        self.report["proposed_update"] = {
            "file": str(self.history_path.relative_to(ROOT)),
            "record": {
                key: getattr(self.record, key)
                for key in ("version", "build", "release_type", "platform", "installer_sha256")
            },
            "changes": {
                key: {"before": original_record.get(key, "(not present)"), "after": value}
                for key, value in fields.items()
                if key not in original_record or original_record[key] != value
            },
        }
        self.log(
            "PROPOSAL ONLY; not yet accepted or written to history:\n"
            + json.dumps(self.report["proposed_update"], indent=2)
        )

    def write_record(self) -> None:
        if self.fields is None:
            raise ArtifactError("No eligible update.")
        if (
            self.digest(self.image) != self.record.installer_sha256
            or self.image.stat().st_size != self.record.size_bytes
            or self.digest(self.launcher()) != self.fields["app_sha256"]
        ):
            raise ArtifactError("Inspected files changed; restart verification instead of saving.")
        with locked(self.history_path.parent):
            if self.history_path.read_text(encoding="utf-8") != self.original:
                raise ArtifactError(
                    "History changed since selection; restart rather than overwrite it."
                )
            payload = json.loads(self.original)
            payload["records"][self.index].update(self.fields)
            transfer.atomic_write(self.work / "history.before.json", self.original)
            transfer.atomic_write(self.history_path, json.dumps(payload, indent=2) + "\n")
        self.written = True
        self.report["history_updated"] = True
        self.log(f"Updated only the selected record in {self.history_path}. No commit was made.")

    def run(self) -> None:
        self.log(
            "Checks run without prompts; review all JSON changes at one final confirmation. "
            "Large files are cleaned up automatically unless --keep-files is set."
        )
        if not self.step("1 Select exact historical record", self.select_record):
            return
        if not self.step("2a Download (or copy) installer", self.download):
            return
        digest_ok = self.step("2b Check installer SHA-256", self.verify_digest)
        size_ok = self.step("2c Check installer size", self.verify_size)
        if self.step(
            "2d Download current checksum sidecar",
            lambda: self.curl(self.record.checksum_url, self.work / "published.sha256"),
        ):
            self.step("2e Compare current published checksum", self.verify_sidecar)
        if not digest_ok or not size_ok:
            self.log(
                "Installer provenance failed; stopping before opening it or proposing an update."
            )
            return
        if self.image.suffix == ".zip":
            self.step("3a List ZIP contents", lambda: self.command("unzip", "-l", str(self.image)))
        if not self.step("3b Mount read-only / extract ZIP without launching", self.open_installer):
            return
        self.step("3c Locate application", self.locate_app)
        if self.app is None and self.args.app_path:
            self.step("3d Use explicitly supplied application path", self.manual_app)
        if self.app is None:
            self.log(
                "Inspect the contents and rerun with --app-path PATH; no bundle will be guessed."
            )
            return
        self.step(
            "4a Lint original plist",
            lambda: self.command(
                "plutil",
                "-lint",
                str(self.bundle_file("Contents/Info.plist")),
            ),
        )
        self.step(
            "4b Display original plist",
            lambda: self.command(
                "plutil",
                "-p",
                str(self.bundle_file("Contents/Info.plist")),
            ),
        )
        self.step(
            "4c Normalize a diagnostic copy, not the bundle",
            lambda: self.command(
                "plutil",
                "-convert",
                "xml1",
                "-o",
                str(self.work / "Info.normalized.plist"),
                str(self.bundle_file("Contents/Info.plist")),
            ),
        )
        self.step("4d Read normalized metadata", self.read_plist)
        launcher_identified = self.step("4e Read CFBundleExecutable", self.read_executable)
        if not launcher_identified and self.args.executable:
            launcher_identified = self.step(
                "4f Use explicitly supplied launcher", self.manual_executable
            )
        if not launcher_identified:
            self.log("Inspect the original metadata and rerun with --executable NAME.")
            return
        for suffix in (
            "Contents/Resources/product-info.json",
            "Contents/Resources/build.txt",
            "Contents/build.txt",
        ):
            self.step(f"4g Inspect {suffix}", lambda suffix=suffix: self.read_build_source(suffix))
        build_identified = self.step("4h Identify actual bundle build", self.choose_build)
        if not build_identified and self.args.app_build:
            build_identified = self.step(
                "4i Use explicitly supplied bundle build", self.manual_build
            )
        if not build_identified:
            self.log("Resolve the original build metadata and rerun with --app-build BUILD.")
            return
        self.step("4j Compare API and observed bundle builds", self.compare_build)
        self.step(
            "5a Identify launcher file type", lambda: self.command("file", str(self.launcher()))
        )
        if not self.step("5b Hash raw main executable", self.hash_launcher):
            return
        if not self.step("6a Prepare fields for review", self.propose):
            return
        failures = [event for event in self.events if event["result"] == "failed"]
        if failures:
            self.log("\nFailed checks requiring your acceptance (not marked as passed):")
            for event in failures:
                self.log(f"- {event['step']}: {event['error']}")
        self.log(
            "\nOnly the fields shown above will change in the selected JSON record. "
            "API build, installer provenance, and other records stay unchanged. "
            "Markdown tables/report under ides/ will also be regenerated. "
            "Confirm only after verifying the product/version/build identity."
        )
        confirmed = self.ask(
            "Apply these JSON changes and accept any listed failures? [Y/n]: "
        ).lower() in ("", "y", "yes")
        self.report["update_confirmed"] = confirmed
        self.report["accepted_failures"] = (
            [event["step"] for event in failures] if confirmed else []
        )
        self.checkpoint()
        if confirmed:
            self.step("6b Update the exact record, preserving other history", self.write_record)
        if self.written:
            self.step(
                "6c Regenerate tables and failure report",
                lambda: self.command(
                    sys.executable,
                    "-m",
                    "jetbrains_hashes",
                    "render",
                ),
            )
            self.step(
                "6d Check diff whitespace",
                lambda: self.command("git", "--no-pager", "diff", "--check"),
            )
            self.step(
                "6e Review resulting diff",
                lambda: self.command(
                    "git",
                    "--no-pager",
                    "diff",
                    "--",
                    str(self.history_path.relative_to(ROOT)),
                    "ides/",
                ),
            )
            self.log(
                "Review and commit JSON plus regenerated tables together, including the evidence."
            )

    def detach(self) -> None:
        for device in transfer.attached_devices(self.image):
            self.command("hdiutil", "detach", device)
        if transfer.attached_devices(self.image) or self.contents.is_mount():
            raise ArtifactError("Image is still attached. Retain the workspace; do not delete it.")

    def remove_payloads(self) -> None:
        if self.mount_attempted:
            self.detach()
        contents = self.contents
        if contents.is_symlink():
            raise ArtifactError("Contents directory became a symlink; refusing cleanup.")
        if contents.exists():
            for parent, _, _ in os.walk(contents, followlinks=False):
                if Path(parent).is_mount():
                    raise ArtifactError(f"Still-mounted directory: {parent}; refusing cleanup.")
            if self.image.suffix == ".dmg":
                contents.rmdir()
            else:
                shutil.rmtree(contents)
        self.image.unlink(missing_ok=True)
        self.log(
            "Removed installer and inspected contents; retained metadata, proposals, and audit logs."
        )

    def finish(self, completed: bool) -> None:
        if self.mount_attempted and not self.step("7a Detach disk image", self.detach):
            self.log("Cleanup skipped because detachment failed. Keep the entire workspace.")
            return
        if completed and self.selected is not None:
            if self.args.keep_files:
                self.log("Keeping large files because --keep-files was supplied.")
            else:
                self.step("7b Remove only this review's payload files", self.remove_payloads)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("product", "version", "build", "channel", "platform"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument(
        "--expected-installer-sha256", default="", help="Pin a particular payload revision."
    )
    parser.add_argument(
        "--installer", type=Path, help="Copy a recovered/local installer instead of downloading."
    )
    parser.add_argument(
        "--work-dir", type=Path, help="Existing parent for a new evidence workspace."
    )
    parser.add_argument(
        "--keep-files", action="store_true", help="Keep large files instead of automatic cleanup."
    )
    parser.add_argument(
        "--app-path", help="Fallback .app path relative to inspected contents if discovery fails."
    )
    parser.add_argument(
        "--executable", help="Fallback CFBundleExecutable from manually inspected metadata."
    )
    parser.add_argument(
        "--app-build", help="Fallback actual bundle build when metadata is missing or conflicting."
    )
    args = parser.parse_args(argv)
    try:
        history.validate_code(args.product)
    except StopRun as exc:
        parser.error(str(exc))
    if args.expected_installer_sha256 and not transfer.SHA256.fullmatch(
        args.expected_installer_sha256
    ):
        parser.error("--expected-installer-sha256 must be a lowercase, 64-character SHA-256.")
    if sys.platform != "darwin" or sys.version_info < (3, 11):
        parser.error("Use macOS and Python 3.11+.")
    if not sys.stdin.isatty():
        parser.error("Run interactively in a terminal for the single JSON-update confirmation.")

    def interrupted(signum, frame):
        raise Aborted(f"Signal {signum}")

    signal.signal(signal.SIGTERM, interrupted)
    try:
        review = Verification(args)
    except OSError as exc:
        parser.error(f"Cannot create the evidence workspace: {exc}")
    completed = False
    try:
        review.run()
        completed = True
        if not review.written:
            review.log("History and generated tables were left unchanged.")
    except (Aborted, KeyboardInterrupt, EOFError) as exc:
        review.log(f"Review aborted: {exc or 'operator interruption'}")
    except FAILURES as exc:
        review.log(f"Review stopped: {exc}")
    finally:
        try:
            review.finish(completed)
        except (Aborted, KeyboardInterrupt, EOFError, *FAILURES) as exc:
            completed = False
            review.log(
                f"Cleanup stopped; retain the workspace and check for attached images: {exc}"
            )
        review.report["outcome"] = (
            "finished_with_failures"
            if completed and review.failed
            else "finished"
            if completed
            else "stopped"
        )
        review.report["has_failures"] = review.failed
        review.checkpoint()
        review.log(f"Evidence retained at: {review.work}")
    if review.failed:
        review.log("Review contains failed checks; see verification.json. Exit status: 1.")
    return 0 if completed and not review.failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
