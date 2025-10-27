#!/usr/bin/env bash
cp env/.backend-env-local env/.backend-env
cp env/.frontend-env-local env/.frontend-env

docker compose build
