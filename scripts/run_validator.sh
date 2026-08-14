#!/usr/bin/env bash
tag=update-list-of-valid-themes
TAG=${tag} docker compose -f docker-compose-schema-validator.yml pull
TAG=${tag} docker compose -f docker-compose-schema-validator.yml up -d
