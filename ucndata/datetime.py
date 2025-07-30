# Convert to and from datetime objects as needed
# Derek Fujimoto
# Nov 2024

import pandas as pd
import numpy as np
from . import ucnbase

def from_datetime(item):
    """Convert to epoch time

    Args:
        item (pd.DataFrame|iterable): if dataframe, convert the index, else convert the array

    Returns:
        pd.DataFrame|np.array

    Example:
        ```python
        >>> run = ucnrun(1846)
        >>> df = to_datetime(run.tfile.BeamlineEpics.to_dataframe())
        >>> df2 = from_datetime(df)
        >>> df2
                    B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
        timestamp                                       ...
        1572460997          0.018750           0.00000  ...                  0.0        0.000000
        1572461002          0.000000           0.01875  ...                  0.0        2.151400
        1572461007          0.021875           0.01250  ...                  0.0        2.151400
        1572461012          0.012500           0.00000  ...                  0.0        2.151400
        1572461017          0.000000           0.00000  ...                  0.0        2.151400
        ...                      ...               ...  ...                  ...             ...
        1572466463          0.000000           0.01250  ...                  0.0       38.294899
        1572466468          0.000000           0.00000  ...                  0.0       38.294899
        1572466473          0.018750           0.00000  ...                  0.0       37.864700
        1572466478          0.034375           0.00000  ...                  0.0       37.864700
        1572466479          0.000000           0.01250  ...                  0.0       38.294899

        [1093 rows x 49 columns]

        # check that conversion worked
        >>> all(df2.index == run.tfile.BeamlineEpics.index)
        np.True_
        ```
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

    Example:
        ```python
        >>> run = ucnrun(1846)
        >>> to_datetime(run.tfile.BeamlineEpics.to_dataframe())
                           B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
        timestamp                                                      ...
        2019-10-30 11:43:17-07:00          0.018750           0.00000  ...                  0.0        0.000000
        2019-10-30 11:43:22-07:00          0.000000           0.01875  ...                  0.0        2.151400
        2019-10-30 11:43:27-07:00          0.021875           0.01250  ...                  0.0        2.151400
        2019-10-30 11:43:32-07:00          0.012500           0.00000  ...                  0.0        2.151400
        2019-10-30 11:43:37-07:00          0.000000           0.00000  ...                  0.0        2.151400
        ...                                     ...               ...  ...                  ...             ...
        2019-10-30 13:14:23-07:00          0.000000           0.01250  ...                  0.0       38.294899
        2019-10-30 13:14:28-07:00          0.000000           0.00000  ...                  0.0       38.294899
        2019-10-30 13:14:33-07:00          0.018750           0.00000  ...                  0.0       37.864700
        2019-10-30 13:14:38-07:00          0.034375           0.00000  ...                  0.0       37.864700
        2019-10-30 13:14:39-07:00          0.000000           0.01250  ...                  0.0       38.294899

        [1093 rows x 49 columns]
        ```
    """

    # dataframe conversion
    df = None
    if isinstance(item, (pd.DataFrame, pd.Series)):
        df = item.copy()
        item = df.index
        name = df.index.name

    # convert values
    converted = pd.to_datetime(item, unit='s', utc=True)
    converted = converted.tz_convert(ucnbase.ucnbase.timezone)

    # dataframe conversion
    if df is not None:
        df.index = converted
        df.index.name = name
        return df

    # array conversion
    else:
        return converted
