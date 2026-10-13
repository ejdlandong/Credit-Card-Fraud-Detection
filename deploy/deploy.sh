#!/bin/bash
set -e

echo "Starting deployment process..."

# 1. Build the new Docker image
echo "Building Docker image: fraud-detection-api..."
docker build -t fraud-detection-api .

# 2. Stop and remove the old container if it exists
if [ "$(docker ps -a -q -f name=fraud-api-server)" ]; then
    echo "Stopping existing fraud-api-server..."
    docker rm -f fraud-api-server
fi

# 3. Run the new container
echo "Launching new container on port 8000..."
docker run -d -p 8000:8000 --name fraud-api-server fraud-detection-api

# 4. Verify health endpoint
echo "Verifying service health..."
sleep 2
response=$(curl -s http://localhost:8000/healthz)

if [[ "$response" == *"ok"* ]]; then
    echo "Deployment successful! Service is healthy: $response"
else
    echo "Deployment failed! Health check response: $response"
    exit 1
fi