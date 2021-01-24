#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

: ${REVISION_FRONTEND:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "frontend:$REVISION_FRONTEND" --tag "frontend:latest" --progress plain .
docker tag "frontend:latest" "$REGISTRY/frontend:latest"
docker tag "frontend:$REVISION_FRONTEND" "$REGISTRY/frontend:$REVISION_FRONTEND"
docker push "$REGISTRY/frontend:latest"
docker push "$REGISTRY/frontend:$REVISION_FRONTEND"
