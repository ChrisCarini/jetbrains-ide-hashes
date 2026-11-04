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


@pytest.mark.parametrize(
    "product,expected", [(None, ["IIU", "PCP"]), ("", ["IIU", "PCP"]), ("PCP", ["PCP"])]
)
def test_discover_product_selection_controls_snapshots_seed_and_matrix(
    tmp_path, product_factory, capsys, product, expected
):
    pcp = product_factory(code="PCP")
    for channel in ("eap", "rc", "preview", "future-channel"):
        pcp["releases"].extend(product_factory(code="PCP", channel=channel)["releases"])
    source = tmp_path / "products.json"
    source.write_text(json.dumps([product_factory(), pcp]))
    data, docs, snapshots = tmp_path / "data", tmp_path / "ides", tmp_path / "catalog"
    output = tmp_path / "github-output"
    output.write_text("existing=value\n")
    args = [
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
        "--github-output",
        str(output),
    ]
    if product is not None:
        args.extend(["--product", product])

    assert cli.main(args) == 0

    matrix = json.dumps({"product": expected}, separators=(",", ":"))
    assert capsys.readouterr().out == matrix + "\n"
    assert output.read_text() == f"existing=value\nmatrix={matrix}\n"
    assert {path.stem for path in snapshots.glob("*.json")} == set(expected)
    assert {path.stem for path in data.glob("*.json")} == set(expected)
    assert {path.stem for path in docs.glob("*.md")} == set(expected) | {"README"}
    snapshot = json.loads((snapshots / "PCP.json").read_text())
    assert {release["type"] for release in snapshot["product"]["releases"]} == {
        "release",
        "eap",
        "rc",
        "preview",
        "future-channel",
    }


@pytest.mark.parametrize(
    "product,error",
    [
        ("UNKNOWN", "Unknown IDE product code: UNKNOWN. Available codes: IIU, PCP"),
        ("TC", "Unknown IDE product code: TC. Available codes: IIU, PCP"),
        ("../PCP", "Invalid product code"),
    ],
)
def test_discover_rejects_unknown_non_ide_and_invalid_products(
    tmp_path, product_factory, capsys, product, error
):
    non_ide = product_factory(code="TC")
    non_ide["categories"] = ["Continuous integration"]
    source = tmp_path / "products.json"
    source.write_text(json.dumps([product_factory(), product_factory(code="PCP"), non_ide]))
    data, docs, snapshots = tmp_path / "data", tmp_path / "ides", tmp_path / "catalog"
    output = tmp_path / "github-output"

    assert (
        cli.main(
            [
                "discover",
                "--product",
                product,
                "--catalog-file",
                str(source),
                "--seed",
                "--data-dir",
                str(data),
                "--docs-dir",
                str(docs),
                "--output-dir",
                str(snapshots),
                "--github-output",
                str(output),
            ]
        )
        == 1
    )

    captured = capsys.readouterr()
    assert error in captured.err
    assert captured.out == ""
    assert not output.exists()
    assert not snapshots.exists()
    assert not list(data.glob("*.json"))
    assert not docs.exists()


def test_discover_can_select_a_retired_product(tmp_path, product_factory, capsys):
    data, snapshots = tmp_path / "data", tmp_path / "catalog"
    history.save(history.History("RETIRED", "Retired IDE"), data)
    source = tmp_path / "products.json"
    source.write_text(json.dumps([product_factory()]))
    before = (data / "RETIRED.json").read_bytes()

    assert (
        cli.main(
            [
                "discover",
                "--product",
                "RETIRED",
                "--catalog-file",
                str(source),
                "--data-dir",
                str(data),
                "--output-dir",
                str(snapshots),
            ]
        )
        == 0
    )

    assert json.loads(capsys.readouterr().out) == {"product": ["RETIRED"]}
    assert {path.stem for path in snapshots.glob("*.json")} == {"RETIRED"}
    assert json.loads((snapshots / "RETIRED.json").read_text())["product"]["absent_from_catalog"]
    assert (data / "RETIRED.json").read_bytes() == before


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
