#!/usr/bin/env bash
docker compose run -e DJANGO_ENV=test --rm backend ./test.sh "$@"