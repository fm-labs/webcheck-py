#!/bin/bash

set -x

EASYLIST_URL="https://easylist.to/easylist/easylist.txt"
EASYLISTP_URL="https://easylist.to/easylist/easyprivacy.txt"
COOKIEMONSTER_URL="https://secure.fanboy.co.nz/fanboy-cookiemonster.txt"
OUTPUT_DIR="./data/adblock"

curl -L -o "$OUTPUT_DIR/easylist.txt" "$EASYLIST_URL"
curl -L -o "$OUTPUT_DIR/easyprivacy.txt" "$EASYLISTP_URL"
curl -L -o "$OUTPUT_DIR/cookiemonster.txt" "$COOKIEMONSTER_URL"