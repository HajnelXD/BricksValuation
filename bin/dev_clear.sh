#!/bin/sh
set -e
{
  docker compose stop
  docker compose rm -svf
} || {
  docker-compose stop
  docker-compose rm -svf
}
docker volume list | egrep 'bricksvaluation-.+data' | awk '{ print $2 }' | xargs docker volume rm
docker volume list | egrep 'bricksvaluation_.+data' | awk '{ print $2 }' | xargs docker volume rm
docker images | egrep 'bricksvaluation-.+' | awk '{ print $1 }' | xargs docker rmi -f || true
docker images | egrep 'bricksvaluation_.+' | awk '{ print $1 }' | xargs docker rmi -f || true
rm env/.backend-env s