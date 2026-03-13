import json
import jester

proc buildSeriesPayload*(metric: string): JsonNode =
  %*{
    "metric": metric,
    "series": [
      {
        "name": metric,
        "points": [
          {"x": "2026-03-01", "y": 18},
          {"x": "2026-03-02", "y": 24},
          {"x": "2026-03-03", "y": 31},
        ],
      }
    ],
  }

routes:
  get "/data/series/@metric":
    resp buildSeriesPayload(@"metric")
