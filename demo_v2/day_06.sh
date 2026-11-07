#!/bin/zsh
# Usage: BAUPLAN_BRANCH=<your-username>.ecommerce-pipeline-4 ./day_06.sh
DIR="${0:A:h}"
BRANCH="${BAUPLAN_BRANCH:?set BAUPLAN_BRANCH to your data branch}"
bauplan run --project-dir "$DIR/upstream_feed_v2" --ref "$BRANCH" --param upto=2026-11-06 --param upper_days=2026-11-06
