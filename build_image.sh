#!/bin/bash

docker buildx build \
  -t webcheck-py \
  --progress=plain \
  --platform linux/amd64,linux/arm64 \
  -f ./Dockerfile \
  .