#!/usr/bin/env sh

set -o errexit
set -o nounset

# Initializing global variables and functions:
: "${DJANGO_ENV:=test}"

# Fail CI if `DJANGO_ENV` is not set to `test`:
if [ "$DJANGO_ENV" != 'test' ]; then
  echo 'DJANGO_ENV is not set to `test`. Running tests is not safe.'
  exit 1
fi

pyclean () {
  # Cleaning cache:
  find . | grep -E '(__pycache__|\.py[cod]$)' | xargs rm -rf
}

run_test () {
  pytest "$@"
}

# Remove any cache before the script:
pyclean

# Clean everything up:
trap pyclean EXIT INT TERM

# Run the CI process:
run_test "$@"
