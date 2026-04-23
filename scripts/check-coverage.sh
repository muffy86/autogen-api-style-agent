#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'EOF'
Usage: bash scripts/check-coverage.sh

Environment variables:
  COVERAGE_THRESHOLD  Minimum coverage percent for each enabled side (default: 70)
  SKIP_PYTHON         Skip Python coverage when set
  SKIP_JS             Skip JS coverage when set
EOF
  exit 0
fi

COVERAGE_THRESHOLD="${COVERAGE_THRESHOLD:-70}"
python_percent="N/A"
python_result="PASS (skipped via SKIP_PYTHON)"
js_percent="N/A"
js_result="PASS (skipped via SKIP_JS)"
overall_status=0

is_ci() {
  [[ "${CI:-}" == "true" ]]
}

ensure_pytest_cov() {
  if python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('pytest_cov') else 1)"; then
    return 0
  fi

  if is_ci; then
    echo "Installing pytest-cov because CI=true"
    pip install pytest-cov
    return 0
  fi

  echo "error: pytest-cov is not installed" >&2
  return 1
}

ensure_vitest() {
  if pnpm exec vitest --version >/dev/null 2>&1; then
    return 0
  fi

  if is_ci; then
    echo "Installing vitest coverage tooling because CI=true"
    pnpm add -D vitest @vitest/coverage-v8
    return 0
  fi

  echo "error: vitest is not installed" >&2
  return 1
}

run_python_coverage() {
  if [[ -n "${SKIP_PYTHON:-}" ]]; then
    python_result="PASS (skipped via SKIP_PYTHON)"
    return 0
  fi

  if ! command -v python >/dev/null 2>&1; then
    echo "error: python is not available" >&2
    python_result="FAIL"
    overall_status=1
    return 0
  fi

  if ! command -v pytest >/dev/null 2>&1; then
    echo "error: pytest is not available" >&2
    python_result="FAIL"
    overall_status=1
    return 0
  fi

  if ! ensure_pytest_cov; then
    python_result="FAIL"
    overall_status=1
    return 0
  fi

  rm -f coverage.xml coverage.json

  set +e
  pytest --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml --cov-report=json:coverage.json --cov-fail-under="${COVERAGE_THRESHOLD}"
  local status=$?
  set -e

  if [[ -f coverage.json ]]; then
    python_percent="$(python -c 'import json; data=json.load(open("coverage.json")); print("{:.2f}".format(data["totals"]["percent_covered"]))')"
    low_files="$(python -c 'import json, sys; threshold=float(sys.argv[1]); data=json.load(open("coverage.json")); rows=["{}: {:.2f}%".format(path, info.get("summary", {}).get("percent_covered", 0.0)) for path, info in sorted(data.get("files", {}).items()) if info.get("summary", {}).get("percent_covered", 100.0) < threshold]; print("\n".join(rows))' "${COVERAGE_THRESHOLD}")"
    echo "Python total coverage: ${python_percent}%"
    if [[ -n "${low_files}" ]]; then
      echo "Python files below ${COVERAGE_THRESHOLD}%:"
      echo "${low_files}"
    fi
  else
    echo "error: coverage.json was not produced by pytest" >&2
  fi

  if [[ ${status} -eq 0 && -f coverage.json ]]; then
    python_result="PASS"
  else
    python_result="FAIL"
    overall_status=1
  fi
}

run_js_coverage() {
  if [[ -n "${SKIP_JS:-}" ]]; then
    js_result="PASS (skipped via SKIP_JS)"
    return 0
  fi

  if [[ ! -f pnpm-lock.yaml ]]; then
    echo "warning: pnpm-lock.yaml not found; skipping JS coverage"
    js_result="PASS (no pnpm lockfile)"
    return 0
  fi

  if [[ ! -f vitest.config.ts ]]; then
    echo "warning: vitest.config.ts not found; skipping JS coverage"
    js_result="PASS (no vitest config)"
    return 0
  fi

  if ! command -v python >/dev/null 2>&1; then
    echo "error: python is not available" >&2
    js_result="FAIL"
    overall_status=1
    return 0
  fi

  if ! command -v pnpm >/dev/null 2>&1; then
    echo "error: pnpm is not available" >&2
    js_result="FAIL"
    overall_status=1
    return 0
  fi

  if ! ensure_vitest; then
    js_result="FAIL"
    overall_status=1
    return 0
  fi

  rm -rf coverage

  set +e
  vitest_output="$(pnpm exec vitest run --coverage 2>&1)"
  local status=$?
  set -e

  printf '%s\n' "${vitest_output}"

  if [[ ${status} -ne 0 && "${vitest_output}" == *"No test files found"* ]]; then
    echo "warning: no JS tests found; skipping JS coverage"
    js_result="PASS (no JS tests found)"
    return 0
  fi

  if [[ ! -f coverage/coverage-summary.json ]]; then
    if [[ ${status} -ne 0 ]]; then
      echo "error: vitest coverage run failed" >&2
      js_result="FAIL"
      overall_status=1
      return 0
    fi

    echo "warning: coverage/coverage-summary.json not found; skipping JS coverage"
    js_result="PASS (no JS coverage summary)"
    return 0
  fi

  js_percent="$(python -c 'import json; data=json.load(open("coverage/coverage-summary.json")); print("{:.2f}".format(data["total"]["lines"]["pct"]))')"
  echo "JS total line coverage: ${js_percent}%"

  if ! python -c 'import sys; sys.exit(0 if float(sys.argv[1]) >= float(sys.argv[2]) else 1)' "${js_percent}" "${COVERAGE_THRESHOLD}"; then
    js_result="FAIL"
    overall_status=1
    return 0
  fi

  if [[ ${status} -eq 0 ]]; then
    js_result="PASS"
  else
    js_result="FAIL"
    overall_status=1
  fi
}

run_python_coverage
run_js_coverage

echo "=== COVERAGE SUMMARY ==="
echo "Python: ${python_percent}% | threshold: ${COVERAGE_THRESHOLD}% | ${python_result}"
echo "JS: ${js_percent}% | threshold: ${COVERAGE_THRESHOLD}% | ${js_result}"

if [[ ${overall_status} -eq 0 ]]; then
  echo "Overall: PASS"
else
  echo "Overall: FAIL"
fi

exit "${overall_status}"
