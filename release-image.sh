#!/usr/bin/env bash
set -euo pipefail

IMAGE_REPO="${IMAGE_REPO:-docker.staticduo.com/icloudpd}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
DOCKERFILE="${DOCKERFILE:-Dockerfile.local}"
PLATFORM="${PLATFORM:-linux/amd64}"
REGISTRY_HOST="${IMAGE_REPO%%/*}"
REGISTRY_USER="${REGISTRY_USER:-}"
REGISTRY_PASSWORD="${REGISTRY_PASSWORD:-}"

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: docker no está disponible"
  exit 1
fi

if [ -n "${REGISTRY_USER}" ] && [ -n "${REGISTRY_PASSWORD}" ]; then
  echo "${REGISTRY_PASSWORD}" | docker login "${REGISTRY_HOST}" -u "${REGISTRY_USER}" --password-stdin
else
  echo "INFO: sin login explícito para ${REGISTRY_HOST}; se usará la sesión docker actual"
fi

if ! docker buildx inspect icloudpd-builder >/dev/null 2>&1; then
  docker buildx create --name icloudpd-builder --use
else
  docker buildx use icloudpd-builder
fi

SHORT_SHA="$(git rev-parse --short HEAD 2>/dev/null || echo local)"
BRANCH_NAME="$(git branch --show-current 2>/dev/null || echo detached)"
SAFE_BRANCH="$(printf '%s' "${BRANCH_NAME}" | tr '/:@ ' '-' | tr -cd '[:alnum:]._-' )"

docker buildx build \
  --platform "${PLATFORM}" \
  --file "${DOCKERFILE}" \
  --label org.opencontainers.image.source="$(git remote get-url origin 2>/dev/null || true)" \
  --label org.opencontainers.image.revision="$(git rev-parse HEAD 2>/dev/null || true)" \
  --label org.opencontainers.image.version="${IMAGE_TAG}" \
  -t "${IMAGE_REPO}:${IMAGE_TAG}" \
  -t "${IMAGE_REPO}:sha-${SHORT_SHA}" \
  -t "${IMAGE_REPO}:branch-${SAFE_BRANCH}" \
  --push \
  .

echo "Publicado: ${IMAGE_REPO}:${IMAGE_TAG}"
echo "Publicado: ${IMAGE_REPO}:sha-${SHORT_SHA}"
echo "Publicado: ${IMAGE_REPO}:branch-${SAFE_BRANCH}"
