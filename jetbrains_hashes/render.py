"""Deterministic release-first Markdown views of the persistent history."""

from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path

from .history import History, Record, coverage, grouped_builds, load
from .transfer import atomic_write

HEADER = (
    "| Version | Build version | Installer type | Installer SHA256 | Application SHA256 | Release date |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)


def cell(value: str) -> str:
    return html.escape(value).replace("|", "&#124;").replace("`", "&#96;").replace("\n", " ")


def natural(value: str) -> tuple:
    return tuple(
        (1, int(part)) if part.isdigit() else (0, part) for part in re.split(r"(\d+)", value)
    )


def hash_cell(row: Record, application: bool) -> str:
    digest = row.app_sha256 if application else row.installer_sha256
    if digest:
        return f"`{digest}`"
    if row.error and (application or row.error_stage in ("checksum", "metadata")):
        return "Unavailable (see collection notes)"
    return "Pending" if row.installer_url else "Not advertised"


def render_product(history: History) -> str:
    builds = grouped_builds(history)
    payloads: dict[tuple, set[str]] = defaultdict(set)
    for row in history.records:
        if row.installer_sha256:
            payloads[row.release_key()].add(row.installer_sha256)
    rows = sorted(
        history.records,
        key=lambda row: (
            natural(row.version),
            natural(row.build),
            row.platform,
            row.release_date,
            row.installer_sha256,
            row.metadata_key(),
        ),
        reverse=True,
    )

    def table(released: bool) -> str:
        lines = [HEADER]
        for row in rows:
            if not row.installer_url or (row.release_type.lower() == "release") != released:
                continue
            version, build = (
                cell(row.version or "(not provided)"),
                cell(row.build or "(not provided)"),
            )
            if len(builds[(row.release_type, row.version)]) > 1:
                version, build = f"**{version}**", f"**{build}**"
            if len(payloads[row.release_key()]) > 1:
                version += " (repacked)"
            if not released:
                version += f" <sub>{cell(row.release_type)}</sub>"
            lines.append(
                f"| {version} | {build} | `{cell(row.platform)}` | {hash_cell(row, False)} | "
                f"{hash_cell(row, True)} | {cell(row.release_date)} |\n"
            )
        return "".join(lines)

    counts = coverage(history)
    result = table(True)
    result += "\n## EAP, RC, preview, and other non-release builds\n\n" + table(False)
    result += (
        f"\n## Collection notes\n\n"
        f"Product: **{cell(history.name)}** (`{history.code}`). "
        f"[Machine-readable history](../data/{history.code}.json).\n\n"
        f"Installer hashes: **{counts['installer_hashes']}/{counts['advertised']}**; "
        f"application hashes: **{counts['app_hashes']}/{counts['advertised']}**; "
        f"not advertised: **{counts['not_advertised']}**.\n\n"
        "Bold versions/builds have multiple observed build numbers for the same version and channel. "
        "`(repacked)` means multiple installer hashes were observed for the same version, build, "
        "channel, and installer type. History is retained even after entries disappear from the API.\n\n"
        "Rows are sorted by version, build version, and installer type, descending, with numeric "
        "version/build components compared numerically rather than by release date.\n\n"
        "`Pending` means collection has not completed. Rows without an advertised macOS installer "
        "are omitted. Missing hashes are not inferred. Application hashes cover "
        "the bundle's main `Contents/MacOS/` executable, not the bundle or signing CDHash.\n"
    )
    if history.empty_downloads:
        result += (
            "\n### Versions with empty downloads\n\n"
            "These releases had an entirely empty `downloads` object in the latest available "
            "catalog. Missing architectures and releases with only non-macOS downloads are not "
            "listed here. This does not prove that an installer never existed.\n\n"
            "| Version | Build version | Channel | Release date |\n"
            "| --- | --- | --- | --- |\n"
        )
        for release in sorted(
            history.empty_downloads,
            key=lambda release: (
                natural(release.version),
                natural(release.build),
                release.release_type,
                release.release_date,
                release.version,
                release.build,
            ),
            reverse=True,
        ):
            result += (
                f"| {cell(release.version or '(not provided)')} | "
                f"{cell(release.build or '(not provided)')} | "
                f"{cell(release.release_type)} | {cell(release.release_date)} |\n"
            )
    errors = [row for row in rows if row.error]
    if errors:
        result += "\n### Collection errors\n\n"
        for row in errors:
            result += (
                f"- {cell(row.version)} / {cell(row.build)} / `{cell(row.platform)}` "
                f"({cell(row.error_stage)}): {cell(row.error)}\n"
            )
    return result


def render_all(data_dir: Path, docs_dir: Path) -> None:
    histories = [load(path) for path in sorted(data_dir.glob("*.json"))]
    index = (
        "# JetBrains IDE hashes\n\n"
        "Each product page starts with released versions, followed by every other API channel. "
        "Rows are sorted by version, build version, and installer type, descending. "
        "Only advertised macOS installers appear in the main tables; versions with entirely "
        "empty downloads are listed in Collection notes. "
        "Product codes keep renamed and legacy editions distinct.\n\n"
        "| IDE / product | Product code | Installer hashes | Application hashes | Not advertised |\n"
        "| --- | --- | --- | --- | --- |\n"
    )
    for history in sorted(histories, key=lambda item: (item.name.casefold(), item.code)):
        atomic_write(docs_dir / f"{history.code}.md", render_product(history))
        count = coverage(history)
        index += (
            f"| [{cell(history.name)}]({history.code}.md) | `{history.code}` | "
            f"{count['installer_hashes']}/{count['advertised']} | "
            f"{count['app_hashes']}/{count['advertised']} | {count['not_advertised']} |\n"
        )
    atomic_write(docs_dir / "README.md", index)
