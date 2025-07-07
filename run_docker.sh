#!/bin/bash

set -e

IMAGE_NAME="dps-app"
PORT=8000

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Running Docker container..."
docker run -p $PORT:$PORT $IMAGE_NAME
