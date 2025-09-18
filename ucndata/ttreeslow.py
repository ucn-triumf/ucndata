# Tree which combines all the EPICS slow control ttrees so you don't have to search columns
# Derek Fujimoto
# June 2025

from rootloader import ttree
import pandas as pd
import numpy as np

class ttreeslow(ttree):

    def __init__(self, ttree_list, parent=None):

        # make dict of which tree to get for which column
        if isinstance(ttree_list, ttreeslow):
            self._columns = ttree_list._columns.copy()
            self._treenames = ttree_list._treenames.copy()

            # save parent object
            if parent is None:
                self._parent = ttree_list._parent
            else:
                self._parent = parent

        else:
            self._columns = {}
            self._treenames = []
            for tr in ttree_list:
                self._treenames.append(tr.name)
                for col in tr.columns:
                    self._columns[col] = tr.name

            # save parent object
            if parent is None:
                raise RuntimeError('Must specify parent object (ucnrun, ucncycle, or ucnperiod)')
            else:
                self._parent = parent

    def __getattr__(self, name):
        if name in self._columns:
            treename = self._columns[name]
            return self._parent.tfile[treename][name]
        else:
            return getattr(object, name)

    def __getitem__(self, key):
        """Fetch a new dataframe with fewer 'columns', as a memory view"""
        return self._parent.tfile[self._columns[key]][key]

    def hist1d(self, column=None, nbins=None, step=None, edges=None):
        """Return histogram of column

        Args:
            column (str): column name, needed if more than one column
            nbins (int): number of bins, span full range
            step (float): bin spacing, span full range

            Pick one or the other

        Returns:
            rootloader.th1
        """
        # get column name
        if column is None:
            if len(self._columns) > 1:
                raise KeyError('tree has more than one column, please specify')
            tree = self[column]
        else:
            if column not in self._columns.keys():
                raise KeyError(f'Column "{column}" must be one of {tuple(self._columns.keys())}')

        # get tree
        return tree.hist1d(self, column=column, nbins=nbins, step=step, edges=edges)

    def reset(self):
        """Make a new set of trees"""
        for name in self._treenames:
            self._parent.tfile[name].reset()
        return ttreeslow(self)

    def set_index(self, column):
        """Set the index column name"""
        for name in self._treenames:
            self._parent.tfile[name].set_index(column)

    def set_filter(self, expression, inplace=True):
        """Set a filter on the dataframe to select a subset of the data"""

        if not inplace:
            raise RuntimeError('Cannot set filters on parent trees which are not in-place')

        for name in self._treenames:
            self._parent.tfile[name].set_filter(expression, inplace=inplace)

     # PROPERTIES ===========================

    @property
    def columns(self):
        return list(self._columns.keys())
    @property
    def treenames(self):
        return np.unique(tuple(self._columns.values()))
    @property
    def filters(self):
        return {name: self._parent.tfile[name].filters for name in self._treenames}
    @property
    def index(self):
        return {name: self._parent.tfile[name].index for name in self._treenames}
    @property
    def index_name(self):
        return {name: self._parent.tfile[name]._index for name in self._treenames}

    def mean(self):
        return pd.concat((self._parent.tfile[name].mean() for name in self._treenames))

    def min(self):
        return pd.concat((self._parent.tfile[name].min() for name in self._treenames))

    def max(self):
        return pd.concat((self._parent.tfile[name].max() for name in self._treenames))

    def rms(self):
        return pd.concat((self._parent.tfile[name].rms() for name in self._treenames))

    def std(self):
        return pd.concat((self._parent.tfile[name].std() for name in self._treenames))
