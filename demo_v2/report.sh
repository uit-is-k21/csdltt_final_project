#!/bin/zsh
# Usage: BAUPLAN_BRANCH=<your-username>.ecommerce-pipeline-4 ./report.sh
DIR="${0:A:h}"
BRANCH="${BAUPLAN_BRANCH:?set BAUPLAN_BRANCH to your data branch}"
bauplan query "SELECT date, COUNT(*) AS segments, SUM(total_purchases) AS purchases FROM daily_segment_stats GROUP BY date ORDER BY date" --ref "$BRANCH"
