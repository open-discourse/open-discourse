#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

: ${REVISION_GRAPHQL:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "graphql:$REVISION_GRAPHQL" --tag "graphql:latest" --progress plain .
docker tag "graphql:latest" "$REGISTRY/graphql:latest"
docker tag "graphql:$REVISION_GRAPHQL" "$REGISTRY/graphql:$REVISION_GRAPHQL"
docker push "$REGISTRY/graphql:latest"
docker push "$REGISTRY/graphql:$REVISION_GRAPHQL"
