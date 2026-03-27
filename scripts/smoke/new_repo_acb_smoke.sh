#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMMIT_ID="$(git -C "$REPO_ROOT" rev-parse --short HEAD)"
TIMESTAMP="$(date "+%Y%m%d-%H%M%S")"
SMOKE_ROOT="/tmp/smoke-acb-${TIMESTAMP}-${COMMIT_ID}"
PYTHON_BIN="${PYTHON_BIN:-python3.14}"

run_case() {
  local label="$1"
  shift
  echo
  echo "== ${label} =="
  "$PYTHON_BIN" "$REPO_ROOT/scripts/new_repo.py" "$@"
}

show_root() {
  local target="$1"
  echo "-- root entries: ${target}"
  find "$target" -maxdepth 1 -mindepth 1 | sort
}

rm -rf "$SMOKE_ROOT"
mkdir -p "$SMOKE_ROOT"

run_case \
  "prompt-kit ordinary" \
  prompt-kit \
  --target-dir "$SMOKE_ROOT/prompt-kit" \
  --archetype prompt-first-repo \
  --primary-stack prompt-first-repo \
  --initial-prompt-text "Bootstrap a prompt-first repo with a compact repo-local .acb support bundle."

run_case \
  "example-001 ordinary" \
  --use-example 1 \
  --target-dir "$SMOKE_ROOT/example-001"

run_case \
  "operator-surface compact" \
  --derived-example operator-surface \
  --target-dir "$SMOKE_ROOT/operator-surface-compact"

run_case \
  "operator-surface maximal" \
  --derived-example operator-surface \
  --derived-context-mode maximal \
  --target-dir "$SMOKE_ROOT/operator-surface-maximal"

run_case \
  "team-a compact" \
  --derived-example team-a \
  --target-dir "$SMOKE_ROOT/team-a-compact"

run_case \
  "team-a maximal" \
  --derived-example team-a \
  --derived-context-mode maximal \
  --target-dir "$SMOKE_ROOT/team-a-maximal"

show_root "$SMOKE_ROOT/operator-surface-compact"
show_root "$SMOKE_ROOT/operator-surface-maximal"
show_root "$SMOKE_ROOT/team-a-compact/ingestion-normalization-core"
show_root "$SMOKE_ROOT/team-a-maximal/ingestion-normalization-core"
show_root "$SMOKE_ROOT/prompt-kit"
show_root "$SMOKE_ROOT/example-001"

echo
echo "Smoke output written under: $SMOKE_ROOT"
