#!/bin/bash

echo "Make sure to be logged into the github package registry"

: ${REVISION:="$(git rev-parse --short HEAD)"}
REGISTRY="docker.pkg.github.com/open-discourse/open-discourse"

if [ -z "$REVISION" ]; then
  echo "git revision not detected, please make sure to run this build only from git repository"
  exit
fi

cd database
docker build --file Dockerfile.prod --tag "database:$REVISION" --tag "database:latest" --progress plain .
docker tag "database:latest" "$REGISTRY/database:latest"
docker tag "database:$REVISION" "$REGISTRY/database:$REVISION"
docker push "$REGISTRY/database:latest"
docker push "$REGISTRY/database:$REVISION"

cd ../frontend
docker build --file Dockerfile.prod --tag "frontend:$REVISION" --tag "frontend:latest" --progress plain .
docker tag "frontend:latest" "$REGISTRY/frontend:latest"
docker tag "frontend:$REVISION" "$REGISTRY/frontend:$REVISION"
docker push "$REGISTRY/frontend:latest"
docker push "$REGISTRY/frontend:$REVISION"

cd ../graphql
docker build --file Dockerfile.prod --tag "graphql:$REVISION" --tag "graphql:latest" --progress plain .
docker tag "graphql:latest" "$REGISTRY/graphql:latest"
docker tag "graphql:$REVISION" "$REGISTRY/graphql:$REVISION"
docker push "$REGISTRY/graphql:latest"
docker push "$REGISTRY/graphql:$REVISION"

cd ../proxy
docker build --file Dockerfile.prod --tag "proxy:$REVISION" --tag "proxy:latest" --progress plain .
docker tag "proxy:latest" "$REGISTRY/proxy:latest"
docker tag "proxy:$REVISION" "$REGISTRY/proxy:$REVISION"
docker push "$REGISTRY/proxy:latest"
docker push "$REGISTRY/proxy:$REVISION"
