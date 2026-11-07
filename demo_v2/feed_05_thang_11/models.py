from typing import Annotated

import pyarrow

import bauplan


class SessionEvents(bauplan.TableSchema):
    event_time: bauplan.Any
    event_type: bauplan.Any
    product_id: bauplan.Any
    category_id: bauplan.Any
    category_code: bauplan.Any
    brand: bauplan.Any
    price: bauplan.Any
    user_id: bauplan.Any
    user_session: bauplan.Any


@bauplan.model(materialization_strategy='REPLACE')
@bauplan.python('3.11', pip={'polars': '2.0.0'})
def sessions_feed(
    raw: Annotated[
        pyarrow.Table,
        bauplan.Model(
            'bauplan.ecommerce_sessions',
            projection_schema=SessionEvents,
            filter="event_time >= '2019-10-01' AND event_time < '2019-10-08'",
        ),
    ],
    upto: Annotated[str, bauplan.Parameter('upto')],
    upper_days: Annotated[str, bauplan.Parameter('upper_days')],
) -> Annotated[pyarrow.Table, SessionEvents]:
    import polars as pl

    df = pl.DataFrame(raw)

    # Shift the 2019-10 source dates to 2026-11 so the feed looks current.
    df = df.with_columns(
        pl.col('event_time').str.replace(r'^2019-10-', '2026-11-')
    )

    # Keep only rows whose date (first 10 chars) is <= upto.
    df = df.filter(pl.col('event_time').str.slice(0, 10) <= upto)

    # Uppercase event_type on the listed (comma-separated) dates.
    days = [d.strip() for d in upper_days.split(',') if d.strip()]
    if days:
        df = df.with_columns(
            pl.when(pl.col('event_time').str.slice(0, 10).is_in(days))
            .then(pl.col('event_type').str.to_uppercase())
            .otherwise(pl.col('event_type'))
            .alias('event_type')
        )
    return df.to_arrow()
