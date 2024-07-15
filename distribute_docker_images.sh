#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="ghcr.io/open-discourse/open-discourse/open-discourse"

docker buildx create \
  --name container \
  --driver=docker-container 2>/dev/null

cd database
: ${REVISION_DATABASE:="$(node -p "require('./package.json').version")"}
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --file Dockerfile.prod \
  --tag "$REGISTRY/database:$REVISION_DATABASE" --tag "$REGISTRY/database:latest" \
  --builder=container \
  --push \
  --progress plain .

cd ../frontend
: ${REVISION_FRONTEND:="$(node -p "require('./package.json').version")"}
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --file Dockerfile.prod \
  --tag "$REGISTRY/frontend:$REVISION_FRONTEND" --tag "$REGISTRY/frontend:latest" \
  --builder=container \
  --push \
  --progress plain .

cd ../proxy
: ${REVISION_PROXY:="$(node -p "require('./package.json').version")"}
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --file Dockerfile.prod \
  --tag "$REGISTRY/proxy:$REVISION_PROXY" --tag "$REGISTRY/proxy:latest" \
  --builder=container \
  --push \
  --progress plain .
