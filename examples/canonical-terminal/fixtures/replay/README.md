# Event Stream Replay

Simulates a live job queue by replaying fixture events in timestamp order.

## Python

```python
from pathlib import Path

from replay.stream import replay_events

events_path = Path("examples/canonical-terminal/fixtures/events-large.json")

for event in replay_events(events_path, speed_factor=10.0):
    print(f"[{event['event_type']}] {event['job_id']}: {event['message']}")
```

## Go

```go
replayer, err := replay.NewReplayer(eventsPath, replay.SpeedFactor(10.0))
if err != nil {
    panic(err)
}
for replayer.Next() {
    event := replayer.Event()
    fmt.Printf("[%s] %s: %s\n", event.EventType, event.JobID, event.Message)
}
```

## Use In Terminal Examples

Pass a `--live-replay` style flag to watch commands to simulate live data.
All replay is fixture-backed: no network required.

## Snapshot Mode

Use `replay_to_state(events_path, jobs_path, up_to_event=N)` to compute the job
list state at a specific point in the event stream without sleeping. This keeps
snapshot tests deterministic.
