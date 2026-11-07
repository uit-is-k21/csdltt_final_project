# csdltt_final_project

Demo for the *Advanced Database Systems* class (UIT): an AI agent (Claude Code) debugging and fixing a
broken [Bauplan](https://www.bauplanlabs.com) data pipeline. The pipeline breaks because the **data**
changes upstream, not because the code does.

## Repository layout

| Path | Content |
|---|---|
| `pipeline/` | Bauplan project `ecommerce_analytics`: `sessions_feed` → `purchase_events` → `purchases_by_segment` → `daily_segment_stats`, plus expectations (data quality checks) in `expectations.py` |
| `upstream_feed/` | Original upstream feed project. Writes `sessions_feed` from `bauplan.ecommerce_sessions` (2019-10-01..07); parameter `event_case` (`lower` / `upper`) simulates a bad upstream release |
| `demo_v2/upstream_feed_v2/` | Dated feed: dates shifted to `2026-11-xx`; parameters `upto` (keep rows with date <= `upto`) and `upper_days` (uppercase `event_type` on the listed dates) |
| `demo_v2/feed_05_thang_11`, `feed_06_thang_11`, `feed_07_thang_11` | Per-day copies of the v2 feed project used in rehearsals |
| `demo_v2/day_05.sh`, `day_06.sh`, `day_07.sh` | Load the feed for each day into the demo data branch |
| `demo_v2/report.sh` | Query `daily_segment_stats` grouped by date |
| `demo_v2/run_pipeline.sh` | Run the pipeline and log the job |
| `CLAUDE.md` | Rules the agent must follow (never touch Bauplan `main`, explicit `--from-ref`, commit every change, ...) |

## The scenario

The pipeline filters `event_type = 'purchase'`. On day 06 upstream starts sending `PURCHASE` (upper case).
The filter matches nothing for that day, so the report silently loses it.

The expectation `test_report_covers_latest_day` catches this: the max `date` in `daily_segment_stats` must equal
the latest day in `sessions_feed`, otherwise the job fails with `report missing latest day <date>`.

| Day | Feed | Pipeline | Report |
|---|---|---|---|
| 05 | `upto=2026-11-05` | green | 01..05 |
| 06 | `upto=2026-11-06`, `upper_days=2026-11-06` | **fails** on `test_report_covers_latest_day` | still 01..05 |
| 07 | `upto=2026-11-07`, `upper_days=2026-11-06` | green | 01..05 and 07, **no 06** (silent gap) |

The bug is intentionally left unfixed. The agent is meant to find it with the `bauplan-debug-and-fix-pipeline`
workflow. A valid fix must work for both the failed data and the current upstream data, so the pipeline should be
case-insensitive on `event_type` rather than matching one exact value.

## Running the demo

Requires the [Bauplan CLI](https://docs.bauplanlabs.com) (logged in) and access to `bauplan.ecommerce_sessions`.
Never run anything on Bauplan `main`; use a dedicated branch created with an explicit `--from-ref`.

```zsh
bauplan branch create cuong-phung-uit.ecommerce-pipeline-4 --from-ref main

cd demo_v2
./day_05.sh
bauplan run --project-dir ../pipeline --ref cuong-phung-uit.ecommerce-pipeline-4
./report.sh

./day_06.sh
bauplan run --project-dir ../pipeline --ref cuong-phung-uit.ecommerce-pipeline-4   # fails on purpose
./report.sh
```

The `day_*.sh` scripts contain absolute paths from the author's machine. Edit the `--project-dir` and `--ref`
values to match yours.
