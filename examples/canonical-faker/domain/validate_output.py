from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ENTITY_ORDER = [
    "organizations",
    "users",
    "memberships",
    "projects",
    "audit_events",
    "api_keys",
    "invitations",
]


def load_generation_module():
    module_path = Path(__file__).with_name("generation_patterns.py")
    spec = importlib.util.spec_from_file_location("canonical_faker_generation_patterns", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load generation module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                rows.append(json.loads(text))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
    return rows


def load_dataset(input_dir: Path) -> dict:
    dataset: dict[str, object] = {}
    for entity in ENTITY_ORDER:
        path = input_dir / f"{entity}.jsonl"
        if not path.exists():
            raise FileNotFoundError(f"missing required JSONL file: {path}")
        dataset[entity] = read_jsonl(path)
    return dataset


def build_summary(report, dataset: dict) -> list[str]:
    lines = []
    lines.append(f"FK and cross-field checks: {'PASS' if report.ok else 'FAIL'}")
    for entity in ENTITY_ORDER:
        count = len(dataset.get(entity, []))
        row_status = "PASS" if count >= 1 else "FAIL"
        lines.append(f"Row count {entity}: {row_status} ({count})")
    lines.append(
        f"Unique org IDs: {'PASS' if len({row['id'] for row in dataset['organizations']}) == len(dataset['organizations']) else 'FAIL'}"
    )
    lines.append(
        f"Unique user emails: {'PASS' if len({row['email'].lower() for row in dataset['users']}) == len(dataset['users']) else 'FAIL'}"
    )
    lines.append(
        f"Unique API key prefixes: {'PASS' if len({row['key_prefix'] for row in dataset['api_keys']}) == len(dataset['api_keys']) else 'FAIL'}"
    )
    return lines


def additional_violations(dataset: dict) -> list[str]:
    violations: list[str] = []
    minimum_rows = {
        "organizations": 1,
        "users": 1,
        "memberships": 1,
        "projects": 1,
        "audit_events": 1,
        "api_keys": 0,
        "invitations": 0,
    }
    for entity in ENTITY_ORDER:
        count = len(dataset.get(entity, []))
        minimum = minimum_rows[entity]
        if count < minimum:
            violations.append(f"row count below minimum for {entity}: {count} < {minimum}")
    if len({row["id"] for row in dataset["organizations"]}) != len(dataset["organizations"]):
        violations.append("duplicate organizations.id detected")
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate canonical faker JSONL output for FK integrity and rule compliance."
    )
    parser.add_argument("--input-dir", required=True, help="Directory containing entity JSONL files")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable JSON report")
    args = parser.parse_args(argv)

    input_dir = Path(args.input_dir)
    dataset = load_dataset(input_dir)

    module = load_generation_module()
    dataset["profile"] = input_dir.name
    dataset["seed"] = -1
    report = module.validate_dataset(dataset)
    extra_violations = additional_violations(dataset)
    ok = report.ok and not extra_violations
    violations = list(report.violations) + extra_violations

    payload = {
        "ok": ok,
        "violations": violations,
        "counts": report.counts,
        "profile": report.profile,
        "seed": report.seed,
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Validation summary")
        print("==================")
        for line in build_summary(report, dataset):
            print(line)
        if violations:
            print("Violations:")
            for violation in violations:
                print(f"- {violation}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
