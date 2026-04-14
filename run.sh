#!/bin/bash
set -e

docker build -t mmm-guildin_1 .

docker run -p 8501:8501 \
  --env-file .env \
  -v "$(pwd)/datasets:/app/datasets" \
  -v "$(pwd)/data:/app/data" \
  mmm-guildin_1
