#!/bin/bash

echo "Make sure to be logged into the github package registry"

REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

cd database
: ${REVISION_DATABASE:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "database:$REVISION_DATABASE" --tag "database:latest" --progress plain .
docker tag "database:latest" "$REGISTRY/database:latest"
docker tag "database:$REVISION_DATABASE" "$REGISTRY/database:$REVISION_DATABASE"
docker push "$REGISTRY/database:latest"
docker push "$REGISTRY/database:$REVISION_DATABASE"

cd ../frontend
: ${REVISION_FRONTEND:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "frontend:$REVISION_FRONTEND" --tag "frontend:latest" --progress plain .
docker tag "frontend:latest" "$REGISTRY/frontend:latest"
docker tag "frontend:$REVISION_FRONTEND" "$REGISTRY/frontend:$REVISION_FRONTEND"
docker push "$REGISTRY/frontend:latest"
docker push "$REGISTRY/frontend:$REVISION_FRONTEND"

cd ../proxy
: ${REVISION_PROXY:="$(node -p "require('./package.json').version")"}
docker build --file Dockerfile.prod --tag "proxy:$REVISION_PROXY" --tag "proxy:latest" --progress plain .
docker tag "proxy:latest" "$REGISTRY/proxy:latest"
docker tag "proxy:$REVISION_PROXY" "$REGISTRY/proxy:$REVISION_PROXY"
docker push "$REGISTRY/proxy:latest"
docker push "$REGISTRY/proxy:$REVISION_PROXY"
