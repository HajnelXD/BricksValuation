#!/usr/bin/env bash
docker compose run --rm frontend sh -c "yarn lint --fix && yarn prettier --write ."
