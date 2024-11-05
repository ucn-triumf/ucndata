# Convert to and from datetime objects as needed
# Derek Fujimoto
# Nov 2024

import pandas as pd
import numpy as np
from . import settings

def from_datetime(item):
    """Convert to epoch time

    Args:
        item (pd.DataFrame|iterable): if dataframe, convert the index, else convert the array

    Returns:
        pd.DataFrame|np.array
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

def to_datetime(item):
    """Convert to datetime objects

    Args:
        item (pd.DataFrame|iterable): if dataframe, convert the index, else convert the array

    Returns:
        pd.DataFrame|np.array
    """

    # dataframe conversion
    df = None
    if isinstance(item, (pd.DataFrame, pd.Series)):
        df = item.copy()
        item = df.index
        name = df.index.name

    # convert values
    converted = pd.to_datetime(item, unit='s', utc=True)
    converted = converted.tz_convert(settings.timezone)

    # dataframe conversion
    if df is not None:
        df.index = converted
        df.index.name = name
        return df

    # array conversion
    else:
        return converted.values
