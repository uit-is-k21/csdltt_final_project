# csdltt_final_project

Demo for the *Advanced Database Systems* class (UIT): an AI agent (Claude Code) debugging and fixing a
broken [Bauplan](https://www.bauplanlabs.com) data pipeline. The pipeline breaks because the **data**
changes upstream, not because the code does.

Video demo: [https://drive.google.com/file/d/1CXOKRYhPqTe2GYEBgAzMNaObwzCQd8K9/view?usp=sharing](https://drive.google.com/file/d/1CXOKRYhPqTe2GYEBgAzMNaObwzCQd8K9/view?usp=sharing)

## Repository layout

| Path | Content |
|---|---|
| `pipeline/` | Bauplan project `ecommerce_analytics`: `sessions_feed` → `purchase_events` → `purchases_by_segment` → `daily_segment_stats`, plus expectations (data quality checks) in `expectations.py` |
| `upstream_feed/` | Original upstream feed project. Writes `sessions_feed` from `bauplan.ecommerce_sessions` (2019-10-01..07); parameter `event_case` (`lower` / `upper`) simulates a bad upstream release |
| `demo_v2/upstream_feed_v2/` | Dated feed: dates shifted to `2026-11-xx`; parameters `upto` (keep rows with date <= `upto`) and `upper_days` (uppercase `event_type` on the listed dates) |
| `demo_v2/feed_05_thang_11`, `feed_06_thang_11`, `feed_07_thang_11` | Per-day copies of the v2 feed project used in rehearsals |
| `demo_v2/day_05.sh`, `day_06.sh`, `day_07.sh` | Load the feed for each day into your data branch (read `BAUPLAN_BRANCH`) |
| `demo_v2/report.sh` | Query `daily_segment_stats` grouped by date |
| `demo_v2/run_pipeline.sh` | Run the pipeline on your data branch and log the job to `runs.log` |
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

## Running the demo end to end

All commands are for zsh. Replace `YOUR_USERNAME` with your own Bauplan username (shown by `bauplan info`).

### 0. Prerequisites
- Python 3.10+ and the Bauplan CLI (`pip install bauplan`, then check with `bauplan --version`).
- Git, and optionally [Claude Code](https://claude.com/claude-code) for the agent part.

### 1. Get your own Bauplan API key
Do **not** reuse anyone else's key. Create your own:
1. Sign up or log in at <https://app.bauplanlabs.com>.
2. Open your account/profile settings in the web app and create an **API key**. Copy it once; treat it like a password.
3. Give it to the CLI:
   ```zsh
   bauplan config set api_key PASTE_YOUR_API_KEY_HERE
   ```
   Alternatively, export it for the current shell only: `export BAUPLAN_API_KEY=PASTE_YOUR_API_KEY_HERE`.
4. Confirm it works. `bauplan info` must print your username:
   ```zsh
   bauplan info
   ```
Never commit the key. This repo contains no credentials.

You also need read access to the table `bauplan.ecommerce_sessions` on `main`. Check with:
```zsh
bauplan query "SELECT COUNT(*) AS n FROM bauplan.ecommerce_sessions" --ref main
```

### 2. Clone and create an isolated data branch
Never run, write or merge anything on `main`. Reading from `main` is fine.
```zsh
git clone https://github.com/uit-is-k21/csdltt_final_project.git
cd csdltt_final_project
export BAUPLAN_BRANCH=YOUR_USERNAME.ecommerce-pipeline-4
bauplan branch create $BAUPLAN_BRANCH --from-ref main
```
Branch names must start with your username. Always pass `--from-ref` explicitly. The CLI's active branch may point to a deleted branch.
All scripts below read `BAUPLAN_BRANCH`, so keep it exported in this shell.

### 3. Day 05: healthy baseline
```zsh
cd demo_v2
./day_05.sh                 # load feed up to 2026-11-05 into sessions_feed
./run_pipeline.sh day_05    # expected: GREEN
./report.sh                 # expected: 2026-11-01 .. 2026-11-05, 3 segments each
```

### 4. Day 06: the pipeline fails
```zsh
./day_06.sh                 # feed up to 2026-11-06, event_type upper-cased on 2026-11-06
./run_pipeline.sh day_06    # expected: FAILED, "report missing latest day 2026-11-06"
./report.sh                 # unchanged: still 01 .. 05
```
Note the failing job id from the output (also see `bauplan job ls`).

### 5. Day 07: green but wrong (silent gap)
```zsh
./day_07.sh                 # feed up to 2026-11-07, 06 still upper case
./run_pipeline.sh day_07    # expected: GREEN
./report.sh                 # 01 .. 05 and 07, day 06 is MISSING
```
The check passes because the latest day (07) is covered, but 2026-11-06 was dropped. This is why the root cause must be fixed, not just the check.

### 6. Debug and fix with Claude Code
From the repo root (`cd ..`), start Claude Code and install the Bauplan skills plugin (`bauplan@bauplan-skills`, via `/plugin`). `CLAUDE.md` loads automatically and tells the agent the rules. Edit its "Demo data branch" line to your own branch first. Then prompt, for example:

> The pipeline failed on my data branch. Use the bauplan-debug-and-fix-pipeline skill to find the root cause with evidence, make a minimal fix, commit it, and rerun on my branch.

What a good run looks like:
1. The agent gets the failed job and pins the exact data state of the branch at failure time.
2. It queries `sessions_feed` and finds `event_type` is `PURCHASE`/`VIEW`/`CART` on 2026-11-06 while other days use lower case, so `event_type = 'purchase'` in `purchase_events` matches nothing for that day.
3. It fixes `pipeline/models.py` so the match is case-insensitive (for example, lower-case `event_type` before filtering in `purchase_events`). Per rule 7 in `CLAUDE.md`, the fix must work for both the failing data and current data.
4. It commits the change with a clear message.

### 7. Verify the fix
Rerun the pipeline on the same branch. The feed already holds days 01..07:
```zsh
cd demo_v2
./run_pipeline.sh fixed     # expected: GREEN
./report.sh                 # expected: 2026-11-01 .. 2026-11-07 including 2026-11-06
```
Cross-check that the case variation is really in the data and that nothing is dropped:
```zsh
bauplan query "SELECT substr(event_time,1,10) AS d, event_type, COUNT(*) AS n FROM sessions_feed GROUP BY 1, 2 ORDER BY 1, 2" --ref $BAUPLAN_BRANCH
```

### 8. Replay or reset
To rerun the story from scratch, create a new branch (`ecommerce-pipeline-5`, ...) from `main` and repeat from step 3. Rolling a branch back is not covered here. Bauplan branches are not deleted by any script in this repo.

## Troubleshooting
- `bauplan info` shows the wrong user or fails: redo step 1.
- `set BAUPLAN_BRANCH to your data branch`: run the `export` line from step 2 in the current shell.
- Branch create is rejected: the name must start with your own username and a `.`.
- `./report.sh` says `daily_segment_stats` does not exist: run the pipeline once (step 3) before the report.
