#!/usr/bin/env bash

set -e

# Start all services in the background
docker compose up -d

# Wait for services to be healthy/ready (give them time to start)
echo "Waiting for services to be ready..."
sleep 15
# Clear database before tests
echo "Clearing database before E2E tests..."
docker compose exec -T backend python manage.py flush --no-input || true

# Run E2E tests
docker compose exec -e NODE_ENV=test frontend sh -c "cd /app && yarn test:e2e:headless"
TEST_EXIT_CODE=$?

# Clear database after tests
echo "Clearing database after E2E tests..."
docker compose exec -T backend python manage.py flush --no-input || true

# Stop all services
docker compose down

exit $TEST_EXIT_CODE
