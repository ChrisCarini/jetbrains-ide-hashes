import json
import shutil

import pytest

from jetbrains_hashes import cli, history, transfer

T1 = "2026-11-03T00:00:00+00:00"


def completed_history(product):
    state = history.History(product["code"], product["name"])
    sources = history.refresh_metadata(state, product, T1)
    for source in sources:
        if source.installer_url:
            row = history.observe_checksum(state, source, "a" * 64, T1)
            row.app_sha256, row.app_path = "b" * 64, "IDE.app/Contents/MacOS/launcher"
            row.app_build, row.app_bundle_id, row.app_version = (
                source.build,
                "com.jetbrains.example",
                source.version,
            )
    return state


def prepare(tmp_path, products, *extra_args):
    catalog = tmp_path / "products.json"
    catalog.write_text(json.dumps(products))
    output = tmp_path / "github-output"
    output.write_text("existing=value\n")
    return cli.main(
        [
            "discover",
            "--prepare",
            "--catalog-file",
            str(catalog),
            "--data-dir",
            str(tmp_path / "data"),
            "--output-dir",
            str(tmp_path / "prepared"),
            "--github-output",
            str(output),
            *extra_args,
        ]
    )


def test_prepare_skips_complete_products_without_changing_saved_history(
    tmp_path, product_factory, monkeypatch, capsys
):
    products = [
        product_factory(code=code, platforms=() if code == "VSCRS" else ("mac", "macM1"))
        for code in ("PCC", "PSL", "RM", "RR", "VSCRS", "WS")
    ]
    for product in products:
        history.save(completed_history(product), tmp_path / "data")
    before = {path.name: path.read_bytes() for path in (tmp_path / "data").glob("*.json")}
    fetched = []

    def fetch(url, deadline):
        fetched.append(url)
        return b"a" * 64

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)
    monkeypatch.setattr(
        transfer, "collect_app", lambda *args: pytest.fail("Preparation never downloads installers")
    )

    assert prepare(tmp_path, products) == 0

    assert capsys.readouterr().out == '{"product":[]}\n'
    assert (tmp_path / "github-output").read_text() == (
        'existing=value\nmatrix={"product":[]}\nhas_work=false\nhas_updates=false\n'
    )
    assert not list((tmp_path / "prepared").glob("*.json"))
    assert len(fetched) == 5
    assert before == {path.name: path.read_bytes() for path in (tmp_path / "data").glob("*.json")}


def test_prepare_publishes_new_unadvertised_releases_without_macos(
    tmp_path, product_factory, monkeypatch, capsys
):
    product = product_factory(code="VSCRS", platforms=())
    history.save(completed_history(product), tmp_path / "data")
    product["releases"].extend(
        product_factory(code="VSCRS", version="2026.3.0", build="263.7307.256", platforms=())[
            "releases"
        ]
    )
    monkeypatch.setattr(
        transfer, "fetch_bytes", lambda *args: pytest.fail("No advertised checksum URLs")
    )

    assert prepare(tmp_path, [product]) == 0
    assert capsys.readouterr().out == '{"product":[]}\n'
    assert "has_work=false\nhas_updates=true\n" in (tmp_path / "github-output").read_text()
    assert (
        cli.main(
            [
                "merge",
                "--from-dir",
                str(tmp_path / "prepared"),
                "--data-dir",
                str(tmp_path / "data"),
                "--docs-dir",
                str(tmp_path / "ides"),
            ]
        )
        == 0
    )
    saved = history.load(tmp_path / "data/VSCRS.json")
    assert saved.catalog_release_count == 2 and len(saved.records) == 4
    assert not any(row.needs_application for row in saved.records)
    assert "263.7307.256" in (tmp_path / "ides/VSCRS.md").read_text()


def test_prepare_queues_only_application_work_and_publishes_checksum_failures(
    tmp_path, product_factory, monkeypatch, capsys
):
    products = [
        product_factory(code=code, url=f"https://download.jetbrains.com/{code}/installer.dmg")
        for code in ("READY", "UNKNOWN", "COMPLETE")
    ]
    history.save(completed_history(products[-1]), tmp_path / "data")
    fetched = []

    def fetch(url, deadline):
        fetched.append(url)
        if "/UNKNOWN/" in url:
            raise transfer.ArtifactError("HTTP 404")
        return b"a" * 64

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)

    assert prepare(tmp_path, products) == 1

    assert capsys.readouterr().out == '{"product":["READY"]}\n'
    assert "has_work=true\nhas_updates=true\n" in (tmp_path / "github-output").read_text()
    assert {path.stem for path in (tmp_path / "prepared").glob("*.json")} == {"READY", "UNKNOWN"}
    assert len(fetched) == 3
    ready = history.load(tmp_path / "prepared/READY.json")
    failed = history.load(tmp_path / "prepared/UNKNOWN.json")
    assert sum(row.needs_application for row in ready.records) == 1
    assert not any(row.needs_application for row in failed.records)
    assert next(row for row in failed.records if row.error).consecutive_failures == 1


def test_prepared_repack_and_metadata_updates_survive_application_handoff_and_publication(
    tmp_path, product_factory, monkeypatch, capsys
):
    ready = product_factory(code="READY")
    metadata = product_factory(code="VSCRS", platforms=())
    for product in (ready, metadata):
        history.save(completed_history(product), tmp_path / "data")
    metadata["releases"].extend(
        product_factory(code="VSCRS", version="2.0", platforms=())["releases"]
    )
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: b"c" * 64)

    assert prepare(tmp_path, [ready, metadata]) == 0
    assert capsys.readouterr().out == '{"product":["READY"]}\n'
    prepared = history.load(tmp_path / "prepared/READY.json")
    assert {row.installer_sha256 for row in prepared.records if row.installer_url} == {
        "a" * 64,
        "c" * 64,
    }
    shutil.copytree(tmp_path / "prepared", tmp_path / "macos")
    monkeypatch.setattr(
        transfer,
        "fetch_bytes",
        lambda *args: pytest.fail("macOS must not fetch metadata/checksums"),
    )
    monkeypatch.setattr(
        history, "refresh_metadata", lambda *args: pytest.fail("Metadata was already prepared")
    )
    downloads = []

    def collect_app(url, size, digest, build, *args):
        downloads.append(digest)
        return transfer.Application("d" * 64, "IDE.app/Contents/MacOS/launcher", build)

    monkeypatch.setattr(transfer, "collect_app", collect_app)
    assert (
        cli.main(
            [
                "sync",
                "--product",
                "READY",
                "--applications-only",
                "--data-dir",
                str(tmp_path / "macos"),
                "--work-dir",
                str(tmp_path / "work"),
                "--no-render",
            ]
        )
        == 0
    )
    assert downloads == ["c" * 64]
    assert history.load(tmp_path / "macos/READY.json").catalog_fetched_at == (
        prepared.catalog_fetched_at
    )
    shutil.copytree(tmp_path / "prepared", tmp_path / "incoming")
    shutil.copyfile(tmp_path / "macos/READY.json", tmp_path / "incoming/READY.json")
    assert (
        cli.main(
            [
                "merge",
                "--from-dir",
                str(tmp_path / "incoming"),
                "--data-dir",
                str(tmp_path / "data"),
                "--docs-dir",
                str(tmp_path / "ides"),
            ]
        )
        == 0
    )
    published = history.load(tmp_path / "data/READY.json")
    assert {
        (row.installer_sha256, row.app_sha256) for row in published.records if row.installer_url
    } == {
        ("a" * 64, "b" * 64),
        ("c" * 64, "d" * 64),
    }
    assert history.load(tmp_path / "data/VSCRS.json").catalog_release_count == 2


def test_prepare_reuses_captured_application_hashes_without_a_macos_job(
    tmp_path, product_factory, monkeypatch, capsys
):
    product = product_factory()
    history.save(completed_history(product), tmp_path / "data")
    product["releases"].extend(product_factory(channel="eap")["releases"])
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: b"a" * 64)

    assert prepare(tmp_path, [product]) == 0
    assert capsys.readouterr().out == '{"product":[]}\n'
    assert "has_updates=true\n" in (tmp_path / "github-output").read_text()
    saved = history.load(tmp_path / "prepared/IIU.json")
    new = next(row for row in saved.records if row.release_type == "eap" and row.installer_url)
    assert (new.app_sha256, new.app_build, new.app_bundle_id, new.app_version) == (
        "b" * 64,
        "123.456.789",
        "com.jetbrains.example",
        "1.2.3",
    )


def test_prepare_defers_unfinished_verification_to_ubuntu_not_macos(
    tmp_path, product_factory, monkeypatch, capsys
):
    product = product_factory()
    history.save(completed_history(product), tmp_path / "data")
    before = (tmp_path / "data/IIU.json").read_bytes()

    def fetch(*args):
        raise transfer.BudgetReached("Retry exceeds budget")

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)

    assert prepare(tmp_path, [product]) == 0
    captured = capsys.readouterr()
    assert captured.out == '{"product":[]}\n'
    assert "checksum verification incomplete; remaining work deferred to Ubuntu" in captured.err
    assert "has_updates=false\n" in (tmp_path / "github-output").read_text()
    assert not list((tmp_path / "prepared").glob("*.json"))
    assert (tmp_path / "data/IIU.json").read_bytes() == before


def test_prepare_preserves_partial_checksums_and_outputs_on_interruption(
    tmp_path, product_factory, monkeypatch, capsys
):
    product = product_factory()
    product["releases"].extend(
        product_factory(build="123.456.799", url="https://download.jetbrains.com/second.dmg")[
            "releases"
        ]
    )

    def fetch(url, deadline):
        if "second.dmg" in url:
            raise KeyboardInterrupt
        return b"a" * 64

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)

    assert prepare(tmp_path, [product]) == 130
    captured = capsys.readouterr()
    assert captured.out == '{"product":[]}\n' and "Interrupted" in captured.err
    assert "has_work=false\nhas_updates=true\n" in (tmp_path / "github-output").read_text()
    assert history.coverage(history.load(tmp_path / "prepared/IIU.json"))["installer_hashes"] == 1
    assert not list((tmp_path / "data").glob("*.json"))


def test_prepare_invalid_product_does_not_discard_other_products(
    tmp_path, product_factory, monkeypatch, capsys
):
    invalid, ready = product_factory(code="INVALID"), product_factory(code="READY")
    history.save(completed_history(invalid), tmp_path / "data")
    before = (tmp_path / "data/INVALID.json").read_bytes()
    invalid["releases"] *= 2
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: b"a" * 64)

    assert prepare(tmp_path, [invalid, ready]) == 1
    captured = capsys.readouterr()
    assert "retaining saved history" in captured.err
    assert captured.out == '{"product":["READY"]}\n'
    assert (tmp_path / "data/INVALID.json").read_bytes() == before
    assert {path.stem for path in (tmp_path / "prepared").glob("*.json")} == {"READY"}


def test_prepare_retains_historical_application_work_for_absent_products(
    tmp_path, product_factory, monkeypatch, capsys
):
    retired = completed_history(product_factory(code="RETIRED"))
    row = next(row for row in retired.records if row.installer_url)
    row.app_sha256, row.app_path = "", ""
    history.save(retired, tmp_path / "data")
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: pytest.fail("No current sidecars"))

    assert prepare(tmp_path, [product_factory()], "--product", "RETIRED") == 0

    assert capsys.readouterr().out == '{"product":["RETIRED"]}\n'
    saved = history.load(tmp_path / "prepared/RETIRED.json")
    assert sum(row.needs_application for row in saved.records) == 1
    assert all(not row.current for row in saved.records)


def test_application_handoff_does_not_reset_retry_allowance_or_change_other_products(
    tmp_path, product_factory, monkeypatch, capsys
):
    for code in ("IIU", "PCP"):
        state = completed_history(product_factory(code=code))
        row = next(row for row in state.records if row.installer_url)
        row.app_sha256, row.app_path = "", ""
        for _ in range(5):
            history.record_error(row, "application", "HTTP 404")
        history.save(state, tmp_path / "data")
    before = (tmp_path / "data/PCP.json").read_bytes()
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: b"a" * 64)
    product = product_factory()

    assert prepare(tmp_path, [product], "--product", "IIU", "--retry-quarantined") == 0
    assert capsys.readouterr().out == '{"product":["IIU"]}\n'
    assert {path.stem for path in (tmp_path / "prepared").glob("*.json")} == {"IIU"}
    assert (tmp_path / "data/PCP.json").read_bytes() == before

    def collect_app(*args):
        raise transfer.ArtifactError("HTTP 404")

    monkeypatch.setattr(transfer, "collect_app", collect_app)
    monkeypatch.setattr(
        transfer, "fetch_bytes", lambda *args: pytest.fail("Preparation must not be repeated")
    )
    for attempt in (1, 2):
        assert (
            cli.main(
                [
                    "sync",
                    "--product",
                    "IIU",
                    "--applications-only",
                    "--data-dir",
                    str(tmp_path / "prepared"),
                    "--no-render",
                ]
            )
            == 1
        )
        saved = history.load(tmp_path / "prepared/IIU.json")
        row = next(row for row in saved.records if row.installer_url)
        assert row.consecutive_failures == attempt and row.error == "HTTP 404"
        assert row.installer_sha256 == "a" * 64


@pytest.mark.parametrize("stage", ["metadata", "checksum"])
def test_ubuntu_only_failures_are_published_quarantined_and_explicitly_retried(
    tmp_path, product_factory, monkeypatch, capsys, stage
):
    product = product_factory()
    if stage == "metadata":
        product["releases"][0]["downloads"] = None

    def fetch(*args):
        raise transfer.ArtifactError("HTTP 404")

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)
    for attempt in range(1, 8):
        monkeypatch.setattr(history, "now", lambda: f"2026-11-04T00:00:0{attempt}+00:00")
        incoming = tmp_path / f"prepared-{attempt}"
        retry = ["--retry-quarantined"] if attempt == 7 else []
        assert prepare(tmp_path, [product], "--output-dir", str(incoming), *retry) == (
            0 if attempt == 6 else 1
        )
        assert capsys.readouterr().out == '{"product":[]}\n'
        if attempt == 6:
            assert "has_updates=false\n" in (tmp_path / "github-output").read_text()
            assert not incoming.exists()
            continue
        assert "has_work=false\nhas_updates=true\n" in (tmp_path / "github-output").read_text()
        assert (
            cli.main(
                [
                    "merge",
                    "--from-dir",
                    str(incoming),
                    "--data-dir",
                    str(tmp_path / "data"),
                    "--docs-dir",
                    str(tmp_path / "ides"),
                ]
            )
            == 0
        )
        saved = history.load(tmp_path / "data/IIU.json")
        failed = [row for row in saved.records if row.error]
        assert failed
        assert all(row.consecutive_failures == (1 if retry else attempt) for row in failed)
        assert all(row.quarantined == (attempt == 5) for row in failed)


@pytest.mark.parametrize("conflict", ["data", "prepared"])
def test_prepare_rejects_output_directories_that_could_mix_histories(
    tmp_path, product_factory, capsys, conflict
):
    product = product_factory()
    directory = tmp_path / conflict
    history.save(completed_history(product), directory)
    before = (directory / "IIU.json").read_bytes()

    assert prepare(tmp_path, [product], "--output-dir", str(directory)) == 1
    assert "separate output directory without existing JSON files" in capsys.readouterr().err
    assert (directory / "IIU.json").read_bytes() == before


@pytest.mark.parametrize("extra", [[], ["--catalog", "catalog.json"], ["--retry-quarantined"]])
def test_applications_only_requires_prepared_history_without_catalog_or_retry_inputs(
    tmp_path, monkeypatch, capsys, extra
):
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: pytest.fail("No metadata requests"))

    assert (
        cli.main(
            [
                "sync",
                "--product",
                "IIU",
                "--applications-only",
                "--data-dir",
                str(tmp_path / "missing"),
                *extra,
            ]
        )
        == 1
    )
    assert "prepared history" in capsys.readouterr().err
