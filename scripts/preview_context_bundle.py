#!/usr/bin/env python3
"""Preview the ordered context bundle for a manifest name or path."""

from __future__ import annotations

import sys
from pathlib import Path


LIST_KEYS = {
    "stacks",
    "triggers",
    "required_context",
    "optional_context",
    "preferred_examples",
    "warnings",
}


def parse_manifest(path: Path) -> dict[str, object]:
    """Parse the limited YAML subset used by repo manifests."""

    data: dict[str, object] = {}
    current_list_key: str | None = None

    for lineno, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("- "):
            if current_list_key is None:
                raise ValueError(f"{path}:{lineno}: list item without an active list key")
            value = stripped[2:].strip()
            if not value:
                raise ValueError(f"{path}:{lineno}: empty list item")
            data[current_list_key].append(value)  # type: ignore[index]
            continue

        current_list_key = None
        if ":" not in stripped:
            raise ValueError(f"{path}:{lineno}: expected 'key: value' or list key")

        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not value:
            if key not in LIST_KEYS:
                raise ValueError(f"{path}:{lineno}: non-list key '{key}' missing a value")
            data[key] = []
            current_list_key = key
            continue

        data[key] = value

    return data


def resolve_manifest(repo_root: Path, raw: str) -> Path:
    """Resolve a manifest name or path into a concrete file path."""

    candidate = Path(raw)
    if candidate.is_absolute():
        path = candidate
    elif "/" in raw or raw.endswith(".yaml"):
        path = (repo_root / candidate).resolve()
    else:
        path = (repo_root / "manifests" / f"{raw}.yaml").resolve()

    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {raw}")
    return path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python scripts/preview_context_bundle.py <manifest-name-or-path>", file=sys.stderr)
        return 1

    repo_root = Path(__file__).resolve().parents[1]

    try:
        manifest_path = resolve_manifest(repo_root, argv[1])
        data = parse_manifest(manifest_path)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    required = data.get("required_context", [])
    optional = data.get("optional_context", [])
    examples = data.get("preferred_examples", [])

    ordered_bundle = [
        "README.md",
        "docs/repo-purpose.md",
        "docs/repo-layout.md",
        manifest_path.relative_to(repo_root).as_posix(),
        *required,
        *optional,
        *examples,
    ]

    seen: set[str] = set()
    deduped_bundle: list[str] = []
    for entry in ordered_bundle:
        if isinstance(entry, str) and entry not in seen:
            seen.add(entry)
            deduped_bundle.append(entry)

    print(f"Manifest: {manifest_path.relative_to(repo_root).as_posix()}")
    if "name" in data:
        print(f"Name: {data['name']}")
    if "archetype" in data:
        print(f"Archetype: {data['archetype']}")
    print()
    print("Load order:")
    for index, entry in enumerate(deduped_bundle, start=1):
        print(f"{index}. {entry}")

    warnings = data.get("warnings", [])
    if isinstance(warnings, list):
        print()
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

