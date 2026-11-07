from typing import Annotated

import pyarrow

import bauplan


class StatsDate(bauplan.TableSchema):
    date: bauplan.String


@bauplan.expectation()
@bauplan.python('3.11')
def test_daily_segment_stats_not_empty(
    data: Annotated[
        pyarrow.Table,
        bauplan.Model(
            'daily_segment_stats',
            projection_schema=StatsDate,
        ),
    ],
) -> bool:
    assert data.num_rows > 0, 'daily_segment_stats is empty'
    return data.num_rows > 0


class FeedTimes(bauplan.TableSchema):
    event_time: bauplan.Any


@bauplan.expectation()
@bauplan.python('3.11')
def test_report_covers_latest_day(
    report: Annotated[
        pyarrow.Table,
        bauplan.Model(
            'daily_segment_stats',
            projection_schema=StatsDate,
        ),
    ],
    feed: Annotated[
        pyarrow.Table,
        bauplan.Model(
            'sessions_feed',
            projection_schema=FeedTimes,
        ),
    ],
) -> bool:
    report_dates = [d for d in report.column('date').to_pylist() if d]
    feed_days = [t[:10] for t in feed.column('event_time').to_pylist() if t]
    assert feed_days, 'sessions_feed is empty'
    latest = max(feed_days)
    report_latest = max(report_dates) if report_dates else None
    assert report_latest == latest, f'report missing latest day {latest}'
    return True
