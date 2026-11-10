import hashlib
import io
import json
import plistlib
import shutil
import subprocess
import sys
import urllib.error
import zipfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from jetbrains_hashes import transfer

DMG_BYTES = b"downloaded disk image"
APP_BYTES = b"the native launcher, not the installer"
DMG_HASH = hashlib.sha256(DMG_BYTES).hexdigest()
APP_HASH = hashlib.sha256(APP_BYTES).hexdigest()
URL = "https://download.jetbrains.com/idea/example.dmg"
BUILD = "123.456.789"
APP_PATH = "Demo IDE.app/Contents/MacOS/pycharm"
BUNDLE_ID = "com.jetbrains.pycharm"
APP_VERSION = "1.2.3"


class Response(io.BytesIO):
    status = 200

    def __init__(self, body):
        super().__init__(body)
        self.headers = {"Content-Length": str(len(body))}


def bundle_files(build=BUILD):
    return {
        "Demo IDE.app/Contents/Info.plist": plistlib.dumps(
            {
                "CFBundleExecutable": "pycharm",
                "CFBundleIdentifier": BUNDLE_ID,
                "CFBundleVersion": APP_VERSION,
                "CFBundleShortVersionString": APP_VERSION,
            }
        ),
        "Demo IDE.app/Contents/Resources/product-info.json": json.dumps(
            {"buildNumber": build}
        ).encode(),
        APP_PATH: APP_BYTES,
    }


@pytest.fixture
def fake_system(monkeypatch):
    state = SimpleNamespace(
        mounted=False,
        workspace=None,
        attach_args=None,
        interrupt_attach=False,
        fail_detach=False,
        build=BUILD,
    )
    original_is_mount = Path.is_mount

    def is_mount(path):
        if state.workspace and path == state.workspace / "mount":
            return state.mounted
        return original_is_mount(path)

    def run(command, **kwargs):
        operation = command[1]
        if operation == "attach":
            state.attach_args = command
            image = Path(command[2])
            state.workspace = image.parent
            for name, body in bundle_files(state.build).items():
                path = image.parent / "mount" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(body)
            state.mounted = True
            if state.interrupt_attach:
                raise KeyboardInterrupt
            payload = {}
        elif operation == "info":
            payload = {"images": []}
            if state.mounted:
                payload["images"].append(
                    {
                        "image-path": str(state.workspace / "installer.dmg"),
                        "system-entities": [{"dev-entry": "/dev/disk-test"}],
                    }
                )
        elif operation == "detach":
            if state.fail_detach:
                raise subprocess.CalledProcessError(1, command, stderr=b"resource busy")
            shutil.rmtree(state.workspace / "mount/Demo IDE.app")
            state.mounted = False
            payload = {}
        else:
            pytest.fail(f"Unexpected subprocess: {command}")
        return subprocess.CompletedProcess(command, 0, stdout=plistlib.dumps(payload))

    monkeypatch.setattr(transfer.subprocess, "run", run)
    monkeypatch.setattr(Path, "is_mount", is_mount)
    monkeypatch.setattr(transfer.urllib.request, "urlopen", lambda *a, **k: Response(DMG_BYTES))
    monkeypatch.setattr(transfer.time, "sleep", lambda delay: None)
    monkeypatch.setattr(transfer.sys, "platform", "darwin")
    monkeypatch.setattr(transfer.shutil, "which", lambda name: "/usr/bin/hdiutil")
    return state


@pytest.mark.parametrize("text", [DMG_HASH, DMG_HASH.upper() + " *example.dmg\n"])
def test_checksum_accepts_published_formats(text):
    assert transfer.parse_checksum(text.encode(), URL) == DMG_HASH


@pytest.mark.parametrize(
    "text",
    [
        "abc *example.dmg",
        DMG_HASH + " *different.dmg",
        DMG_HASH + "\n" + APP_HASH,
        "<html>404 Not Found</html>",
    ],
)
def test_checksum_rejects_bad_or_ambiguous_values(text):
    with pytest.raises(transfer.ArtifactError):
        transfer.parse_checksum(text.encode(), URL)


@pytest.mark.parametrize("code", [429, 529])
def test_transient_http_errors_retry_with_visible_backoff(monkeypatch, capsys, code):
    outcomes = [
        urllib.error.HTTPError(URL, code, "temporary", {}, None),
        urllib.error.HTTPError(URL, code, "temporary", {}, None),
        Response(b"ok"),
    ]
    delays = []

    def open_url(*args, **kwargs):
        outcome = outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(transfer.urllib.request, "urlopen", open_url)
    monkeypatch.setattr(transfer.time, "sleep", delays.append)

    assert transfer.fetch_bytes(URL) == b"ok"
    assert delays == [1, 2]
    assert f"HTTP {code}" in capsys.readouterr().err


def test_download_reports_periodic_progress_to_stderr(tmp_path, monkeypatch, capsys):
    body = b"x" * (5 * transfer.MIB)
    ticks = iter([0, 5, 10, 15, 20, 21])
    monkeypatch.setattr(transfer.urllib.request, "urlopen", lambda *a, **k: Response(body))
    monkeypatch.setattr(transfer.time, "monotonic", lambda: next(ticks))
    image = tmp_path / "installer.dmg"

    transfer.download_image(URL, len(body), hashlib.sha256(body).hexdigest(), image)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.splitlines() == [
        f"  Downloading {URL} (5.0 MiB)",
        "  Download progress: 2.0/5.0 MiB (40.0%), 0.2 MiB/s",
        "  Download progress: 4.0/5.0 MiB (80.0%), 0.2 MiB/s",
        "  Download complete: 5.0 MiB (100%), SHA-256 verified",
    ]
    assert image.read_bytes() == body


def test_fast_download_logs_start_and_completion_without_dividing_by_zero(
    tmp_path, monkeypatch, capsys
):
    monkeypatch.setattr(transfer.urllib.request, "urlopen", lambda *a, **k: Response(DMG_BYTES))
    monkeypatch.setattr(transfer.time, "monotonic", lambda: 0)

    transfer.download_image(URL, len(DMG_BYTES), DMG_HASH, tmp_path / "installer.dmg")

    assert capsys.readouterr().err.splitlines() == [
        f"  Downloading {URL} (0.0 MiB)",
        "  Download complete: 0.0 MiB (100%), SHA-256 verified",
    ]


def test_short_download_retries_without_appending_partial_bytes(tmp_path, monkeypatch, capsys):
    body = b"x" * (2 * transfer.MIB)
    outcomes = [Response(body[: transfer.MIB]), Response(body)]
    ticks = iter([0, 10, 20, 30, 31])
    monkeypatch.setattr(transfer.urllib.request, "urlopen", lambda *a, **k: outcomes.pop(0))
    monkeypatch.setattr(transfer.time, "sleep", lambda delay: None)
    monkeypatch.setattr(transfer.time, "monotonic", lambda: next(ticks))
    image = tmp_path / "installer.dmg"

    transfer.download_image(URL, len(body), hashlib.sha256(body).hexdigest(), image)

    assert image.read_bytes() == body
    messages = capsys.readouterr().err
    assert messages.count(f"Downloading {URL}") == 2
    assert messages.count("Download progress: 1.0/2.0 MiB (50.0%), 0.1 MiB/s") == 2
    assert "retry 1/5" in messages
    assert messages.count("Download complete") == 1


def test_discovers_non_idea_launcher_verifies_build_and_cleans_up(tmp_path, fake_system):
    app = transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, BUILD, tmp_path)

    assert app == transfer.Application(APP_HASH, APP_PATH, BUILD, BUNDLE_ID, APP_VERSION)
    assert "-readonly" in fake_system.attach_args
    assert "-nobrowse" in fake_system.attach_args
    assert not fake_system.mounted
    assert list(tmp_path.iterdir()) == []


def test_replaced_installer_is_never_mounted(tmp_path, fake_system, capsys):
    with pytest.raises(transfer.ArtifactError, match="SHA-256 mismatch"):
        transfer.collect_app(URL, len(DMG_BYTES), APP_HASH, BUILD, tmp_path)

    assert fake_system.attach_args is None
    assert list(tmp_path.iterdir()) == []
    assert "Download complete" not in capsys.readouterr().err


@pytest.mark.parametrize("bundle_build", ["PY-139.1803.14", "139.1803.14"])
def test_abbreviated_api_build_keeps_exact_bundle_identity(tmp_path, fake_system, bundle_build):
    fake_system.build = bundle_build

    app = transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, "139.1803", tmp_path)

    assert app == transfer.Application(APP_HASH, APP_PATH, bundle_build, BUNDLE_ID, APP_VERSION)
    assert not fake_system.mounted
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "api_build,bundle_build",
    [
        (BUILD, "123.456.799"),
        ("253.31033.213", "253.31033.21"),
        ("139.1803", "PY-139.18030.14"),
        ("107.756", "PY-107.576"),
        ("139.1803", "PY-139.1803.14.1"),
        ("139", "PY-139.1803"),
        ("139.1803.14", "PY-139.1803"),
        ("139.1803", "PY-139.1803.14-EAP"),
    ],
)
def test_bundle_build_mismatch_is_not_attributed_to_old_release(
    tmp_path, fake_system, api_build, bundle_build
):
    fake_system.build = bundle_build

    with pytest.raises(transfer.ArtifactError, match="Bundle build mismatch"):
        transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, api_build, tmp_path)

    assert not fake_system.mounted
    assert list(tmp_path.iterdir()) == []


def test_interrupt_after_attach_recovers_mount_and_removes_download(tmp_path, fake_system):
    fake_system.interrupt_attach = True

    with pytest.raises(KeyboardInterrupt):
        transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, BUILD, tmp_path)

    assert not fake_system.mounted
    assert list(tmp_path.iterdir()) == []


def test_failed_detach_preserves_image_and_stops_collection(tmp_path, fake_system):
    fake_system.fail_detach = True

    with pytest.raises(transfer.StopRun, match="Cleanup failed"):
        transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, BUILD, tmp_path)

    assert fake_system.mounted
    assert (fake_system.workspace / "installer.dmg").read_bytes() == DMG_BYTES


def test_low_disk_space_fails_before_download(tmp_path, monkeypatch):
    monkeypatch.setattr(transfer.shutil, "disk_usage", lambda path: SimpleNamespace(free=100))
    monkeypatch.setattr(transfer.sys, "platform", "darwin")
    monkeypatch.setattr(transfer.shutil, "which", lambda name: "/usr/bin/hdiutil")
    monkeypatch.setattr(
        transfer.urllib.request,
        "urlopen",
        lambda *a, **k: pytest.fail("Low disk space must prevent the request"),
    )

    with pytest.raises(transfer.StopRun, match="Insufficient disk space"):
        transfer.collect_app(URL, len(DMG_BYTES), DMG_HASH, BUILD, tmp_path)

    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("api_build,bundle_build", [(BUILD, BUILD), ("139.1803", "PY-139.1803.14")])
def test_zip_hashes_launcher_without_extracting_bundle(tmp_path, api_build, bundle_build):
    image = tmp_path / "app.zip"
    with zipfile.ZipFile(image, "w") as archive:
        for name, body in bundle_files(bundle_build).items():
            archive.writestr(name, body)

    assert transfer.hash_zipped_app(image, api_build, None) == transfer.Application(
        APP_HASH, APP_PATH, bundle_build, BUNDLE_ID, APP_VERSION
    )
    assert list(tmp_path.iterdir()) == [image]


@pytest.mark.parametrize(
    "api_build,bundle_build", [("111.277", "IU-111.277"), ("139.1803", "PY-139.1803.14")]
)
def test_legacy_plist_build_prefix_is_supported(api_build, bundle_build):
    content = plistlib.dumps(
        {
            "CFBundleExecutable": "idea",
            "CFBundleVersion": bundle_build,
            "CFBundleShortVersionString": "11.0.2",
        }
    )

    name, build, bundle_id, version = transfer.bundle_metadata(
        "IntelliJ IDEA.app", lambda name: content, lambda name: False, api_build
    )

    assert name == "IntelliJ IDEA.app/Contents/MacOS/idea"
    assert build == bundle_build
    assert bundle_id == ""
    assert version == "11.0.2"


@pytest.mark.parametrize(
    "key,value", [("CFBundleIdentifier", 123), ("CFBundleShortVersionString", ["1.2.3"])]
)
def test_invalid_bundle_identity_is_not_silently_discarded(key, value):
    files = bundle_files()
    path = "Demo IDE.app/Contents/Info.plist"
    info = plistlib.loads(files[path])
    info[key] = value
    files[path] = plistlib.dumps(info)

    with pytest.raises(transfer.ArtifactError, match=f"{key} is not a string"):
        transfer.bundle_metadata("Demo IDE.app", files.__getitem__, files.__contains__, BUILD)


@pytest.mark.native
@pytest.mark.skipif(sys.platform != "darwin", reason="Requires native macOS disk images")
def test_native_dmg_round_trip(tmp_path, monkeypatch):
    source = tmp_path / "source"
    for name, body in bundle_files().items():
        path = source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(body)
    image = tmp_path / "fixture.dmg"
    transfer.hdiutil(
        "create",
        "-srcfolder",
        str(source),
        "-volname",
        "JetBrains Hash Test",
        "-format",
        "UDZO",
        "-o",
        str(image),
    )
    payload = image.read_bytes()
    monkeypatch.setattr(transfer.urllib.request, "urlopen", lambda *a, **k: Response(payload))
    work = tmp_path / "work"
    work.mkdir()

    app = transfer.collect_app(URL, len(payload), hashlib.sha256(payload).hexdigest(), BUILD, work)

    assert app == transfer.Application(APP_HASH, APP_PATH, BUILD, BUNDLE_ID, APP_VERSION)
    assert list(work.iterdir()) == []
