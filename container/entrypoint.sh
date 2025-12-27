#!/bin/bash

CMD=${1:-"scan"}
shift

case $CMD in
  "webcheckcli")
    /usr/local/bin/webcheckcli $@
    ;;
  "webchecksrv")
    /usr/local/bin/webchecksrv $@
    ;;
  *)
    echo "Unknown command: $CMD"
    exit 1
    ;;
esac
