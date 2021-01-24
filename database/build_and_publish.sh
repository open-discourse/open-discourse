#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

: ${REVISION_DATABASE:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "database:$REVISION_DATABASE" --tag "database:latest" --progress plain .
docker tag "database:latest" "$REGISTRY/database:latest"
docker tag "database:$REVISION_DATABASE" "$REGISTRY/database:$REVISION_DATABASE"
docker push "$REGISTRY/database:latest"
docker push "$REGISTRY/database:$REVISION_DATABASE"
