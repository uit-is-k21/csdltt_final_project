#!/bin/zsh
echo "=== Pipeline ngày $1 ==="
bauplan run --project-dir pipeline --ref cuong-phung-uit.ecommerce-pipeline-6
echo "--- $1 ---" >> ../demo_v2/runs.log
bauplan job ls --kind run --max-count 1 | tee -a ../demo_v2/runs.log
