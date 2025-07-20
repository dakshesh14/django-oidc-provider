#!/usr/bin/env bash

set -e

docker compose -f production.compose.yml exec django python manage.py createsuperuser
