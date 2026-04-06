from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input

from taskflow.core.filters import filter_jobs, sort_jobs
from taskflow.core.loader import FixtureError, default_fixtures_path, load_jobs
from taskflow.core.stats import compute_stats
from taskflow.tui.widgets import JobDetail, JobTable, StatsBar


class TaskFlowApp(App[None]):
    CSS = """
    Screen {
      layout: vertical;
    }
    #body {
      height: 1fr;
    }
    JobTable {
      width: 2fr;
    }
    JobDetail {
      width: 1fr;
      padding: 1;
      border: round $accent;
    }
    #filter {
      dock: top;
      display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "toggle_filter", "Filter"),
        Binding("enter", "show_selected", "Detail"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]

    def __init__(self, fixtures_path: Path | None = None) -> None:
        super().__init__()
        self.fixtures_path = fixtures_path or default_fixtures_path()
        self.jobs = []
        self.filtered_jobs = []

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Input(placeholder="status:done or tag:ci", id="filter")
        yield StatsBar(id="stats")
        with Horizontal(id="body"):
            yield JobTable()
            yield JobDetail()
        yield Footer()

    def on_mount(self) -> None:
        self._reload_jobs()

    def _reload_jobs(self, status: str | None = None, tag: str | None = None) -> None:
        try:
            self.jobs = load_jobs(self.fixtures_path)
        except FixtureError as error:
            self.notify(str(error), severity="error")
            return
        self.filtered_jobs = sort_jobs(filter_jobs(self.jobs, status=status, tag=tag))
        self.query_one(JobTable).load_jobs(self.filtered_jobs)
        stats = compute_stats(self.filtered_jobs)
        self.query_one(StatsBar).update_text(
            "TaskFlow Monitor | total={total} done={done} failed={failed} running={running} pending={pending}".format(
                total=stats.total,
                done=stats.by_status["done"],
                failed=stats.by_status["failed"],
                running=stats.by_status["running"],
                pending=stats.by_status["pending"],
            )
        )
        detail = self.filtered_jobs[0] if self.filtered_jobs else None
        self.query_one(JobDetail).show_job(detail)

    def action_refresh(self) -> None:
        self._reload_jobs()

    def action_toggle_filter(self) -> None:
        widget = self.query_one("#filter", Input)
        if widget.display:
            widget.display = False
            widget.value = ""
            self.set_focus(self.query_one(JobTable))
            return
        widget.display = True
        self.set_focus(widget)

    def action_show_selected(self) -> None:
        table = self.query_one(JobTable)
        if table.cursor_row is None or not self.filtered_jobs:
            return
        self.query_one(JobDetail).show_job(self.filtered_jobs[table.cursor_row])

    def action_cursor_up(self) -> None:
        self.query_one(JobTable).action_cursor_up()
        self.action_show_selected()

    def action_cursor_down(self) -> None:
        self.query_one(JobTable).action_cursor_down()
        self.action_show_selected()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        status = None
        tag = None
        if raw.startswith("status:"):
            status = raw.split(":", 1)[1].strip()
        elif raw.startswith("tag:"):
            tag = raw.split(":", 1)[1].strip()
        self.query_one("#filter", Input).display = False
        self._reload_jobs(status=status, tag=tag)
        self.set_focus(self.query_one(JobTable))

