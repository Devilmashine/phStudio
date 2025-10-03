#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DOCS_DIR="${PROJECT_ROOT}/docs/legal"
TARGET_DIRS=(
  "${PROJECT_ROOT}/public/legal"
  "${PROJECT_ROOT}/frontend/public/legal"
)

shopt -s nullglob
for source_file in "${DOCS_DIR}"/*.html; do
  filename="$(basename "${source_file}")"
  for target_dir in "${TARGET_DIRS[@]}"; do
    mkdir -p "${target_dir}"
    cp "${source_file}" "${target_dir}/${filename}"
  done
  echo "Copied ${filename}"
done
shopt -u nullglob

printf 'Legal documents updated in:\n'
for target_dir in "${TARGET_DIRS[@]}"; do
  printf '  - %s\n' "${target_dir}"
done
