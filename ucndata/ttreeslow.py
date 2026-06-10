# Tree which combines all the EPICS slow control ttrees so you don't have to search columns
# Derek Fujimoto
# June 2025

from rootloader import ttree
import pandas as pd
import numpy as np

class ttreeslow(ttree):
    """Unified interface to multiple EPICS slow-control ROOT trees.

    Merges several rootloader.ttree objects (e.g. BeamlineEpics, UCN2Epics)
    into a single object so callers can access any column without knowing
    which underlying tree it lives in. Aggregate statistics (mean, min, max,
    std, rms) concatenate results across all trees into a single pd.Series.

    Attributes:
        _columns (dict): maps column name to the source tree name
        _treenames (list): names of all underlying trees
        _parent: ucnrun/ucncycle/ucnperiod object that owns the tfile

    Example:

        >>> # Access any EPICS column without specifying the source tree
        >>> run.epics.UCN_UGD_ISOCP_RDVOL.mean()
        >>> run.epics.mean()   # aggregate mean across all EPICS trees
    """

    def __init__(self, ttree_list, parent=None):
        """Initialize from a list of ttree objects or an existing ttreeslow.

        When initialized from a list of ttree objects, builds internal column-
        to-tree mapping and requires a parent object for tfile access. When
        initialized from an existing ttreeslow, copies its mapping and inherits
        the parent unless a new one is provided.

        Args:
            ttree_list (list[ttree] | ttreeslow): source trees to merge, or an
                existing ttreeslow to copy
            parent: ucnrun, ucncycle, or ucnperiod instance that owns the tfile;
                required when ttree_list is a list

        Raises:
            RuntimeError: if ttree_list is a list and parent is not provided
        """
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
        """Return the data series for a single column from its source tree.

        Args:
            key (str): column name to retrieve

        Returns:
            pd.Series: time-indexed series for the requested column
        """
        return self._parent.tfile[self._columns[key]][key]

    def hist1d(self, column=None, nbins=None, step=None, edges=None):
        """Return a 1D histogram of a column's data.

        Args:
            column (str): column name to histogram; required when the object
                contains more than one column
            nbins (int): number of equally-spaced bins spanning the full data
                range; mutually exclusive with step and edges
            step (float): bin width in data units, spanning the full range;
                mutually exclusive with nbins and edges
            edges (array-like): explicit bin-edge array; mutually exclusive with
                nbins and step

        Returns:
            rootloader.th1: histogram object

        Raises:
            KeyError: if column is not specified when there are multiple columns,
                or if the specified column does not exist

        Example:

            >>> h = run.epics.hist1d('UCN_UGD_ISOCP_RDVOL', nbins=50)
        """
        # get column name
        if column is None:
            if len(self._columns) > 1:
                raise KeyError('tree has more than one column, please specify')
            column = self.columns[0]
        else:
            if column not in self._columns.keys():
                raise KeyError(f'Column "{column}" must be one of {tuple(self._columns.keys())}')

        # get tree and return histogram
        tree = self[column]
        return tree.hist1d(column=column, nbins=nbins, step=step, edges=edges)

    def reset(self):
        """Reset all underlying trees and return a fresh ttreeslow copy.

        Calls reset() on each source tree (clearing any cached data or filters)
        and then constructs a new ttreeslow with the same column mapping.

        Returns:
            ttreeslow: new instance wrapping the reset trees

        Example:

            >>> run.epics.set_filter('timestamp > 1000')
            >>> clean = run.epics.reset()  # filters cleared
        """
        for name in self._treenames:
            self._parent.tfile[name].reset()
        return ttreeslow(self)

    def set_index(self, column):
        """Set the index column on all underlying trees.

        Args:
            column (str): name of the column to use as the row index
        """
        for name in self._treenames:
            self._parent.tfile[name].set_index(column)

    def set_filter(self, expression, inplace=True):
        """Apply a row-selection filter to all underlying trees.

        Args:
            expression (str): boolean expression string evaluated against each
                tree's columns (e.g. 'timestamp > 1000')
            inplace (bool): must be True; non-inplace filtering on parent trees
                is not supported

        Raises:
            RuntimeError: if inplace is False

        Example:

            >>> run.epics.set_filter('UCN_UGD_ISOCP_RDVOL > 0')
        """

        if not inplace:
            raise RuntimeError('Cannot set filters on parent trees which are not in-place')

        for name in self._treenames:
            self._parent.tfile[name].set_filter(expression, inplace=inplace)

     # PROPERTIES ===========================

    @property
    def columns(self):
        """list[str]: all column names available across all underlying trees."""
        return list(self._columns.keys())

    @property
    def treenames(self):
        """np.ndarray: unique names of the underlying source trees."""
        return np.unique(tuple(self._columns.values()))

    @property
    def filters(self):
        """dict: mapping of tree name to its current filter expression."""
        return {name: self._parent.tfile[name].filters for name in self._treenames}

    @property
    def index(self):
        """dict: mapping of tree name to its current index (pd.Index)."""
        return {name: self._parent.tfile[name].index for name in self._treenames}

    @property
    def index_name(self):
        """dict: mapping of tree name to its index column name string."""
        return {name: self._parent.tfile[name]._index for name in self._treenames}

    def mean(self):
        """Return the column-wise mean across all underlying trees.

        Returns:
            pd.Series: mean value for each column, indexed by column name

        Example:

            >>> run.epics.mean()
        """
        return pd.concat((self._parent.tfile[name].mean() for name in self._treenames))

    def min(self):
        """Return the column-wise minimum across all underlying trees.

        Returns:
            pd.Series: minimum value for each column, indexed by column name

        Example:

            >>> run.epics.min()
        """
        return pd.concat((self._parent.tfile[name].min() for name in self._treenames))

    def max(self):
        """Return the column-wise maximum across all underlying trees.

        Returns:
            pd.Series: maximum value for each column, indexed by column name

        Example:

            >>> run.epics.max()
        """
        return pd.concat((self._parent.tfile[name].max() for name in self._treenames))

    def rms(self):
        """Return the column-wise root-mean-square across all underlying trees.

        Returns:
            pd.Series: RMS value for each column, indexed by column name

        Example:

            >>> run.epics.rms()
        """
        return pd.concat((self._parent.tfile[name].rms() for name in self._treenames))

    def std(self):
        """Return the column-wise standard deviation across all underlying trees.

        Returns:
            pd.Series: standard deviation for each column, indexed by column name

        Example:

            >>> run.epics.std()
        """
        return pd.concat((self._parent.tfile[name].std() for name in self._treenames))
