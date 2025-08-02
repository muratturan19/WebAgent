export JINA_KEY="your_jina_key"
export SEARCH_API_URL="your_search_api_url"
export GOOGLE_SEARCH_KEY="your_google_search_key"

export SUMMARY_MODEL_PATH="/path/Qwen2.5-72B-Instruct"
export MAX_LENGTH=$((1024 * 31 - 500))

cd src

# The arguments are the model path, the dataset name, and the location of the prediction file.
# bash run.sh <model_path> <dataset> <output_path>

# Dataset names (strictly match the following names):
# - gaia
# - browsecomp_zh (Full set, 289 Cases)
# - browsecomp_en (Full set, 1266 Cases)
# - xbench-deepsearch

# Directory containing the WebSailor-3B model shards.
# This folder must include:
#   - model-00001-of-00002.safetensors
#   - model-00002-of-00002.safetensors
MODEL_PATH="D:/Mira/WebSailor-3B"

# Run evaluation using the local model directory.
bash run.sh "$MODEL_PATH" gaia output_path
