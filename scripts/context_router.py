from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class KeywordCapabilityRule:
    keyword: str
    capabilities: tuple[str, ...]


@dataclass(frozen=True)
class ManifestMetadata:
    name: str
    archetype: str | None
    primary_stack: str | None
    secondary_stacks: tuple[str, ...]
    triggers: tuple[str, ...]
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class RouteInference:
    implied_capabilities: tuple[str, ...]
    candidate_archetypes: tuple[str, ...]
    candidate_manifests: tuple[str, ...]
    primary_archetype: str | None
    primary_manifest: str | None
    is_multi_capability: bool
    is_likely_juicy: bool
    suggested_budget_profile: str
    confidence: float
    warnings: tuple[str, ...]
    keyword_hits: dict[str, list[str]]


KEYWORD_CAPABILITY_RULES: tuple[KeywordCapabilityRule, ...] = (
    KeywordCapabilityRule("fastapi", ("api",)),
    KeywordCapabilityRule("flask", ("api",)),
    KeywordCapabilityRule("django", ("api",)),
    KeywordCapabilityRule("api", ("api",)),
    KeywordCapabilityRule("endpoint", ("api",)),
    KeywordCapabilityRule("route", ("api",)),
    KeywordCapabilityRule("postgres", ("storage",)),
    KeywordCapabilityRule("postgresql", ("storage",)),
    KeywordCapabilityRule("mysql", ("storage",)),
    KeywordCapabilityRule("sqlite", ("storage",)),
    KeywordCapabilityRule("database", ("storage",)),
    KeywordCapabilityRule("schema", ("storage",)),
    KeywordCapabilityRule("redis", ("storage",)),
    KeywordCapabilityRule("keydb", ("storage",)),
    KeywordCapabilityRule("cache", ("storage",)),
    KeywordCapabilityRule("caching", ("storage",)),
    KeywordCapabilityRule("duckdb", ("storage",)),
    KeywordCapabilityRule("polars", ("storage",)),
    KeywordCapabilityRule("parquet", ("storage",)),
    KeywordCapabilityRule("dataframe", ("storage",)),
    KeywordCapabilityRule("qdrant", ("rag", "search")),
    KeywordCapabilityRule("meilisearch", ("rag", "search")),
    KeywordCapabilityRule("vector", ("rag", "search")),
    KeywordCapabilityRule("embedding", ("rag", "search")),
    KeywordCapabilityRule("rag", ("rag", "search")),
    KeywordCapabilityRule("search", ("rag", "search")),
    KeywordCapabilityRule("celery", ("workers",)),
    KeywordCapabilityRule("worker", ("workers",)),
    KeywordCapabilityRule("queue", ("workers",)),
    KeywordCapabilityRule("background task", ("workers",)),
    KeywordCapabilityRule("schedule", ("workers",)),
    KeywordCapabilityRule("scheduler", ("workers",)),
    KeywordCapabilityRule("kafka", ("eventing",)),
    KeywordCapabilityRule("rabbitmq", ("eventing",)),
    KeywordCapabilityRule("event", ("eventing",)),
    KeywordCapabilityRule("stream", ("eventing",)),
    KeywordCapabilityRule("pubsub", ("eventing",)),
    KeywordCapabilityRule("pipeline", ("pipelines",)),
    KeywordCapabilityRule("etl", ("pipelines",)),
    KeywordCapabilityRule("transform", ("pipelines",)),
    KeywordCapabilityRule("transforms", ("pipelines",)),
    KeywordCapabilityRule("ingest", ("pipelines",)),
    KeywordCapabilityRule("scrape", ("scraping",)),
    KeywordCapabilityRule("scrapes", ("scraping",)),
    KeywordCapabilityRule("scraping", ("scraping",)),
    KeywordCapabilityRule("crawler", ("scraping",)),
    KeywordCapabilityRule("crawl", ("scraping",)),
    KeywordCapabilityRule("fetch", ("scraping",)),
    KeywordCapabilityRule("dokku", ("cloud-deployment",)),
    KeywordCapabilityRule("deploy", ("cloud-deployment",)),
    KeywordCapabilityRule("deployment", ("cloud-deployment",)),
    KeywordCapabilityRule("heroku", ("cloud-deployment",)),
    KeywordCapabilityRule("production", ("cloud-deployment",)),
    KeywordCapabilityRule("cli", ("cli",)),
    KeywordCapabilityRule("command line", ("cli",)),
    KeywordCapabilityRule("typer", ("cli",)),
    KeywordCapabilityRule("click", ("cli",)),
    KeywordCapabilityRule("argparse", ("cli",)),
    KeywordCapabilityRule("tui", ("cli",)),
    KeywordCapabilityRule("textual", ("cli",)),
    KeywordCapabilityRule("rich", ("cli",)),
    KeywordCapabilityRule("terminal ui", ("cli",)),
    KeywordCapabilityRule("smoke test", ("verification",)),
    KeywordCapabilityRule("integration test", ("verification",)),
    KeywordCapabilityRule("pytest", ("verification",)),
    KeywordCapabilityRule("test", ("verification",)),
)

CAPABILITY_WORKFLOW_MAP: dict[str, tuple[str, ...]] = {
    "api": ("context/workflows/add-api-endpoint.md",),
    "storage": ("context/workflows/add-storage-integration.md",),
    "rag": ("context/workflows/add-local-rag-indexing.md",),
    "search": ("context/workflows/add-local-rag-indexing.md",),
    "workers": ("context/workflows/add-recurring-sync.md",),
    "eventing": ("context/workflows/add-event-driven-sync.md",),
    "pipelines": ("context/workflows/add-parser-normalizer.md",),
    "scraping": ("context/workflows/add-scraping-source.md",),
    "cloud-deployment": ("context/workflows/add-deployment-support.md",),
    "cli": ("context/workflows/extend-cli.md",),
    "verification": ("context/workflows/add-smoke-tests.md",),
}

KEYWORD_STACK_HINTS: dict[str, str] = {
    "fastapi": "context/stacks/python-fastapi-uv-ruff-orjson-polars.md",
    "qdrant": "context/stacks/qdrant.md",
    "meilisearch": "context/stacks/meilisearch.md",
    "postgres": "context/stacks/postgresql.md",
    "postgresql": "context/stacks/postgresql.md",
    "redis": "context/stacks/redis.md",
    "duckdb": "context/stacks/duckdb-trino-polars.md",
    "polars": "context/stacks/duckdb-trino-polars.md",
    "dokku": "context/stacks/dokku-conventions.md",
    "scrape": "context/stacks/scraping-and-ingestion-patterns.md",
    "scraping": "context/stacks/scraping-and-ingestion-patterns.md",
    "kafka": "context/stacks/kafka.md",
    "rabbitmq": "context/stacks/rabbitmq.md",
}

DOMAIN_CAPABILITIES: dict[str, set[str]] = {
    "data-domain": {"storage", "rag", "pipelines", "search"},
    "infra-domain": {"workers", "eventing", "cloud-deployment"},
    "interface-domain": {"api", "cli"},
    "quality-domain": {"verification"},
}

CAPABILITY_PRIORITY: dict[str, int] = {
    "api": 0,
    "storage": 1,
    "rag": 2,
    "search": 3,
    "pipelines": 4,
    "scraping": 5,
    "workers": 6,
    "eventing": 7,
    "cloud-deployment": 8,
    "cli": 9,
    "verification": 10,
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _profile_rules(repo_root: Path) -> dict[str, Any]:
    return _read_json(repo_root / "context" / "acb" / "profile-rules.json")


def _support_service_capabilities(repo_root: Path) -> dict[str, list[str]]:
    mapping = _profile_rules(repo_root).get("support_service_capabilities", {})
    return {
        str(service).lower(): [str(capability) for capability in capabilities]
        for service, capabilities in mapping.items()
    }


def load_capability_to_archetype_map(repo_root: Path) -> dict[str, list[str]]:
    mapping = _profile_rules(repo_root).get("archetype_capabilities", {})
    inverted: dict[str, list[str]] = {}
    for archetype, capabilities in mapping.items():
        for capability in capabilities:
            inverted.setdefault(capability, []).append(archetype)
    return {key: sorted(values) for key, values in inverted.items()}


def load_capability_to_manifest_map(repo_root: Path) -> dict[str, list[str]]:
    mapping = _profile_rules(repo_root).get("manifest_capabilities", {})
    inverted: dict[str, list[str]] = {}
    for manifest, capabilities in mapping.items():
        for capability in capabilities:
            inverted.setdefault(capability, []).append(manifest)
    return {key: sorted(values) for key, values in inverted.items()}


def _keyword_pattern(keyword: str) -> re.Pattern[str]:
    if re.search(r"[^a-z0-9 ]", keyword):
        return re.compile(re.escape(keyword), flags=re.IGNORECASE)
    parts = [re.escape(part) for part in keyword.split()]
    return re.compile(r"\b" + r"\s+".join(parts) + r"\b", flags=re.IGNORECASE)


def _normalize_prompt(prompt_text: str) -> str:
    return " ".join(prompt_text.lower().split())


def _tokenize_prompt(prompt_text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", prompt_text.lower()))


def _ordered_capabilities(capabilities: set[str]) -> tuple[str, ...]:
    return tuple(sorted(capabilities, key=lambda item: (CAPABILITY_PRIORITY.get(item, 999), item)))


def _load_manifest_metadata(path: Path) -> ManifestMetadata:
    scalar_fields = {"name", "archetype", "primary_stack"}
    list_fields = {"secondary_stacks", "triggers", "aliases"}
    scalars: dict[str, str] = {}
    lists: dict[str, list[str]] = {field: [] for field in list_fields}
    active_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - ") and active_list is not None:
            lists[active_list].append(stripped[2:].strip())
            continue
        if line.startswith("  "):
            continue
        if ":" not in stripped:
            active_list = None
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if key in scalar_fields:
            scalars[key] = value or ""
            active_list = None
        elif key in list_fields:
            active_list = key
            if value:
                lists[key].append(value)
        else:
            active_list = None

    name = scalars.get("name") or path.stem
    return ManifestMetadata(
        name=name,
        archetype=scalars.get("archetype") or None,
        primary_stack=scalars.get("primary_stack") or None,
        secondary_stacks=tuple(lists["secondary_stacks"]),
        triggers=tuple(lists["triggers"]),
        aliases=tuple(lists["aliases"]),
    )


def _load_all_manifest_metadata(repo_root: Path) -> dict[str, ManifestMetadata]:
    manifests_dir = repo_root / "manifests"
    metadata: dict[str, ManifestMetadata] = {}
    if not manifests_dir.exists():
        return metadata
    for path in sorted(manifests_dir.glob("*.yaml")):
        manifest = _load_manifest_metadata(path)
        metadata[manifest.name] = manifest
    return metadata


def _collect_keyword_hits(prompt_text: str) -> dict[str, list[str]]:
    hits: dict[str, list[str]] = {}
    for rule in KEYWORD_CAPABILITY_RULES:
        if _keyword_pattern(rule.keyword).search(prompt_text):
            hits[rule.keyword] = list(rule.capabilities)
    return hits


def _rank_candidates(
    capability_map: dict[str, list[str]],
    implied_capabilities: tuple[str, ...],
    prompt_tokens: set[str],
    prompt_text: str,
    extras: dict[str, tuple[str, ...]] | None = None,
) -> tuple[str, ...]:
    scores: dict[str, float] = {}
    for capability in implied_capabilities:
        for candidate in capability_map.get(capability, []):
            scores[candidate] = scores.get(candidate, 0.0) + 1.0

    extras = extras or {}
    for candidate, terms in extras.items():
        bonus = 0.0
        candidate_tokens = set(candidate.replace("-", " ").split())
        if candidate_tokens & prompt_tokens:
            bonus += 0.35 * len(candidate_tokens & prompt_tokens)
        for term in terms:
            normalized = term.strip().lower()
            if not normalized:
                continue
            if normalized in prompt_text:
                bonus += 0.75
        if bonus:
            scores[candidate] = scores.get(candidate, 0.0) + bonus

    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return tuple(candidate for candidate, score in ordered if score > 0)


def _detected_domains(capabilities: tuple[str, ...]) -> set[str]:
    detected: set[str] = set()
    for domain, domain_capabilities in DOMAIN_CAPABILITIES.items():
        if any(capability in domain_capabilities for capability in capabilities):
            detected.add(domain)
    return detected


def _is_multi_backend_comparison(prompt_text: str, keyword_hits: dict[str, list[str]]) -> bool:
    normalized = f" {_normalize_prompt(prompt_text)} "
    comparison_terms = (" compare ", " versus ", " vs ", "same dataset", " latency ")
    has_comparison = any(term in normalized for term in comparison_terms)
    backend_terms = {"qdrant", "meilisearch", "postgres", "mysql", "sqlite", "redis", "duckdb"}
    matched_backends = [keyword for keyword in keyword_hits if keyword in backend_terms]
    return has_comparison and len(matched_backends) >= 2


def _budget_profile_for(
    capabilities: tuple[str, ...],
    *,
    is_likely_juicy: bool,
    multi_backend_comparison: bool,
    domain_count: int,
    keyword_hit_count: int,
) -> str:
    capability_count = len(capabilities)
    if capability_count == 0:
        return "tiny"
    if capability_count >= 5:
        return "cross-system"
    if capability_count >= 4:
        return "cross-system" if "cloud-deployment" in capabilities else "large"
    if multi_backend_comparison:
        return "large"
    if capability_count == 3:
        return "large" if is_likely_juicy or domain_count >= 3 else "medium"
    if capability_count == 2:
        return "medium" if domain_count >= 2 or keyword_hit_count >= 4 else "small"
    return "small" if keyword_hit_count >= 2 else "tiny"


def _confidence_for(
    capabilities: tuple[str, ...],
    keyword_hit_count: int,
    *,
    is_multi_backend_comparison: bool,
) -> float:
    capability_count = max(1, len(capabilities))
    consistency_ratio = keyword_hit_count / capability_count
    if keyword_hit_count >= 5 and consistency_ratio >= 1.5:
        confidence = 0.9
    elif keyword_hit_count >= 3:
        confidence = 0.76
    elif keyword_hit_count >= 1:
        confidence = 0.6
    else:
        confidence = 0.45
    if is_multi_backend_comparison:
        confidence = max(0.7, min(confidence, 0.79))
    return round(confidence, 2)


def infer_route(prompt_text: str, repo_root: Path) -> RouteInference:
    normalized_prompt = _normalize_prompt(prompt_text)
    prompt_tokens = _tokenize_prompt(prompt_text)
    keyword_hits = _collect_keyword_hits(normalized_prompt)

    capabilities: set[str] = set()
    for matched_capabilities in keyword_hits.values():
        capabilities.update(matched_capabilities)
    support_capabilities = _support_service_capabilities(repo_root)
    for keyword in keyword_hits:
        capabilities.update(support_capabilities.get(keyword, ()))
    implied_capabilities = _ordered_capabilities(capabilities)

    capability_to_archetype = load_capability_to_archetype_map(repo_root)
    capability_to_manifest = load_capability_to_manifest_map(repo_root)
    manifest_metadata = _load_all_manifest_metadata(repo_root)

    manifest_extras = {
        name: tuple(
            list(metadata.aliases)
            + list(metadata.triggers)
            + ([metadata.primary_stack] if metadata.primary_stack else [])
            + ([metadata.archetype] if metadata.archetype else [])
        )
        for name, metadata in manifest_metadata.items()
    }
    candidate_archetypes = _rank_candidates(
        capability_to_archetype,
        implied_capabilities,
        prompt_tokens,
        normalized_prompt,
    )
    candidate_manifests = _rank_candidates(
        capability_to_manifest,
        implied_capabilities,
        prompt_tokens,
        normalized_prompt,
        extras=manifest_extras,
    )

    multi_backend_comparison = _is_multi_backend_comparison(normalized_prompt, keyword_hits)
    detected_domains = _detected_domains(implied_capabilities)
    has_interface = "interface-domain" in detected_domains
    has_data = "data-domain" in detected_domains
    has_cloud = "cloud-deployment" in implied_capabilities
    is_likely_juicy = len(detected_domains) >= 3 or (has_data and has_interface and has_cloud) or multi_backend_comparison
    confidence = _confidence_for(
        implied_capabilities,
        len(keyword_hits),
        is_multi_backend_comparison=multi_backend_comparison,
    )

    warnings: list[str] = []
    if not keyword_hits:
        warnings.append("no keyword hits detected; route is highly ambiguous")
    if len(implied_capabilities) >= 4:
        warnings.append(f"{len(implied_capabilities)} capabilities implied - expect a large context budget")
    if multi_backend_comparison:
        warnings.append("multi-backend comparison; cross-system profile may be appropriate")
    if has_cloud:
        warnings.append("cloud-deployment capability requires an explicit trigger")
    if not candidate_manifests:
        warnings.append("no manifest scored above zero; rely on archetype and workflow heuristics")

    return RouteInference(
        implied_capabilities=implied_capabilities,
        candidate_archetypes=candidate_archetypes,
        candidate_manifests=candidate_manifests,
        primary_archetype=candidate_archetypes[0] if candidate_archetypes else None,
        primary_manifest=candidate_manifests[0] if candidate_manifests else None,
        is_multi_capability=len(implied_capabilities) >= 3,
        is_likely_juicy=is_likely_juicy,
        suggested_budget_profile=_budget_profile_for(
            implied_capabilities,
            is_likely_juicy=is_likely_juicy,
            multi_backend_comparison=multi_backend_comparison,
            domain_count=len(detected_domains),
            keyword_hit_count=len(keyword_hits),
        ),
        confidence=confidence,
        warnings=tuple(warnings),
        keyword_hits={keyword: sorted(capabilities) for keyword, capabilities in keyword_hits.items()},
    )


def _append_if_exists(paths: list[str], seen: set[str], repo_root: Path, relative_path: str) -> None:
    normalized = relative_path.replace("\\", "/")
    if normalized in seen:
        return
    if (repo_root / normalized).exists():
        seen.add(normalized)
        paths.append(normalized)


def suggest_context_bundle(inference: RouteInference, repo_root: Path) -> list[str]:
    bundle: list[str] = []
    seen: set[str] = set()
    _append_if_exists(bundle, seen, repo_root, "AGENT.md")
    _append_if_exists(bundle, seen, repo_root, "context/doctrine/context-complexity-budget.md")

    manifest_metadata = _load_all_manifest_metadata(repo_root)
    metadata = manifest_metadata.get(inference.primary_manifest or "")

    if inference.primary_manifest is not None:
        _append_if_exists(bundle, seen, repo_root, f"manifests/{inference.primary_manifest}.yaml")
    if inference.primary_archetype is not None:
        _append_if_exists(bundle, seen, repo_root, f"context/archetypes/{inference.primary_archetype}.md")

    for capability in inference.implied_capabilities:
        for workflow_path in CAPABILITY_WORKFLOW_MAP.get(capability, ()):
            _append_if_exists(bundle, seen, repo_root, workflow_path)

    if "cloud-deployment" in inference.implied_capabilities:
        _append_if_exists(bundle, seen, repo_root, "context/doctrine/deployment-philosophy-dokku.md")

    stack_candidates: list[str] = []
    if metadata is not None:
        if metadata.primary_stack is not None:
            stack_candidates.append(f"context/stacks/{metadata.primary_stack}.md")
        for stack_name in metadata.secondary_stacks:
            stack_candidates.append(f"context/stacks/{stack_name}.md")

    for keyword in inference.keyword_hits:
        stack_path = KEYWORD_STACK_HINTS.get(keyword)
        if stack_path is not None:
            stack_candidates.append(stack_path)

    added_stacks = 0
    for stack_path in stack_candidates:
        if added_stacks >= 2:
            break
        before = len(bundle)
        _append_if_exists(bundle, seen, repo_root, stack_path)
        if len(bundle) > before:
            added_stacks += 1

    return bundle


def route_inference_payload(inference: RouteInference, repo_root: Path) -> dict[str, Any]:
    payload = asdict(inference)
    payload["heuristic"] = True
    payload["label"] = "HEURISTIC"
    payload["suggested_context_bundle"] = suggest_context_bundle(inference, repo_root)
    return payload
