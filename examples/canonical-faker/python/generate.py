from __future__ import annotations

import argparse
import sys
from pathlib import Path

from factory_graph.runner import run_factory_graph
from faker_pipeline.generators import run_faker_pipeline
from mimesis_pipeline.generators import run_mimesis_pipeline
from profiles import resolve_profile


def _print_report(report) -> None:
    print("Validation report")
    print("=================")
    print(f"Profile: {report.profile}")
    print(f"Seed: {report.seed}")
    print(f"OK: {report.ok}")
    for entity, count in report.counts.items():
        print(f"- {entity}: {count}")
    if report.violations:
        print("Violations:")
        for violation in report.violations:
            print(f"- {violation}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate canonical TenantCore faker datasets.")
    parser.add_argument(
        "--pipeline",
        choices=("faker", "mimesis", "factory"),
        default="faker",
        help="Which generation pipeline to use.",
    )
    parser.add_argument(
        "--profile",
        choices=("smoke", "small", "medium", "large"),
        default="smoke",
        help="Which output profile to generate.",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Base directory for generated output.",
    )
    parser.add_argument("--seed", type=int, help="Override the profile seed.")
    parser.add_argument(
        "--format",
        choices=("jsonl", "csv", "both"),
        default="jsonl",
        help="Output format.",
    )
    args = parser.parse_args(argv)

    profile = resolve_profile(args.profile, seed=args.seed)
    pipeline_output_dir = Path(args.output_dir) / profile.name
    formats = ("jsonl", "csv") if args.format == "both" else (args.format,)

    runners = {
        "faker": run_faker_pipeline,
        "mimesis": run_mimesis_pipeline,
        "factory": run_factory_graph,
    }
    report = runners[args.pipeline](profile=profile, output_dir=pipeline_output_dir, formats=formats)
    _print_report(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
