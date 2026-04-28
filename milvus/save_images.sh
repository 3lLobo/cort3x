#!/usr/bin/env bash
set -euo pipefail

# Usage:
# ./export-compose-images.sh [docker-compose.yml]
#
# Reads image references from docker-compose.yml,
# pulls them, then saves all images into one tar
# in the current directory.

COMPOSE_FILE="${1:-docker-compose.yml}"

if [[ ! -f "$COMPOSE_FILE" ]]; then
    echo "Error: File not found: $COMPOSE_FILE"
    exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: docker is not installed."
    exit 1
fi

# Prefer docker compose parser if available
if docker compose version >/dev/null 2>&1; then
    echo "Reading images via docker compose..."
    mapfile -t IMAGES < <(docker compose -f "$COMPOSE_FILE" config --images | sort -u)
else
    echo "docker compose not available, using yaml grep fallback..."
    mapfile -t IMAGES < <(
        grep -E '^[[:space:]]*image:' "$COMPOSE_FILE" \
        | sed -E 's/^[[:space:]]*image:[[:space:]]*//g' \
        | tr -d '"' \
        | sort -u
    )
fi

if [[ ${#IMAGES[@]} -eq 0 ]]; then
    echo "No images found."
    exit 1
fi

echo "Found images:"
printf ' - %s\n' "${IMAGES[@]}"

echo
echo "Pulling images..."
for img in "${IMAGES[@]}"; do
    echo "Pulling $img"
    docker pull "$img"
done

STAMP="$(date +%Y%m%d_%H%M%S)"
OUTFILE="docker-images-${STAMP}.tar"

echo
echo "Saving images to $OUTFILE ..."
docker save -o "$OUTFILE" "${IMAGES[@]}"

echo "Done."
echo "Created: $OUTFILE"
