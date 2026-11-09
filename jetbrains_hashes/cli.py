"""Local and GitHub Actions entry points."""

from __future__ import annotations

import argparse
import fcntl
import json
import signal
import sys
import tempfile
import time
import urllib.parse
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from . import history, render, transfer
from .history import History
from .transfer import StopRun, atomic_write, log


@contextmanager
def locked(directory: Path):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise StopRun(f"Another collector is using {directory}") from exc
        yield


def existing(directory: Path) -> list[History]:
    return [history.load(path) for path in sorted(directory.glob("*.json"))]


def discover_command(args: argparse.Namespace) -> int:
    selected_code = history.validate_code(args.product) if args.product else None
    if args.catalog_file:
        products = json.loads(args.catalog_file.read_text(encoding="utf-8"))
        fetched_at = datetime.fromtimestamp(
            args.catalog_file.stat().st_mtime, timezone.utc
        ).isoformat()
    else:
        products = json.loads(transfer.fetch_bytes(history.API_URL))
        fetched_at = history.now()
    with locked(args.data_dir):
        histories = {item.code: item for item in existing(args.data_dir)}
        products = history.discover(products, list(histories.values()))
        if selected_code:
            selected = [product for product in products if product["code"] == selected_code]
            if not selected:
                available = ", ".join(product["code"] for product in products)
                raise StopRun(
                    f"Unknown IDE product code: {selected_code}. Available codes: {available}"
                )
            products = selected
        codes = []
        deadline = time.monotonic() + args.max_minutes * 60
        for product in products:
            code = history.validate_code(product["code"])
            state = histories.get(code, History(code, product["name"]))
            if args.only_pending:
                requested_retry = args.retry_quarantined and any(
                    row.quarantined for row in state.records
                )
                if not requested_retry and not history.needs_sync(
                    state, product, fetched_at, deadline
                ):
                    log(f"{code}: up to date; skipping collection")
                    quarantined = sum(row.quarantined for row in state.records)
                    if quarantined:
                        log(
                            f"{code}: {quarantined} quarantined records remain in the failure report"
                        )
                    continue
                log(f"{code}: queued for collection")
            codes.append(code)
            snapshot = {"fetched_at": fetched_at, "product": product}
            atomic_write(args.output_dir / f"{code}.json", json.dumps(snapshot, indent=2) + "\n")
            if args.seed:
                history.refresh_metadata(state, product, fetched_at)
                history.save(state, args.data_dir)
        if args.seed:
            render.render_all(args.data_dir, args.docs_dir)
    matrix = json.dumps({"product": codes}, separators=(",", ":"))
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"matrix={matrix}\n")
            output.write(f"has_work={str(bool(codes)).lower()}\n")
    print(matrix)
    return 0


def sync_command(args: argparse.Namespace) -> int:
    code = history.validate_code(args.product)
    deadline = time.monotonic() + args.max_minutes * 60
    with locked(args.data_dir):
        if args.catalog:
            snapshot = json.loads(args.catalog.read_text(encoding="utf-8"))
            product, fetched_at = snapshot["product"], snapshot["fetched_at"]
        else:
            url = history.API_URL + "?" + urllib.parse.urlencode({"code": code})
            products = json.loads(transfer.fetch_bytes(url, deadline))
            if not isinstance(products, list) or len(products) != 1 or products[0]["code"] != code:
                raise StopRun(f"Expected exactly one {code} product")
            product, fetched_at = products[0], history.now()
        path = args.data_dir / f"{code}.json"
        state = history.load(path) if path.exists() else History(code, product["name"])
        failures = 0
        try:
            if args.retry_quarantined:
                count = history.retry_quarantined(state)
                log(f"{code}: reset {count} quarantined records for an explicit retry")
            sources = history.refresh_metadata(state, product, fetched_at)
            history.save(state, args.data_dir)
            if not args.catalog_only:
                failures = history.collect(
                    state,
                    sources,
                    lambda: history.save(state, args.data_dir),
                    args.work_dir.resolve(),
                    args.max_installers,
                    deadline,
                    args.checksums_only,
                )
        finally:
            history.save(state, args.data_dir)
            if not args.no_render:
                render.render_all(args.data_dir, args.docs_dir)
        counts = history.coverage(state)
        log(f"{code}: {json.dumps(counts, sort_keys=True)}")
        if counts["app_hashes"] < counts["advertised"]:
            log(
                "Application coverage is partial; future runs continue retryable work. "
                f"{counts['quarantined']} records are quarantined."
            )
        return int(failures > 0)


def merge_command(args: argparse.Namespace) -> int:
    paths = sorted(args.from_dir.rglob("*.json"))
    if not paths:
        raise StopRun("No product history artifacts found; refusing an empty publication")
    incoming = [history.load(path) for path in paths]
    if len({item.code for item in incoming}) != len(incoming):
        raise StopRun("Multiple incoming artifacts for the same product")
    with locked(args.data_dir):
        merged = []
        for item in incoming:
            path = args.data_dir / f"{item.code}.json"
            destination = history.load(path) if path.exists() else History(item.code, item.name)
            history.merge(destination, item)
            merged.append(destination)
        for item in merged:
            history.save(item, args.data_dir)
        render.render_all(args.data_dir, args.docs_dir)
    return 0


def positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Maintain historical JetBrains IDE installer and app hashes."
    )
    commands = result.add_subparsers(dest="command", required=True)

    def paths(command: argparse.ArgumentParser) -> None:
        command.add_argument("--data-dir", type=Path, default=Path("data"))
        command.add_argument("--docs-dir", type=Path, default=Path("ides"))

    def retry_option(command: argparse.ArgumentParser) -> None:
        command.add_argument(
            "--retry-quarantined",
            action="store_true",
            help="Retry quarantined records with a fresh five-failure allowance",
        )

    discover = commands.add_parser(
        "discover", help="Discover IDEs and prepare per-product API snapshots"
    )
    paths(discover)
    retry_option(discover)
    discover.add_argument(
        "--product", default="", help="JetBrains IDE product code; omit or leave blank for all"
    )
    discover.add_argument(
        "--catalog-file", type=Path, help="Read a saved /products response instead of HTTP"
    )
    discover.add_argument("--output-dir", type=Path, default=Path("catalog-snapshot"))
    discover.add_argument(
        "--github-output", type=Path, help="Append matrix and has_work to this GitHub output file"
    )
    modes = discover.add_mutually_exclusive_group()
    modes.add_argument(
        "--seed", action="store_true", help="Seed metadata/tables without fetching hashes"
    )
    modes.add_argument(
        "--only-pending",
        action="store_true",
        help="Skip unchanged IDEs with only completed or quarantined records",
    )
    discover.add_argument(
        "--max-minutes",
        type=positive_int,
        default=5,
        help="Checksum preflight budget for --only-pending (default: 5); unverified IDEs stay queued",
    )
    discover.set_defaults(run=discover_command)

    sync = commands.add_parser(
        "sync", help="Refresh one IDE and collect a bounded batch of missing hashes"
    )
    paths(sync)
    retry_option(sync)
    sync.add_argument("--product", required=True, help="JetBrains product code, e.g. IIU or PCP")
    sync.add_argument("--catalog", type=Path, help="Per-product snapshot produced by discover")
    sync.add_argument("--work-dir", type=Path, default=Path(tempfile.gettempdir()))
    sync.add_argument("--max-installers", type=positive_int, default=10)
    sync.add_argument("--max-minutes", type=positive_int, default=40)
    modes = sync.add_mutually_exclusive_group()
    modes.add_argument("--catalog-only", action="store_true")
    modes.add_argument("--checksums-only", action="store_true")
    sync.add_argument(
        "--no-render", action="store_true", help="Leave rendering to the publication job"
    )
    sync.set_defaults(run=sync_command)

    merge = commands.add_parser(
        "merge", help="Merge job artifacts without dropping historical observations"
    )
    paths(merge)
    merge.add_argument("--from-dir", type=Path, required=True)
    merge.set_defaults(run=merge_command)

    render_parser = commands.add_parser(
        "render", help="Regenerate all Markdown without network access"
    )
    paths(render_parser)

    legacy = commands.add_parser(
        "import-legacy", help="Import the original idea-hashes CSV checkpoint"
    )
    paths(legacy)
    legacy.add_argument("--source", type=Path, required=True)
    return result


def interrupted(signum, frame) -> None:
    raise KeyboardInterrupt


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    previous_handler = signal.signal(signal.SIGTERM, interrupted)
    try:
        if args.command == "render":
            with locked(args.data_dir):
                render.render_all(args.data_dir, args.docs_dir)
            return 0
        if args.command == "import-legacy":
            with locked(args.data_dir):
                state = history.load(args.data_dir / "IIU.json")
                history.import_legacy(args.source, state)
                history.save(state, args.data_dir)
                render.render_all(args.data_dir, args.docs_dir)
                log(f"Imported legacy hashes: {history.coverage(state)}")
            return 0
        return args.run(args)
    except KeyboardInterrupt:
        log("Interrupted. Checkpoints are retained; rerun to resume.")
        return 130
    except (transfer.ArtifactError, StopRun, transfer.BudgetReached, OSError, ValueError) as exc:
        log(f"ERROR: {exc}")
        return 1
    finally:
        signal.signal(signal.SIGTERM, previous_handler)


if __name__ == "__main__":
    sys.exit(main())
