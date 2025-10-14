#!/usr/bin/env bash
cp env/.backend-env-local env/.backend-env

docker compose build
