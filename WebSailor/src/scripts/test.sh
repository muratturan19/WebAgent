#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
if [ -f "$ROOT_DIR/.env" ]; then
    set -a
    source "$ROOT_DIR/.env"
    set +a
fi

export MAX_LENGTH=$((1024 * 31 - 500))

cd "$ROOT_DIR/WebSailor/src"

# The arguments are the dataset name and the location of the prediction file.
# bash run.sh <dataset> <output_path>

# Dataset names (strictly match the following names):
# - gaia
# - browsecomp_zh (Full set, 289 Cases)
# - browsecomp_en (Full set, 1266 Cases)
# - xbench-deepsearch
# - sahibinden

# Directory containing the WebSailor-3B model shards.
# This folder must include:
#   - model-00001-of-00002.safetensors
#   - model-00002-of-00002.safetensors
export MODEL_PATH=${MODEL_PATH:-/models}

# Run evaluation using the local model directory for the sahibinden dataset.
bash run.sh sahibinden output_path

