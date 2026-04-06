from __future__ import annotations

from blessed import Terminal

from taskflow.core.filters import filter_jobs


term = Terminal()


def _color_status(status: str) -> str:
    palette = {
        "done": term.green(status),
        "failed": term.red(status),
        "running": term.yellow(status),
        "pending": term.white(status),
    }
    return palette.get(status, status)


def _render_jobs(jobs: list, index: int) -> None:
    print(term.clear + term.home, end="")
    print(term.bold("TaskFlow Monitor"), "- q=quit, arrows=scroll, f=filter")
    window = jobs[max(0, index - 5): index + 6]
    for offset, job in enumerate(window, start=max(0, index - 5)):
        marker = ">" if offset == index else " "
        print(f"{marker} {job.id} {job.name:<24} {_color_status(job.status.value)}")


def run_pager(jobs: list) -> None:
    if not jobs:
        print("No jobs available.")
        return

    visible = list(jobs)
    index = 0
    with term.cbreak(), term.hidden_cursor():
        while True:
            _render_jobs(visible, index)
            key = term.inkey(timeout=1)
            if not key:
                continue
            if key.lower() == "q":
                print(term.normal, end="")
                return
            if key.name == "KEY_UP":
                index = max(0, index - 1)
            elif key.name == "KEY_DOWN":
                index = min(len(visible) - 1, index + 1)
            elif key.lower() == "f":
                print(term.clear + term.home + "Filter status (pending/running/done/failed, blank=clear): ", end="")
                value = input().strip()
                visible = filter_jobs(jobs, status=value or None)
                if not visible:
                    visible = list(jobs)
                index = 0

