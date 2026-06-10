# Convert to and from datetime objects as needed
# Derek Fujimoto
# Nov 2024

import pandas as pd
import numpy as np
from . import ucnbase

def from_datetime(item):
    """Convert datetime-indexed data back to integer Unix epoch timestamps.

    Accepts either a `DataFrame`/`Series` (converts its index) or any iterable of
    datetime-like values. Timezone-aware inputs are converted to UTC first;
    naive inputs are treated as UTC. The result is truncated to whole seconds.

    Args:
        item (pd.DataFrame|pd.Series|iterable): data to convert. If a
            `DataFrame` or `Series`, the index is replaced with epoch integers and
            the original object is returned; otherwise an array of integers is
            returned.

    Returns:
        pd.DataFrame|pd.Series|np.ndarray: input with index (or values)
            replaced by integer Unix epoch timestamps (seconds since 1970-01-01
            UTC).

    Example:
        >>> run = ucnrun(1846)
        >>> df = to_datetime(run.tfile.BeamlineEpics.to_dataframe())
        >>> df2 = from_datetime(df)
        >>> df2
                    B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
        timestamp                                       ...
        1572460997          0.018750           0.00000  ...                  0.0        0.000000
        1572461002          0.000000           0.01875  ...                  0.0        2.151400
        ...

        >>> all(df2.index == run.tfile.BeamlineEpics.index)
        np.True_
    """

    # dataframe conversion
    df = None
    if isinstance(item, (pd.DataFrame, pd.Series)):
        df = item.copy()
        item = df.index
        name = df.index.name

    # convert values
    converted = pd.Series(item)

    try:
        converted = converted.dt.tz_convert('UTC')
    except TypeError:
        converted = converted.dt.tz_localize('UTC')

    converted -= pd.Timestamp('1970-01-01').tz_localize("UTC")
    converted = converted // pd.Timedelta('1s')

    # dataframe conversion
    if df is not None:
        df.index = converted
        df.index.name = name
        return df

    # array conversion
    else:
        return converted.values

def to_datetime(item, timezone='America/Vancouver'):
    """Convert Unix epoch timestamps to timezone-aware datetime objects.

    Accepts either a `DataFrame`/`Series` (converts its index) or any iterable of
    numeric epoch values. Timestamps are interpreted as seconds since
    1970-01-01 UTC and then converted to the requested timezone.

    Args:
        item (pd.DataFrame|pd.Series|iterable): data to convert. If a
            `DataFrame` or `Series`, the index is replaced with datetime values and
            the original object is returned; otherwise an array of datetime
            values is returned.
        timezone (str): IANA timezone name for the output timestamps. Defaults
            to `'America/Vancouver'`.

    Returns:
        pd.DataFrame|pd.Series|pd.DatetimeIndex: input with index (or values)
            replaced by timezone-aware datetime objects.

    Example:
        >>> run = ucnrun(1846)
        >>> to_datetime(run.tfile.BeamlineEpics.to_dataframe())
                           B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
        timestamp                                                      ...
        2019-10-30 11:43:17-07:00          0.018750           0.00000  ...                  0.0        0.000000
        2019-10-30 11:43:22-07:00          0.000000           0.01875  ...                  0.0        2.151400
        ...

        >>> to_datetime([1572460997, 1572461002], timezone='UTC')
        DatetimeIndex(['2019-10-30 18:43:17+00:00', '2019-10-30 18:43:22+00:00'],
                      dtype='datetime64[ns, UTC]', freq=None)
    """

    # dataframe conversion
    df = None
    if isinstance(item, (pd.DataFrame, pd.Series)):
        df = item.copy()
        item = df.index
        name = df.index.name

    # convert values
    converted = pd.to_datetime(item, unit='s', utc=True)
    converted = converted.tz_convert(timezone)

    # dataframe conversion
    if df is not None:
        df.index = converted
        df.index.name = name
        return df

    # array conversion
    else:
        return converted
