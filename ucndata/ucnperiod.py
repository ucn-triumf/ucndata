# Open and analyze UCN data for a one cycle
# Derek Fujimoto
# Oct 2024

import ucndata
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
        """Initialize a ucnperiod by slicing a ucncycle to a single period's time window.

        Copies all attributes from ``ucycle``, replacing ``tfile`` with a
        ``tsubfile`` restricted to [period_start, period_stop] and rebuilding
        ``epics`` against the new tsubfile. ``period_durations_s`` and
        ``period_end_times`` in ``cycle_param`` are trimmed to the scalar
        values for this period.

        Args:
            ucycle (ucncycle): parent cycle object to slice.
            period (int): zero-based period index within the cycle.
        """
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
        """Return a human-readable string listing all public attributes in columns.

        The column count is derived from the current terminal width. The header
        line includes the run number, cycle index, and period index.

        Returns:
            str: formatted multi-column attribute listing, e.g.
                ``"run 1846 (cycle 0, period 1):\\n  attr1  attr2  ..."``.
        """
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
            detector (str): one of the keys to ucndata.DET_NAMES

        Returns:
            bool: true if pileup detected

        Example:
            >>> p = run[0, 0]
            >>> p.is_pileup('Li6')
            False
        """

        # get hit timestamps as array
        t = self.get_hits_array(detector)

        ## filter pileup for period data

        # get thresholds
        dt = ucndata.DATA_CHECK_THRESH['pileup_within_first_s']
        count_thresh = ucndata.DATA_CHECK_THRESH['pileup_cnt_per_ms']

        # make histogram
        counts, _ = np.histogram(t, bins=int(1/0.001*dt),
                                        range=(min(t), min(t)+dt))

        # look for pileup
        piled_up = counts > count_thresh

        return any(piled_up)

    def get_nhits(self, detector, bin_ms=0):
        """Get the total number of UCN hits recorded in this period.

        Delegates to the parent run's ``_get_nhits`` with this cycle and period
        index. See that method for full caching and performance details.

        Args:
            detector (str): detector to query — ``'Li6'`` or ``'He3'``.
            bin_ms (int): hit-event time resolution in milliseconds.
                When 0, raw hit timestamps are used for maximum precision and a
                per-period histogram is cached keyed on the current period
                boundaries. When > 0, a fixed-bin histogram of that width is
                built and reused across repeated calls with the same value,
                which is faster when period timings are modified frequently.

        Returns:
            int: total number of UCN hit events in this period.

        Notes:
            With ``bin_ms=0`` the hit histogram is cached against the current
            period boundaries. Modifying timings invalidates the cache and
            forces a rebuild on the next call. To avoid per-iteration rebuilds,
            finish all timing modifications before calling ``get_nhits``::

                # slow — rebuilds histogram every iteration
                hits = []
                for cycle in run:
                    cycle[1].modify_timing(1)
                    hits.append(cycle[1].get_nhits('Li6'))

                # fast — histogram built once after all modifications
                for cycle in run:
                    cycle[1].modify_timing(1)
                hits = run[:, 1].get_nhits('Li6')

        Example:
            >>> period = run[0, 1]
            >>> period.get_nhits('Li6')
            1204
            >>> period.get_nhits('He3', bin_ms=100)
            1197
        """
        return self._run._get_nhits(detector,
                                    cycle=self.cycle,
                                    period=self.period,
                                    bin_ms=bin_ms)

    def modify_timing(self, dt_start_s=0, dt_stop_s=0):
        """Change the start and/or end time of this period.

        Adjusts ``period_start`` by ``dt_start_s`` and ``period_stop`` by
        ``dt_stop_s``, then propagates the change back into the parent run via
        ``ucnrun._modify_ptiming`` so that the run-level ``cycle_param`` and
        the ``tsubfile`` window stay consistent.

        Args:
            dt_start_s (float): seconds to add to the period start time.
                Negative values move the boundary earlier.
            dt_stop_s (float): seconds to add to the period stop time.
                Negative values move the boundary earlier.

        Returns:
            None

        Notes:
            * Adjacent periods are forced to remain contiguous (no overlap,
              no gap), so changing one boundary shifts the neighbouring period
              boundary accordingly.
            * The cycle end time cannot be changed; only the cycle start time
              can be shifted (by adjusting period 0's start).
            * All cached hit histograms are reset after the timing change.

        Example:
            >>> period = run[0, 1]
            >>> period.modify_timing(dt_start_s=2.0, dt_stop_s=-1.0)
        """
        self._run._modify_ptiming(cycle = self.cycle,
                                  period = self.period,
                                  dt_start_s = dt_start_s,
                                  dt_stop_s = dt_stop_s)

        # Sync this period object's timing attributes from the updated run cycle_param
        cycpar = self._run.cycle_param
        if self.period == 0:
            self.period_start = cycpar.cycle_times.loc[self.cycle, 'start']
        else:
            self.period_start = cycpar.period_end_times.loc[self.period - 1, self.cycle]
        self.period_stop = cycpar.period_end_times.loc[self.period, self.cycle]
        self.period_dur = self.period_stop - self.period_start

        # Update tsubfile window and discard cached filtered slices (now stale)
        self.tfile._items['_start'] = self.period_start
        self.tfile._items['_stop'] = self.period_stop
        for key in [k for k in self.tfile._items if k not in ('_start', '_stop')]:
            del self.tfile._items[key]