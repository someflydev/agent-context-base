"""Coverage verification for the 100 example prompts and 8 derived examples.

This module validates that:
- All 100 example-prompts entries are structurally sound
- All 8 derived-examples entries are structurally sound
- Every archetype and stack in new_repo.py is exercised by at least one example
- Dokku and integration-test flags are meaningfully represented
"""

from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path
from typing import Any

from verification.helpers import load_yaml_like


# ---------------------------------------------------------------------------
# Block-scalar pre-processor
# ---------------------------------------------------------------------------

def _preprocess_yaml_block_scalars(text: str) -> str:
    """Replace YAML block scalar (|) content with a single-line placeholder.

    The repo's custom YAML parser does not handle multi-line block scalars.
    This function converts every ``key: |`` + indented-content block into
    ``key: block-scalar-content`` so the parser can proceed normally.
    """
    lines = text.splitlines()
    result: list[str] = []
    i = 0
    while i < len(lines):
        raw = lines[i]
        rstripped = raw.rstrip()
        stripped = rstripped.strip()
        # Detect a block scalar indicator at the end of a non-comment line
        if stripped and not stripped.startswith("#") and rstripped.rstrip().endswith("|"):
            # Only treat it as a block scalar if there is a colon before the |
            if re.search(r":\s*\|$", rstripped):
                key_indent = len(rstripped) - len(rstripped.lstrip())
                # Replace trailing | with a placeholder value
                placeholder = re.sub(r"\|\s*$", "block-scalar-content", rstripped)
                result.append(placeholder)
                i += 1
                # Skip all continuation lines (indented deeper than the key)
                while i < len(lines):
                    cont = lines[i].rstrip()
                    if not cont.strip():
                        # blank line: may be part of block scalar, skip
                        i += 1
                        continue
                    cont_indent = len(cont) - len(cont.lstrip())
                    if cont_indent > key_indent:
                        i += 1  # still inside block scalar content
                    else:
                        break  # back to normal indentation level
                continue
        result.append(raw)
        i += 1
    return "\n".join(result)


def _load_yaml_with_block_scalars(path: Path) -> Any:
    """Load a YAML file that may contain block scalar (|) strings."""
    text = path.read_text(encoding="utf-8")
    cleaned = _preprocess_yaml_block_scalars(text)
    # Write to a temp-like Path via write_text + load, or reuse parser internals
    from verification.helpers import _prepare_yaml_lines, _parse_yaml_block  # noqa: PLC0415
    import json as _json  # noqa: PLC0415
    try:
        return _json.loads(cleaned)
    except _json.JSONDecodeError:
        prepared = _prepare_yaml_lines(cleaned)
        if not prepared:
            return {}
        parsed, _ = _parse_yaml_block(prepared, 0, prepared[0][0])
        return parsed


# ---------------------------------------------------------------------------
# Inline list parser (for source_examples: [28, 1, 35])
# ---------------------------------------------------------------------------

def _coerce_int_list(value: object) -> list[int]:
    """Return a list of ints from either a list or an inline '[1, 2, 3]' string."""
    if isinstance(value, list):
        return [int(x) for x in value]
    if isinstance(value, str):
        s = value.strip()
        if s.startswith("[") and s.endswith("]"):
            inner = s[1:-1].strip()
            if not inner:
                return []
            return [int(x.strip()) for x in inner.split(",")]
    return []


# ---------------------------------------------------------------------------
# YAML loaders
# ---------------------------------------------------------------------------

def load_example_prompts() -> list[dict]:
    """Load and return the examples list from examples/derived/example-prompts.yaml."""
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "examples" / "derived" / "example-prompts.yaml"
    data = _load_yaml_with_block_scalars(path)
    return data["examples"]


def load_derived_examples() -> list[dict]:
    """Load and return the derived list from examples/derived/derived-examples.yaml."""
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "examples" / "derived" / "derived-examples.yaml"
    data = _load_yaml_with_block_scalars(path)
    return data["derived"]


def load_spin_outs() -> list[dict]:
    """Load and return the spin_outs list from examples/derived/spin-outs.yaml."""
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "examples" / "derived" / "spin-outs.yaml"
    data = _load_yaml_with_block_scalars(path)
    return data["spin_outs"]


def load_tier_rankings() -> list[dict]:
    """Load and return the tier_rankings list from examples/derived/tier-rankings.yaml."""
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "examples" / "derived" / "tier-rankings.yaml"
    data = load_yaml_like(path)
    return data["tier_rankings"]


def load_orchestration_strategies() -> list[dict]:
    """Load and return the orchestration_strategies list from examples/derived/orchestration-strategies.yaml."""
    repo_root = Path(__file__).resolve().parents[3]
    path = repo_root / "examples" / "derived" / "orchestration-strategies.yaml"
    data = _load_yaml_with_block_scalars(path)
    return data["orchestration_strategies"]


# ---------------------------------------------------------------------------
# new_repo.py importer
# ---------------------------------------------------------------------------

def _load_new_repo():
    """Load new_repo.py as a module, injecting scripts/ into sys.path first."""
    repo_root = Path(__file__).resolve().parents[3]
    scripts_dir = str(repo_root / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(
        "new_repo", repo_root / "scripts" / "new_repo.py"
    )
    if spec is None or spec.loader is None:
        raise ImportError("could not create module spec for scripts/new_repo.py")
    mod = importlib.util.module_from_spec(spec)
    # Must register in sys.modules before exec_module so that @dataclass can
    # resolve the module's __dict__ when Python 3.14 processes frozen=True.
    previous = sys.modules.get("new_repo")
    sys.modules["new_repo"] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception as exc:
        raise ImportError(f"failed to load scripts/new_repo.py: {exc}") from exc
    finally:
        if previous is None:
            sys.modules.pop("new_repo", None)
        else:
            sys.modules["new_repo"] = previous
    return mod


# Module-level constants loaded once from new_repo.py
_new_repo = _load_new_repo()
ARCHETYPES: list[str] = list(_new_repo.ARCHETYPES.keys())
STACKS: dict = _new_repo.STACKS


# ---------------------------------------------------------------------------
# Test class
# ---------------------------------------------------------------------------

class TestDerivedCoverage(unittest.TestCase):

    # ------------------------------------------------------------------
    # example-prompts.yaml tests
    # ------------------------------------------------------------------

    def test_example_prompts_count(self) -> None:
        examples = load_example_prompts()
        self.assertEqual(
            len(examples),
            101,
            f"expected 101 example prompts, got {len(examples)}",
        )

    def test_example_prompts_sequential_numbering(self) -> None:
        examples = load_example_prompts()
        numbers = sorted(int(e["number"]) for e in examples)
        self.assertEqual(
            numbers,
            list(range(1, 102)),
            "example numbers must increment from 1 to 101 without gaps or duplicates",
        )

    def test_example_prompts_required_fields(self) -> None:
        examples = load_example_prompts()
        errors: list[str] = []
        top_level_fields = ("number", "codename", "category", "category_name", "prompt", "new_repo_args")
        new_repo_args_fields = ("archetype", "primary_stack")
        for entry in examples:
            n = entry.get("number", "?")
            for field in top_level_fields:
                if field not in entry:
                    errors.append(f"entry {n}: missing field '{field}'")
            nra = entry.get("new_repo_args")
            if not isinstance(nra, dict):
                errors.append(f"entry {n}: new_repo_args must be a mapping")
            else:
                for field in new_repo_args_fields:
                    if field not in nra:
                        errors.append(f"entry {n}: new_repo_args missing '{field}'")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_example_prompts_valid_archetypes(self) -> None:
        examples = load_example_prompts()
        valid = set(ARCHETYPES)
        errors: list[str] = []
        for entry in examples:
            n = entry.get("number", "?")
            nra = entry.get("new_repo_args", {})
            archetype = nra.get("archetype", "")
            if archetype not in valid:
                errors.append(f"entry {n}: invalid archetype '{archetype}' (valid: {sorted(valid)})")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_example_prompts_valid_stacks(self) -> None:
        examples = load_example_prompts()
        valid = set(STACKS.keys())
        errors: list[str] = []
        for entry in examples:
            n = entry.get("number", "?")
            nra = entry.get("new_repo_args", {})
            stack = nra.get("primary_stack", "")
            if stack not in valid:
                errors.append(f"entry {n}: invalid primary_stack '{stack}' (valid: {sorted(valid)})")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_example_prompts_nonempty_prompt_text(self) -> None:
        examples = load_example_prompts()
        errors: list[str] = []
        for entry in examples:
            n = entry.get("number", "?")
            prompt = entry.get("prompt", "")
            if not isinstance(prompt, str) or not prompt.strip():
                errors.append(f"entry {n}: prompt must be a non-empty string")
        self.assertEqual(errors, [], "\n".join(errors))

    # ------------------------------------------------------------------
    # derived-examples.yaml tests
    # ------------------------------------------------------------------

    def test_derived_examples_count(self) -> None:
        derived = load_derived_examples()
        self.assertEqual(
            len(derived),
            8,
            f"expected 8 derived examples, got {len(derived)}",
        )

    def test_derived_examples_team_split(self) -> None:
        derived = load_derived_examples()
        team_a = [e for e in derived if e.get("team") == "A"]
        team_b = [e for e in derived if e.get("team") == "B"]
        self.assertEqual(len(team_a), 4, f"expected 4 Team A entries, got {len(team_a)}")
        self.assertEqual(len(team_b), 4, f"expected 4 Team B entries, got {len(team_b)}")

    def test_derived_examples_required_fields(self) -> None:
        derived = load_derived_examples()
        errors: list[str] = []
        required = ("name", "team", "team_name", "description", "source_examples", "prompt", "new_repo_args")
        for entry in derived:
            name = entry.get("name", "?")
            for field in required:
                if field not in entry:
                    errors.append(f"derived '{name}': missing field '{field}'")
            # source_examples must be non-empty (list or inline string list)
            src = entry.get("source_examples")
            coerced = _coerce_int_list(src) if src is not None else []
            if not coerced:
                errors.append(f"derived '{name}': source_examples must be a non-empty list")
            # new_repo_args must be non-empty list
            nra = entry.get("new_repo_args")
            if not isinstance(nra, list) or not nra:
                errors.append(f"derived '{name}': new_repo_args must be a non-empty list")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_derived_examples_source_references_valid(self) -> None:
        examples = load_example_prompts()
        valid_numbers = {int(e["number"]) for e in examples}
        derived = load_derived_examples()
        errors: list[str] = []
        for entry in derived:
            name = entry.get("name", "?")
            src = _coerce_int_list(entry.get("source_examples", []))
            for num in src:
                if num not in valid_numbers:
                    errors.append(f"derived '{name}': source_examples ref {num} not in example-prompts.yaml")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_derived_examples_valid_archetypes(self) -> None:
        derived = load_derived_examples()
        valid = set(ARCHETYPES)
        errors: list[str] = []
        for entry in derived:
            name = entry.get("name", "?")
            for item in entry.get("new_repo_args", []):
                archetype = item.get("archetype", "")
                if archetype not in valid:
                    errors.append(
                        f"derived '{name}': invalid archetype '{archetype}'"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_derived_examples_valid_stacks(self) -> None:
        derived = load_derived_examples()
        valid = set(STACKS.keys())
        errors: list[str] = []
        for entry in derived:
            name = entry.get("name", "?")
            for item in entry.get("new_repo_args", []):
                stack = item.get("primary_stack", "")
                if stack not in valid:
                    errors.append(
                        f"derived '{name}': invalid primary_stack '{stack}'"
                    )
        self.assertEqual(errors, [], "\n".join(errors))

    # ------------------------------------------------------------------
    # Coverage tests
    # ------------------------------------------------------------------

    def test_archetype_coverage(self) -> None:
        """Every archetype in new_repo.py must be exercised by at least one example."""
        examples = load_example_prompts()
        covered = {e["new_repo_args"]["archetype"] for e in examples}
        expected = set(ARCHETYPES)
        missing = expected - covered
        self.assertEqual(
            missing,
            set(),
            f"archetypes not covered by any example: {sorted(missing)}\n"
            f"Add examples for these archetypes to examples/derived/example-prompts.yaml.",
        )

    def test_stack_coverage(self) -> None:
        """Every stack in new_repo.py must be exercised by at least one example."""
        examples = load_example_prompts()
        covered = {e["new_repo_args"]["primary_stack"] for e in examples}
        expected = set(STACKS.keys())
        missing = expected - covered
        self.assertEqual(
            missing,
            set(),
            f"stacks not covered by any example: {sorted(missing)}\n"
            f"Add examples for these stacks to examples/derived/example-prompts.yaml.",
        )

    def test_dokku_flag_coverage(self) -> None:
        """At least 8 examples must have dokku=True."""
        examples = load_example_prompts()
        dokku_examples = [
            e for e in examples if e.get("new_repo_args", {}).get("dokku") is True
        ]
        self.assertGreaterEqual(
            len(dokku_examples),
            8,
            f"expected at least 8 examples with dokku=True, got {len(dokku_examples)}",
        )

    def test_integration_tests_flag_coverage(self) -> None:
        """At least 5 examples must have integration_tests=True."""
        examples = load_example_prompts()
        integration_examples = [
            e for e in examples
            if e.get("new_repo_args", {}).get("integration_tests") is True
        ]
        self.assertGreaterEqual(
            len(integration_examples),
            5,
            f"expected at least 5 examples with integration_tests=True, got {len(integration_examples)}",
        )


    # ------------------------------------------------------------------
    # spin-outs.yaml tests
    # ------------------------------------------------------------------

    def test_spin_outs_loaded(self) -> None:
        spin_outs = load_spin_outs()
        self.assertEqual(
            len(spin_outs),
            10,
            f"expected 10 spin-out entries, got {len(spin_outs)}",
        )

    def test_spin_outs_required_fields(self) -> None:
        spin_outs = load_spin_outs()
        required = ("name", "title", "origin", "description", "source_examples",
                    "what_it_becomes", "value", "seam_notes")
        errors: list[str] = []
        for entry in spin_outs:
            name = entry.get("name", "?")
            for field in required:
                if field not in entry:
                    errors.append(f"spin-out '{name}': missing field '{field}'")
            src = _coerce_int_list(entry.get("source_examples", []))
            if not src:
                errors.append(f"spin-out '{name}': source_examples must be a non-empty list")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_spin_outs_valid_origin(self) -> None:
        spin_outs = load_spin_outs()
        valid_origins = {"team_a", "team_b", "cross_team"}
        errors: list[str] = []
        for entry in spin_outs:
            name = entry.get("name", "?")
            origin = entry.get("origin", "")
            if origin not in valid_origins:
                errors.append(
                    f"spin-out '{name}': invalid origin '{origin}' (valid: {sorted(valid_origins)})"
                )
        self.assertEqual(errors, [], "\n".join(errors))

    def test_spin_outs_source_references_valid(self) -> None:
        spin_outs = load_spin_outs()
        errors: list[str] = []
        for entry in spin_outs:
            name = entry.get("name", "?")
            src = _coerce_int_list(entry.get("source_examples", []))
            for num in src:
                if num not in range(1, 101):
                    errors.append(f"spin-out '{name}': source_examples ref {num} not in range 1-100")
        self.assertEqual(errors, [], "\n".join(errors))

    # ------------------------------------------------------------------
    # tier-rankings.yaml tests
    # ------------------------------------------------------------------

    def test_tier_rankings_loaded(self) -> None:
        tier_rankings = load_tier_rankings()
        self.assertEqual(
            len(tier_rankings),
            5,
            f"expected 5 tier entries, got {len(tier_rankings)}",
        )

    def test_tier_rankings_all_100_covered(self) -> None:
        tier_rankings = load_tier_rankings()
        all_numbers: set[int] = set()
        for tier in tier_rankings:
            for entry in tier.get("entries", []):
                num = entry.get("number")
                if num is not None:
                    all_numbers.add(int(num))
        expected = set(range(1, 101))
        missing = expected - all_numbers
        extra = all_numbers - expected
        errors: list[str] = []
        if missing:
            errors.append(f"numbers missing from tier-rankings: {sorted(missing)}")
        if extra:
            errors.append(f"numbers outside 1-100 in tier-rankings: {sorted(extra)}")
        self.assertEqual(errors, [], "\n".join(errors))

    # ------------------------------------------------------------------
    # orchestration-strategies.yaml tests
    # ------------------------------------------------------------------

    def test_orchestration_strategies_loaded(self) -> None:
        strategies = load_orchestration_strategies()
        self.assertEqual(
            len(strategies),
            5,
            f"expected 5 orchestration strategies, got {len(strategies)}",
        )

    def test_orchestration_strategies_required_fields(self) -> None:
        strategies = load_orchestration_strategies()
        required = ("name", "title", "primary_examples", "summary", "when_to_use", "tradeoffs")
        errors: list[str] = []
        for entry in strategies:
            name = entry.get("name", "?")
            for field in required:
                if field not in entry:
                    errors.append(f"strategy '{name}': missing field '{field}'")
            src = _coerce_int_list(entry.get("primary_examples", []))
            if not src:
                errors.append(f"strategy '{name}': primary_examples must be a non-empty list")
            for num in src:
                if num not in range(1, 101):
                    errors.append(f"strategy '{name}': primary_examples ref {num} not in range 1-100")
        self.assertEqual(errors, [], "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
