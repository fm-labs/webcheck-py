#!/bin/bash

docker buildx build \
  -t webcheck-py \
  --progress=plain \
  --platform linux/arm64 \
  -f ./Dockerfile \
  .