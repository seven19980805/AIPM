#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
RELEASE_DIR="${ROOT_DIR}/release"
PACKAGE_DIR="${RELEASE_DIR}/aipm-docker-deploy-${STAMP}"

mkdir -p "${PACKAGE_DIR}/images" "${PACKAGE_DIR}/data/prd_docs" "${PACKAGE_DIR}/data/design_docs" "${PACKAGE_DIR}/recordings"
cp -R "${ROOT_DIR}/data/PRD_template" "${PACKAGE_DIR}/data/PRD_template"

cp "${ROOT_DIR}/deploy/docker/docker-compose.yml" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/.env.docker.example" "${PACKAGE_DIR}/"
cp "${ROOT_DIR}/deploy/docker/部署说明.md" "${PACKAGE_DIR}/"

if [ -f "${ROOT_DIR}/aipm_images.tar" ]; then
  cp "${ROOT_DIR}/aipm_images.tar" "${PACKAGE_DIR}/images/aipm_images.tar"
fi

tar -czf "${PACKAGE_DIR}.tar.gz" -C "${RELEASE_DIR}" "$(basename "${PACKAGE_DIR}")"

echo "Deployment package created:"
echo "${PACKAGE_DIR}.tar.gz"
if [ ! -f "${PACKAGE_DIR}/images/aipm_images.tar" ]; then
  echo "Note: images/aipm_images.tar is not included because ${ROOT_DIR}/aipm_images.tar was not found."
fi
