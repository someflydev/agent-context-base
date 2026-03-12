from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import polars as pl
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportSummary(BaseModel):
    report_id: str = Field(description="Stable report identifier")
    total_events: int = Field(ge=0)
    error_rate: float = Field(ge=0.0, le=1.0)


class ReportWarehouse(Protocol):
    async def fetch_report_totals(self, tenant_id: str, limit: int) -> pl.DataFrame:
        """Return one row per report with total and error counts."""


@dataclass(slots=True)
class ReportService:
    warehouse: ReportWarehouse

    async def list_summaries(self, tenant_id: str, limit: int) -> list[ReportSummary]:
        frame = await self.warehouse.fetch_report_totals(tenant_id=tenant_id, limit=limit)
        normalized = (
            frame.with_columns(
                pl.when(pl.col("total_events") == 0)
                .then(0.0)
                .otherwise(pl.col("error_events") / pl.col("total_events"))
                .alias("error_rate")
            )
            .select("report_id", "total_events", "error_rate")
            .sort("total_events", descending=True)
        )

        return [
            ReportSummary(
                report_id=row["report_id"],
                total_events=row["total_events"],
                error_rate=row["error_rate"],
            )
            for row in normalized.to_dicts()
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

