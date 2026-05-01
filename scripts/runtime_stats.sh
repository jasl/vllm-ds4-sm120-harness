RUNTIME_STATS="${RUNTIME_STATS:-1}"
RUNTIME_STATS_INTERVAL_SECONDS="${RUNTIME_STATS_INTERVAL_SECONDS:-5}"
RUNTIME_STATS_CURL_TIMEOUT_SECONDS="${RUNTIME_STATS_CURL_TIMEOUT_SECONDS:-5}"
RUNTIME_STATS_BASE_URL="${RUNTIME_STATS_BASE_URL:-${BASE_URL:-http://${HOST:-127.0.0.1}:${PORT:-8000}}}"
RUNTIME_METRICS_URL="${RUNTIME_METRICS_URL:-${RUNTIME_STATS_BASE_URL%/}/metrics}"
RUNTIME_METRICS_PROM="${OUT_DIR}/vllm_metrics.prom"
RUNTIME_METRICS_ERR="${OUT_DIR}/vllm_metrics.err"
SERVE_LOG="${SERVE_LOG:-}"
RUNTIME_SERVE_LOG_SLICE="${OUT_DIR}/serve_log_phase.log"
RUNTIME_SERVE_LOG_OFFSET_FILE="${OUT_DIR}/serve_log_offset.txt"
RUNTIME_STATS_PID=""

start_runtime_stats() {
  if [[ "${RUNTIME_STATS}" != "1" && "${RUNTIME_STATS}" != "true" ]]; then
    return 0
  fi

  if [[ -n "${SERVE_LOG}" && -f "${SERVE_LOG}" ]]; then
    wc -c < "${SERVE_LOG}" | tr -d '[:space:]' > "${RUNTIME_SERVE_LOG_OFFSET_FILE}"
  else
    printf '%s\n' "0" > "${RUNTIME_SERVE_LOG_OFFSET_FILE}"
  fi

  if ! command -v curl >/dev/null 2>&1; then
    printf '%s\n' "curl is not available; vLLM runtime stats were not captured." \
      > "${OUT_DIR}/runtime_stats_unavailable.txt"
    return 0
  fi

  (
    while true; do
      printf '# DS4_HARNESS_SNAPSHOT %s url=%s\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "${RUNTIME_METRICS_URL}"
      if ! curl -fsS --max-time "${RUNTIME_STATS_CURL_TIMEOUT_SECONDS}" \
        "${RUNTIME_METRICS_URL}"; then
        printf '# DS4_HARNESS_ERROR %s failed to fetch %s\n' \
          "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
          "${RUNTIME_METRICS_URL}" >&2
      fi
      sleep "${RUNTIME_STATS_INTERVAL_SECONDS}"
    done
  ) > "${RUNTIME_METRICS_PROM}" 2> "${RUNTIME_METRICS_ERR}" &
  RUNTIME_STATS_PID="$!"
}

stop_runtime_stats() {
  if [[ "${RUNTIME_STATS}" != "1" && "${RUNTIME_STATS}" != "true" ]]; then
    return 0
  fi

  if [[ -n "${RUNTIME_STATS_PID}" ]]; then
    kill "${RUNTIME_STATS_PID}" >/dev/null 2>&1 || true
    wait "${RUNTIME_STATS_PID}" >/dev/null 2>&1 || true
  fi

  SUMMARY_ARGS=()
  if [[ -s "${RUNTIME_METRICS_PROM}" ]]; then
    SUMMARY_ARGS+=(--metrics-input "${RUNTIME_METRICS_PROM}")
  fi
  if [[ -n "${SERVE_LOG}" && -s "${SERVE_LOG}" ]]; then
    start_offset="0"
    if [[ -s "${RUNTIME_SERVE_LOG_OFFSET_FILE}" ]]; then
      start_offset="$(cat "${RUNTIME_SERVE_LOG_OFFSET_FILE}")"
    fi
    if [[ ! "${start_offset}" =~ ^[0-9]+$ ]]; then
      start_offset="0"
    fi
    current_size="$(wc -c < "${SERVE_LOG}" | tr -d '[:space:]')"
    if [[ "${current_size}" =~ ^[0-9]+$ && "${current_size}" -ge "${start_offset}" ]]; then
      tail -c "+$((start_offset + 1))" "${SERVE_LOG}" > "${RUNTIME_SERVE_LOG_SLICE}" 2>/dev/null || true
    else
      cp "${SERVE_LOG}" "${RUNTIME_SERVE_LOG_SLICE}" 2>/dev/null || true
    fi
    if [[ -s "${RUNTIME_SERVE_LOG_SLICE}" ]]; then
      SUMMARY_ARGS+=(--serve-log "${RUNTIME_SERVE_LOG_SLICE}")
    fi
  fi
  if [[ "${#SUMMARY_ARGS[@]}" -gt 0 ]]; then
    "${PYTHON}" -m ds4_harness.cli runtime-summary \
      "${SUMMARY_ARGS[@]}" \
      --json-output "${OUT_DIR}/runtime_stats_summary.json" \
      --markdown-output "${OUT_DIR}/runtime_stats_summary.md" \
      >/dev/null || true
  fi
}
