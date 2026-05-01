GPU_STATS="${GPU_STATS:-1}"
GPU_STATS_INTERVAL_SECONDS="${GPU_STATS_INTERVAL_SECONDS:-1}"
GPU_STATS_QUERY="${GPU_STATS_QUERY:-timestamp,index,name,memory.used,memory.total,power.draw,power.limit,utilization.gpu}"
GPU_STATS_CSV="${OUT_DIR}/gpu_stats.csv"
GPU_STATS_ERR="${OUT_DIR}/gpu_stats.err"
GPU_STATS_PID=""

start_gpu_stats() {
  if [[ "${GPU_STATS}" != "1" && "${GPU_STATS}" != "true" ]]; then
    return 0
  fi

  if ! command -v nvidia-smi >/dev/null 2>&1; then
    printf '%s\n' "nvidia-smi is not available; GPU stats were not captured." \
      > "${OUT_DIR}/gpu_stats_unavailable.txt"
    return 0
  fi

  nvidia-smi \
    --query-gpu="${GPU_STATS_QUERY}" \
    --format=csv,nounits \
    -l "${GPU_STATS_INTERVAL_SECONDS}" \
    > "${GPU_STATS_CSV}" \
    2> "${GPU_STATS_ERR}" &
  GPU_STATS_PID="$!"
}

stop_gpu_stats() {
  if [[ -n "${GPU_STATS_PID}" ]]; then
    kill "${GPU_STATS_PID}" >/dev/null 2>&1 || true
    wait "${GPU_STATS_PID}" >/dev/null 2>&1 || true
  fi

  if [[ -s "${GPU_STATS_CSV}" ]]; then
    "${PYTHON}" -m ds4_harness.cli gpu-summary \
      --csv-input "${GPU_STATS_CSV}" \
      --json-output "${OUT_DIR}/gpu_stats_summary.json" \
      --markdown-output "${OUT_DIR}/gpu_stats_summary.md" \
      >/dev/null || true
  fi
}
