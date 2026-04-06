from __future__ import annotations

from textual.widgets import DataTable, Static

from taskflow.core.models import Job


class StatsBar(Static):
    def update_text(self, content: str) -> None:
        self.update(content)


class JobDetail(Static):
    def show_job(self, job: Job | None) -> None:
        if job is None:
            self.update("Select a job to inspect its detail.")
            return
        started_at = job.started_at.isoformat().replace("+00:00", "Z") if job.started_at else "-"
        lines = [
            f"{job.name} ({job.id})",
            f"status={job.status.value}",
            f"started_at={started_at}",
            f"duration_s={job.duration_s if job.duration_s is not None else '-'}",
            f"tags={', '.join(job.tags)}",
            "",
            "output:",
            *[f"  {line}" for line in job.output_lines],
        ]
        self.update("\n".join(lines))


class JobTable(DataTable):
    def __init__(self) -> None:
        super().__init__(zebra_stripes=True)
        self.cursor_type = "row"

    def load_jobs(self, jobs: list[Job]) -> None:
        self.clear(columns=True)
        self.add_columns("ID", "Name", "Status", "Started", "Tags")
        for job in jobs:
            started = job.started_at.isoformat().replace("+00:00", "Z") if job.started_at else "-"
            self.add_row(job.id, job.name, job.status.value, started, ", ".join(job.tags), key=job.id)

