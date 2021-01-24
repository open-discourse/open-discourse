#!/bin/bash

echo "Make sure to be logged into the github package registry"

cd database
chmod +x build_and_push.sh
./build_and_push.sh

cd ../frontend
chmod +x build_and_push.sh
./build_and_push.sh

cd ../graphql
chmod +x build_and_push.sh
./build_and_push.sh

cd ../proxy
chmod +x build_and_push.sh
./build_and_push.sh
