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
