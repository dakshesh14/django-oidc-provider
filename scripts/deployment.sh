#!/usr/bin/env bash

set -e

echo "🚀 Starting production environment..."
docker compose -f production.compose.yml up --build -d
