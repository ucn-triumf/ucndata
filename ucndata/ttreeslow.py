# Tree which combines all the EPICS slow control ttrees so you don't have to search columns
# Derek Fujimoto
# June 2025

from rootloader import ttree
import pandas as pd

class ttreeslow(ttree):

    def __init__(self, ttree_list):

        # copy
        if isinstance(ttree_list, ttreeslow):
            self._ttrees = {key: ttree(t) for key, t in ttree_list._ttrees.items()}

        else:
            # save list of ttrees
            self._ttrees = {t.name: t for t in ttree_list}

        # make dict of which tree to get for which column
        self._columns = {}
        for name, tr in self._ttrees.items():
            for col in tr.columns:
                self._columns[col] = name

    def __getattr__(self, name):
        if name in self._columns:
            treename = self._columns[name]
            return self._ttrees[treename][name]
        else:
            return getattr(object, name)

    def __getitem__(self, key):
        """Fetch a new dataframe with fewer 'columns', as a memory view"""
        return self._ttrees[self._columns[key]][key]

    def hist1d(self, column=None, nbins=None, step=None):
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
            column = self._columns[0]
        else:
            if column not in self._columns.keys():
                raise KeyError(f'Column "{column}" must be one of {tuple(self._columns.keys())}')

        # get tree
        tree = self._ttree[self._columns[column]]
        return tree.hist1d(self, column=None, nbins=None, step=None)

    def reset(self):
        """Make a new set of trees"""
        treelist = (tr.reset() for tr in self._ttrees.values())
        return ttreeslow(treelist)

    def reset_columns(self):
        """Include all columns again"""
        self._columns = {}
        for name, tr in self._ttrees.items():
            tr.reset_columns()
            for col in tr.columns:
                self._columns[col] = name

    def set_index(self, column):
        """Set the index column name"""
        if column not in self._columns:
            raise KeyError(f'{column} not found in branch names list: {self._columns}')

        for tr in self._ttrees.values():
            tr.set_index(column)

    def set_filter(self, expression, inplace=False):
        """Set a filter on the dataframe to select a subset of the data"""

        if inplace:
            for tr in self._ttrees.values():
                tr.set_filter(expression, inplace=True)
        else:
            treelist = (tr.set_filter(expression, inplace=False) for tr in self._ttrees.values())
            return ttreeslow(treelist)

    def to_dataframe(self):
        df_list= (tr.to_dataframe() for tr in self._ttrees.values())
        df_list2 = (d.loc[~d.index.duplicated(keep='first')] for d in df_list)
        return pd.concat(df_list2, axis='columns')

    def to_dict(self):
        d = {}
        for tr in self._ttrees.values():
            d2 = tr.to_dict()
            for key, val in d2.items():
                d[key] = val
        return d

     # PROPERTIES ===========================

    @property
    def columns(self):
        return list(self._columns.keys())
    @property
    def filters(self):
        return {name: tr.filters for name, tr in self._ttrees.items()}
    @property
    def index(self):
        return {name: tr.index for name, tr in self._ttrees.items()}
    @property
    def index_name(self):
        return {name: tr._index for name, tr in self._ttrees.items()}

    @property
    def loc(self):
        return _ttreeslow_indexed(self)

    @property
    def size(self):
        return {name: tr.size for name, tr in self._ttrees.items()}

# ttree but slice on time
class _ttreeslow_indexed(object):

    def __init__(self, tree):
        self._treeslow = ttreeslow(tree)

    def __getitem__(self, key):

        # get tree
        tree = self._treeslow

        # slicing or indexing
        for name, tr in tree._ttrees.items():
            tree._ttrees[name] = tr.loc[key]

        return tree
