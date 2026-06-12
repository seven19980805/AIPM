#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
RELEASE_DIR="${ROOT_DIR}/release"
PACKAGE_DIR="${RELEASE_DIR}/aipm-docker-offline-${STAMP}"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker command not found. Run this script on a machine with Docker installed." >&2
  exit 1
fi

if [ ! -f "${ROOT_DIR}/.env.docker" ]; then
  echo "Missing ${ROOT_DIR}/.env.docker. Copy .env.docker.example to .env.docker and edit it first." >&2
  exit 1
fi

cd "${ROOT_DIR}"
export DOCKER_DEFAULT_PLATFORM="${DOCKER_DEFAULT_PLATFORM:-linux/amd64}"
set -a
# shellcheck disable=SC1091
source "${ROOT_DIR}/.env.docker"
set +a
export VITE_API_BASE_URL="${VITE_API_BASE_URL:-}"
export VITE_GO_CODING_URL="${VITE_GO_CODING_URL:-http://localhost:8888}"

(
  cd "${ROOT_DIR}/frontend"
  npm ci
  npm run build
)

docker compose --env-file .env.docker build

mkdir -p "${PACKAGE_DIR}/images" "${PACKAGE_DIR}/data/prd_docs" "${PACKAGE_DIR}/data/design_docs" "${PACKAGE_DIR}/recordings"
cp -R "${ROOT_DIR}/data/PRD_template" "${PACKAGE_DIR}/data/PRD_template"
docker save -o "${PACKAGE_DIR}/images/aipm_images.tar" localhost/aipm-api:latest localhost/aipm-web:latest

cp "${ROOT_DIR}/deploy/docker/docker-compose.yml" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/.env.docker.example" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/部署说明.md" "${PACKAGE_DIR}/"

tar -czf "${PACKAGE_DIR}.tar.gz" -C "${RELEASE_DIR}" "$(basename "${PACKAGE_DIR}")"

echo "Offline Docker package created:"
echo "${PACKAGE_DIR}.tar.gz"
