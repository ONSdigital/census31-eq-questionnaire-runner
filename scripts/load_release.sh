#!/usr/bin/env bash

set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "${DIR}"/.. || exit

GITHUB_API_VERSION="2026-03-10"

GITHUB_API_HEADERS=(
    -H "Accept: application/vnd.github+json"
    -H "X-GitHub-Api-Version: ${GITHUB_API_VERSION}"
)

if [ -n "${GITHUB_PAT:-}" ]; then
    echo "Using provided GITHUB_PAT for authenticated API requests"
    GITHUB_API_HEADERS+=(
        -H "Authorization: Bearer ${GITHUB_PAT}"
    )
fi

REPO_NAME="${1:-}"
ASSET_NAME="${2:-}"
TAG_NAME="${3:-}"

if [ -z "${REPO_NAME}" ] || [ -z "${TAG_NAME}" ] || [ -z "${ASSET_NAME}" ]; then
    echo "Usage: load_release.sh {REPO_NAME} {ASSET_NAME} {TAG_NAME}"
    exit 1
fi

RELEASE_JSON=$(curl -fsSL "${GITHUB_API_HEADERS[@]}" "https://api.github.com/repos/${REPO_NAME}/releases/tags/${TAG_NAME}")

TAG_NAME=$(echo "${RELEASE_JSON}" | jq -r '.tag_name')
RELEASE_NAME=$(echo "${RELEASE_JSON}" | jq -r '.name')
ASSET_ID=$(echo "${RELEASE_JSON}" | jq -r --arg asset_name "${ASSET_NAME}" '.assets[] | select(.name == $asset_name) | .id')

if [ -z "${TAG_NAME}" ] || [ "${TAG_NAME}" = "null" ]; then
    echo "Unable to determine release tag for ${REPO_NAME}" >&2
    exit 1
fi

if [ -z "${ASSET_ID}" ] || [ "${ASSET_ID}" = "null" ] || [ -z "${ASSET_NAME}" ] || [ "${ASSET_NAME}" = "null" ]; then
    echo "No downloadable '${ASSET_NAME}' asset found for ${REPO_NAME} tag ${TAG_NAME}" >&2
    exit 1
fi

echo "Fetching asset '${ASSET_NAME}' from ${REPO_NAME} release '${RELEASE_NAME}' (tag ${TAG_NAME})"

TEMP_DIR=$(mktemp -d)

ASSET_API_HEADERS=("${GITHUB_API_HEADERS[@]}")
ASSET_API_HEADERS[1]="Accept: application/octet-stream"

curl -fL --retry 3 "${ASSET_API_HEADERS[@]}" \
    --url "https://api.github.com/repos/${REPO_NAME}/releases/assets/${ASSET_ID}" \
    --output "${TEMP_DIR}/${ASSET_NAME}"
unzip -o "${TEMP_DIR}/${ASSET_NAME}" -d ./
rm -rf "${TEMP_DIR}"
