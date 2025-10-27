#!/usr/bin/env bash

# Start all services in the background
docker compose up -d

# Wait for services to be healthy/ready (give them time to start)
echo "Waiting for services to be ready..."
sleep 30

# Run E2E tests
docker compose exec -e NODE_ENV=test frontend sh -c "cd /app && yarn install && yarn test:e2e:headless"
TEST_EXIT_CODE=$?

# Stop all services
docker compose down

exit $TEST_EXIT_CODE
