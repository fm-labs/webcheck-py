#!/bin/bash

TRANCO_LIST_URL="https://tranco-list.eu/download/NN23W/1000000"
TRANCO_OUTPUT_FILE="./data/tranco-1m.csv"

UMBRELLA_DL_URL="https://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
UMBRELLA_OUTPUT_FILE="./data/top-1m.csv"

echo "Downloading Tranco list from $TRANCO_LIST_URL ..."
if [ ! -f $TRANCO_OUTPUT_FILE ]; then
  curl -L -o "$TRANCO_OUTPUT_FILE" "$TRANCO_LIST_URL"
  echo "Tranco list downloaded to $TRANCO_OUTPUT_FILE"
fi

echo "Downloading Umbrella list from $UMBRELLA_DL_URL ..."
if [ ! -f $UMBRELLA_OUTPUT_FILE ]; then
  curl -L -o "./data/top-1m.csv.zip" "$UMBRELLA_DL_URL"
  unzip -o "./data/top-1m.csv.zip" -d "./data/"

  if [[ ! -f $UMBRELLA_OUTPUT_FILE ]]; then
    echo "Error: Failed to extract Umbrella list to $UMBRELLA_OUTPUT_FILE"
    exit 1
  fi
  echo "Umbrella list downloaded and extracted to $UMBRELLA_OUTPUT_FILE"
fi






# the csv format is:
# rank,domain
# 1,google.com
# 2,facebook.com

# strip the rank and keep only the domain names
#tail -n +2 "$TRANCO_OUTPUT_FILE" | cut -d',' -f2 > "${TRANCO_OUTPUT_FILE%.csv}_domains.txt"
#echo "Domain names extracted to ${TRANCO_OUTPUT_FILE%.csv}_domains.txt"
#
#if [ $1 == "--scan" ]; then
#  # iterate through each domain and run xscan
#  while IFS= read -r domain; do
#    echo "Scanning domain: $domain"
#    uv run ./src/webcheckcli.py "$domain"
#    #sleep 1  # brief pause between scans
#  done < "${TRANCO_OUTPUT_FILE%.csv}_domains.txt"
#fi