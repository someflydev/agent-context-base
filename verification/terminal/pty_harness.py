from __future__ import annotations

import os
from typing import Optional

try:
    import pexpect
except ImportError:  # pragma: no cover - optional dependency
    pexpect = None


PEXPECT_AVAILABLE = pexpect is not None


class PtySession:
    """Wrap a pexpect session for scripted TUI interaction."""

    def __init__(self, cmd: list[str], env: Optional[dict] = None, timeout: int = 10):
        if not PEXPECT_AVAILABLE:
            raise RuntimeError("pexpect is not installed")
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        self.child = pexpect.spawn(
            cmd[0],
            cmd[1:],
            env=merged_env,
            timeout=timeout,
            encoding="utf-8",
            codec_errors="replace",
        )

    def expect(self, pattern: str, timeout: Optional[int] = None) -> str:
        self.child.expect(pattern, timeout=timeout)
        return self.child.before + self.child.after

    def send_key(self, key: str) -> None:
        self.child.send(key)

    def send_line(self, line: str) -> None:
        self.child.sendline(line)

    def close(self) -> int:
        self.child.close()
        if self.child.exitstatus is not None:
            return self.child.exitstatus
        return self.child.signalstatus or 1


def scripted_tui_test(cmd: list[str], script: list[dict], env: Optional[dict] = None) -> bool:
    if not PEXPECT_AVAILABLE:
        return False

    session = PtySession(cmd, env=env)
    try:
        for step in script:
            action = step["action"]
            value = step["value"]
            if action == "expect":
                session.expect(str(value))
            elif action == "send_key":
                session.send_key(str(value))
            elif action == "send_line":
                session.send_line(str(value))
            elif action == "expect_exit":
                exit_code = session.close()
                if exit_code != int(value):
                    return False
            else:
                raise ValueError(f"unknown PTY action: {action}")
    except Exception:
        session.close()
        return False
    return True


def make_watch_script() -> list[dict]:
    return [
        {"action": "expect", "value": "build-frontend|job-001|TaskFlow"},
        {"action": "send_key", "value": "q"},
        {"action": "expect_exit", "value": 0},
    ]
