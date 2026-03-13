from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import types
import dataclasses as _stdlib_dataclasses
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFICATION_ROOT = REPO_ROOT / "verification"

VALID_VERIFICATION_LEVELS = {
    "draft",
    "syntax-checked",
    "smoke-verified",
    "behavior-verified",
    "golden",
}


def parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value.startswith(("'", '"')) and value.endswith(("'", '"')) and len(value) >= 2:
        return value[1:-1]
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered == "null":
        return None
    if value.isdigit():
        return int(value)
    return value


def _prepare_yaml_lines(text: str) -> list[tuple[int, str]]:
    prepared: list[tuple[int, str]] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        prepared.append((len(line) - len(line.lstrip(" ")), stripped))
    return prepared


def _parse_yaml_block(lines: list[tuple[int, str]], start: int, indent: int) -> tuple[Any, int]:
    mapping: dict[str, Any] = {}
    sequence: list[Any] | None = None
    index = start

    while index < len(lines):
        current_indent, content = lines[index]
        if current_indent < indent:
            break
        if current_indent != indent:
            raise ValueError(f"unexpected indentation at line {index + 1}: {content}")

        if content.startswith("- "):
            if sequence is None:
                sequence = []
            item_text = content[2:].strip()
            index += 1

            if not item_text:
                nested, index = _parse_yaml_block(lines, index, indent + 2)
                sequence.append(nested)
                continue

            if ":" in item_text:
                key, raw_value = item_text.split(":", 1)
                item: dict[str, Any] = {}
                raw_value = raw_value.strip()
                if raw_value:
                    item[key.strip()] = parse_scalar(raw_value)
                else:
                    nested, index = _parse_yaml_block(lines, index, indent + 2)
                    item[key.strip()] = nested

                while index < len(lines):
                    child_indent, child_content = lines[index]
                    if child_indent < indent + 2:
                        break
                    if child_indent > indent + 2:
                        raise ValueError(
                            f"unexpected indentation for sequence mapping at line {index + 1}: {child_content}"
                        )
                    if child_content.startswith("- "):
                        break
                    child_key, child_raw = child_content.split(":", 1)
                    child_raw = child_raw.strip()
                    index += 1
                    if child_raw:
                        item[child_key.strip()] = parse_scalar(child_raw)
                    else:
                        nested, index = _parse_yaml_block(lines, index, indent + 4)
                        item[child_key.strip()] = nested
                sequence.append(item)
                continue

            sequence.append(parse_scalar(item_text))
            continue

        key, raw_value = content.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()
        index += 1
        if raw_value:
            mapping[key] = parse_scalar(raw_value)
            continue
        nested, index = _parse_yaml_block(lines, index, indent + 2)
        mapping[key] = nested

    if sequence is not None:
        return sequence, index
    return mapping, index


def load_yaml_like(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        lines = _prepare_yaml_lines(text)
        if not lines:
            return {}
        parsed, index = _parse_yaml_block(lines, 0, lines[0][0])
        if index != len(lines):
            raise ValueError(f"did not fully parse {path}")
        return parsed


def load_registry() -> list[dict[str, Any]]:
    data = load_yaml_like(VERIFICATION_ROOT / "example_registry.yaml")
    entries = data.get("examples", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        raise ValueError("verification/example_registry.yaml: 'examples' must be a list")
    return [entry for entry in entries if isinstance(entry, dict)]


def load_stack_matrix() -> list[dict[str, Any]]:
    data = load_yaml_like(VERIFICATION_ROOT / "stack_support_matrix.yaml")
    entries = data.get("stacks", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        raise ValueError("verification/stack_support_matrix.yaml: 'stacks' must be a list")
    return [entry for entry in entries if isinstance(entry, dict)]


def registry_by_path() -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("path", "")).strip(): entry
        for entry in load_registry()
        if isinstance(entry.get("path"), str)
    }


def load_python_module(
    path: Path,
    *,
    module_name: str,
    stub_modules: dict[str, types.ModuleType] | None = None,
) -> types.ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not create module spec for {path}")
    module = importlib.util.module_from_spec(spec)
    injected = stub_modules or {}
    previous = {name: sys.modules.get(name) for name in injected}
    previous_module = sys.modules.get(module_name)
    try:
        sys.modules[module_name] = module
        for name, stub in injected.items():
            sys.modules[name] = stub
        spec.loader.exec_module(module)
        return module
    finally:
        if previous_module is None:
            sys.modules.pop(module_name, None)
        else:
            sys.modules[module_name] = previous_module
        for name, old_value in previous.items():
            if old_value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = old_value


def compat_dataclasses_module() -> types.ModuleType:
    module = types.ModuleType("dataclasses")
    for name in dir(_stdlib_dataclasses):
        setattr(module, name, getattr(_stdlib_dataclasses, name))

    def dataclass(*args: Any, **kwargs: Any):
        kwargs.pop("slots", None)
        return _stdlib_dataclasses.dataclass(*args, **kwargs)

    module.dataclass = dataclass
    module.asdict = _stdlib_dataclasses.asdict
    return module


def command_available(command: str) -> bool:
    return shutil.which(command) is not None


def docker_enabled() -> bool:
    flag = os.environ.get("VERIFY_DOCKER", "").strip().lower()
    return flag in {"1", "true", "yes", "on"} and command_available("docker")


def to_module_name(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).with_suffix("")
    return ".".join(relative.parts)
