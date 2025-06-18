    # TTree object for the giant UCN hits trees
# Derek Fujimoto
# June 2025

from rootloader import th1
import pandas as pd
import numpy as np
from collections.abc import Iterable
import os
import ROOT
ROOT.EnableImplicitMT()

class hitstree(object):
    """Extract ROOT.TTree with lazy operation. Looks like a dataframe in most ways

    Args:
        tree (str|hitstree): tree to load
        filter_string (str|None): if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
        columns (list|None): list of column names to include in fetch, if None, get all
    """

    def __init__(self, tree, filename=None):

        # copy
        if isinstance(tree, hitstree):
            self._treename = tree._treename
            self._filename = tree._filename
            self._rdf = ROOT.RDataFrame(self._treename, self._filename)
            self._columns = tree._columns
            self._index = tree._index
            self._filters = tree._filters.copy()

        # new
        elif isinstance(tree, str):
            self._rdf = ROOT.RDataFrame(tree, filename)
            self._columns = tuple((str(s) for s in self._rdf.GetColumnNames()))
            self._filters = list()
            self._treename = tree
            self._filename = filename

            # set index, default to times
            if 'tUnixTimePrecise' in self._columns:
                self._index = 'tUnixTimePrecise'
            elif 'timestamp' in self._columns:
                self._index = 'timestamp'
            else:
                self._index = 'tEntry'

        # viewing - see __getitem__
        elif tree is None:
            return

        else:
            raise RuntimeError('tree must be of type hitstree|str')

        # set filters
        for filt in self._filters:
            self._rdf = self._rdf.Filter(filt, filt)

        # set stats
        self._stats = {col:self._rdf.Stats(col) for col in self._columns}

    def __dir__(self):
        superdir = [d for d in super().__dir__() if d[0] != '_']
        return sorted(self._columns) + superdir

    def __getattr__(self, name):
        if name in self._columns:
            return self[name]
        else:
            return getattr(object, name)

    def __getitem__(self, key):
        """Fetch a new dataframe with fewer 'columns', as a memory view"""

        h = hitstree(None)

        h._treename = self._treename
        h._filename = self._filename
        h._rdf = self._rdf
        h._columns = self._columns
        h._index = self._index
        h._filters = self._filters
        h._stats = self._stats

        # get list of keys
        if isinstance(key, str):
            h._columns = (key,)
        else:
            h._columns = tuple(key)

        return h

    def __len__(self):
        return self.size

    def __repr__(self):
        klist = list(self._columns)
        if klist:
            klist.sort()

            # get number of columns based on terminal size
            maxsize = max((len(k) for k in klist)) + 2
            terminal_width = os.get_terminal_size().columns - 4 # indent by 4 spaces below
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min(ncolumns, len(klist))

            # split into chunks
            needed_len = int(np.ceil(len(klist) / ncolumns)*ncolumns) - len(klist)
            klist = np.concatenate((klist, np.full(needed_len, '')))
            klist = np.array_split(klist, ncolumns)

            # print
            s = 'ttree branches:\n'
            for key in zip(*klist):
                s += ' '*4
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def set_filter_isucn(self):
        """Filter on tIsUCN==1"""
        self.set_filter('tIsUCN == 1')

    def get_hits_histogram(self, nbins=None, step=None):
        """Return histogram of hit times

        Args:
            nbins (int): number of bins, span full range
            step (float): bin spacing, span full range

            Pick one or the other

        Returns:
            np.array: array of size 2 (bin centers, weights)
        """

        minval = self['tUnixTimePrecise'].min()
        maxval = self['tUnixTimePrecise'].max()

        if nbins is not None:
            hist = self._rdf.Histo1D(('UCNHits', "UCN Hits", nbins, minval, maxval), 'tUnixTimePrecise')

        elif step is not None:

            nbins = int((maxval-minval)/step)
            hist = self._rdf.Histo1D(('UCNHits', "UCN Hits;Unix Time;UCN Hits", nbins, minval, maxval), 'tUnixTimePrecise')

        return th1(hist)

    def reset_columns(self):
        """Include all columns again"""
        self._columns = tuple((str(s) for s in self._rdf.GetColumnNames()))

    def set_index(self, column):
        if column not in self._columns:
            raise KeyError(f'{column} not found in branch names list: {self._columns}')
        self._index = column

    def set_filter(self, expression):
        self._rdf = self._rdf.Filter(expression, expression)
        self._filters.append(expression)
        self._stats = {col:self._rdf.Stats(col) for col in self._columns}

    def to_dataframe(self):
        """Return pandas dataframe of the data"""
        columns = np.unique([*self._columns, self._index])
        df = pd.DataFrame(self._rdf.AsNumpy(columns=columns))
        df.set_index(self._index, inplace=True)
        return df

    # PROPERTIES ===========================
    @property
    def columns(self):
        return self._columns
    @property
    def filters(self):
        return self._filters
    @property
    def index(self):
        return self[self._index]
    @property
    def index_name(self):
        return self._index
    @property
    def loc(self):
        return _hitstree_indexed(self)
    @property
    def size(self):
        # use precomputed stats if available
        for col in self._columns:
            if self._stats[col].IsReady():
                break

        # get size
        return self._stats[col].GetN()

    # STATS ================================
    def min(self):
        vals = [self._stats[col].GetMin() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def max(self):
        vals = [self._stats[col].GetMax() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def mean(self):
        vals = [self._stats[col].GetMean() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def rms(self):
        vals = [self._stats[col].GetRMS() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

    def std(self):
        vals = [self._rdf.StdDev(col).GetValue() for col in self._columns]
        if len(vals) == 1:  return vals[0]
        return pd.Series(vals, index=self._columns)

# hitstree but slice on time
class _hitstree_indexed(object):

    def __init__(self, tree):
        self._tree = hitstree(tree)

    def __getitem__(self, key):

        # get rdataframe
        tr = self._tree

        # set fancy slicing
        if isinstance(key, slice):
            if key.start is not None:
                tr.set_filter(f'{tr._index} >= {key.start}')
            if key.stop is not None:
                tr.set_filter(f'{tr._index} < {key.stop}')
            if key.step is not None:
                raise NotImplementedError('Slicing steps not implemented')

        elif isinstance(key, (int, float)):
            tr.set_filter(f'{self._index} == {key}')

        return tr