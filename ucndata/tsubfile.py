# Fetch a subrange of tfile object
# Derek Fujimoto
# Oct 2024

from .exceptions import *
import numpy as np
import pandas as pd
from rootloader import tfile, ttree

class tsubfile(tfile):
    """Time-bounded wrapper around a rootloader.tfile object.

    Acts like a tfile but silently filters any DataFrame or ttree whose index
    is a time axis, returning only rows whose timestamp falls within [start, stop].
    Non-time-indexed data is returned unchanged. Accessed values are cached in
    the internal _items dict to avoid redundant filtering on repeated access.

    Args:
        tfileobj (tfile): rootloader tfile object to wrap
        start (int): inclusive start of the allowed epoch time range (seconds)
        stop (int): inclusive end of the allowed epoch time range (seconds)

    Example:

        >>> # Wrap an open run's tfile to the time window of one cycle
        >>> sub = tsubfile(run.tfile, cycle_start, cycle_stop)
        >>> sub['He3'].head()   # only rows within [cycle_start, cycle_stop]
    """

    def __init__(self, tfileobj, start, stop):

        for key, value in tfileobj.items():
            self[key] = value

        items = {'_start':start, '_stop':stop}
        object.__setattr__(self, '_items', items)

    def __getitem__(self, key):

        # quick return
        if key in self._items.keys():
            return self._items[key]

        # get the data
        val = super().__getitem__(key)

        # get sub range: pd.DataFrame
        if isinstance(val, pd.DataFrame):
            try:
                index_name = val.index.name.lower()
            except AttributeError:
                pass
            else:
                if 'time' in index_name:
                    idx = (val.index >= self._start) & (val.index <= self._stop)
                    val = val.loc[idx]

        # get sub range: rootloader.ttree
        elif isinstance(val, ttree):
            try:
                index_name = val.index_name.lower()
            except AttributeError:
                pass
            else:
                if 'time' in index_name:
                    val = val.loc[self._start:self._stop]

        self._items[key] = val

        return val

    def __getattr__(self, name):

        if name in self.keys():
            return self[name]
        elif name in self._items.keys():
            return self._items[name]
        else:
            return self.__getattribute__(name)

