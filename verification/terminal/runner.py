from __future__ import annotations

import argparse
import sys

from verification.terminal.harness import GOLDEN_DIR, run_all
from verification.terminal.registry import TERMINAL_EXAMPLES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run cross-language terminal smoke tests.")
    parser.add_argument("--example", action="append", default=[], help="Run one named example.")
    parser.add_argument("--all", action="store_true", help="Run all registered examples.")
    parser.add_argument("--parallel", action="store_true", help="Run examples concurrently.")
    parser.add_argument(
        "--update-goldens",
        action="store_true",
        help="Regenerate normalized golden transcripts for passing examples.",
    )
    return parser


def select_examples(names: list[str]) -> list:
    if not names:
        return list(TERMINAL_EXAMPLES)
    known = {example.name: example for example in TERMINAL_EXAMPLES}
    missing = [name for name in names if name not in known]
    if missing:
        raise SystemExit(f"unknown example(s): {', '.join(missing)}")
    return [known[name] for name in names]


def _status_line(name: str, result) -> str:
    if result.skipped:
        reason = f" ({result.skip_reason})" if result.skip_reason else ""
        return f"SKIP {name} [{result.duration_s:.2f}s]{reason}"
    outcome = "PASS" if result.passed else "FAIL"
    marker = f", exit={result.exit_code}" if result.exit_code is not None else ""
    return f"{outcome} {name} [{result.duration_s:.2f}s{marker}]"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if not args.all and not args.example:
        parser.error("pass --all or at least one --example")

    examples = select_examples(args.example)
    results = run_all(
        examples,
        parallel=args.parallel,
        golden_dir=GOLDEN_DIR,
        update_golden=args.update_goldens,
    )

    passed = failed = skipped = 0
    for name in [example.name for example in examples]:
        result = results[name]
        print(_status_line(name, result))
        if result.skipped:
            skipped += 1
            continue
        if result.passed:
            passed += 1
        else:
            failed += 1
            if result.stderr.strip():
                print(result.stderr.strip())

    print(f"Summary: {passed} passed, {failed} failed, {skipped} skipped")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
