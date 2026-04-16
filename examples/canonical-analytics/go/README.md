# Analytics Workbench Go

A Go implementation of the Ops & Product Analytics Workbench.
Uses `echo` for routing, `templ` for components, HTMX for interactions, and Plotly for visualization.

## How to run

```bash
go run cmd/server/main.go
```
(Server starts on port 8080 by default. Set `PORT` to change.)

## How to test

```bash
go test -tags unit ./tests/unit/...
go test -tags smoke ./tests/smoke/...
```
