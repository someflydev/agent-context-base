from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(slots=True)
class PreviewRow:
    name: str
    status: str
    owner: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="opsctl")
    subcommands = parser.add_subparsers(dest="command", required=True)

    preview = subcommands.add_parser("preview-runs", help="Show the current run summary.")
    preview.add_argument("--limit", type=int, default=5)
    preview.add_argument("--format", choices=("table", "json"), default="table")
    return parser


def load_rows(limit: int) -> list[PreviewRow]:
    rows = [
        PreviewRow(name="daily-signups", status="ready", owner="analytics"),
        PreviewRow(name="failed-payments", status="warning", owner="ops"),
        PreviewRow(name="trial-conversions", status="ready", owner="growth"),
    ]
    return rows[:limit]


def render_rows(rows: list[PreviewRow], output_format: str) -> None:
    if output_format == "json":
        print(json.dumps([asdict(row) for row in rows], indent=2))
        return

    print("name                status   owner")
    print("----                ------   -----")
    for row in rows:
        print(f"{row.name:<18}  {row.status:<7}  {row.owner}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    rows = load_rows(limit=args.limit)
    render_rows(rows, output_format=args.format)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

