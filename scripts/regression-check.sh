#!/usr/bin/env bash
set -euo pipefail

BASELINE_DIR=".regression-baseline"
CURRENT_DIR=".regression-current"
PYTEST_BASELINE="${BASELINE_DIR}/baseline-pytest.json"
VITEST_BASELINE="${BASELINE_DIR}/baseline-vitest.json"
PYTEST_CURRENT="${CURRENT_DIR}/pytest.json"
VITEST_CURRENT="${CURRENT_DIR}/vitest.json"
MODE="${1:-check}"

usage() {
  cat <<'EOF'
Usage: bash scripts/regression-check.sh [check|update]
EOF
}

ensure_pytest_json_report() {
  local pytest_help
  pytest_help="$(pytest --help 2>/dev/null || true)"

  if grep -q -- '--json-report' <<<"${pytest_help}"; then
    return 0
  fi

  if [[ "${CI:-}" == "true" ]]; then
    echo "Installing pytest-json-report because CI=true"
    pip install pytest-json-report
    return 0
  fi

  echo "error: pytest-json-report plugin is not installed" >&2
  return 1
}

run_pytest_report() {
  local output_path="$1"

  if ! command -v pytest >/dev/null 2>&1; then
    echo "error: pytest is not available" >&2
    return 1
  fi

  if ! ensure_pytest_json_report; then
    return 1
  fi

  set +e
  pytest --json-report --json-report-file="${output_path}"
  local status=$?
  set -e
  return "${status}"
}

run_vitest_report() {
  local output_path="$1"

  if [[ ! -f pnpm-lock.yaml || ! -f vitest.config.ts ]]; then
    echo "warning: vitest stack not configured; skipping vitest regression report"
    return 2
  fi

  if ! command -v pnpm >/dev/null 2>&1; then
    echo "error: pnpm is not available" >&2
    return 1
  fi

  set +e
  local output
  output="$(pnpm exec vitest run --reporter=json --outputFile="${output_path}" 2>&1)"
  local status=$?
  set -e

  printf '%s\n' "${output}"

  if [[ ${status} -ne 0 && "${output}" == *"No test files found"* ]]; then
    echo "warning: no JS tests found; skipping vitest regression report"
    rm -f "${output_path}"
    return 2
  fi

  return "${status}"
}

compare_reports() {
  python - "$PYTEST_BASELINE" "$PYTEST_CURRENT" "$VITEST_BASELINE" "$VITEST_CURRENT" <<'PY'
import json
import sys
from pathlib import Path


def load_json(path_str: str):
    path = Path(path_str)
    if not path.exists():
        return {}
    with path.open() as handle:
        return json.load(handle)


def load_pytest(path_str: str):
    data = load_json(path_str)
    return {
        f"pytest::{item['nodeid']}": item.get("outcome", "unknown")
        for item in data.get("tests", [])
        if item.get("nodeid")
    }


def load_vitest(path_str: str):
    data = load_json(path_str)
    collected = {}

    def visit(node, current_file: str | None = None):
        if isinstance(node, dict):
            node_file = current_file
            candidate = node.get("name") or node.get("testFilePath")
            if isinstance(candidate, str) and candidate.endswith((".js", ".ts", ".jsx", ".tsx")):
                node_file = candidate
            if "assertionResults" in node and isinstance(node["assertionResults"], list):
                file_name = node_file or node.get("name") or "unknown"
                for item in node["assertionResults"]:
                    full_name = item.get("fullName")
                    if not full_name:
                        parts = list(item.get("ancestorTitles", []))
                        title = item.get("title")
                        if title:
                            parts.append(title)
                        full_name = " > ".join(parts) or item.get("title") or "unknown"
                    collected[f"vitest::{file_name} :: {full_name}"] = item.get("status", "unknown")
            for value in node.values():
                visit(value, node_file)
        elif isinstance(node, list):
            for value in node:
                visit(value, current_file)

    visit(data)
    return collected


baseline = {}
baseline.update(load_pytest(sys.argv[1]))
baseline.update(load_vitest(sys.argv[3]))

current = {}
current.update(load_pytest(sys.argv[2]))
current.update(load_vitest(sys.argv[4]))

FAILING_STATUSES = {"failed", "error"}
PRIOR_NON_FAILING = {"passed", "skipped", "xfailed", "xpassed", "pending", "todo"}

shared = set(baseline) & set(current)
new_failures = sorted(
    node_id
    for node_id in shared
    if baseline[node_id] in PRIOR_NON_FAILING and current[node_id] in FAILING_STATUSES
)
removed = sorted(set(baseline) - set(current))
new_tests = sorted(set(current) - set(baseline))

print("=== REGRESSION SUMMARY ===")
print(f"Baseline tests: {len(baseline)}")
print(f"Current tests: {len(current)}")
print(f"New failures: {len(new_failures)}")
for node_id in new_failures:
    print(f"  - {node_id}")
print(f"Removed tests: {len(removed)}")
for node_id in removed:
    print(f"  - {node_id}")
print(f"New tests: {len(new_tests)}")
for node_id in new_tests:
    print(f"  - {node_id}")

if new_failures:
    print("Regression detected: new failures found.", file=sys.stderr)
if removed:
    print(
        "Regression detected: removed tests found; if intentional, run scripts/regression-check.sh update to refresh baseline.",
        file=sys.stderr,
    )

sys.exit(1 if new_failures or removed else 0)
PY
}

case "${MODE}" in
  check|update)
    ;;
  -h|--help)
    usage
    exit 0
    ;;
  *)
    usage >&2
    exit 1
    ;;
esac

mkdir -p "${BASELINE_DIR}"
rm -rf "${CURRENT_DIR}"
mkdir -p "${CURRENT_DIR}"

pytest_status=0
vitest_status=0
vitest_skipped=0

set +e
run_pytest_report "${PYTEST_CURRENT}"
pytest_status=$?
run_vitest_report "${VITEST_CURRENT}"
vitest_status=$?
set -e

if [[ ${vitest_status} -eq 2 ]]; then
  vitest_skipped=1
fi

if [[ ! -f "${PYTEST_CURRENT}" ]]; then
  echo "error: pytest JSON report was not produced" >&2
  exit 1
fi

if [[ ${vitest_skipped} -eq 0 && -f vitest.config.ts && ! -f "${VITEST_CURRENT}" ]]; then
  echo "error: vitest JSON report was not produced" >&2
  exit 1
fi

if [[ "${MODE}" == "check" ]]; then
  baseline_missing=0
  if [[ -f "${PYTEST_CURRENT}" && ! -f "${PYTEST_BASELINE}" ]]; then
    baseline_missing=1
  fi
  if [[ -f "${VITEST_CURRENT}" && ! -f "${VITEST_BASELINE}" ]]; then
    baseline_missing=1
  fi
  if [[ ${baseline_missing} -eq 1 ]]; then
    echo "no baseline found — run ./scripts/regression-check.sh update to create one"
    exit 0
  fi
fi

if [[ "${MODE}" == "update" ]]; then
  cp "${PYTEST_CURRENT}" "${PYTEST_BASELINE}"
  if [[ ${vitest_skipped} -eq 0 && -f "${VITEST_CURRENT}" ]]; then
    cp "${VITEST_CURRENT}" "${VITEST_BASELINE}"
  else
    rm -f "${VITEST_BASELINE}"
  fi

  echo "updated regression baseline in ${BASELINE_DIR}"
  exit 0
fi

comparison_status=0
set +e
compare_reports
comparison_status=$?
set -e

if [[ ${comparison_status} -ne 0 ]]; then
  exit 1
fi

exit 0
