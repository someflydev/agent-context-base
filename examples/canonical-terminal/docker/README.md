# Docker Live-Data Mode (Optional)

Run a local API server backed by fixture data.

Terminal examples can connect via `--api-url http://localhost:8765` to
simulate a live backend without any real queue system.

This is optional. All smoke tests use fixture files directly. The Docker mode
is for demonstration and exploratory use only.

Start:

```bash
docker compose up
```

Connect:

```bash
taskflow list --api-url http://localhost:8765
```
