# Fetch a subrange of tfile object
# Derek Fujimoto
# Oct 2024

from .exceptions import *
import numpy as np
import pandas as pd
from rootloader import tfile, ttree

class tsubfile(tfile):
    """Wrapper for tfile which restricts access to values only within given times

    Args:
        tfileobj (tfile): object to wrap
        start (int): starting epoch time
        stop (int): stopping epoch time
    """

    def __init__(self, tfileobj, start, stop):

        for key, value in tfileobj.items():
            self[key] = value

        # self._start = start
        # self._stop = stop
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

