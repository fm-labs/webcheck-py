#!/bin/bash

mkdir -p ./build
rm -rf ./build/
mkdir -p ./dist/bin
rm -rf ./dist/bin

uv run pyinstaller --clean --onefile --distpath ./dist/bin --workpath ./build --specpath ./build --name webcheckcli ./src/webcheckcli.py
uv run pyinstaller --clean --onefile --distpath ./dist/bin --workpath ./build --specpath ./build --name webchecksrv ./src/webchecksrv.py
