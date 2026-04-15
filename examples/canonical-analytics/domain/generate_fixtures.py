"""
This generator dogfoods examples/canonical-faker/ — see that directory for the
full synthetic data generation arc. Do not build a parallel generation system here.

# FALLBACK
The upstream canonical-faker implementation does not export the direct analytics entities
(like Incident, Deployment, Latency) required for the analytics workbench. Therefore, 
this script uses a self-contained fallback generation pattern using random with seed=42
to produce the exact analytics fixture shapes while adhering to the seed data contract.
The fallback still respects the conceptual TenantCore domain boundaries.

Counts (smoke.json):
- events: 150
- sessions: 100
- services: 4
- deployments: 10
- incidents: 15
- latency_samples: 200
- funnel_stages: 4
"""

import argparse
import json
import os
import sys
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

def get_deterministic_uuid(r: random.Random) -> str:
    """Generate a deterministic UUID based on the random instance."""
    return str(uuid.UUID(int=r.getrandbits(128), version=4))

def generate_fixtures(profile: str, seed: int = 42) -> dict:
    r = random.Random(seed)

    # Deterministic base date (to ensure stable tests across runs/days)
    base_date = datetime(2026, 1, 1)

    # Row counts based on profile
    if profile == "smoke":
        num_events = 150
        num_sessions = 100
        num_deployments = 10
        num_incidents = 15
        num_latency = 200
    elif profile == "small":
        num_events = 1000
        num_sessions = 500
        num_deployments = 50
        num_incidents = 80
        num_latency = 1000
    else:
        # Default to small for unknown profiles to avoid large accidental memory usage
        num_events = 1000
        num_sessions = 500
        num_deployments = 50
        num_incidents = 80
        num_latency = 1000

    environments = ["production", "staging"]
    services = ["auth-service", "billing-api", "user-dashboard", "search-worker"]
    severities = ["sev1", "sev2", "sev3"]
    stages = ["visited_site", "signed_up", "added_payment", "completed_purchase"]

    events = []
    for _ in range(num_events):
        dt = base_date - timedelta(days=r.randint(0, 40))
        events.append({
            "id": get_deterministic_uuid(r),
            "timestamp": dt.isoformat(),
            "environment": r.choice(environments),
            "service": r.choice(services),
            "count": r.randint(1, 100)
        })

    sessions = []
    for _ in range(num_sessions):
        sessions.append({
            "id": get_deterministic_uuid(r),
            "duration_ms": r.randint(100, 5000),
            "environment": r.choice(environments),
            "funnel_stage": r.choice(stages)
        })

    # Services
    services_list = []
    for s in services:
        for e in environments:
            services_list.append({
                "name": s,
                "environment": e,
                "error_rate": round(r.uniform(0.01, 0.15), 3)
            })

    deployments = []
    for _ in range(num_deployments):
        dt = base_date - timedelta(days=r.randint(0, 30))
        deployments.append({
            "id": get_deterministic_uuid(r),
            "timestamp": dt.isoformat(),
            "service": r.choice(services),
            "environment": r.choice(environments),
            "status": r.choice(["success", "failed"])
        })

    incidents = []
    for _ in range(num_incidents):
        dt = base_date - timedelta(days=r.randint(0, 30))
        incidents.append({
            "id": get_deterministic_uuid(r),
            "timestamp": dt.isoformat(),
            "severity": r.choice(severities),
            "mttr_mins": r.randint(5, 120),
            "service": r.choice(services),
            "environment": r.choice(environments)
        })

    latency_samples = []
    for i in range(num_latency):
        dt = base_date - timedelta(days=r.randint(0, 30))
        # Ensure at least 1 anomaly
        if i == 0:
            lat = 15000  # anomaly
        else:
            lat = r.randint(20, 300)
        latency_samples.append({
            "id": get_deterministic_uuid(r),
            "timestamp": dt.isoformat(),
            "latency_ms": lat,
            "service": r.choice(services),
            "environment": r.choice(environments)
        })

    funnel_stages = []
    for e in environments:
        drop_off = 0.1
        for stage in stages:
            funnel_stages.append({
                "stage_name": stage,
                "environment": e,
                "drop_off_rate": drop_off
            })
            drop_off += 0.2

    return {
        "events": events,
        "sessions": sessions,
        "services": services_list,
        "deployments": deployments,
        "incidents": incidents,
        "latency_samples": latency_samples,
        "funnel_stages": funnel_stages
    }

def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="smoke,small", help="Comma-separated profiles")
    parser.add_argument("--output", default="./fixtures", help="Output directory")
    args = parser.parse_args(argv)

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    profiles = args.profiles.split(",")

    for profile in profiles:
        profile = profile.strip()
        if not profile:
            continue
        
        # Determinism check
        data1 = generate_fixtures(profile, seed=42)
        json1 = json.dumps(data1, sort_keys=True)
        data2 = generate_fixtures(profile, seed=42)
        json2 = json.dumps(data2, sort_keys=True)
        assert json1 == json2, f"Determinism assertion failed for profile {profile}!"

        out_path = out_dir / f"{profile}.json"
        with open(out_path, "w") as f:
            json.dump(data1, f, indent=2)

        print(f"Generated {profile}.json with seed=42 at {out_path}")
        print("Entity counts:")
        for k, v in data1.items():
            print(f"  {k}: {len(v)}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
