#!/bin/bash

set -xe

export USE_MONGODB=true
export MONGODB_URI="mongodb://webcheck:webcheck@localhost:18017?authSource=admin"

uv run src/webcheckworker.py "$@"
