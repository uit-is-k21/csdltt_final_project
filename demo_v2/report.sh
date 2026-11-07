#!/bin/zsh
bauplan query "SELECT date, COUNT(*) AS segments, SUM(total_purchases) AS purchases FROM daily_segment_stats GROUP BY date ORDER BY date" --ref cuong-phung-uit.ecommerce-pipeline-6
