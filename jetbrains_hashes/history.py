"""Refresh catalogs without discarding previously observed builds or payloads."""

from __future__ import annotations

import csv
import json
import re
import urllib.parse
from collections import defaultdict
from dataclasses import asdict, dataclass, field, fields, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from . import transfer
from .transfer import ArtifactError, BudgetReached, StopRun, atomic_write, log

API_URL = "https://data.services.jetbrains.com/products"
PLATFORMS = {
    "mac": ("mac", "macos_x64"),
    "macM1": ("macM1", "macos_aarch64"),
}
PRODUCT_CODE = re.compile(r"[A-Z][A-Z0-9]*")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Record:
    version: str
    build: str
    release_type: str
    release_date: str
    platform: str
    installer_url: str = ""
    checksum_url: str = ""
    size_bytes: int = 0
    installer_sha256: str = ""
    app_sha256: str = ""
    app_path: str = ""
    app_build: str = ""
    first_seen: str = ""
    current: bool = True
    last_attempt: str = ""
    error_stage: str = ""
    error: str = ""

    def release_key(self) -> tuple:
        return self.version, self.build, self.release_type, self.platform

    def metadata_key(self) -> tuple:
        return (*self.release_key(), self.installer_url, self.checksum_url, self.size_bytes)

    def artifact_key(self) -> tuple:
        return (*self.metadata_key(), self.installer_sha256)

    @property
    def status(self) -> str:
        if self.app_sha256:
            return "complete"
        if self.error:
            return "error"
        if not self.installer_url:
            return "not_advertised"
        return "app_pending" if self.installer_sha256 else "checksum_pending"


@dataclass(frozen=True, order=True)
class EmptyDownloadRelease:
    version: str
    build: str
    release_type: str
    release_date: str


@dataclass
class History:
    code: str
    name: str
    records: list[Record] = field(default_factory=list)
    catalog_fetched_at: str = ""
    catalog_release_count: int = 0
    ignored_download_types: list[str] = field(default_factory=list)
    empty_downloads: list[EmptyDownloadRelease] | None = None


def validate_code(code: str) -> str:
    if not isinstance(code, str) or not PRODUCT_CODE.fullmatch(code):
        raise StopRun(f"Invalid product code: {code!r}")
    return code


def save(history: History, directory: Path) -> None:
    history.records.sort(key=lambda r: (r.metadata_key(), r.installer_sha256))
    if history.empty_downloads is not None:
        history.empty_downloads.sort()
    payload = {"schema_version": 1, **asdict(history)}
    if history.empty_downloads is None:
        del payload["empty_downloads"]
    atomic_write(
        directory / f"{validate_code(history.code)}.json", json.dumps(payload, indent=2) + "\n"
    )


def load(path: Path) -> History:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.pop("schema_version", None) != 1:
        raise StopRun(f"Unsupported history schema in {path}")
    try:
        records = [Record(**row) for row in data.pop("records")]
        empty_downloads = data.pop("empty_downloads", None)
        if empty_downloads is not None and not isinstance(empty_downloads, list):
            raise TypeError("Expected an empty-download release array")
        history = History(
            **data,
            records=records,
            empty_downloads=(
                [EmptyDownloadRelease(**release) for release in empty_downloads]
                if empty_downloads is not None
                else None
            ),
        )
    except (KeyError, TypeError) as exc:
        raise StopRun(f"Invalid history structure in {path}: {exc}") from exc
    if validate_code(history.code) != path.stem:
        raise StopRun(f"Product code does not match history filename: {path}")
    for release in history.empty_downloads or []:
        if any(
            not isinstance(getattr(release, item.name), str)
            for item in fields(EmptyDownloadRelease)
        ):
            raise StopRun(f"Invalid empty-download release types in {path}")
    if len(set(history.empty_downloads or [])) != len(history.empty_downloads or []):
        raise StopRun(f"Duplicate empty-download release in {path}")
    seen = set()
    string_fields = [f.name for f in fields(Record) if f.name not in ("size_bytes", "current")]
    for row in records:
        if (
            any(not isinstance(getattr(row, name), str) for name in string_fields)
            or type(row.size_bytes) is not int
            or row.size_bytes < 0
            or type(row.current) is not bool
        ):
            raise StopRun(f"Invalid record types in {path}")
        if row.platform not in {p for aliases in PLATFORMS.values() for p in aliases}:
            raise StopRun(f"Unsupported platform in {path}: {row.platform}")
        if row.artifact_key() in seen:
            raise StopRun(f"Duplicate artifact in {path}: {row.release_key()}")
        seen.add(row.artifact_key())
        for digest in (row.installer_sha256, row.app_sha256):
            if digest and not transfer.SHA256.fullmatch(digest):
                raise StopRun(f"Invalid SHA-256 in {path}")
        if row.app_sha256 and (not row.installer_sha256 or not row.app_path):
            raise StopRun(f"Application hash lacks installer provenance in {path}")
    return history


def valid_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urllib.parse.urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def descriptors(product: dict, observed_at: str) -> list[Record]:
    validate_code(product.get("code"))
    releases = product.get("releases")
    if not isinstance(releases, list):
        raise StopRun(f"{product['code']}: expected a releases array")
    rows = []
    seen = set()
    for release in releases:
        if not isinstance(release, dict):
            raise StopRun(f"{product['code']}: release is not an object")
        for key in ("version", "build", "date", "type"):
            if release.get(key) is not None and not isinstance(release[key], str):
                raise StopRun(f"{product['code']}: invalid release field {key}")
        downloads = release.get("downloads", {})
        for canonical, aliases in PLATFORMS.items():
            available_keys = (
                [key for key in aliases if key in downloads] if isinstance(downloads, dict) else []
            )
            for platform in available_keys or [canonical]:
                row = Record(
                    version=release.get("version") or "",
                    build=release.get("build") or "",
                    release_type=release.get("type") or "unknown",
                    release_date=release.get("date") or "",
                    platform=platform,
                    first_seen=observed_at,
                )
                if not isinstance(downloads, dict):
                    row.error_stage, row.error = (
                        "metadata",
                        "Missing or non-object downloads metadata",
                    )
                elif platform in downloads:
                    download = downloads[platform]
                    if (
                        not isinstance(download, dict)
                        or not valid_url(download.get("link"))
                        or not valid_url(download.get("checksumLink"))
                        or type(download.get("size")) is not int
                        or download["size"] <= 0
                    ):
                        row.error_stage, row.error = (
                            "metadata",
                            f"Invalid {platform} installer metadata",
                        )
                    else:
                        row.installer_url = download["link"]
                        row.checksum_url = download["checksumLink"]
                        row.size_bytes = download["size"]
                if row.metadata_key() in seen:
                    raise StopRun(
                        f"{product['code']}: duplicate catalog artifact: {row.metadata_key()}"
                    )
                seen.add(row.metadata_key())
                rows.append(row)
    return rows


def discover(products: list[dict], existing: list[History]) -> list[dict]:
    if not isinstance(products, list) or not products:
        raise StopRun("Expected a nonempty product array from JetBrains")
    by_code = {}
    for product in products:
        if not isinstance(product, dict):
            raise StopRun("Product is not an object")
        code = validate_code(product.get("code"))
        if code in by_code:
            raise StopRun(f"Duplicate product code: {code}")
        by_code[code] = product
    selected = {
        code
        for code, product in by_code.items()
        if "IDE" in (product.get("categories") or []) or code in ("RD", "GW")
    } | {history.code for history in existing}
    result = []
    for code in sorted(selected):
        if code in by_code:
            product = by_code[code]
            result.append(
                {
                    "code": code,
                    "name": product["name"],
                    "releases": [
                        {key: release.get(key) for key in ("version", "build", "date", "type")}
                        | ({"downloads": release["downloads"]} if "downloads" in release else {})
                        for release in product["releases"]
                    ],
                }
            )
        else:
            previous = next(history for history in existing if history.code == code)
            log(f"{code}: absent from current catalog; retaining its historical records")
            result.append(
                {
                    "code": code,
                    "name": previous.name,
                    "releases": [],
                    "absent_from_catalog": True,
                }
            )
    return result


def matching(history: History, descriptor: Record) -> list[Record]:
    return [row for row in history.records if row.metadata_key() == descriptor.metadata_key()]


def refresh_metadata(history: History, product: dict, observed_at: str) -> list[Record]:
    if product.get("code") != history.code:
        raise StopRun("Cannot apply a different product's catalog to this history")
    if observed_at < history.catalog_fetched_at:
        raise StopRun(f"{history.code}: refusing a catalog snapshot older than the saved history")
    sources = descriptors(product, observed_at)
    if not sources and history.records and not product.get("absent_from_catalog"):
        raise StopRun(
            f"{history.code}: unexpectedly empty release catalog; retaining previous state"
        )
    for row in history.records:
        row.current = False
    for source in sources:
        matches = matching(history, source)
        if not matches:
            placeholders = [
                row
                for row in history.records
                if row.release_key() == source.release_key() and not row.installer_url
            ]
            historical = [
                row
                for row in history.records
                if row.release_key() == source.release_key() and row.installer_url
            ]
            if not source.installer_url and not source.error and historical:
                continue
            if source.installer_url and placeholders:
                previous = placeholders[0]
                previous.installer_url = source.installer_url
                previous.checksum_url = source.checksum_url
                previous.size_bytes = source.size_bytes
                previous.error_stage, previous.error = "", ""
                matches = [previous]
            else:
                history.records.append(source)
                matches = [source]
        for row in matches:
            row.current = True
            if row.error_stage == "metadata" or source.error_stage == "metadata":
                row.error_stage, row.error = source.error_stage, source.error
    history.name = product["name"]
    history.catalog_fetched_at = observed_at
    history.catalog_release_count = len(product["releases"])
    if not product.get("absent_from_catalog"):
        history.empty_downloads = [
            EmptyDownloadRelease(
                version=release.get("version") or "",
                build=release.get("build") or "",
                release_type=release.get("type") or "unknown",
                release_date=release.get("date") or "",
            )
            for release in product["releases"]
            if release.get("downloads", {}) == {}
        ]
    supported = {p for aliases in PLATFORMS.values() for p in aliases}
    history.ignored_download_types = sorted(
        {
            key
            for release in product["releases"]
            for key in (release.get("downloads") or {})
            if key not in supported
        }
    )
    return sources


def observe_checksum(history: History, source: Record, digest: str, observed_at: str) -> Record:
    matches = matching(history, source)
    target = next((row for row in matches if row.installer_sha256 == digest), None)
    if target is None:
        target = next((row for row in matches if not row.installer_sha256), None)
    if target is None:
        target = replace(source, first_seen=observed_at)
        history.records.append(target)
    for row in matches:
        row.current = False
    target.installer_sha256 = digest
    target.current = True
    if target.error_stage == "checksum":
        target.error_stage, target.error = "", ""
    return target


def collect(
    history: History,
    sources: list[Record],
    persist: Callable[[], None],
    work_dir: Path,
    max_installers: int,
    deadline: float | None,
    checksums_only: bool = False,
) -> int:
    failures = 0
    cache: dict[str, bytes] = {}
    url_builds: dict[str, set[str]] = defaultdict(set)
    for source in sources:
        if source.installer_url:
            url_builds[source.installer_url].add(source.build)
    try:
        for source in sources:
            transfer.check_deadline(deadline)
            if source.error:
                log(f"ERROR {history.code} {source.release_key()}: {source.error}")
                failures += 1
            if not source.checksum_url:
                continue
            try:
                if len(url_builds[source.installer_url]) > 1:
                    raise ArtifactError(
                        "Installer URL is advertised for multiple builds; "
                        "a checksum sidecar cannot establish which build it belongs to"
                    )
                if source.checksum_url not in cache:
                    cache[source.checksum_url] = transfer.fetch_bytes(source.checksum_url, deadline)
                digest = transfer.parse_checksum(cache[source.checksum_url], source.installer_url)
                observe_checksum(history, source, digest, history.catalog_fetched_at)
            except ArtifactError as exc:
                candidates = matching(history, source)
                target = max(candidates, key=lambda row: row.first_seen)
                target.error_stage, target.error = "checksum", str(exc)
                failures += 1
                log(f"ERROR {history.code} {source.release_key()}: {exc}")
            persist()
        if checksums_only:
            return failures

        work_dir.mkdir(parents=True, exist_ok=True)
        pending = [row for row in history.records if row.installer_sha256 and not row.app_sha256]
        # New builds and never-attempted history precede retries, so one bad URL cannot starve backfill.
        pending.sort(key=lambda row: (row.release_date, row.build, row.platform), reverse=True)
        pending.sort(key=lambda row: (bool(row.last_attempt), row.last_attempt, not row.current))
        downloaded = 0
        for row in pending:
            transfer.check_deadline(deadline)
            cached = next(
                (
                    previous
                    for previous in history.records
                    if previous.app_sha256
                    and previous.installer_sha256 == row.installer_sha256
                    and transfer.normalize_build(previous.build)
                    == transfer.normalize_build(row.build)
                ),
                None,
            )
            if cached:
                row.app_sha256, row.app_path, row.app_build = (
                    cached.app_sha256,
                    cached.app_path,
                    cached.app_build,
                )
                row.error_stage, row.error = "", ""
                persist()
                continue
            if downloaded >= max_installers:
                log(
                    f"{history.code}: installer budget reached ({max_installers}); backfill remains pending"
                )
                break
            downloaded += 1
            row.last_attempt = now()
            persist()
            log(
                f"{history.code} app [{downloaded}/{max_installers}]: "
                f"{row.version} {row.build} {row.platform} ({row.size_bytes / transfer.GIB:.2f} GiB)"
            )
            try:
                app = transfer.collect_app(
                    row.installer_url,
                    row.size_bytes,
                    row.installer_sha256,
                    row.build,
                    work_dir,
                    deadline,
                )
                row.app_sha256, row.app_path, row.app_build = app.sha256, app.path, app.build
                row.error_stage, row.error = "", ""
            except (ArtifactError, StopRun) as exc:
                row.error_stage = "application"
                row.error = str(exc).replace(str(work_dir.resolve()), "<work-dir>")
                failures += 1
                log(f"ERROR {history.code} {row.release_key()}: {exc}")
                persist()
                if isinstance(exc, StopRun):
                    raise
            persist()
    except BudgetReached as exc:
        log(f"{history.code}: {exc}; checkpoint retained for the next run")
    finally:
        persist()
    return failures


def merge(destination: History, incoming: History) -> None:
    if destination.code != incoming.code:
        raise StopRun("Cannot merge different products")
    newer = incoming.catalog_fetched_at >= destination.catalog_fetched_at
    if newer:
        for row in destination.records:
            row.current = False
    for observation in incoming.records:
        matches = matching(destination, observation)
        target = next(
            (row for row in matches if row.installer_sha256 == observation.installer_sha256), None
        )
        if target is None and observation.installer_sha256:
            target = next((row for row in matches if not row.installer_sha256), None)
        if target is None and not observation.installer_sha256 and matches:
            continue
        if target is None:
            placeholders = [
                row
                for row in destination.records
                if row.release_key() == observation.release_key()
                and not row.installer_url
                and not row.installer_sha256
            ]
            if observation.installer_url and placeholders:
                target = placeholders[0]
                target.installer_url = observation.installer_url
                target.checksum_url = observation.checksum_url
                target.size_bytes = observation.size_bytes
            else:
                destination.records.append(replace(observation))
                continue
        if (
            target.app_sha256
            and observation.app_sha256
            and (
                target.app_sha256 != observation.app_sha256
                or target.app_path != observation.app_path
            )
        ):
            raise StopRun(
                f"Conflicting app hashes for the same installer: {observation.artifact_key()}"
            )
        if observation.installer_sha256:
            target.installer_sha256 = observation.installer_sha256
        if observation.app_sha256:
            target.app_sha256 = observation.app_sha256
            target.app_path = observation.app_path
            target.app_build = observation.app_build
        if observation.first_seen:
            target.first_seen = min(filter(None, (target.first_seen, observation.first_seen)))
        if newer:
            target.current = observation.current
        if observation.last_attempt > target.last_attempt or (
            newer and observation.last_attempt == target.last_attempt
        ):
            target.last_attempt = observation.last_attempt
            target.error_stage, target.error = observation.error_stage, observation.error
    if newer:
        destination.name = incoming.name
        destination.catalog_fetched_at = incoming.catalog_fetched_at
        destination.catalog_release_count = incoming.catalog_release_count
        destination.ignored_download_types = incoming.ignored_download_types
        if incoming.empty_downloads is not None:
            destination.empty_downloads = list(incoming.empty_downloads)


def import_legacy(directory: Path, destination: History) -> None:
    snapshot = json.loads((directory / "catalog.json").read_text(encoding="utf-8"))
    if snapshot.get("api_url") != API_URL + "?release.type=release&code=IIU":
        raise StopRun("Legacy import expects the original IIU release-only snapshot")
    if destination.code != "IIU":
        raise StopRun("Legacy IntelliJ data can only be imported into IIU")
    imported = History(code="IIU", name=destination.name)
    with (directory / "hashes.csv").open(encoding="utf-8", newline="") as source:
        for row in csv.DictReader(source):
            if row["status"] == "error":
                raise StopRun("Resolve legacy collection errors before importing")
            imported.records.append(
                Record(
                    version=row["version"],
                    build=row["build"],
                    release_type="release",
                    release_date=row["release_date"],
                    platform=row["platform"],
                    installer_url=row["installer_url"],
                    checksum_url=row["checksum_url"],
                    size_bytes=int(row["size_bytes"]),
                    installer_sha256=row["installer_sha256"],
                    app_sha256=row["app_sha256"],
                    app_path=row["app_path"],
                    first_seen=snapshot["fetched_at"],
                    current=False,
                )
            )
    merge(destination, imported)


def coverage(history: History) -> dict[str, int]:
    return {
        "entries": len(history.records),
        "advertised": sum(bool(row.installer_url) for row in history.records),
        "installer_hashes": sum(bool(row.installer_sha256) for row in history.records),
        "app_hashes": sum(bool(row.app_sha256) for row in history.records),
        "not_advertised": sum(row.status == "not_advertised" for row in history.records),
        "errors": sum(bool(row.error) for row in history.records),
    }


def grouped_builds(history: History) -> dict[tuple[str, str], set[str]]:
    result: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in history.records:
        if row.build:
            result[(row.release_type, row.version)].add(row.build)
    return result
