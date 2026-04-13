from __future__ import annotations

import importlib.util
import sys
from dataclasses import replace
from pathlib import Path


def _load_domain_module():
    module_path = Path(__file__).resolve().parent.parent / "domain" / "generation_patterns.py"
    spec = importlib.util.spec_from_file_location(
        "canonical_faker_domain_generation_patterns", module_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load domain module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(spec.name, module)
    spec.loader.exec_module(module)
    return module


_DOMAIN = _load_domain_module()
Profile = _DOMAIN.Profile


PROFILE_FACTORIES = {
    "smoke": Profile.SMOKE,
    "small": Profile.SMALL,
    "medium": Profile.MEDIUM,
    "large": Profile.LARGE,
}


def resolve_profile(name: str, seed: int | None = None) -> Profile:
    try:
        profile = PROFILE_FACTORIES[name]()
    except KeyError as exc:
        known = ", ".join(sorted(PROFILE_FACTORIES))
        raise ValueError(f"unknown profile {name!r}; expected one of: {known}") from exc
    if seed is not None:
        profile = replace(profile, seed=seed)
    return profile
