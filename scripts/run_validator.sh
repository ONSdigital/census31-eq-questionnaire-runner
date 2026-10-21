#!/usr/bin/env bash
tag=pr-83-CTE-342-introduce-schemas-version-into-each-built-schema-in-schemas-zip-release
TAG=${tag} docker compose -f docker-compose-schema-validator.yml pull
TAG=${tag} docker compose -f docker-compose-schema-validator.yml up -d
