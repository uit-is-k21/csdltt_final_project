#!/bin/zsh
# Usage: BAUPLAN_BRANCH=<your-username>.ecommerce-pipeline-4 ./run_pipeline.sh
DIR="${0:A:h}"
BRANCH="${BAUPLAN_BRANCH:?set BAUPLAN_BRANCH to your data branch}"
# Runs the analytics pipeline on the data branch and appends the job to runs.log.
echo "=== Pipeline run ${1:-} ==="
bauplan run --project-dir "$DIR/../pipeline" --ref "$BRANCH"
echo "--- ${1:-} ---" >> "$DIR/runs.log"
bauplan job ls --kind run --max-count 1 | tee -a "$DIR/runs.log"
