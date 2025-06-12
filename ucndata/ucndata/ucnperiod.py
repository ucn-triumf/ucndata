# Open and analyze UCN data for a one cycle
# Derek Fujimoto
# Oct 2024

"""
    TODO List, things which haven't been ported from WS code

    * get temperature
    * get vapour pressure
    * data checks for periods
    * check that period durations match between detector frontends
"""

from .exceptions import *
from . import settings
from .ucnbase import ucnbase
from .tsubfile import tsubfile

import numpy as np
import os

class ucnperiod(ucnbase):
    """Stores the data from a single UCN period from a single cycle

    Args:
        ucycle (ucncycle): object to pull period from
        period (int): period number
    """

    def __init__(self, ucycle, period):

        # get start and stop time
        if period > 0:      start = int(ucycle.cycle_param.period_end_times[period-1])
        else:               start = int(ucycle.cycle_start)

        stop = int(ucycle.cycle_param.period_end_times[period])

        # copy data
        for key, value in ucycle.__dict__.items():
            if key == 'tfile':
                setattr(self, key, tsubfile(value, start, stop))
            elif hasattr(value, 'copy'):
                setattr(self, key, value.copy())
            else:
                setattr(self, key, value)

        # trim cycle parameters
        self.cycle_param.period_durations_s = self.cycle_param.period_durations_s[period]
        self.cycle_param.period_end_times = self.cycle_param.period_end_times[period]

        self.period = period
        self.period_start = start
        self.period_stop = stop

    def __repr__(self):
        klist = [d for d in self.__dict__.keys() if d[0] != '_']
        if klist:

            # sort without caps
            klist.sort(key=lambda x: x.lower())

            # get number of columns based on terminal size
            maxsize = max((len(k) for k in klist)) + 2
            terminal_width = os.get_terminal_size().columns
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min(ncolumns, len(klist))

            # split into chunks
            needed_len = int(np.ceil(len(klist) / ncolumns)*ncolumns) - len(klist)
            klist = np.concatenate((klist, np.full(needed_len, '')))
            klist = np.array_split(klist, ncolumns)

            # print
            cyc_str = f' (cycle {self.cycle}, period {self.period})'
            s = f'run {self.run_number}{cyc_str}:\n'
            for key in zip(*klist):
                s += '  '
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def get_counts(self, detector, bkgd=None, dbkgd=None, norm=None, dnorm=None):
        """Get sum of ucn hits

        Args:
            detector (str): one of the keys to self.DET_NAMES
            bkgd (float|None): background counts
            dbkgd(float|None): error in background counts
            norm (float|None): normalize to this value
            dnorm (float|None): error in normalization

        Returns:
            tuple: (count, error) number of hits

        Example:
            ```python
            >>> p = run[0,0]
            >>> p.get_counts('Li6')
            (347, np.float64(18.627936010197157))
            ```
        """
        hit_tree = self.get_hits(detector)
        counts = len(hit_tree.index)
        dcounts = np.sqrt(counts) # error assumed poissonian

        # subtract background, but no less than 0 counts
        if bkgd is not None:

            # check if iterable, else fetch only for this period
            try:                iter(bkgd)
            except TypeError:   b = bkgd
            else:               b = bkgd[self.period]
            counts = max(counts-b, 0)

            # error correction
            if dbkgd is not None:

                # check if iterable, else fetch only for this period
                try:                iter(dbkgd)
                except TypeError:   db = dbkgd
                else:               db = dbkgd[self.period]
                dcounts = (dcounts**2 + db**2)**0.5

        # normalize with error corretion
        if dnorm is not None:

            # check if iterable, else fetch only for this period
            try:
                iter(dnorm)
            except TypeError:
                dn = dnorm
                n  = norm
            else:
                dn = dnorm[self.period]
                n  = norm[self.period]

            # normalize
            dcounts = counts*((dcounts/counts)**2 + (dn/n)**2)**0.5
            counts /= n

        # normalize without error correction
        elif norm is not None:

            try:                iter(norm)
            except TypeError:   n = norm
            else:               n = norm[self.period]
            counts /= n

        return (counts, dcounts)

    def is_pileup(self, detector):
        """Check if pileup may be an issue in this period.

        Histograms the first `pileup_within_first_s` seconds of data in 1 ms bins and checks if any of those bins are greater than the `pileup_cnt_per_ms` threshold. Set these settings in the [settings.py](../settings.py) file.

        Args:
            detector (str): one of the keys to self.DET_NAMES

        Returns:
            bool: true if pileup detected

        Example:
            ```python
            >>> p = run[0, 0]
            >>> p.is_pileup('Li6')
            False
            ```
        """

        # get the tree
        hit_tree = super().get_hits(detector)

        ## filter pileup for period data

        # get thresholds
        dt = self.DATA_CHECK_THRESH['pileup_within_first_s']
        count_thresh = self.DATA_CHECK_THRESH['pileup_cnt_per_ms']

        # make histogram
        t = hit_tree.index.values
        counts, _ = np.histogram(t, bins=int(1/0.001*dt),
                                        range=(min(t), min(t)+dt))

        # look for pileup
        piled_up = counts > count_thresh

        return any(piled_up)

    def get_rate(self, detector, bkgd=None, dbkgd=None, norm=None, dnorm=None):
        """Get sum of ucn hits per unit time of period

        Args:
            detector (str): one of the keys to self.DET_NAMES
            bkgd (float|None): background counts
            dbkgd(float|None): error in background counts
            norm (float|None): normalize to this value
            dnorm (float|None): error in normalization

        Returns:
            tuple: (count rate, error)

        Example:
            ```python
            >>> p = run[0,0]
            >>> p.get_rate('Li6')
            (np.float64(5.783333333333333), np.float64(0.3104656001699526))
            ```
        """
        # get counts
        counts, dcounts = self.get_counts(detector=detector,
                                          bkgd=bkgd,
                                          dbkgd=dbkgd,
                                          norm=norm,
                                          dnorm=dnorm,
                                          )

        # get rate
        duration = self.cycle_param.period_durations_s

        counts /= duration
        dcounts /= duration

        return (counts, dcounts)

