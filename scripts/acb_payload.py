#!/usr/bin/env python3
"""Compose repo-local `.acb/` spec and validation payloads."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from manifest_tools import parse_manifest


SPEC_OUTPUTS = {
    "product": ".acb/specs/PRODUCT.md",
    "architecture": ".acb/specs/ARCHITECTURE.md",
    "agent": ".acb/specs/AGENT_RULES.md",
    "evolution": ".acb/specs/EVOLUTION.md",
    "validation": ".acb/specs/VALIDATION.md",
}

SPEC_TITLES = {
    "product": "Product Spec",
    "architecture": "Architecture Spec",
    "agent": "Agent Behavior Spec",
    "evolution": "Evolution Spec",
    "validation": "Validation Spec",
}

REQUIRED_SOURCE_HEADER_KEYS = {
    "acb_origin",
    "acb_source_path",
    "acb_role",
    "acb_version",
}


@dataclass(frozen=True)
class CanonicalModule:
    path: Path
    metadata: dict[str, object]
    body: str
    sha256: str


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _load_rules() -> dict[str, object]:
    return json.loads((repo_root() / "context/acb/profile-rules.json").read_text(encoding="utf-8"))


def _default_startup_features() -> dict[str, bool]:
    return {
        "budget_report_enabled": False,
        "startup_trace_enabled": False,
        "route_check_enabled": False,
    }


def _startup_features_from_rules(rules: dict[str, object]) -> dict[str, bool]:
    defaults = _default_startup_features()
    configured = rules.get("startup_features")
    if not isinstance(configured, dict):
        return defaults
    merged = defaults.copy()
    for key in defaults:
        if key in configured:
            merged[key] = bool(configured[key])
    return merged


def _enabled_context_tools(startup_features: dict[str, bool]) -> list[str]:
    tools: list[str] = []
    if startup_features.get("budget_report_enabled"):
        tools.append("- Budget scoring: `python3 scripts/work.py budget-report --bundle <files>`")
    if startup_features.get("startup_trace_enabled"):
        tools.append('- Startup trace: `python3 scripts/work.py startup-trace write --session "<task>" --files <files>`')
    if startup_features.get("route_check_enabled"):
        tools.append('- Route check: `python3 scripts/work.py route-check "<prompt>"`')
    return tools


def _unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        normalized = item.strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result


def _existing(paths: list[Path]) -> list[Path]:
    existing: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if not path.exists() or path in seen:
            continue
        seen.add(path)
        existing.append(path)
    return existing


def _parse_header_scalar(raw: str) -> object:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip() for item in inner.split(",") if item.strip()]
    if value.isdigit():
        return int(value)
    return value


def _split_frontmatter(text: str) -> tuple[dict[str, object], str]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        return {}, text.strip()
    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return {}, text.strip()

    metadata: dict[str, object] = {}
    for line in lines[1:closing_index]:
        if not line.strip():
            continue
        key, raw_value = line.split(":", 1)
        metadata[key.strip()] = _parse_header_scalar(raw_value)
    body = "\n".join(lines[closing_index + 1 :]).strip()
    return metadata, body


def _read_canonical_module(path: Path) -> CanonicalModule:
    text = path.read_text(encoding="utf-8")
    metadata, body = _split_frontmatter(text)
    relative_path = path.relative_to(repo_root()).as_posix()
    missing = REQUIRED_SOURCE_HEADER_KEYS.difference(metadata)
    if missing:
        raise ValueError(f"{relative_path} is missing required ACB header keys: {sorted(missing)}")
    if metadata["acb_origin"] != "canonical":
        raise ValueError(f"{relative_path} must declare acb_origin: canonical")
    if metadata["acb_source_path"] != relative_path:
        raise ValueError(
            f"{relative_path} declares acb_source_path={metadata['acb_source_path']!r}, expected {relative_path!r}"
        )
    return CanonicalModule(
        path=path,
        metadata=metadata,
        body=body,
        sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
    )


def _doctrine_slug_from_path(path: str) -> str | None:
    normalized = path.strip()
    if not normalized.startswith("context/doctrine/") or not normalized.endswith(".md"):
        return None
    return Path(normalized).stem


def load_available_manifests() -> dict[str, dict[str, object]]:
    manifests: dict[str, dict[str, object]] = {}
    for path in sorted((repo_root() / "manifests").glob("*.yaml")):
        manifests[path.stem] = parse_manifest(path)
    return manifests


def infer_doctrines(selected_manifests: list[str], manifests: dict[str, dict[str, object]], rules: dict[str, object]) -> list[str]:
    defaults = list(rules.get("default_doctrines", []))
    inferred: list[str] = []
    for manifest_name in selected_manifests:
        manifest = manifests.get(manifest_name, {})
        for key in ("required_context", "optional_context"):
            for item in manifest.get(key, []):  # type: ignore[union-attr]
                if not isinstance(item, str):
                    continue
                slug = _doctrine_slug_from_path(item)
                if slug:
                    inferred.append(slug)
    return _unique([*defaults, *inferred])


def infer_capabilities(
    *,
    archetype: str,
    primary_stack: str,
    selected_manifests: list[str],
    support_services: list[str] | None,
    prompt_first: bool,
    dokku: bool,
    rules: dict[str, object],
) -> list[str]:
    capabilities = list(
        (rules.get("archetype_capabilities", {}) or {}).get(archetype, [])  # type: ignore[union-attr]
    )
    manifest_caps = rules.get("manifest_capabilities", {}) or {}
    for manifest_name in selected_manifests:
        capabilities.extend(manifest_caps.get(manifest_name, []))
    service_caps = rules.get("support_service_capabilities", {}) or {}
    for service in support_services or []:
        capabilities.extend(service_caps.get(service, []))
        capabilities.extend(service_caps.get(service.lower(), []))
    stack_name = primary_stack.lower()
    if "fastapi" in stack_name or "hono" in stack_name or "axum" in stack_name or "echo" in stack_name:
        capabilities.append("api")
    if "qdrant" in stack_name:
        capabilities.extend(["rag", "storage"])
    if prompt_first:
        capabilities.append("cli" if archetype == "cli-tool" else "")
    if dokku:
        capabilities.append("cloud-deployment")
    return _unique(capabilities)


def infer_routers(rules: dict[str, object]) -> list[str]:
    return _unique(list(rules.get("default_routers", [])))


def _spec_path(layer: str, category: str, name: str | None = None) -> Path:
    root = repo_root() / "context/specs" / layer
    if category == "base":
        return root / "base.md"
    return root / category / f"{name}.md"


def _validation_path(category: str, name: str | None = None) -> Path:
    root = repo_root() / "context/validation"
    if category == "base":
        return root / "base.md"
    return root / category / f"{name}.md"


def _build_layer_sources(
    *,
    archetype: str,
    primary_stack: str,
    doctrines: list[str],
    routers: list[str],
    capabilities: list[str],
    rules: dict[str, object],
) -> dict[str, list[Path]]:
    doctrine_map = rules.get("doctrine_module_map", {}) or {}
    layer_sources = {
        "product": _existing(
            [
                _spec_path("product", "base"),
                _spec_path("product", "archetypes", archetype),
            ]
        ),
        "architecture": _existing(
            [
                _spec_path("architecture", "base"),
                _spec_path("architecture", "archetypes", archetype),
                _spec_path("architecture", "stacks", primary_stack),
                *[_spec_path("architecture", "capabilities", capability) for capability in capabilities],
            ]
        ),
        "agent": _existing(
            [
                _spec_path("agent", "base"),
                *[
                    _spec_path("agent", "doctrine", str(doctrine_map.get(doctrine, doctrine)))
                    for doctrine in doctrines
                ],
                *[_spec_path("agent", "routers", router) for router in routers],
            ]
        ),
        "evolution": _existing(
            [
                _spec_path("evolution", "base"),
                _spec_path("evolution", "archetypes", archetype),
            ]
        ),
        "validation": _existing(
            [
                _validation_path("base"),
                _validation_path("archetypes", archetype),
                _validation_path("stacks", primary_stack),
            ]
        ),
    }
    return layer_sources


def _format_metadata_list(values: object, fallback: str = "`all`") -> str:
    if not isinstance(values, list) or not values:
        return fallback
    return ", ".join(f"`{value}`" for value in values)


def _compose_markdown(
    *,
    title: str,
    selection: dict[str, object],
    modules: list[CanonicalModule],
) -> str:
    relative_sources = [module.path.relative_to(repo_root()).as_posix() for module in modules]
    header = [
        f"# {title}",
        "",
        "Generated from canonical agent-context-base modules.",
        "Composition mode: canonical modules are concatenated into one repo-local document, and each module keeps explicit origin metadata below.",
        "",
        "Selection:",
        f"- archetype: `{selection['archetype']}`",
        f"- primary stack: `{selection['primary_stack']}`",
        f"- manifests: {', '.join(f'`{name}`' for name in selection['selected_manifests']) or '`none`'}",
        f"- capabilities: {', '.join(f'`{name}`' for name in selection['capabilities']) or '`none`'}",
        "",
        "Canonical source modules:",
        *[f"- `{path}`" for path in relative_sources],
        "",
    ]
    body: list[str] = []
    for index, module in enumerate(modules):
        if not module.body:
            continue
        if index:
            body.extend(["", "---", ""])
        relative_path = module.path.relative_to(repo_root()).as_posix()
        body.extend(
            [
                f"## Canonical Module: `{relative_path}`",
                "",
                "Origin metadata:",
                f"- role: `{module.metadata['acb_role']}`",
                f"- archetypes: {_format_metadata_list(module.metadata.get('acb_archetypes'))}",
                f"- stacks: {_format_metadata_list(module.metadata.get('acb_stacks'))}",
                f"- doctrines: {_format_metadata_list(module.metadata.get('acb_doctrines'))}",
                f"- routers: {_format_metadata_list(module.metadata.get('acb_routers'))}",
                f"- capabilities: {_format_metadata_list(module.metadata.get('acb_capabilities'))}",
                f"- version: `{module.metadata['acb_version']}`",
                "",
                module.body,
            ]
        )
    return "\n".join(header + body).rstrip() + "\n"


def _validation_gates(
    *,
    archetype: str,
    primary_stack: str,
    capabilities: list[str],
    rules: dict[str, object],
) -> list[dict[str, str]]:
    gates = list(rules.get("default_validation_gates", []))
    gates.extend((rules.get("archetype_validation_gates", {}) or {}).get(archetype, []))
    gates.extend((rules.get("stack_validation_gates", {}) or {}).get(primary_stack, []))
    capability_gates = rules.get("capability_validation_gates", {}) or {}
    for capability in capabilities:
        gates.extend(capability_gates.get(capability, []))

    unique_gates: list[dict[str, str]] = []
    seen: set[str] = set()
    for gate in gates:
        gate_id = str(gate.get("id", "")).strip()
        if not gate_id or gate_id in seen:
            continue
        seen.add(gate_id)
        unique_gates.append(
            {
                "id": gate_id,
                "category": str(gate.get("category", "misc")),
                "summary": str(gate.get("summary", "")).strip(),
                "command_hint": str(gate.get("command_hint", "")).strip(),
            }
        )
    return unique_gates


def _coverage_dimensions(
    *,
    selection: dict[str, object],
    gates: list[dict[str, str]],
) -> list[dict[str, object]]:
    gate_ids = {gate["id"] for gate in gates}
    dimensions: list[dict[str, object]] = []

    def add_dimension(
        dimension_id: str,
        *,
        label: str,
        reason: str,
        evidence_gate_ids: list[str],
    ) -> None:
        matched = [gate_id for gate_id in evidence_gate_ids if gate_id in gate_ids]
        dimensions.append(
            {
                "id": dimension_id,
                "label": label,
                "required": True,
                "reason": reason,
                "covered": bool(matched),
                "evidence_gate_ids": matched,
                "expected_gate_ids": evidence_gate_ids,
            }
        )

    capability_map = {
        "api": ("API surface", ["api-smoke", "api-contract-check", "fastapi-health-and-shape", "hono-route-behavior", "echo-handler-behavior"]),
        "cli": ("CLI surface", ["cli-contract", "cli-operator-sanity"]),
        "storage": ("Storage and persistence", ["storage-roundtrip", "schema-and-data-integrity"]),
        "frontend": ("UI or fragment behavior", ["frontend-behavior"]),
        "pipelines": ("Pipeline execution", ["pipeline-fixture-run"]),
        "workers": ("Worker execution", ["worker-readiness"]),
        "scraping": ("Source fetch and normalization", ["source-normalization", "ingestion-smoke", "idempotent-replay"]),
        "eventing": ("Event flow and durability", ["event-flow", "event-or-checkpoint-durability", "cross-source-sync", "seam-contract"]),
        "rag": ("Retrieval and indexing", ["retrieval-sanity"]),
        "cloud-deployment": ("Deployment readiness", ["deploy-readiness"]),
    }
    for capability in selection["capabilities"]:
        if capability not in capability_map:
            continue
        label, expected = capability_map[capability]
        add_dimension(
            capability.replace("frontend", "ui"),
            label=label,
            reason=f"Capability `{capability}` is active in the repo-local profile.",
            evidence_gate_ids=expected,
        )

    archetype = str(selection["archetype"])
    if archetype == "data-acquisition-service":
        add_dimension(
            "ingestion-replay",
            label="Ingestion and replay safety",
            reason="Data acquisition repos need both fetch-to-persist proof and replay safety visibility.",
            evidence_gate_ids=["ingestion-smoke", "idempotent-replay"],
        )
    if archetype == "multi-backend-service":
        add_dimension(
            "service-seam",
            label="Cross-service seam contract",
            reason="Multi-backend repos need one real seam proof across services.",
            evidence_gate_ids=["seam-contract"],
        )
    if archetype == "multi-source-sync-platform":
        add_dimension(
            "sync-orchestration",
            label="Cross-source sync orchestration",
            reason="Multi-source sync repos need orchestration and durability proof.",
            evidence_gate_ids=["cross-source-sync", "event-or-checkpoint-durability"],
        )
    if selection.get("primary_stack") == "prompt-first-repo":
        add_dimension(
            "startup-profile",
            label="Prompt and startup profile integrity",
            reason="Prompt-first repos must reload cleanly in future sessions.",
            evidence_gate_ids=["prompt-sequence-integrity"],
        )

    return dimensions


def _build_coverage_report(
    *,
    selection: dict[str, object],
    gates: list[dict[str, str]],
) -> dict[str, object]:
    spec_documents = []
    for layer, path in SPEC_OUTPUTS.items():
        spec_documents.append(
            {
                "id": layer,
                "path": path,
                "required": True,
                "present": True,
            }
        )
    dimensions = _coverage_dimensions(selection=selection, gates=gates)
    missing_dimensions = [dimension["id"] for dimension in dimensions if not dimension["covered"]]
    return {
        "schema_version": 1,
        "selection": selection,
        "spec_documents": spec_documents,
        "validation_dimensions": dimensions,
        "summary": {
            "required_spec_documents": len(spec_documents),
            "present_spec_documents": len(spec_documents),
            "required_validation_dimensions": len(dimensions),
            "covered_validation_dimensions": len(dimensions) - len(missing_dimensions),
            "missing_validation_dimensions": missing_dimensions,
        },
    }


def _render_validation_checklist(selection: dict[str, object], gates: list[dict[str, str]]) -> str:
    lines = [
        "# Validation Checklist",
        "",
        "This checklist is the autonomy rail for repo-local work. Agents should finish coding only after the relevant checks below were executed or explicitly deferred.",
        "",
        f"- Archetype: `{selection['archetype']}`",
        f"- Primary stack: `{selection['primary_stack']}`",
        f"- Capabilities: {', '.join(f'`{name}`' for name in selection['capabilities']) or '`none`'}",
        "",
    ]
    for gate in gates:
        lines.extend(
            [
                f"## {gate['id']}",
                "",
                f"- Category: `{gate['category']}`",
                f"- Required truth: {gate['summary']}",
                f"- Proof hint: {gate['command_hint']}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_coverage_markdown(coverage: dict[str, object]) -> str:
    lines = [
        "# Validation Coverage",
        "",
        "Coverage is a visibility aid, not a claim of completeness. It shows which validation dimensions the current repo-local profile expects and whether the generated validation gates cover them.",
        "",
        "## Spec Documents",
        "",
    ]
    for spec_doc in coverage["spec_documents"]:
        status = "present" if spec_doc["present"] else "missing"
        lines.append(f"- `{spec_doc['id']}`: {status} via `{spec_doc['path']}`")
    lines.extend(["", "## Validation Dimensions", ""])
    for dimension in coverage["validation_dimensions"]:
        status = "covered" if dimension["covered"] else "gap"
        evidence = (
            ", ".join(f"`{gate_id}`" for gate_id in dimension["evidence_gate_ids"])
            if dimension["evidence_gate_ids"]
            else "`none found`"
        )
        lines.extend(
            [
                f"### {dimension['label']}",
                "",
                f"- Status: `{status}`",
                f"- Reason: {dimension['reason']}",
                f"- Evidence gates: {evidence}",
                "",
            ]
        )
    missing = coverage["summary"]["missing_validation_dimensions"]
    lines.extend(
        [
            "## Gaps",
            "",
            (
                "- No required validation dimensions are currently uncovered."
                if not missing
                else f"- Missing dimensions: {', '.join(f'`{item}`' for item in missing)}"
            ),
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def _render_doctrine_summary(doctrines: list[str]) -> str:
    lines = [
        "# Active Doctrines",
        "",
        "These doctrine slugs were selected into the local autonomy profile. Use the vendored files under `.acb/context/doctrine/` when present as the repo-local source copies.",
        "",
    ]
    for doctrine in doctrines:
        lines.append(f"- `{doctrine}`")
    lines.append("")
    return "\n".join(lines)


def _render_router_summary(routers: list[str], selection: dict[str, object]) -> str:
    lines = [
        "# Router Hints",
        "",
        "Routers remain small by design. They help a future session decide what to read first without loading a giant universal spec.",
        "",
        "Recommended order:",
        "- `task-router`: identify the active workflow and changed boundary",
        "- `stack-router`: confirm the active implementation surface",
        "- `archetype-router`: confirm repo shape and constraints",
        "- `repo-signal-hints`: reconcile the current file tree with the intended profile",
        "",
        "Selected routers:",
    ]
    lines.extend(f"- `{router}`" for router in routers)
    lines.extend(
        [
            "",
            "Current selection:",
            f"- archetype: `{selection['archetype']}`",
            f"- primary stack: `{selection['primary_stack']}`",
            "",
        ]
    )
    return "\n".join(lines)


def _render_session_boot(selection: dict[str, object], key_paths: dict[str, str]) -> str:
    startup_features = selection.get("startup_features")
    if not isinstance(startup_features, dict):
        startup_features = _default_startup_features()
    context_tools = _enabled_context_tools(startup_features)
    lines = [
        "# Session Boot",
        "",
        "Read these files first when starting or resuming work in the generated repo:",
        "",
        "1. `AGENT.md`",
        "2. `CLAUDE.md`",
        f"3. `{key_paths['selection_path']}`",
        f"4. `{SPEC_OUTPUTS['agent']}`",
        f"5. `{SPEC_OUTPUTS['validation']}`",
        f"6. `{key_paths['checklist_path']}`",
        f"7. `{key_paths['coverage_path']}`",
        "8. `.acb/generation-report.json`",
        "9. `.prompts/*.txt` if present",
        "",
        "Operator rhythm:",
        "1. Rehydrate the local profile and constraints at session start. Do not assume prior memory is still current.",
        "2. Pick one workflow, one active stack surface, and one validation path.",
        "3. Implement a narrow slice.",
        "4. Run the required validation gates before claiming completion.",
        "5. If validation is blocked, say blocked; if work remains, say incomplete; use done only after proof ran.",
        "6. Refresh continuity notes when the working truth changed.",
        "",
        "Context model:",
        f"- archetype: `{selection['archetype']}`",
        f"- primary stack: `{selection['primary_stack']}`",
        f"- capabilities: {', '.join(f'`{name}`' for name in selection['capabilities']) or '`none`'}",
        "",
    ]
    if context_tools:
        lines.extend(
            [
                "## Context Tools",
                "",
                *context_tools,
                "",
            ]
        )
    return "\n".join(lines)


def _render_acb_readme(selection: dict[str, object], key_paths: dict[str, str]) -> str:
    return "\n".join(
        [
            "# Repo-Local ACB Payload",
            "",
            "This hidden directory is the repo-local operating context payload synthesized from agent-context-base.",
            "",
            "Primary files:",
            f"- `{key_paths['session_boot_path']}`",
            f"- `{key_paths['selection_path']}`",
            f"- `{SPEC_OUTPUTS['product']}`",
            f"- `{SPEC_OUTPUTS['architecture']}`",
            f"- `{SPEC_OUTPUTS['agent']}`",
            f"- `{SPEC_OUTPUTS['validation']}`",
            f"- `{SPEC_OUTPUTS['evolution']}`",
            f"- `{key_paths['checklist_path']}`",
            f"- `{key_paths['coverage_path']}`",
            f"- `{key_paths['index_path']}`",
            "",
            "Purpose:",
            "- keep future assistant sessions repo-local and resumable",
            "- make autonomy bounded by explicit specs and validation gates",
            "- preserve the canonical source lineage for drift-aware future tooling",
            "- make local payload drift and coverage gaps visible with lightweight tooling",
            "",
            "Helpful commands:",
            "- `python .acb/scripts/acb_inspect.py`",
            "- `python .acb/scripts/acb_verify.py`",
            "",
            f"Selected manifests: {', '.join(f'`{name}`' for name in selection['selected_manifests']) or '`none`'}",
            "",
        ]
    )


def build_payload(
    *,
    archetype: str,
    primary_stack: str,
    selected_manifests: list[str],
    manifests: dict[str, dict[str, object]],
    support_services: list[str] | None = None,
    prompt_first: bool = False,
    dokku: bool = False,
) -> tuple[dict[str, str], dict[str, object]]:
    rules = _load_rules()
    doctrines = infer_doctrines(selected_manifests, manifests, rules)
    capabilities = infer_capabilities(
        archetype=archetype,
        primary_stack=primary_stack,
        selected_manifests=selected_manifests,
        support_services=support_services,
        prompt_first=prompt_first,
        dokku=dokku,
        rules=rules,
    )
    routers = infer_routers(rules)
    startup_features = _startup_features_from_rules(rules)
    selection = {
        "schema_version": 1,
        "archetype": archetype,
        "primary_stack": primary_stack,
        "selected_manifests": selected_manifests,
        "doctrines": doctrines,
        "routers": routers,
        "capabilities": capabilities,
        "support_services": support_services or [],
        "prompt_first": prompt_first,
        "dokku": dokku,
        "startup_features": startup_features,
    }
    layer_sources = _build_layer_sources(
        archetype=archetype,
        primary_stack=primary_stack,
        doctrines=doctrines,
        routers=routers,
        capabilities=capabilities,
        rules=rules,
    )
    layer_modules = {
        layer: [_read_canonical_module(path) for path in sources]
        for layer, sources in layer_sources.items()
    }
    gates = _validation_gates(
        archetype=archetype,
        primary_stack=primary_stack,
        capabilities=capabilities,
        rules=rules,
    )
    coverage = _build_coverage_report(selection=selection, gates=gates)
    key_paths = {
        "session_boot_path": ".acb/SESSION_BOOT.md",
        "selection_path": ".acb/profile/selection.json",
        "checklist_path": ".acb/validation/CHECKLIST.md",
        "coverage_path": ".acb/validation/COVERAGE.md",
        "index_path": ".acb/INDEX.json",
    }
    files = {
        ".acb/README.md": _render_acb_readme(selection, key_paths),
        ".acb/SESSION_BOOT.md": _render_session_boot(selection, key_paths),
        ".acb/profile/selection.json": json.dumps(selection, indent=2) + "\n",
        ".acb/routers/README.md": _render_router_summary(routers, selection),
        ".acb/doctrines/ACTIVE_DOCTRINES.md": _render_doctrine_summary(doctrines),
        ".acb/validation/CHECKLIST.md": _render_validation_checklist(selection, gates),
        ".acb/validation/MATRIX.json": json.dumps(
            {
                "schema_version": 1,
                "selection": selection,
                "validation_gates": gates,
            },
            indent=2,
        )
        + "\n",
        ".acb/validation/COVERAGE.md": _render_coverage_markdown(coverage),
        ".acb/validation/COVERAGE.json": json.dumps(coverage, indent=2) + "\n",
    }
    files.update(
        {
            SPEC_OUTPUTS[layer]: _compose_markdown(
                title=SPEC_TITLES[layer],
                selection=selection,
                modules=modules,
            )
            for layer, modules in layer_modules.items()
        }
    )
    generated_file_hashes = {
        relative_path: hashlib.sha256(content.encode("utf-8")).hexdigest()
        for relative_path, content in files.items()
    }
    index = {
        "schema_version": 1,
        "selection": selection,
        "generated_files": sorted([*files, ".acb/INDEX.json"]),
        "generated_file_hashes": generated_file_hashes,
        "source_modules": {
            layer: [
                {
                    "source": module.path.relative_to(repo_root()).as_posix(),
                    "sha256": module.sha256,
                    "target": SPEC_OUTPUTS[layer],
                    "target_role": layer,
                    "composition_mode": "concatenated-into-generated-spec",
                    "metadata": module.metadata,
                }
                for module in modules
            ]
            for layer, modules in layer_modules.items()
        },
        "layer_sources": {
            layer: [module.path.relative_to(repo_root()).as_posix() for module in modules]
            for layer, modules in layer_modules.items()
        },
        "router_summary_path": ".acb/routers/README.md",
        "doctrine_summary_path": ".acb/doctrines/ACTIVE_DOCTRINES.md",
        "validation_checklist_path": ".acb/validation/CHECKLIST.md",
        "validation_coverage_paths": [
            ".acb/validation/COVERAGE.md",
            ".acb/validation/COVERAGE.json",
        ],
        "selection_manifest_path": ".acb/profile/selection.json",
        "session_boot_path": ".acb/SESSION_BOOT.md",
        "drift_detection": {
            "local_payload_hash_mode": "compare generated_file_hashes against on-disk `.acb/` files",
            "canonical_source_hash_mode": "compare source_modules[*].sha256 against the current canonical source tree when available",
        },
    }
    files[".acb/INDEX.json"] = json.dumps(index, indent=2) + "\n"
    metadata = {
        "version": 1,
        "selection_manifest_path": ".acb/profile/selection.json",
        "session_boot_path": ".acb/SESSION_BOOT.md",
        "index_path": ".acb/INDEX.json",
        "coverage_paths": [
            ".acb/validation/COVERAGE.md",
            ".acb/validation/COVERAGE.json",
        ],
        "spec_paths": [SPEC_OUTPUTS[layer] for layer in ("product", "architecture", "agent", "validation", "evolution")],
        "validation_paths": [
            ".acb/validation/CHECKLIST.md",
            ".acb/validation/MATRIX.json",
            ".acb/validation/COVERAGE.md",
            ".acb/validation/COVERAGE.json",
        ],
        "router_paths": [".acb/routers/README.md"],
        "doctrine_paths": [".acb/doctrines/ACTIVE_DOCTRINES.md"],
    }
    return files, metadata


def _write_files(target_dir: Path, files: dict[str, str]) -> None:
    for relative_path, content in sorted(files.items()):
        destination = target_dir / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compose a repo-local `.acb/` payload.")
    parser.add_argument("--archetype", required=True)
    parser.add_argument("--primary-stack", required=True)
    parser.add_argument("--manifest", action="append", dest="manifests", default=[])
    parser.add_argument("--support-service", action="append", dest="support_services", default=[])
    parser.add_argument("--output-dir", required=True, help="Repo root where `.acb/` should be written.")
    parser.add_argument("--prompt-first", action="store_true")
    parser.add_argument("--dokku", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manifests = load_available_manifests()
    files, metadata = build_payload(
        archetype=args.archetype,
        primary_stack=args.primary_stack,
        selected_manifests=args.manifests,
        manifests=manifests,
        support_services=args.support_services,
        prompt_first=args.prompt_first,
        dokku=args.dokku,
    )
    if args.dry_run:
        print(json.dumps({"files": sorted(files), "metadata": metadata}, indent=2))
        return 0
    _write_files(Path(args.output_dir), files)
    print(f"Wrote {len(files)} files under {Path(args.output_dir) / '.acb'}")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
