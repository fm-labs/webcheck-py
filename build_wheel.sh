#!/bin/bash

rm -rf dist/
mkdir -p ./dist/

echo "Building wheel..."
uv build --wheel
