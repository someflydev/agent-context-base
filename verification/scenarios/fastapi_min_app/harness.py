from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from verification.helpers import REPO_ROOT, fastapi_stub_module, load_python_module, python_api_stub_modules


EXAMPLE_PATH = REPO_ROOT / "examples/canonical-api/fastapi-endpoint-example.py"


class FakeWarehouse:
    async def fetch_report_totals(self, tenant_id: str, limit: int) -> Any:
        module = load_python_module(
            EXAMPLE_PATH,
            module_name="verification.scenarios.fastapi_min_app.bootstrap",
            stub_modules=python_api_stub_modules(),
        )
        frame_type = module.pl.DataFrame
        rows = [
            {"report_id": "daily-signups", "total_events": 42, "error_events": 3},
            {"report_id": "failed-payments", "total_events": 3, "error_events": 1},
            {"report_id": "stale-report", "total_events": 0, "error_events": 0},
        ]
        return frame_type(rows[:limit] if limit < len(rows) else rows)


def load_example_module() -> Any:
    return load_python_module(
        EXAMPLE_PATH,
        module_name="verification.scenarios.fastapi_min_app.example",
        stub_modules=python_api_stub_modules(),
    )


async def run_fastapi_summary_scenario() -> dict[str, Any]:
    module = load_example_module()
    service = module.ReportService(warehouse=FakeWarehouse())
    payload = await module.list_report_summaries(
        tenant_id="acme",
        limit=3,
        service=service,
    )
    response = [
        item.model_dump() if hasattr(item, "model_dump") else dict(item.__dict__)
        for item in payload
    ]

    app = fastapi_stub_module().FastAPI()
    app.include_router(module.router)
    return {
        "routes": [route["path"] for route in module.router.routes],
        "mounted_routes": [route["path"] for route in app.routes],
        "response": response,
    }


def main() -> int:
    result = asyncio.run(run_fastapi_summary_scenario())
    if "/reports/summary" not in result["mounted_routes"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
