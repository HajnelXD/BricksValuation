#!/usr/bin/env bash
docker compose run -e NODE_ENV=test --rm frontend sh -c "cd /app && yarn test:unit"
