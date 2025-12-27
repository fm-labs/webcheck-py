#!/bin/bash

set -x

WEBCHECK_DATA_DIR=${WEBCHECK_DATA_DIR:-"./data"}

EASYLIST_URL="https://easylist.to/easylist/easylist.txt"
EASYLISTP_URL="https://easylist.to/easylist/easyprivacy.txt"
COOKIEMONSTER_URL="https://secure.fanboy.co.nz/fanboy-cookiemonster.txt"
OUTPUT_DIR="${WEBCHECK_DATA_DIR}/adblock"

curl -L -o "$OUTPUT_DIR/easylist.txt" "$EASYLIST_URL"
curl -L -o "$OUTPUT_DIR/easyprivacy.txt" "$EASYLISTP_URL"
curl -L -o "$OUTPUT_DIR/cookiemonster.txt" "$COOKIEMONSTER_URL"