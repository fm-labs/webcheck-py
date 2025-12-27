#!/bin/bash

CMD=${1:-"scan"}
shift

case $CMD in
  "scan")
    /usr/local/bin/webcheckcli $@
    ;;
  "server")
    /usr/local/bin/webchecksrv $@
    ;;
  "serve")
    uv run uvicorn --app-dir /app --port 8000 --host 0.0.0.0 --no-cache-dir webchecksrv:app
    ;;
  *)
    echo "Unknown command: $CMD"
    exit 1
    ;;
esac