import json
from dataclasses import replace

import pytest

from jetbrains_hashes import cli, history, render

T1 = "2026-11-03T00:00:00+00:00"


@pytest.mark.parametrize("channel", ["release", "eap", "rc", "preview", "future-channel"])
def test_build_version_column_between_version_and_installer_type(product_factory, channel):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(channel=channel), T1)
    row = next(row for row in state.records if row.platform == "mac")
    row.installer_sha256, row.app_sha256 = "a" * 64, "b" * 64

    text = render.render_product(state)

    header = (
        "| Version | Build version | Installer type | Installer SHA256 | "
        "Application SHA256 | Release date |\n"
    )
    assert text.count(header) == 2
    version = "1.2.3" if channel == "release" else f"1.2.3 <sub>{channel}</sub>"
    assert (
        f"| {version} | 123.456.789 | `mac` | `{'a' * 64}` | `{'b' * 64}` | 2026-11-03 |\n" in text
    )


def test_tables_start_with_only_releases_then_all_other_channels(product_factory):
    product = product_factory()
    for channel in ("eap", "rc", "preview", "future-channel"):
        product["releases"].extend(product_factory(channel=channel)["releases"])
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)
    state.records.append(replace(state.records[0], build="123.456.799"))

    text = render.render_product(state)
    releases, other = text.split("\n## EAP, RC, preview, and other non-release builds\n\n")

    assert releases.startswith(render.HEADER)
    assert releases.count("| **1.2.3**") == 3
    assert "<sub>" not in releases
    assert all(
        f"<sub>{channel}</sub>" in other for channel in ("eap", "rc", "preview", "future-channel")
    )
    assert "**123.456.789**" in releases and "**123.456.799**" in releases


def test_markdown_is_deterministic_and_escapes_cells(product_factory):
    state = history.History("IIU", "Example <IDE>")
    product = product_factory(version="1|<script>")
    history.refresh_metadata(state, product, T1)

    first = render.render_product(state)
    state.records.reverse()

    assert render.render_product(state) == first
    assert "1&#124;&lt;script&gt;" in first


def test_cli_seeds_without_network_and_render_is_idempotent(tmp_path, product_factory, monkeypatch):
    source = tmp_path / "products.json"
    source.write_text(json.dumps([product_factory(), product_factory(code="PCP")]))
    data, docs, snapshots = tmp_path / "data", tmp_path / "ides", tmp_path / "catalog"
    monkeypatch.setattr(
        history.transfer.urllib.request,
        "urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Unexpected network")),
    )

    assert (
        cli.main(
            [
                "discover",
                "--catalog-file",
                str(source),
                "--seed",
                "--data-dir",
                str(data),
                "--docs-dir",
                str(docs),
                "--output-dir",
                str(snapshots),
            ]
        )
        == 0
    )
    before = {path.name: path.read_bytes() for path in docs.glob("*.md")}
    assert cli.main(["render", "--data-dir", str(data), "--docs-dir", str(docs)]) == 0

    assert before == {path.name: path.read_bytes() for path in docs.glob("*.md")}
    assert set(before) == {"IIU.md", "PCP.md", "README.md"}
    assert len(history.load(data / "IIU.json").records) == 2


def test_publication_merges_partial_artifacts_without_dropping_other_products(
    tmp_path, product_factory
):
    data, incoming, docs = tmp_path / "data", tmp_path / "incoming", tmp_path / "ides"
    for code in ("IIU", "PCP"):
        state = history.History(code, code)
        history.refresh_metadata(state, product_factory(code=code), T1)
        history.save(state, data)
    pcp_before = (data / "PCP.json").read_bytes()
    state = history.load(data / "IIU.json")
    row = next(row for row in state.records if row.installer_url)
    row.installer_sha256 = "a" * 64
    row.app_sha256, row.app_path = "b" * 64, "IDE.app/Contents/MacOS/idea"
    history.save(state, incoming)

    assert (
        cli.main(
            [
                "merge",
                "--from-dir",
                str(incoming),
                "--data-dir",
                str(data),
                "--docs-dir",
                str(docs),
            ]
        )
        == 0
    )

    assert (data / "PCP.json").read_bytes() == pcp_before
    assert history.coverage(history.load(data / "IIU.json"))["app_hashes"] == 1
    assert (docs / "PCP.md").exists()


def test_empty_publication_is_an_error(tmp_path):
    assert (
        cli.main(
            [
                "merge",
                "--from-dir",
                str(tmp_path / "missing"),
                "--data-dir",
                str(tmp_path / "data"),
                "--docs-dir",
                str(tmp_path / "ides"),
            ]
        )
        == 1
    )
