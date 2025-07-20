#!/usr/bin/env bash

set -e

TEMPLATE_FILE="$1"
OUTPUT_FILE="$2"
shift 2

# Load key=value arguments into environment
for ARG in "$@"; do
  export "$ARG"
done

# Copy template to temp file for editing
TMP_FILE=$(mktemp)
cp "$TEMPLATE_FILE" "$TMP_FILE"

# Replace all {{ VAR }} placeholders with env values
for VAR in $(env | cut -d= -f1); do
  sed -i "s|{{ $VAR }}|${!VAR}|g" "$TMP_FILE"
done

# Move final result
mv "$TMP_FILE" "$OUTPUT_FILE"
