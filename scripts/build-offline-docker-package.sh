#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-${ROOT_DIR}/.env.docker}"
export ENV_FILE
STAMP="$(date +%Y%m%d_%H%M%S)"
RELEASE_DIR="${ROOT_DIR}/release"
PACKAGE_DIR="${RELEASE_DIR}/aipm-docker-offline-${STAMP}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found. Run this script on a machine with Docker installed." >&2
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "Missing ${ENV_FILE}. Copy deploy/docker/.env.docker.example and edit it first." >&2
  exit 1
fi

cd "${ROOT_DIR}"
set -a
# shellcheck disable=SC1091
source "${ENV_FILE}"
set +a
export DOCKER_DEFAULT_PLATFORM="${DOCKER_PLATFORM:-${DOCKER_DEFAULT_PLATFORM:-linux/amd64}}"
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-}"
export VITE_GO_CODING_URL="${VITE_GO_CODING_URL:-http://localhost:8888}"

docker compose --env-file "${ENV_FILE}" build

mkdir -p "${PACKAGE_DIR}/images" "${PACKAGE_DIR}/data/prd_docs" "${PACKAGE_DIR}/data/design_docs" "${PACKAGE_DIR}/recordings"
cp -R "${ROOT_DIR}/data/PRD_template" "${PACKAGE_DIR}/data/PRD_template"
cp -R "${ROOT_DIR}/data/ic_substrate" "${PACKAGE_DIR}/data/ic_substrate"
docker save -o "${PACKAGE_DIR}/images/aipm_images.tar" localhost/aipm-api:latest localhost/aipm-web:latest

cp "${ROOT_DIR}/deploy/docker/docker-compose.yml" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/.env.docker.example" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/部署说明.md" "${PACKAGE_DIR}/"
if [ -f "${ROOT_DIR}/deploy/IC_Substrate_专家PM验收说明.md" ]; then
  cp "${ROOT_DIR}/deploy/IC_Substrate_专家PM验收说明.md" "${PACKAGE_DIR}/"
fi

tar -czf "${PACKAGE_DIR}.tar.gz" -C "${RELEASE_DIR}" "$(basename "${PACKAGE_DIR}")"

echo "Offline Docker package created:"
echo "${PACKAGE_DIR}.tar.gz"
