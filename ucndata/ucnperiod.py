# Open and analyze UCN data for a one cycle
# Derek Fujimoto
# Oct 2024

from .exceptions import *
from .ucnbase import ucnbase
from .tsubfile import tsubfile
from .ttreeslow import ttreeslow

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
        if period > 0:      start = ucycle.cycle_param.period_end_times[period-1]
        else:               start = ucycle.cycle_start

        stop = ucycle.cycle_param.period_end_times[period]

        # copy data
        for key, value in ucycle.__dict__.items():
            if key == 'tfile':
                setattr(self, key, tsubfile(value, start, stop))
            elif key == 'epics':
                setattr(self, key, ttreeslow(value, self))
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
        self.period_dur = stop-start

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

    def is_pileup(self, detector):
        """Check if pileup may be an issue in this period.

        Histograms the first `pileup_within_first_s` seconds of data in 1 ms bins and checks if any of those bins are greater than the `pileup_cnt_per_ms` threshold.

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

    def get_nhits(self, detector, bin_ms=0):
        """Get number of ucn hits

        Args:
            detector (str): Li6|He3
            bin_ms (int): UCN hit event resolution in milliseconds. 
                If 0, use raw hits for max precision. Else construct histogram
                with bins of size resolution_ms, and compute per-period/cycle hits
                from that.
        
        Returns: 
            int: number of events

        Notes: 
            Getting the hits with bin_ms=0 requires that you parse the 
            entire tree, so to speed this up, a histogram is created where the 
            bin edges are set to the period and cycle start/end times. This 
            histogram is cached as `self._nhits` so future requests of the 
            number of hits is fast. However, if you modify the start/end times 
            of the periods, this histogram is no longer accurate and so must 
            be recomputed. This happens automatically, but rebuilding the 
            histogram adds to your runtime. Thus the following works, but is 
            slow:
            
            ```python
                hits = []
                for cycle in run: 
                    cycle[1].modify_timing(1)
                    hits.append(cycle[1].get_nhits('Li6')) # hits histogram recomputed every loop
            ```

            Whereas the following is much faster but does the same thing:
            
            ```python
                for cycle in run: 
                    cycle[1].modify_timing(1)
                hits = run[:, 1].get_nhits('Li6') # hits histogram recomputed only once
            ```

            In contrast, when bin_ms > 0, a histogram with bins of size bins_ms 
            is created. This histogram is independent of the period timings and 
            is only recreated when get_nhits is called with a new value of 
            bin_ms is changed. While the above rules still apply, recreating 
            the periods hits histogram from the bin_ms histogram is much faster, 
            allowing for speedups of analyses where modifying the period timings 
            frequently is important. 
        """
        return self._run._get_nhits(detector, 
                                    cycle=self.cycle, 
                                    period=self.period,
                                    bin_ms=bin_ms)

    def modify_timing(self, dt_start_s=0, dt_stop_s=0):
        """Change start and end times of period

        Args:
            dt_start_s (float): change to the period start time
            dt_stop_s (float): change to the period stop time

        Notes:
            * as a result of this, cycles may overlap or have gaps
            * periods are forced to not overlap and have no gaps
            * cannot change cycle end time, but can change cycle start time
            * this function resets all saved histgrams and hits
        """
        self._run._modify_ptiming(cycle = self.cycle,
                                  period = self.period,
                                  dt_start_s = dt_start_s,
                                  dt_stop_s = dt_stop_s)