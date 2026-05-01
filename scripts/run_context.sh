load_harness_env() {
  if [[ -f "${REPO_ROOT}/.env" ]]; then
    while IFS= read -r line || [[ -n "${line}" ]]; do
      line="${line#"${line%%[![:space:]]*}"}"
      line="${line%"${line##*[![:space:]]}"}"
      if [[ -z "${line}" || "${line}" == \#* || "${line}" != *=* ]]; then
        continue
      fi
      local key value
      key="${line%%=*}"
      value="${line#*=}"
      if [[ ! "${key}" =~ ^[A-Za-z_][A-Za-z0-9_]*$ ]]; then
        continue
      fi
      if [[ -z "${!key+x}" ]]; then
        export "${key}=${value}"
      fi
    done < "${REPO_ROOT}/.env"
  fi
}

slugify_context_value() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's#[^a-z0-9]+#_#g; s#^_+##; s#_+$##'
}

detect_gpu_topology_slug() {
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    printf '%s\n' "unknown_gpu"
    return 0
  fi

  local names
  names="$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | sed '/^[[:space:]]*$/d' || true)"
  if [[ -z "${names}" ]]; then
    printf '%s\n' "unknown_gpu"
    return 0
  fi

  local parts=()
  while IFS= read -r line; do
    local count name slug
    count="$(printf '%s' "${line}" | awk '{print $1}')"
    name="$(printf '%s' "${line}" | sed -E 's/^[[:space:]]*[0-9]+[[:space:]]+//')"
    slug="$(slugify_context_value "${name}")"
    parts+=("${count}x_${slug:-unknown}")
  done < <(printf '%s\n' "${names}" | sort | uniq -c)

  local joined=""
  local part
  for part in "${parts[@]}"; do
    if [[ -n "${joined}" ]]; then
      joined+="__"
    fi
    joined+="${part}"
  done
  printf '%s\n' "${joined:-unknown_gpu}"
}

write_run_environment() {
  "${PYTHON}" -m ds4_harness.cli env-summary \
    --json-output "${OUT_DIR}/run_environment.json" \
    --markdown-output "${OUT_DIR}/run_environment.md" \
    >/dev/null || true
}

server_ready() {
  if [[ "${SERVER_GUARD:-1}" == "0" ]]; then
    return 0
  fi

  "${PYTHON}" -m ds4_harness.cli health \
    --base-url "${BASE_URL}" \
    --timeout "${SERVER_HEALTH_TIMEOUT:-10}" \
    > "${OUT_DIR}/server_health_last.jsonl" \
    2> "${OUT_DIR}/server_health_last.err"
}

wait_for_server_ready() {
  local timeout_seconds="${1:-${SERVER_STARTUP_TIMEOUT:-1800}}"
  local interval_seconds="${2:-${SERVER_STARTUP_INTERVAL_SECONDS:-15}}"
  local label="${3:-server startup}"

  if [[ "${SERVER_GUARD:-1}" == "0" ]]; then
    return 0
  fi

  local started now elapsed
  started="$(date +%s)"
  while true; do
    if server_ready; then
      printf '[%s] %s ready after %ss\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${label}" "$(( $(date +%s) - started ))" \
        >> "${OUT_DIR}/server_wait.log"
      return 0
    fi

    now="$(date +%s)"
    elapsed="$((now - started))"
    if (( elapsed >= timeout_seconds )); then
      printf '[%s] %s not ready after %ss\n' \
        "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${label}" "${elapsed}" \
        >> "${OUT_DIR}/server_wait.log"
      return 1
    fi

    printf '[%s] waiting for %s: elapsed=%ss timeout=%ss\n' \
      "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${label}" "${elapsed}" "${timeout_seconds}" \
      >> "${OUT_DIR}/server_wait.log"
    sleep "${interval_seconds}"
  done
}

run_server_recovery() {
  if [[ -z "${SERVER_RECOVERY_CMD:-}" ]]; then
    return 0
  fi

  {
    printf '[%s] running SERVER_RECOVERY_CMD\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    bash -lc "${SERVER_RECOVERY_CMD}"
    printf '[%s] SERVER_RECOVERY_CMD finished\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } >> "${OUT_DIR}/server_recovery.log" 2>&1 || true
}

mark_server_unresponsive() {
  local gate_name="${1:-unknown_gate}"
  local detail="${2:-server unresponsive}"

  {
    printf '[%s] %s: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "${gate_name}" "${detail}"
  } >> "${OUT_DIR}/server_unresponsive.txt"
  printf '%s\n' "${detail}" > "${OUT_DIR}/${gate_name}.server_unresponsive"
  run_server_recovery
}
