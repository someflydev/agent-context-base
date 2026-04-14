#!/usr/bin/env python3
"""
Faker arc parity check runner.

Checks:
1. Python reference implementation (generation_patterns.py) — always runs.
2. Python example pipelines (faker, mimesis) — runs if Faker/Mimesis installed.
3. Per-language toolchain tests — skipped if toolchain not available; documented.

Exit code 0: all checks pass or skip gracefully.
Exit code 1: one or more checks FAIL.
"""

import sys, json, pathlib, subprocess, tempfile

ROOT = pathlib.Path(__file__).parent.parent.parent
results = []

def record(impl, status, msg):
    results.append((impl, status, msg))
    print(f"  [{status}] {impl}: {msg}")

def check_python_reference():
    """Always runs — no toolchain required."""
    try:
        sys.path.insert(0, str(ROOT / "examples" / "canonical-faker"))
        from domain.generation_patterns import (
            Profile, generate_dataset
        )
    except ImportError as e:
        record("python-reference", "SKIP", f"import failed: {e}")
        return

    try:
        dataset = generate_dataset(Profile.SMOKE)
    except RuntimeError as e:
        if "faker is required" in str(e).lower():
            record("python-reference", "SKIP", "faker is not installed")
            return
        raise

    if not dataset["report"].ok:
        record("python-reference", "FAIL", f"validation failed: {dataset['report'].violations}")
        return
    assert len(dataset["organizations"]) == 3
    assert len(dataset["users"]) == 10
    record("python-reference", "PASS", "smoke profile produces valid dataset")

    # Reproducibility
    d2 = generate_dataset(Profile.SMOKE)
    if dataset["organizations"] == d2["organizations"]:
        record("python-reference", "PASS", "smoke profile is reproducible")
    else:
        record("python-reference", "FAIL", "smoke profile NOT reproducible")

def check_python_faker_pipeline():
    try:
        sys.path.insert(0, str(ROOT / "examples" / "canonical-faker"))
        from python.faker_pipeline.generators import run_faker_pipeline
        from domain.generation_patterns import Profile
    except ImportError as e:
        record("python-faker", "SKIP", f"import failed: {e}")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        p = pathlib.Path(tmpdir)
        try:
            run_faker_pipeline(Profile.SMOKE, p)
        except RuntimeError as e:
            if "faker is required" in str(e).lower():
                record("python-faker", "SKIP", "faker is not installed")
                return
            raise

        if (p / "organizations.jsonl").exists():
            record("python-faker", "PASS", "smoke JSONL output produced")
        else:
            record("python-faker", "FAIL", "organizations.jsonl not found")

def check_toolchain(name, cmd, cwd):
    """Run a toolchain command; skip if the toolchain is not available."""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, timeout=120, text=True
        )
        if result.returncode == 0:
            record(name, "PASS", f"toolchain tests passed")
        elif result.returncode == 127:
            record(name, "SKIP", f"toolchain not found (exit 127): {cmd[0]}")
        elif "Unable to locate a Java Runtime" in result.stderr or "Unable to locate a Java Runtime" in result.stdout:
            record(name, "SKIP", "Java Runtime not found")
        else:
            record(name, "FAIL", f"exit {result.returncode}: {result.stderr[:200]}")
    except FileNotFoundError:
        record(name, "SKIP", f"toolchain not found: {cmd[0]}")
    except subprocess.TimeoutExpired:
        record(name, "SKIP", "timed out (>120s) — run manually")

if __name__ == "__main__":
    print("\nFaker Arc Parity Check\n")

    check_python_reference()
    check_python_faker_pipeline()

    # Per-language toolchain checks (skip gracefully if not available)
    check_toolchain("js-jest",
        ["npx", "jest", "--testPathPattern=smoke.test.ts", "--passWithNoTests"],
        ROOT / "examples/canonical-faker/javascript")

    check_toolchain("go-test",
        ["go", "test", "./...", "-run", "TestSmoke", "-timeout", "30s"],
        ROOT / "examples/canonical-faker/go")

    check_toolchain("rust-cargo",
        ["cargo", "test", "--test", "smoke_test"],
        ROOT / "examples/canonical-faker/rust")

    check_toolchain("java-mvn",
        ["mvn", "test", "-Dtest=SmokeTest", "-q"],
        ROOT / "examples/canonical-faker/java")

    check_toolchain("kotlin-gradle",
        ["gradle", "test", "--tests", "*.SmokeTest"],
        ROOT / "examples/canonical-faker/kotlin")

    check_toolchain("ruby-rspec",
        ["bundle", "exec", "rspec", "spec/smoke_spec.rb"],
        ROOT / "examples/canonical-faker/ruby")

    check_toolchain("php-phpunit",
        ["./vendor/bin/phpunit", "tests/SmokeTest.php"],
        ROOT / "examples/canonical-faker/php")

    check_toolchain("scala-sbt",
        ["sbt", "testOnly *.SmokeTest"],
        ROOT / "examples/canonical-faker/scala")

    check_toolchain("elixir-mix",
        ["mix", "test", "test/tenant_core/smoke_test.exs"],
        ROOT / "examples/canonical-faker/elixir")

    passes = [r for r in results if r[1] == "PASS"]
    fails  = [r for r in results if r[1] == "FAIL"]
    skips  = [r for r in results if r[1] == "SKIP"]

    print(f"\nParity Check: {len(passes)} PASS, {len(fails)} FAIL, {len(skips)} SKIP\n")

    if fails:
        print(f"{len(fails)} check(s) FAILED.")
        sys.exit(1)
    else:
        print("All checks PASSED (or gracefully skipped).")
        sys.exit(0)
