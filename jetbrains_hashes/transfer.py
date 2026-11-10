"""Download verified installers and read their launchers without running them."""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import plistlib
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Callable, TypeVar
from xml.parsers.expat import ExpatError

MIB = 1024**2
GIB = 1024**3
CHUNK = MIB
DOWNLOAD_PROGRESS_INTERVAL = 10
SHA256 = re.compile(r"[0-9a-f]{64}")
T = TypeVar("T")


class ArtifactError(RuntimeError):
    """This artifact failed; other artifacts can still be collected."""


class StopRun(RuntimeError):
    """Continuing would risk disk exhaustion, unsafe cleanup, or lost history."""


class BudgetReached(RuntimeError):
    """Save progress and continue in the next scheduled run."""


def log(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


def check_deadline(deadline: float | None) -> None:
    if deadline is not None and time.monotonic() >= deadline:
        raise BudgetReached("Time budget reached")


def request(
    url: str, consume: Callable[[http.client.HTTPResponse], T], deadline: float | None = None
) -> T:
    for attempt in range(6):
        check_deadline(deadline)
        delay = 2**attempt
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "jetbrains-ide-hashes/1", "Accept-Encoding": "identity"}
            )
            timeout = 60 if deadline is None else min(60, max(1, deadline - time.monotonic()))
            with urllib.request.urlopen(req, timeout=timeout) as response:
                if response.status != 200:
                    raise ArtifactError(f"Unexpected HTTP {response.status}: {url}")
                return consume(response)
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (408, 429) or 500 <= exc.code <= 599
            retry_after = exc.headers.get("Retry-After", "")
            if retry_after.isdigit():
                delay = max(delay, int(retry_after))
            reason = f"HTTP {exc.code}"
            exc.close()
            if not retryable:
                raise ArtifactError(f"{reason}: {url}") from exc
        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            http.client.IncompleteRead,
        ) as exc:
            reason = str(exc)
        if attempt == 5:
            raise ArtifactError(f"Request failed after 6 attempts: {url}: {reason}")
        if deadline is not None and time.monotonic() + delay >= deadline:
            raise BudgetReached(f"Retry would exceed time budget: {url}")
        log(f"Retrying {url} in {delay}s ({reason}; retry {attempt + 1}/5)")
        time.sleep(delay)
    raise AssertionError("unreachable")


def fetch_bytes(url: str, deadline: float | None = None) -> bytes:
    def read(response: http.client.HTTPResponse) -> bytes:
        data = response.read(64 * CHUNK + 1)
        if len(data) > 64 * CHUNK:
            raise ArtifactError(f"Metadata exceeds 64 MiB: {url}")
        length = response.headers.get("Content-Length")
        if length is not None and len(data) != int(length):
            raise http.client.IncompleteRead(data, max(0, int(length) - len(data)))
        return data

    return request(url, read, deadline)


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False
        ) as output:
            temporary = Path(output.name)
            output.write(text)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def parse_checksum(data: bytes, installer_url: str) -> str:
    try:
        text = data.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ArtifactError("Checksum file is not UTF-8 text") from exc
    match = re.fullmatch(r"([0-9a-fA-F]{64})(?:[ \t]+\*?([^\r\n]+))?", text)
    if not match:
        raise ArtifactError("Expected exactly one SHA-256 in the checksum file")
    filename = match.group(2)
    expected = Path(urllib.parse.unquote(urllib.parse.urlsplit(installer_url).path)).name
    if filename is not None and filename != expected:
        raise ArtifactError(f"Checksum names {filename!r}, expected {expected!r}")
    return match.group(1).lower()


def require_space(directory: Path, required: int) -> None:
    free = shutil.disk_usage(directory).free
    if free < required:
        raise StopRun(
            f"Insufficient disk space: {free / GIB:.2f} GiB free, "
            f"{required / GIB:.2f} GiB required (includes 1 GiB reserve)"
        )


def download_image(
    url: str, size: int, expected_sha256: str, image: Path, deadline: float | None = None
) -> None:
    def download(response: http.client.HTTPResponse) -> str:
        digest = hashlib.sha256()
        total = 0
        with image.open("wb") as target:
            require_space(image.parent, size + GIB)
            started = time.monotonic()
            last_progress = started
            log(f"  Downloading {url} ({size / MIB:.1f} MiB)")
            while True:
                check_deadline(deadline)
                chunk = response.read(CHUNK)
                if not chunk:
                    break
                if total + len(chunk) > size:
                    raise ArtifactError("Download is larger than the API's advertised size")
                if total % (64 * CHUNK) == 0:
                    require_space(image.parent, GIB + len(chunk))
                target.write(chunk)
                digest.update(chunk)
                total += len(chunk)
                now = time.monotonic()
                if now - last_progress >= DOWNLOAD_PROGRESS_INTERVAL:
                    log(
                        f"  Download progress: {total / MIB:.1f}/{size / MIB:.1f} MiB "
                        f"({total / size:.1%}), {total / MIB / (now - started):.1f} MiB/s"
                    )
                    last_progress = now
        if total != size:
            raise http.client.IncompleteRead(b"", size - total)
        return digest.hexdigest()

    actual = request(url, download, deadline)
    if actual != expected_sha256:
        raise ArtifactError(
            f"Installer SHA-256 mismatch: expected {expected_sha256}, got {actual}. "
            "The historical URL may have been replaced."
        )
    log(f"  Download complete: {size / MIB:.1f} MiB (100%), SHA-256 verified")


def hdiutil(*args: str) -> bytes:
    try:
        result = subprocess.run(
            ["hdiutil", *args], input=b"", capture_output=True, check=True, timeout=180
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", errors="replace").strip()
        raise ArtifactError(f"hdiutil {args[0]}: {detail}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ArtifactError(f"hdiutil {args[0]} timed out") from exc
    return result.stdout


def attached_devices(image: Path) -> list[str]:
    try:
        info = plistlib.loads(hdiutil("info", "-plist"))
    except (plistlib.InvalidFileException, ExpatError) as exc:
        raise ArtifactError("hdiutil info did not return a valid plist") from exc
    devices = []
    for mounted in info.get("images", []):
        if Path(mounted.get("image-path", "")).resolve() != image.resolve():
            continue
        device = next(
            (e["dev-entry"] for e in mounted.get("system-entities", []) if e.get("dev-entry")),
            None,
        )
        if not device:
            raise ArtifactError("No detachable device found for the downloaded image")
        devices.append(device)
    return devices


def cleanup_workspace(workspace: Path, image: Path, mount_attempted: bool) -> None:
    mount = workspace / "mount"
    old_handlers = {
        sig: signal.signal(sig, signal.SIG_IGN) for sig in (signal.SIGINT, signal.SIGTERM)
    }
    try:
        if mount_attempted:
            for device in attached_devices(image):
                for attempt in range(3):
                    try:
                        hdiutil("detach", device)
                        break
                    except ArtifactError:
                        if attempt == 2:
                            raise
                        log(f"Retrying detach of {device} in {2**attempt}s")
                        time.sleep(2**attempt)
            if attached_devices(image) or mount.is_mount():
                raise ArtifactError("Disk image is still attached")
        # A failed detach must preserve the workspace, never recursively delete it.
        image.unlink(missing_ok=True)
        mount.rmdir()
        workspace.rmdir()
    except (ArtifactError, OSError) as exc:
        raise StopRun(
            f"Cleanup failed; stopping without starting another download. Workspace: {workspace}. "
            f"Detach its image before removing it. {exc}"
        ) from exc
    finally:
        for sig, handler in old_handlers.items():
            signal.signal(sig, handler)


def hash_stream(source: BinaryIO, deadline: float | None = None) -> str:
    digest = hashlib.sha256()
    while True:
        check_deadline(deadline)
        chunk = source.read(CHUNK)
        if not chunk:
            return digest.hexdigest()
        digest.update(chunk)


def normalize_build(build: str) -> str:
    return re.sub(r"^[A-Z][A-Z0-9]*-", "", build.strip())


def is_abbreviated_build(api_build: str, app_build: str) -> bool:
    api_build = normalize_build(api_build)
    app_build = normalize_build(app_build)
    return bool(
        re.fullmatch(r"[0-9]+\.[0-9]+", api_build)
        and re.fullmatch(re.escape(api_build) + r"\.[0-9]+", app_build)
    )


def build_matches(api_build: str, app_build: str) -> bool:
    return normalize_build(api_build) == normalize_build(app_build) or is_abbreviated_build(
        api_build, app_build
    )


@dataclass(frozen=True)
class Application:
    sha256: str
    path: str
    build: str
    bundle_id: str = ""
    version: str = ""


def bundle_metadata(
    app: str, read: Callable[[str], bytes], exists: Callable[[str], bool], expected_build: str
) -> tuple[str, str, str, str]:
    try:
        info = plistlib.loads(read(f"{app}/Contents/Info.plist"))
        if not isinstance(info, dict):
            raise ArtifactError("Info.plist is not a dictionary")
        bundle_id = info.get("CFBundleIdentifier", "")
        version = info.get("CFBundleShortVersionString", "")
        if not isinstance(bundle_id, str):
            raise ArtifactError("CFBundleIdentifier is not a string")
        if not isinstance(version, str):
            raise ArtifactError("CFBundleShortVersionString is not a string")
        executable = info.get("CFBundleExecutable")
        if (
            not isinstance(executable, str)
            or not executable
            or executable in (".", "..")
            or Path(executable).name != executable
        ):
            raise ArtifactError("Missing or invalid CFBundleExecutable")
        build = ""
        product_info = f"{app}/Contents/Resources/product-info.json"
        if exists(product_info):
            product = json.loads(read(product_info))
            if not isinstance(product, dict):
                raise ArtifactError("product-info.json is not an object")
            build = product.get("buildNumber", "")
        if not build:
            for suffix in ("Contents/Resources/build.txt", "Contents/build.txt"):
                name = f"{app}/{suffix}"
                if exists(name):
                    build = read(name).decode("utf-8").strip()
                    break
        if not build:
            bundle_version = info.get("CFBundleVersion", "")
            if bundle_version != info.get("CFBundleShortVersionString"):
                build = bundle_version
        if not isinstance(build, str):
            raise ArtifactError("Bundle build number is not a string")
        if build and expected_build and not build_matches(expected_build, build):
            raise ArtifactError(
                f"Bundle build mismatch: API says {expected_build}, bundle says {build}; "
                "refusing to attribute this executable to the wrong build"
            )
        if is_abbreviated_build(expected_build, build):
            log(f"  Abbreviated API build {expected_build}; recording exact bundle build {build}")
        return f"{app}/Contents/MacOS/{executable}", build, bundle_id, version
    except (plistlib.InvalidFileException, ExpatError, ValueError, UnicodeDecodeError) as exc:
        raise ArtifactError(f"Invalid application metadata: {exc}") from exc


def hash_mounted_app(mount: Path, expected_build: str, deadline: float | None) -> Application:
    apps = [
        path
        for path in mount.glob("*.app")
        if path.is_dir() and not path.is_symlink() and (path / "Contents/Info.plist").is_file()
    ]
    if len(apps) != 1:
        raise ArtifactError(f"Expected one top-level application bundle; found {len(apps)}")

    def resolve(name: str) -> Path:
        path = (mount / name).resolve()
        if not path.is_relative_to(mount.resolve()):
            raise ArtifactError("Bundle path resolves outside the mounted image")
        return path

    def read(name: str) -> bytes:
        path = resolve(name)
        if path.stat().st_size > 4 * CHUNK:
            raise ArtifactError("Bundle metadata exceeds 4 MiB")
        return path.read_bytes()

    name, build, bundle_id, version = bundle_metadata(
        apps[0].name, read, lambda name: resolve(name).is_file(), expected_build
    )
    try:
        with resolve(name).open("rb") as source:
            return Application(hash_stream(source, deadline), name, build, bundle_id, version)
    except (FileNotFoundError, IsADirectoryError) as exc:
        raise ArtifactError("Bundle launcher is missing or is not a regular file") from exc


def hash_zipped_app(image: Path, expected_build: str, deadline: float | None) -> Application:
    try:
        with zipfile.ZipFile(image) as archive:
            names = archive.namelist()
            apps = [
                name.removesuffix("/Contents/Info.plist")
                for name in names
                if name.endswith(".app/Contents/Info.plist") and "__MACOSX/" not in name
            ]
            if len(apps) != 1:
                raise ArtifactError(f"Expected one application bundle in ZIP; found {len(apps)}")

            def read(name: str) -> bytes:
                if archive.getinfo(name).file_size > 4 * CHUNK:
                    raise ArtifactError("Bundle metadata exceeds 4 MiB")
                return archive.read(name)

            name, build, bundle_id, version = bundle_metadata(
                apps[0], read, lambda name: name in names, expected_build
            )
            if ".." in PurePosixPath(name).parts or PurePosixPath(name).is_absolute():
                raise ArtifactError("Unsafe application path in ZIP")
            entry = archive.getinfo(name)
            if stat.S_ISLNK(entry.external_attr >> 16):
                raise ArtifactError(
                    "ZIP launcher is a symlink; cannot hash it as a regular executable"
                )
            if entry.file_size > GIB:
                raise ArtifactError("ZIP launcher exceeds 1 GiB")
            with archive.open(name) as source:
                return Application(hash_stream(source, deadline), name, build, bundle_id, version)
    except (zipfile.BadZipFile, KeyError) as exc:
        raise ArtifactError(f"Invalid application ZIP: {exc}") from exc


def collect_app(
    url: str,
    size: int,
    sha256: str,
    build: str,
    work_parent: Path,
    deadline: float | None = None,
) -> Application:
    suffix = Path(urllib.parse.urlsplit(url).path).suffix.lower()
    if suffix not in (".dmg", ".zip"):
        raise ArtifactError(f"Unsupported macOS installer format: {suffix}")
    if suffix == ".dmg" and (sys.platform != "darwin" or shutil.which("hdiutil") is None):
        raise StopRun("DMG application hashing requires macOS and hdiutil")
    require_space(work_parent, size + GIB)
    workspace = Path(tempfile.mkdtemp(prefix="jetbrains-sha256-", dir=work_parent))
    mount = workspace / "mount"
    mount.mkdir()
    image = workspace / f"installer{suffix}"
    mount_attempted = False
    log(f"  Temporary workspace: {workspace}")
    try:
        download_image(url, size, sha256, image, deadline)
        if suffix == ".zip":
            return hash_zipped_app(image, build, deadline)
        mount_attempted = True
        hdiutil(
            "attach",
            str(image),
            "-readonly",
            "-nobrowse",
            "-noautoopen",
            "-mountpoint",
            str(mount),
            "-plist",
        )
        if not mount.is_mount():
            raise ArtifactError("Image did not mount at the requested mountpoint")
        return hash_mounted_app(mount, build, deadline)
    finally:
        cleanup_workspace(workspace, image, mount_attempted)
