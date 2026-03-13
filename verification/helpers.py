from __future__ import annotations

import dataclasses as _stdlib_dataclasses
import importlib.util
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import types
import urllib.error
import urllib.request
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

VERIFICATION_LEVEL_SCORES = {
    "draft": 0,
    "syntax-checked": 1,
    "smoke-verified": 2,
    "behavior-verified": 3,
    "golden": 4,
}

CONFIDENCE_SCORES = {
    "low": 1,
    "medium": 2,
    "high": 3,
}

EXAMPLE_SUPPORT_FILENAMES = {
    "README.md",
    "catalog.json",
    "Dockerfile",
    "build.zig",
    "build.zig.zon",
    "requirements.txt",
    "go.mod",
    "Cargo.toml",
    "Cargo.lock",
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


def registry_by_name() -> dict[str, dict[str, Any]]:
    return {
        str(entry.get("name", "")).strip(): entry
        for entry in load_registry()
        if isinstance(entry.get("name"), str)
    }


def verification_score(entry: dict[str, Any]) -> int:
    return VERIFICATION_LEVEL_SCORES.get(str(entry.get("verification_level", "")).strip(), 0)


def confidence_score(entry: dict[str, Any]) -> int:
    return CONFIDENCE_SCORES.get(str(entry.get("confidence", "")).strip(), 0)


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


def run_command(
    args: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
    timeout: int = 60,
) -> subprocess.CompletedProcess[str]:
    command_env = os.environ.copy()
    if env:
        command_env.update(env)
    return subprocess.run(
        args,
        cwd=cwd,
        env=command_env,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def free_tcp_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def wait_for_http_json(url: str, *, timeout: float = 20.0) -> tuple[int, Any]:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2.0) as response:
                payload = response.read().decode("utf-8")
                try:
                    return response.status, json.loads(payload)
                except json.JSONDecodeError:
                    return response.status, payload
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
            time.sleep(0.25)
    raise AssertionError(f"timed out waiting for {url}: {last_error}")


def to_module_name(path: Path) -> str:
    relative = path.relative_to(REPO_ROOT).with_suffix("")
    return ".".join(relative.parts)


class _FakePolarsExpression:
    def __eq__(self, _other: object) -> "_FakePolarsExpression":
        return self

    def __truediv__(self, _other: object) -> "_FakePolarsExpression":
        return self

    def then(self, _value: object) -> "_FakePolarsExpression":
        return self

    def otherwise(self, _value: object) -> "_FakePolarsExpression":
        return self

    def alias(self, _name: str) -> "_FakePolarsExpression":
        return self


class FakePolarsFrame:
    def __init__(self, data: list[dict[str, Any]] | dict[str, list[Any]]) -> None:
        if isinstance(data, dict):
            keys = list(data.keys())
            values = list(data.values())
            row_count = len(values[0]) if values else 0
            self._rows = [
                {key: data[key][index] for key in keys}
                for index in range(row_count)
            ]
        else:
            self._rows = [dict(row) for row in data]

    def with_columns(self, *_expressions: object) -> "FakePolarsFrame":
        rows: list[dict[str, Any]] = []
        for row in self._rows:
            updated = dict(row)
            if "total_events" in row and "error_events" in row:
                total = row["total_events"]
                updated["error_rate"] = 0.0 if not total else row["error_events"] / total
            rows.append(updated)
        return FakePolarsFrame(rows)

    def select(self, *columns: str) -> "FakePolarsFrame":
        return FakePolarsFrame([{column: row[column] for column in columns} for row in self._rows])

    def sort(self, column: str, *, descending: bool = False) -> "FakePolarsFrame":
        return FakePolarsFrame(sorted(self._rows, key=lambda row: row[column], reverse=descending))

    def to_dicts(self) -> list[dict[str, Any]]:
        return [dict(row) for row in self._rows]

    def write_parquet(self, target: Path | str) -> None:
        Path(target).write_text(json.dumps(self._rows, indent=2), encoding="utf-8")


class FakeDuckDBConnection:
    def __init__(self, database_path: Path | str) -> None:
        self.database_path = Path(database_path)
        self.rows: list[dict[str, Any]] = []
        self.statements: list[str] = []

    def __enter__(self) -> "FakeDuckDBConnection":
        return self

    def __exit__(self, _exc_type: object, _exc: object, _tb: object) -> None:
        return None

    def execute(self, statement: str) -> "FakeDuckDBConnection":
        normalized = " ".join(statement.lower().split())
        self.statements.append(normalized)
        if normalized.startswith("insert into report_runs values"):
            self.rows.extend(
                [
                    {"tenant_id": "acme", "report_id": "daily-signups", "total_events": 42},
                    {"tenant_id": "globex", "report_id": "daily-signups", "total_events": 11},
                ]
            )
        return self


def polars_stub_module() -> types.ModuleType:
    module = types.ModuleType("polars")
    module.DataFrame = FakePolarsFrame
    module.when = lambda _value: _FakePolarsExpression()
    module.col = lambda _name: _FakePolarsExpression()
    module.read_database = lambda _query, *, connection: FakePolarsFrame(connection.rows)
    return module


def duckdb_stub_module() -> types.ModuleType:
    module = types.ModuleType("duckdb")
    module.connect = lambda database_path: FakeDuckDBConnection(database_path)
    return module


def fastapi_stub_module() -> types.ModuleType:
    module = types.ModuleType("fastapi")

    class APIRouter:
        def __init__(self, *, prefix: str = "", tags: list[str] | None = None) -> None:
            self.prefix = prefix
            self.tags = tags or []
            self.routes: list[dict[str, Any]] = []

        def get(self, path: str, *, response_model: object | None = None):
            def decorator(func: Any) -> Any:
                self.routes.append(
                    {
                        "path": f"{self.prefix}{path}",
                        "endpoint": func,
                        "response_model": response_model,
                    }
                )
                return func

            return decorator

    class FastAPI:
        def __init__(self) -> None:
            self.routes: list[dict[str, Any]] = []

        def include_router(self, router: APIRouter) -> None:
            self.routes.extend(router.routes)

    module.APIRouter = APIRouter
    module.FastAPI = FastAPI
    module.Depends = lambda dependency: dependency
    module.Query = lambda default=None, **_kwargs: default
    return module


def pydantic_stub_module() -> types.ModuleType:
    module = types.ModuleType("pydantic")

    class BaseModel:
        def __init__(self, **kwargs: Any) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

        def model_dump(self) -> dict[str, Any]:
            return dict(self.__dict__)

    module.BaseModel = BaseModel
    module.Field = lambda default=None, **_kwargs: default
    return module


def python_api_stub_modules() -> dict[str, types.ModuleType]:
    return {
        "dataclasses": compat_dataclasses_module(),
        "fastapi": fastapi_stub_module(),
        "pydantic": pydantic_stub_module(),
        "polars": polars_stub_module(),
    }


def python_data_stub_modules() -> dict[str, types.ModuleType]:
    return {
        "dataclasses": compat_dataclasses_module(),
        "duckdb": duckdb_stub_module(),
        "polars": polars_stub_module(),
    }
