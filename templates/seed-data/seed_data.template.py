from __future__ import annotations

from pathlib import Path


def main() -> None:
    root = Path("docker/volumes/dev")
    root.mkdir(parents=True, exist_ok=True)
    target = root / "{{seed_filename}}"
    target.write_text("replace this with deterministic seed data\n", encoding="utf-8")
    print(f"Seeded {target}")


if __name__ == "__main__":
    main()

