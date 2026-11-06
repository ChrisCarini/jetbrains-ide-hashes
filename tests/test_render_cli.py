import json
from dataclasses import replace

import pytest

from jetbrains_hashes import cli, history, render

T1 = "2026-11-03T00:00:00+00:00"
T2 = "2026-11-04T00:00:00+00:00"


def main_table_rows(text):
    tables = text.split("\n## Collection notes\n", 1)[0]
    return [
        [value.strip().replace("**", "").strip("`") for value in line.split("|")[1:-1]]
        for line in tables.splitlines()
        if line.startswith("| ") and not line.startswith(("| Version |", "| --- |"))
    ]


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
    assert releases.count("| **1.2.3**") == 2
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


@pytest.mark.parametrize("channel", ["release", "eap", "rc", "preview", "future-channel"])
def test_tables_sort_version_build_and_installer_type_before_date(product_factory, channel):
    product = product_factory()
    product["releases"] = []
    for version, build, date in (
        ("2026.9", "999.99", "2026-12-03"),
        ("2026.10", "261.9", "2026-12-02"),
        ("2026.10", "261.10", "2026-01-01"),
        ("2026.10.1", "1", "2025-01-01"),
    ):
        release = product_factory(
            version=version,
            build=build,
            channel=channel,
            platforms=("mac", "macM1", "macos_x64", "macos_aarch64"),
        )["releases"][0]
        release["date"] = date
        product["releases"].append(release)
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)
    for row in state.records:
        if row.platform == "mac":
            row.release_date = "2099-01-01"

    text = render.render_product(state)
    suffix = "" if channel == "release" else f" <sub>{channel}</sub>"
    expected = [
        [version + suffix, build, platform]
        for version, build in (
            ("2026.10.1", "1"),
            ("2026.10", "261.10"),
            ("2026.10", "261.9"),
            ("2026.9", "999.99"),
        )
        for platform in ("macos_x64", "macos_aarch64", "macM1", "mac")
    ]
    assert [row[:3] for row in main_table_rows(text)] == expected
    state.records.reverse()
    assert render.render_product(state) == text


def test_matching_version_build_type_and_date_have_deterministic_ties(product_factory):
    product = product_factory(channel="eap")
    product["releases"].extend(product_factory(channel="rc")["releases"])
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)
    state.records.append(
        replace(state.records[0], installer_url="https://download.jetbrains.com/other.dmg")
    )

    text = render.render_product(state)
    state.records.reverse()

    assert render.render_product(state) == text


@pytest.mark.parametrize("channel", ["release", "eap"])
@pytest.mark.parametrize(
    "platforms,expected",
    [
        (("mac",), {"mac"}),
        (("macM1",), {"macM1"}),
        (("macos_x64",), {"macos_x64"}),
        (("macos_aarch64",), {"macos_aarch64"}),
        (("mac", "macM1"), {"mac", "macM1"}),
        (("macos_x64", "macos_aarch64"), {"macos_x64", "macos_aarch64"}),
        (("linux",), set()),
        (("mac-jbr17",), set()),
        (("thirdPartyLibrariesJson",), set()),
        ((), set()),
    ],
)
def test_only_advertised_installers_and_no_download_notes(
    product_factory, channel, platforms, expected
):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(channel=channel, platforms=platforms), T1)

    text = render.render_product(state)

    assert {row[2] for row in main_table_rows(text)} == expected
    assert len(main_table_rows(text)) == len(expected)
    assert "Not advertised" not in text.split("\n## Collection notes\n", 1)[0]
    assert ("### Versions with no advertised downloads" in text) == (not platforms)
    if not platforms:
        assert text.count(f"| 1.2.3 | 123.456.789 | {channel} | 2026-11-03 |") == 1


def test_empty_download_notes_sort_and_distinguish_builds_and_channels(product_factory):
    product = product_factory(platforms=(), version="2026.9", build="999")
    for build, channel in (("261.9", "release"), ("261.10", "eap"), ("261.10", "release")):
        product["releases"].extend(
            product_factory(platforms=(), version="2026.10", build=build, channel=channel)[
                "releases"
            ]
        )
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)

    text = render.render_product(state)

    assert not main_table_rows(text)
    assert (
        "| 2026.10 | 261.10 | release | 2026-11-03 |\n"
        "| 2026.10 | 261.10 | eap | 2026-11-03 |\n"
        "| 2026.10 | 261.9 | release | 2026-11-03 |\n"
        "| 2026.9 | 999 | release | 2026-11-03 |\n"
    ) in text
    state.empty_downloads.reverse()
    assert render.render_product(state) == text


def test_empty_download_notes_escape_cells_and_handle_missing_values(product_factory):
    product = product_factory(
        platforms=(), version="1|<script>", build="2|<build>", channel="preview|<channel>"
    )
    product["releases"].extend(product_factory(platforms=(), version=None, build=None)["releases"])
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)

    text = render.render_product(state)

    assert (
        "| 1&#124;&lt;script&gt; | 2&#124;&lt;build&gt; | "
        "preview&#124;&lt;channel&gt; | 2026-11-03 |"
    ) in text
    assert "| (not provided) | (not provided) | release | 2026-11-03 |" in text


@pytest.mark.parametrize("downloads", [None, [], "", 0, False])
def test_metadata_errors_are_reported_without_claiming_no_downloads(product_factory, downloads):
    product = product_factory()
    product["releases"][0]["downloads"] = downloads
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)

    text = render.render_product(state)

    assert not main_table_rows(text)
    assert "### Versions with no advertised downloads" not in text
    assert "### Collection errors" in text
    assert "Missing or non-object downloads metadata" in text


def test_advertised_installer_with_missing_hash_stays_visible(product_factory):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(), T1)
    assert main_table_rows(render.render_product(state))[0][3:5] == ["Pending", "Pending"]
    row = next(row for row in state.records if row.platform == "mac")
    row.error_stage, row.error = "checksum", "HTTP 404"

    text = render.render_product(state)

    assert len(main_table_rows(text)) == 1
    assert main_table_rows(text)[0][3:5] == ["Unavailable (see collection notes)"] * 2
    assert "HTTP 404" in text
    assert "### Versions with no advertised downloads" not in text


def test_historical_installer_stays_visible_when_downloads_disappear(product_factory):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(), T1)
    row = next(row for row in state.records if row.platform == "mac")
    row.installer_sha256, row.app_sha256 = "a" * 64, "b" * 64

    history.refresh_metadata(state, product_factory(platforms=()), T2)
    text = render.render_product(state)

    assert len(main_table_rows(text)) == 1
    assert main_table_rows(text)[0][3:5] == ["a" * 64, "b" * 64]
    assert not row.current
    assert text.count("| 1.2.3 | 123.456.789 | release | 2026-11-03 |") == 1


def test_legacy_missing_installer_does_not_imply_empty_downloads():
    state = history.History(
        "IIU", "IntelliJ IDEA", [history.Record("1.2.3", "123", "release", "2026-11-03", "mac")]
    )

    text = render.render_product(state)

    assert not main_table_rows(text)
    assert "### Versions with no advertised downloads" not in text


def test_cli_seeds_without_network_and_render_is_idempotent(tmp_path, product_factory, monkeypatch):
    source = tmp_path / "products.json"
    source.write_text(json.dumps([product_factory(), product_factory(code="PCP", platforms=())]))
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
    assert b"### Versions with no advertised downloads" in before["PCP.md"]
    assert not main_table_rows(before["PCP.md"].decode())


def test_catalog_refresh_and_publication_keep_missing_and_empty_download_notes_together(
    tmp_path, product_factory, monkeypatch
):
    product = product_factory()
    for version in ("1.2.2", "1.2.1"):
        product["releases"].extend(product_factory(version=version, platforms=())["releases"])
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)
    row = next(row for row in state.records if row.installer_url)
    row.installer_sha256 = "a" * 64
    row.app_sha256, row.app_path = "b" * 64, "IDE.app/Contents/MacOS/idea"
    data, incoming, docs = tmp_path / "data", tmp_path / "incoming", tmp_path / "ides"
    history.save(state, data)
    history.save(state, incoming)
    del product["releases"][1]["downloads"]
    source = tmp_path / "catalog.json"
    source.write_text(
        json.dumps({"fetched_at": T2, "product": history.discover([product], [state])[0]})
    )
    monkeypatch.setattr(
        history.transfer.urllib.request,
        "urlopen",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("Unexpected network")),
    )

    assert (
        cli.main(
            [
                "sync",
                "--product",
                "IIU",
                "--catalog",
                str(source),
                "--catalog-only",
                "--no-render",
                "--data-dir",
                str(incoming),
            ]
        )
        == 0
    )
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

    restored = history.load(data / "IIU.json")
    assert restored.empty_downloads == state.empty_downloads
    assert restored.records == state.records
    assert restored.catalog_fetched_at == T2
    text = (docs / "IIU.md").read_text()
    assert len(main_table_rows(text)) == 1
    assert text.count("### Versions with no advertised downloads") == 1
    for version in ("1.2.2", "1.2.1"):
        assert text.count(f"| {version} | 123.456.789 | release | 2026-11-03 |") == 1


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
    assert output.read_text() == f"existing=value\nmatrix={matrix}\nhas_work=true\n"
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
    "product,pcp_complete,expected,checks",
    [
        (None, False, ["PCP"], 1),
        ("", False, ["PCP"], 1),
        ("AIR", False, [], 1),
        ("PCP", False, ["PCP"], 0),
        (None, True, [], 2),
    ],
)
def test_pending_discovery_skips_complete_air_and_handles_empty_matrix(
    tmp_path, product_factory, monkeypatch, capsys, product, pcp_complete, expected, checks
):
    air = product_factory(code="AIR", channel="preview", platforms=("macos_x64", "macos_aarch64"))
    pcp = product_factory(code="PCP")
    for channel in ("eap", "rc", "preview", "future-channel"):
        pcp["releases"].extend(product_factory(code="PCP", channel=channel)["releases"])
    source = tmp_path / "products.json"
    source.write_text(json.dumps([air, pcp]))
    data, docs, snapshots = tmp_path / "data", tmp_path / "ides", tmp_path / "catalog"
    for complete_product in [air, pcp] if pcp_complete else [air]:
        state = history.History(complete_product["code"], complete_product["name"])
        sources = history.refresh_metadata(state, complete_product, T1)
        for descriptor in sources:
            if descriptor.installer_url:
                row = history.observe_checksum(state, descriptor, "a" * 64, T1)
                row.app_sha256, row.app_path = "b" * 64, "IDE.app/Contents/MacOS/launcher"
        history.save(state, data)
    before = {path.name: path.read_bytes() for path in data.glob("*.json")}
    fetched = []

    def fetch(url, deadline):
        assert deadline is not None
        fetched.append(url)
        return b"a" * 64

    monkeypatch.setattr(history.transfer, "fetch_bytes", fetch)
    monkeypatch.setattr(
        history.transfer,
        "collect_app",
        lambda *args: pytest.fail("Discovery must not download installers"),
    )
    output = tmp_path / "github-output"
    output.write_text("existing=value\n")
    args = [
        "discover",
        "--only-pending",
        "--catalog-file",
        str(source),
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

    captured = capsys.readouterr()
    matrix = json.dumps({"product": expected}, separators=(",", ":"))
    assert captured.out == matrix + "\n"
    assert output.read_text() == (
        f"existing=value\nmatrix={matrix}\nhas_work={str(bool(expected)).lower()}\n"
    )
    assert {path.stem for path in snapshots.glob("*.json")} == set(expected)
    assert before == {path.name: path.read_bytes() for path in data.glob("*.json")}
    assert not docs.exists()
    assert len(fetched) == checks
    if product != "PCP":
        assert "AIR: up to date; skipping collection" in captured.err
    if "PCP" in expected:
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
