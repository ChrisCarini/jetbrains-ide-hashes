import json
from copy import deepcopy
from dataclasses import replace

import pytest

from jetbrains_hashes import history, transfer

T1 = "2026-11-03T00:00:00+00:00"
T2 = "2026-11-04T00:00:00+00:00"
SHA_A, SHA_B, APP_A, APP_B = "a" * 64, "b" * 64, "c" * 64, "d" * 64


def observed(product_factory, build="123.456.789"):
    state = history.History("IIU", "IntelliJ IDEA")
    sources = history.refresh_metadata(state, product_factory(build=build), T1)
    row = history.observe_checksum(state, sources[0], SHA_A, T1)
    row.app_sha256, row.app_path = APP_A, "IntelliJ IDEA.app/Contents/MacOS/idea"
    return state, row


def test_rerelease_preserves_both_builds_and_completed_hashes(product_factory):
    state, old = observed(product_factory)
    sources = history.refresh_metadata(state, product_factory(build="123.456.799"), T2)
    new = history.observe_checksum(state, sources[0], SHA_B, T2)

    assert old in state.records and new in state.records
    assert old.build == "123.456.789" and old.app_sha256 == APP_A
    assert new.build == "123.456.799" and new.installer_sha256 == SHA_B
    assert not old.current and new.current
    assert not new.app_sha256


def test_same_build_repack_preserves_old_payload_without_copying_app_hash(product_factory):
    state, old = observed(product_factory)
    sources = history.refresh_metadata(state, product_factory(), T2)
    new = history.observe_checksum(state, sources[0], SHA_B, T2)

    assert old.installer_sha256 == SHA_A and old.app_sha256 == APP_A
    assert new.installer_sha256 == SHA_B and new.app_sha256 == ""
    assert not old.current and new.current
    assert len({row.artifact_key() for row in state.records}) == len(state.records)


def test_disappearing_download_retains_hash_without_empty_duplicate(product_factory):
    state, old = observed(product_factory)
    product = product_factory()
    product["releases"][0]["downloads"] = {}

    history.refresh_metadata(state, product, T2)

    assert old.app_sha256 == APP_A and not old.current
    assert len(state.records) == 2


def test_null_download_metadata_and_mac_aliases_are_not_silently_discarded(product_factory):
    product = product_factory(
        code="AIR", platforms=("macos_x64", "macos_aarch64"), channel="preview"
    )
    rows = history.descriptors(product, T1)
    assert {row.platform for row in rows} == {"macos_x64", "macos_aarch64"}
    assert {row.release_type for row in rows} == {"preview"}

    product["releases"][0]["downloads"] = None
    rows = history.descriptors(product, T1)
    assert len(rows) == 2
    assert all(row.error_stage == "metadata" for row in rows)


def test_omitted_downloads_are_retained_as_unadvertised_and_clear_resolved_metadata_errors(
    product_factory,
):
    state = history.History("IIU", "IntelliJ IDEA")
    malformed = product_factory()
    malformed["releases"][0]["downloads"] = None
    history.refresh_metadata(state, malformed, T1)
    omitted = product_factory()
    del omitted["releases"][0]["downloads"]

    history.refresh_metadata(state, omitted, T2)

    assert len(state.records) == 2
    assert all(row.status == "not_advertised" for row in state.records)
    assert all(row.first_seen == T1 for row in state.records)


@pytest.mark.parametrize("omit_downloads", [False, True])
def test_empty_download_releases_are_persisted_once_per_build_and_channel(
    tmp_path, product_factory, omit_downloads
):
    state = history.History("IIU", "IntelliJ IDEA")
    product = product_factory(platforms=(), build=None)
    if omit_downloads:
        del product["releases"][0]["downloads"]
    history.refresh_metadata(state, product, T1)

    history.save(state, tmp_path)
    restored = history.load(tmp_path / "IIU.json")

    assert len(restored.records) == 2
    assert restored.empty_downloads == [
        history.EmptyDownloadRelease("1.2.3", "", "release", "2026-11-03")
    ]


@pytest.mark.parametrize("platforms", [("mac",), ("macos_aarch64",), ("linux",)])
def test_empty_download_notes_clear_when_any_download_is_advertised(product_factory, platforms):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(platforms=()), T1)
    assert state.empty_downloads

    history.refresh_metadata(state, product_factory(platforms=platforms), T2)

    assert state.empty_downloads == []


def test_discovery_does_not_turn_omitted_downloads_into_explicitly_empty_metadata(
    product_factory,
):
    product = product_factory()
    del product["releases"][0]["downloads"]
    discovered = history.discover([product], [])
    assert "downloads" not in discovered[0]["releases"][0]
    state = history.History("IIU", "IntelliJ IDEA")

    history.refresh_metadata(state, discovered[0], T1)

    assert state.empty_downloads == [
        history.EmptyDownloadRelease("1.2.3", "123.456.789", "release", "2026-11-03")
    ]
    assert all(row.status == "not_advertised" for row in state.records)


def test_disappearing_product_preserves_empty_download_metadata(product_factory):
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product_factory(platforms=()), T1)
    before = list(state.empty_downloads)

    history.refresh_metadata(
        state,
        {"code": state.code, "name": state.name, "releases": [], "absent_from_catalog": True},
        T2,
    )

    assert state.empty_downloads == before


@pytest.mark.parametrize(
    "observed_at,empty_downloads,replace_notes",
    [
        (T1, [], False),
        (T2, [], True),
        (T2, [history.EmptyDownloadRelease("2", "222", "eap", "2026-11-04")], True),
        (T2, None, False),
    ],
)
def test_merge_only_replaces_empty_download_notes_with_known_current_metadata(
    observed_at, empty_downloads, replace_notes
):
    before = [history.EmptyDownloadRelease("1", "111", "release", "2026-11-03")]
    destination = history.History(
        "IIU", "IntelliJ IDEA", catalog_fetched_at=T2, empty_downloads=before
    )
    incoming = history.History(
        "IIU", "IntelliJ IDEA", catalog_fetched_at=observed_at, empty_downloads=empty_downloads
    )

    history.merge(destination, incoming)

    assert destination.empty_downloads == (empty_downloads if replace_notes else before)
    if replace_notes:
        assert destination.empty_downloads is not incoming.empty_downloads


def test_legacy_history_loads_without_inventing_empty_download_metadata(tmp_path):
    state = history.History("IIU", "IntelliJ IDEA")
    history.save(state, tmp_path)
    path = tmp_path / "IIU.json"
    assert "empty_downloads" not in json.loads(path.read_text())

    assert history.load(path).empty_downloads is None


@pytest.mark.parametrize(
    "empty_downloads,error",
    [
        ({}, "Invalid history structure"),
        ("empty", "Invalid history structure"),
        ([{"version": "1"}], "Invalid history structure"),
        (
            [{"version": 1, "build": "", "release_type": "release", "release_date": ""}],
            "Invalid empty-download release types",
        ),
        (
            [{"version": "1", "build": "", "release_type": "release", "release_date": ""}] * 2,
            "Duplicate empty-download release",
        ),
    ],
)
def test_load_rejects_invalid_empty_download_metadata(tmp_path, empty_downloads, error):
    history.save(history.History("IIU", "IntelliJ IDEA"), tmp_path)
    path = tmp_path / "IIU.json"
    payload = json.loads(path.read_text())
    payload["empty_downloads"] = empty_downloads
    path.write_text(json.dumps(payload))

    with pytest.raises(transfer.StopRun, match=error):
        history.load(path)


def test_old_catalog_cannot_rewind_build_identity(product_factory):
    state, old = observed(product_factory)
    state.catalog_fetched_at = T2

    with pytest.raises(transfer.StopRun, match="older than"):
        history.refresh_metadata(state, product_factory(build="123.456.799"), T1)

    assert state.catalog_fetched_at == T2
    assert old.current and old.app_sha256 == APP_A
    assert len(state.records) == 2


def test_discovery_keeps_legacy_and_miscategorized_ides(product_factory):
    rider = product_factory(code="RD")
    rider["categories"] = [".NET tool"]
    cloud = product_factory(code="DL")
    cloud["releases"][0]["build"] = None
    cloud["releases"][0]["downloads"] = {}
    old = history.History("RETIRED", "Retired IDE")

    products = history.discover([rider, cloud], [old])

    assert {p["code"] for p in products} == {"RD", "DL", "RETIRED"}
    assert next(p for p in products if p["code"] == "RETIRED")["absent_from_catalog"]
    assert all(row.status == "not_advertised" for row in history.descriptors(cloud, T1))


def test_needs_sync_verifies_complete_history_without_mutating_it(product_factory, monkeypatch):
    state, row = observed(product_factory)
    before = deepcopy(state)
    fetched = []

    def fetch(url, deadline):
        fetched.append(url)
        return SHA_A.encode()

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)
    monkeypatch.setattr(
        transfer, "collect_app", lambda *args: pytest.fail("Preflight must not download installers")
    )

    assert not history.needs_sync(state, product_factory(), T2, None)
    assert fetched == [row.checksum_url]
    assert state == before


@pytest.mark.parametrize(
    "changes",
    [
        {"installer_sha256": "", "app_sha256": "", "app_path": ""},
        {"app_sha256": "", "app_path": ""},
        {"error_stage": "checksum", "error": "HTTP 404"},
        {"error_stage": "application", "error": "Missing launcher"},
        {"error_stage": "metadata", "error": "Invalid metadata"},
    ],
)
def test_needs_sync_keeps_missing_hashes_and_errors(product_factory, monkeypatch, changes):
    state, row = observed(product_factory)
    for name, value in changes.items():
        setattr(row, name, value)
    before = deepcopy(state)
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: SHA_A.encode())

    assert history.needs_sync(state, product_factory(), T2, None)
    assert state == before


@pytest.mark.parametrize(
    "kwargs",
    [
        {"version": "2.0"},
        {"build": "123.456.799"},
        {"channel": "eap"},
        {"channel": "rc"},
        {"channel": "preview"},
        {"channel": "future-channel"},
        {"platforms": ("mac", "macM1")},
        {"url": "https://download.jetbrains.com/idea/new.dmg"},
    ],
)
def test_needs_sync_keeps_new_catalog_artifacts_without_preflight(
    product_factory, monkeypatch, kwargs
):
    state, _ = observed(product_factory)
    monkeypatch.setattr(
        transfer, "fetch_bytes", lambda *args: pytest.fail("Known work needs no checksum preflight")
    )

    assert history.needs_sync(state, product_factory(**kwargs), T2, None)


@pytest.mark.parametrize("digest", [SHA_A, SHA_B, "e" * 64])
def test_needs_sync_detects_repacks_but_skips_unchanged_completed_revisions(
    product_factory, monkeypatch, digest
):
    state, old = observed(product_factory)
    source = history.descriptors(product_factory(), T1)[0]
    current = history.observe_checksum(state, source, SHA_B, T1)
    current.app_sha256, current.app_path = APP_B, old.app_path
    before = deepcopy(state)
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: digest.encode())

    assert history.needs_sync(state, product_factory(), T2, None) == (digest != SHA_B)
    assert state == before
    assert not old.current and current.current


@pytest.mark.parametrize(
    "change", ["name", "downloads", "ignored_download_types", "empty_downloads"]
)
def test_needs_sync_keeps_metadata_only_changes(product_factory, monkeypatch, change):
    state, _ = observed(product_factory)
    product = product_factory()
    if change == "name":
        product["name"] = "Renamed IDE"
    elif change == "downloads":
        product["releases"][0]["downloads"] = {}
    elif change == "ignored_download_types":
        product["releases"][0]["downloads"]["linux"] = {}
    else:
        product["releases"].extend(product_factory(version="2.0", platforms=())["releases"])
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: SHA_A.encode())

    assert history.needs_sync(state, product, T2, None)


@pytest.mark.parametrize("problem", ["empty", "build", "duplicate", "url", "stale"])
def test_needs_sync_leaves_catalog_validation_failures_to_collection(
    product_factory, monkeypatch, capsys, problem
):
    state, _ = observed(product_factory)
    product = product_factory()
    if problem == "empty":
        product["releases"] = []
    elif problem == "build":
        product["releases"][0]["build"] = 123
    elif problem == "duplicate":
        product["releases"] *= 2
    elif problem == "url":
        product["releases"][0]["downloads"]["mac"]["link"] = "https://["
    else:
        state.catalog_fetched_at = T2
    before = deepcopy(state)
    monkeypatch.setattr(
        transfer, "fetch_bytes", lambda *args: pytest.fail("Catalog validation failed")
    )

    assert history.needs_sync(state, product, T1, None)
    assert state == before
    assert "keeping IDE queued for collection" in capsys.readouterr().err


def test_needs_sync_skips_unchanged_unadvertised_releases_even_after_budget(
    tmp_path, product_factory, monkeypatch
):
    product = product_factory(version="2.0", platforms=())
    product["releases"].extend(product_factory(platforms=())["releases"])
    state = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(state, product, T1)
    history.save(state, tmp_path)
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: pytest.fail("No sidecars to check"))

    assert not history.needs_sync(state, product, T2, -1)
    product["releases"].reverse()
    assert not history.needs_sync(state, product, T2, -1)


@pytest.mark.parametrize("incomplete", [False, True])
def test_needs_sync_retains_historical_backfill_for_absent_products(product_factory, incomplete):
    state, row = observed(product_factory)
    if incomplete:
        row.app_sha256, row.app_path = "", ""
    product = {
        "code": state.code,
        "name": state.name,
        "releases": [],
        "absent_from_catalog": True,
    }
    history.refresh_metadata(state, product, T1)

    assert history.needs_sync(state, product, T2, -1) == incomplete


@pytest.mark.parametrize(
    "failure",
    [None, transfer.ArtifactError("HTTP 404"), transfer.BudgetReached("Retry exceeds budget")],
)
def test_needs_sync_keeps_unverifiable_checksums_queued(
    product_factory, monkeypatch, capsys, failure
):
    state, _ = observed(product_factory)
    before = deepcopy(state)

    def fetch(*args):
        if failure is not None:
            raise failure
        return b"not a checksum"

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)

    assert history.needs_sync(state, product_factory(), T2, None)
    assert state == before
    assert capsys.readouterr().err


def test_needs_sync_does_not_skip_unchecked_sidecars_after_budget(
    product_factory, monkeypatch, capsys
):
    state, _ = observed(product_factory)
    monkeypatch.setattr(
        transfer, "fetch_bytes", lambda *args: pytest.fail("The preflight budget is exhausted")
    )

    assert history.needs_sync(state, product_factory(), T2, -1)
    assert "checksum refresh incomplete" in capsys.readouterr().err


def test_merge_keeps_newer_history_and_rejects_conflicting_app_hash(product_factory):
    destination, old = observed(product_factory)
    incoming = history.History("IIU", "IntelliJ IDEA", [replace(old)], T1)
    new_sources = history.refresh_metadata(destination, product_factory(build="123.456.799"), T2)
    history.observe_checksum(destination, new_sources[0], SHA_B, T2)

    history.merge(destination, incoming)

    assert len(destination.records) == 4
    assert destination.catalog_fetched_at == T2
    assert old.app_sha256 == APP_A
    incoming.records[0].app_sha256 = APP_B
    with pytest.raises(transfer.StopRun, match="Conflicting app hashes"):
        history.merge(destination, incoming)


def test_publisher_upgrades_pending_record_without_leaving_duplicate(product_factory):
    destination = history.History("IIU", "IntelliJ IDEA")
    history.refresh_metadata(destination, product_factory(), T1)
    incoming, _ = observed(product_factory)

    history.merge(destination, incoming)
    history.merge(destination, incoming)

    assert len(destination.records) == 2
    assert history.coverage(destination)["app_hashes"] == 1


def test_bounded_collection_checkpoints_and_resumes_other_installers(
    tmp_path, product_factory, monkeypatch
):
    state = history.History("IIU", "IntelliJ IDEA")
    product = product_factory()
    for build in ("123.456.799", "123.456.809"):
        product["releases"].extend(product_factory(build=build)["releases"])
    sources = history.refresh_metadata(state, product, T1)
    for index, row in enumerate(source for source in sources if source.installer_url):
        history.observe_checksum(state, row, format(index + 1, "064x"), T1)
    attempted = []

    def collect_app(url, size, digest, build, work_dir, deadline):
        attempted.append(build)
        return transfer.Application(APP_A, "IDE.app/Contents/MacOS/launcher", build)

    monkeypatch.setattr(transfer, "collect_app", collect_app)

    def persist():
        history.save(state, tmp_path)

    assert history.collect(state, [], persist, tmp_path, 1, None) == 0
    assert len(attempted) == 1
    state = history.load(tmp_path / "IIU.json")
    assert history.coverage(state)["app_hashes"] == 1
    assert history.collect(state, [], lambda: history.save(state, tmp_path), tmp_path, 1, None) == 0
    assert len(attempted) == len(set(attempted)) == 2
    assert history.coverage(history.load(tmp_path / "IIU.json"))["app_hashes"] == 2


def test_failed_old_installer_does_not_starve_never_attempted_history(
    tmp_path, product_factory, monkeypatch
):
    state, old = observed(product_factory, build="123.456.799")
    old.app_sha256, old.app_path = "", ""
    old.last_attempt, old.error_stage, old.error = T1, "application", "HTTP 404"
    sources = history.refresh_metadata(state, product_factory(build="123.456.789"), T2)
    history.observe_checksum(state, sources[0], SHA_B, T2)
    attempted = []

    def collect_app(url, size, digest, build, work_dir, deadline):
        attempted.append(build)
        raise transfer.ArtifactError("HTTP 404")

    monkeypatch.setattr(transfer, "collect_app", collect_app)

    assert history.collect(state, [], lambda: None, tmp_path, 1, None) == 1
    assert attempted == ["123.456.789"]
    assert history.coverage(state)["app_hashes"] == 0


def test_time_budget_preserves_pending_work_without_claiming_hashes(tmp_path, product_factory):
    state = history.History("IIU", "IntelliJ IDEA")
    sources = history.refresh_metadata(state, product_factory(), T1)

    result = history.collect(
        state,
        sources,
        lambda: history.save(state, tmp_path),
        tmp_path,
        10,
        -1,
    )

    assert result == 0
    assert history.coverage(history.load(tmp_path / "IIU.json"))["installer_hashes"] == 0


def test_checksum_failure_is_recorded_and_reported(tmp_path, product_factory, monkeypatch):
    state = history.History("IIU", "IntelliJ IDEA")
    sources = history.refresh_metadata(state, product_factory(), T1)
    monkeypatch.setattr(transfer, "fetch_bytes", lambda *args: b"<html>not a checksum</html>")

    result = history.collect(
        state,
        sources,
        lambda: history.save(state, tmp_path),
        tmp_path,
        10,
        None,
        True,
    )

    restored = history.load(tmp_path / "IIU.json")
    assert result == 1
    assert any(row.error_stage == "checksum" for row in restored.records)
    assert history.coverage(restored)["installer_hashes"] == 0


def test_checksum_budget_preserves_earlier_failures(tmp_path, product_factory, monkeypatch):
    product = product_factory()
    product["releases"].extend(
        product_factory(build="123.456.799", url="https://download.jetbrains.com/idea/second.dmg")[
            "releases"
        ]
    )
    state = history.History("IIU", "IntelliJ IDEA")
    sources = history.refresh_metadata(state, product, T1)

    def fetch(url, deadline):
        if "second.dmg" in url:
            raise transfer.BudgetReached("Retry exceeds budget")
        raise transfer.ArtifactError("HTTP 404")

    monkeypatch.setattr(transfer, "fetch_bytes", fetch)
    monkeypatch.setattr(
        transfer, "collect_app", lambda *args: pytest.fail("Checksum refresh was incomplete")
    )

    assert (
        history.collect(state, sources, lambda: history.save(state, tmp_path), tmp_path, 10, None)
        == 1
    )
    restored = history.load(tmp_path / "IIU.json")
    assert history.coverage(restored)["errors"] == 1
    assert history.coverage(restored)["installer_hashes"] == 0


def test_shared_url_cannot_assign_new_checksum_to_two_different_builds(
    tmp_path, product_factory, monkeypatch
):
    state, old = observed(product_factory)
    product = product_factory()
    product["releases"].extend(product_factory(build="123.456.799")["releases"])
    sources = history.refresh_metadata(state, product, T2)
    monkeypatch.setattr(
        transfer,
        "fetch_bytes",
        lambda *args: pytest.fail("Ambiguous URLs must not be assigned to either build"),
    )

    result = history.collect(state, sources, lambda: None, tmp_path, 10, None, True)

    assert result == 2
    assert old.installer_sha256 == SHA_A and old.app_sha256 == APP_A
    new = next(row for row in state.records if row.build == "123.456.799" and row.installer_url)
    assert not new.installer_sha256
    assert "multiple builds" in new.error


def test_stale_artifact_does_not_clear_newer_collection_error(product_factory):
    destination, old = observed(product_factory)
    incoming = history.History("IIU", "IntelliJ IDEA", [replace(old)], T1)
    destination.catalog_fetched_at = T2
    old.error_stage, old.error = "checksum", "HTTP 404"

    history.merge(destination, incoming)

    assert old.error_stage == "checksum" and old.error == "HTTP 404"
