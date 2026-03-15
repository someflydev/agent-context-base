from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportSummary(BaseModel):
    report_id: str = Field(description="Stable report identifier")
    total_events: int = Field(ge=0)
    error_rate: float = Field(ge=0.0, le=1.0)


class ReportWarehouse(Protocol):
    async def fetch_report_rows(self, tenant_id: str, limit: int) -> list[dict[str, object]]:
        """Return one row per report with total and error counts."""


@dataclass(slots=True)
class ReportService:
    warehouse: ReportWarehouse

    async def list_summaries(self, tenant_id: str, limit: int) -> list[ReportSummary]:
        rows = await self.warehouse.fetch_report_rows(tenant_id=tenant_id, limit=limit)
        sorted_rows = sorted(rows, key=lambda row: int(row["total_events"]), reverse=True)
        return [
            ReportSummary(
                report_id=str(row["report_id"]),
                total_events=int(row["total_events"]),
                error_rate=(
                    int(row["error_events"]) / int(row["total_events"])
                    if int(row["total_events"]) > 0
                    else 0.0
                ),
            )
            for row in sorted_rows
        ]


def get_report_service() -> ReportService:
    raise NotImplementedError("Wire the report service from application dependencies.")


@router.get("/summary", response_model=list[ReportSummary])
async def list_report_summaries(
    tenant_id: str = Query(min_length=3),
    limit: int = Query(default=20, ge=1, le=200),
    service: ReportService = Depends(get_report_service),
) -> list[ReportSummary]:
    return await service.list_summaries(tenant_id=tenant_id, limit=limit)
