#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env.docker"
OUTPUT_FILE="${1:-${ROOT_DIR}/aipm_docker_images_$(date +%Y%m%d_%H%M%S).tar}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found. Please run this script on a machine with Docker installed." >&2
  exit 1
fi

if [ ! -f "${ENV_FILE}" ]; then
  echo "Missing ${ENV_FILE}. Copy .env.docker.example to .env.docker and fill it first." >&2
  exit 1
fi

cd "${ROOT_DIR}"
export DOCKER_DEFAULT_PLATFORM="${DOCKER_DEFAULT_PLATFORM:-linux/amd64}"
set -a
# shellcheck disable=SC1090
source "${ENV_FILE}"
set +a
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-}"
export VITE_GO_CODING_URL="${VITE_GO_CODING_URL:-http://localhost:8888}"

(
  cd "${ROOT_DIR}/frontend"
  npm ci
  npm run build
)

docker compose --env-file "${ENV_FILE}" build
docker save -o "${OUTPUT_FILE}" localhost/aipm-api:latest localhost/aipm-web:latest

echo "Exported Docker images to: ${OUTPUT_FILE}"
