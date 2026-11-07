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
    event_case: Annotated[str, bauplan.Parameter('event_case')],
) -> Annotated[pyarrow.Table, SessionEvents]:
    import polars as pl

    df = pl.DataFrame(raw)
    if event_case == 'upper':
        df = df.with_columns(pl.col('event_type').str.to_uppercase())
    return df.to_arrow()
