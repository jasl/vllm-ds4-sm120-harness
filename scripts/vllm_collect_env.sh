collect_vllm_env() {
  local enabled="${VLLM_COLLECT_ENV:-1}"
  if [[ "${enabled}" == "0" || "${enabled}" == "false" ]]; then
    printf '%s\n' "disabled" > "${OUT_DIR}/vllm_collect_env.skipped"
    return 0
  fi

  local url="${VLLM_COLLECT_ENV_URL:-https://raw.githubusercontent.com/vllm-project/vllm/main/vllm/collect_env.py}"
  local download_timeout="${VLLM_COLLECT_ENV_DOWNLOAD_TIMEOUT:-30}"
  local run_timeout="${VLLM_COLLECT_ENV_TIMEOUT:-180}"
  local script_path="${OUT_DIR}/vllm_collect_env.py"
  local output_path="${OUT_DIR}/vllm_collect_env.txt"
  local error_path="${OUT_DIR}/vllm_collect_env.err"
  local exit_code_path="${OUT_DIR}/vllm_collect_env.exit_code"
  local sha_path="${OUT_DIR}/vllm_collect_env.sha256"

  mkdir -p "${OUT_DIR}"
  if command -v curl >/dev/null 2>&1; then
    if ! curl -fsSL --max-time "${download_timeout}" -o "${script_path}" "${url}" > "${OUT_DIR}/vllm_collect_env.download.log" 2>&1; then
      printf '%s\n' "download_failed" > "${exit_code_path}"
      printf 'failed to download %s\n' "${url}" > "${OUT_DIR}/vllm_collect_env.skipped"
      return 0
    fi
  elif command -v wget >/dev/null 2>&1; then
    if ! wget -q -T "${download_timeout}" -O "${script_path}" "${url}" > "${OUT_DIR}/vllm_collect_env.download.log" 2>&1; then
      printf '%s\n' "download_failed" > "${exit_code_path}"
      printf 'failed to download %s\n' "${url}" > "${OUT_DIR}/vllm_collect_env.skipped"
      return 0
    fi
  else
    printf '%s\n' "download_tool_missing" > "${exit_code_path}"
    printf '%s\n' "curl and wget are unavailable" > "${OUT_DIR}/vllm_collect_env.skipped"
    return 0
  fi

  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "${script_path}" > "${sha_path}" 2>/dev/null || true
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "${script_path}" > "${sha_path}" 2>/dev/null || true
  fi

  set +e
  if command -v timeout >/dev/null 2>&1; then
    timeout "${run_timeout}" "${PYTHON}" "${script_path}" > "${output_path}" 2> "${error_path}"
  else
    "${PYTHON}" "${script_path}" > "${output_path}" 2> "${error_path}"
  fi
  local code="$?"
  set -e
  printf '%s\n' "${code}" > "${exit_code_path}"
  return 0
}
