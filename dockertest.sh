#!/usr/bin/env bash
./prepare_docker.sh
docker-compose -f docker_test/docker-compose.yml build
docker-compose -f docker_test/docker-compose.yml up
