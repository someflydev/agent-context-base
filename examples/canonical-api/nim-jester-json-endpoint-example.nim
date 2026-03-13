import json
import jester

type HealthSnapshot* = object
  service*: string
  status*: string

routes:
  get "/api/health":
    let snapshot = HealthSnapshot(service: "nim-jester-happyx", status: "ok")
    resp %*{
      "service": snapshot.service,
      "status": snapshot.status,
    }
