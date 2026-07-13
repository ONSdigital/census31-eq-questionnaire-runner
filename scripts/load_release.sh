#!/usr/bin/env bash

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "${DIR}"/.. || exit

if [ $# -eq 0 ] || [ "$1" == "" ] && [ "$2" == "" ]; then
    echo "Usage: load_release.sh {REPO_NAME} {TAG_NAME} [TARGET_DIR]"
elif [ "$2" == "" ]; then
    REPO_NAME="$1"
    TAG_NAME=$(curl "https://api.github.com/repos/${REPO_NAME}/releases" | jq '.[0].name' | tr -d '"')
else
    REPO_NAME="$1"
    TAG_NAME="$2"
    TARGET_DIR="$3"
fi

DOWNLOAD_URL=$(curl "https://api.github.com/repos/${REPO_NAME}/releases/tags/${TAG_NAME}" | jq '.assets[0].browser_download_url' | tr -d '"')
RELEASE_NAME=${DOWNLOAD_URL##*/}

echo "Fetching ${DOWNLOAD_URL}"

TEMP_DIR=$(mktemp -d)

curl -L --url "https://github.com/${REPO_NAME}/releases/download/${TAG_NAME}/${RELEASE_NAME}" --output "${TEMP_DIR}/${RELEASE_NAME}"

if [ -n "${TARGET_DIR}" ]; then
    unzip -o "${TEMP_DIR}/${RELEASE_NAME}" -d "${TEMP_DIR}/extracted"
    mkdir -p "${TARGET_DIR}"
    cp -r "${TEMP_DIR}/extracted/schemas/." "${TARGET_DIR}/"
else
    unzip -o "${TEMP_DIR}/${RELEASE_NAME}" -d ./
fi

rm -rf "${TEMP_DIR}"
