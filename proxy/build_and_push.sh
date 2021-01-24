#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

: ${REVISION_PROXY:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "proxy:$REVISION_PROXY" --tag "proxy:latest" --progress plain .
docker tag "proxy:latest" "$REGISTRY/proxy:latest"
docker tag "proxy:$REVISION_PROXY" "$REGISTRY/proxy:$REVISION_PROXY"
docker push "$REGISTRY/proxy:latest"
docker push "$REGISTRY/proxy:$REVISION_PROXY"
