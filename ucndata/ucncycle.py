# Open and analyze UCN data for a one cycle
# Derek Fujimoto
# Oct 2024

import ucndata
from .exceptions import *
from .applylist import applylist
from .ucnbase import ucnbase
from .ucnperiod import ucnperiod
from .tsubfile import tsubfile
from .ttreeslow import ttreeslow
from tqdm import tqdm
import pandas as pd
import matplotlib.pyplot as plt

import numpy as np
import os

class ucncycle(ucnbase):
    """View for the data from a single UCN cycle

    Notes:
        Any changes to the data frame affects all periods (for the time steps
        contained in that period) and the containing run

    Args:
        urun (ucnrun): object to pull cycle from
        cycle (int): cycle number
    """

    def __init__(self, urun, cycle):
        """Initialize a ucncycle by slicing a ucnrun to a single cycle's time window.

        Copies all attributes from ``urun``, replacing ``tfile`` with a
        ``tsubfile`` restricted to [cycle_start, cycle_stop] and rebuilding
        ``epics`` against the new tsubfile. Cycle-level ``period_durations_s``
        and ``period_end_times`` are trimmed to the selected cycle.

        Args:
            urun (ucnrun): parent run object to pull cycle data from.
            cycle (int): zero-based cycle index within the run.
        """
        # get cycles to keep
        cycles = urun.cycle_param.cycle_times
        start = int(cycles.loc[cycle, 'start'])
        stop = int(cycles.loc[cycle, 'stop'])
        supercycle = int(cycles.loc[cycle, 'supercycle'])

        # copy data
        for key, value in urun.__dict__.items():
            if key == 'tfile':
                setattr(self, key, tsubfile(value, start, stop))
            elif key == 'epics':
                setattr(self, key, ttreeslow(value, self))
            elif hasattr(value, 'copy'):
                setattr(self, key, value.copy())
            else:
                setattr(self, key, value)

        # trim cycle parameters
        self.cycle_param.period_durations_s = self.cycle_param.period_durations_s[cycle]
        self.cycle_param.period_end_times = self.cycle_param.period_end_times[cycle]

        if self.cycle_param.filter is not None:
            self.cycle_param.filter = self.cycle_param.filter[cycle]

        self.cycle = cycle
        self.supercycle = supercycle
        self.cycle_start = start
        self.cycle_stop = stop
        self.cycle_dur = stop-start

        # store fetched periods
        self._perioddict = dict()

    def __len__(self):
        """Return the number of periods in this cycle.

        Returns:
            int: number of periods defined in ``cycle_param.nperiods``.
        """
        return self.cycle_param.nperiods

    def __next__(self):
        """Advance the iterator and return the next period.

        Enables ``for period in cycle`` iteration. Internally increments
        ``_iter_current`` and delegates to ``__getitem__``.

        Returns:
            ucnperiod: the next period object.

        Raises:
            StopIteration: when all periods have been yielded.
        """
        # permit iteration over object like it was a list

        # iterate
        if self._iter_current < self.cycle_param.nperiods:
            cyc = self[self._iter_current]
            self._iter_current += 1
            return cyc

        # end of iteration
        else:
            raise StopIteration()

    def __repr__(self):
        """Return a human-readable string listing all public attributes in columns.

        The column count is derived from the current terminal width so the
        output fills the screen without wrapping. Includes the run number and
        cycle index in the header line.

        Returns:
            str: formatted multi-column attribute listing, e.g.
                ``"run 1846 (cycle 0):\\n  attr1  attr2  ..."``.
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
            cyc_str = '' if self.cycle is None else f' (cycle {self.cycle})'
            s = f'run {self.run_number}{cyc_str}:\n'
            for key in zip(*klist):
                s += '  '
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"

    def __getitem__(self, key):
        """Index into the cycle to retrieve one or more periods.

        Args:
            key (int | slice): period index or slice. Negative integers are
                supported and wrap around from the last period.

        Returns:
            ucnperiod | applylist: a single ``ucnperiod`` for an integer key,
                or an ``applylist`` of ``ucnperiod`` objects for a slice.

        Raises:
            IndexError: if ``key`` is an integer larger than the number of
                periods, or if ``key`` is not an int or slice.

        Example:
            >>> cycle = run[0]
            >>> period0 = cycle[0]        # first period
            >>> last = cycle[-1]          # last period
            >>> first_two = cycle[0:2]    # applylist of two periods
        """
        # get cycle or period based on slicing indexes

        # get a single key
        if isinstance(key, (np.integer, int)):
            if key < 0:
                key = self.cycle_param.nperiods + key

            if key > self.cycle_param.nperiods:
                raise IndexError(f'Run {self.run_number}, cycle {self.cycle}: Index larger than number of periods ({self.cycle_param.nperiods})')

            return self.get_period(key)

        # slice on cycles
        if isinstance(key, slice):
            period = self.get_period()[:self.cycle_param.nperiods]
            return applylist(period[key])

        raise IndexError('Cycles indexable only as a 1-dimensional object')

    def _inspect_draw(self, current, hist, run_start, axes, xmode='duration', slow=None):
        # drawing portion of the inspect function
        for i, per in enumerate(self):

            # draw current
            cur = current.loc[per.period_start:per.period_stop]

            if len(cur) > 0:
                if xmode in 'datetime':
                    cur.index = pd.to_datetime(cur.index, unit='s')
                elif xmode in 'duration':
                    cur.index -= run_start

                cur.plot(ax=axes[0], color=f'C{i}')

            # draw histogram
            hi = hist.loc[per.period_start:per.period_stop]

            if len(hi) > 0:
                if xmode in 'datetime':
                    hi.index = pd.to_datetime(hi.index, unit='s')
                elif xmode in 'duration':
                    hi.index -= run_start

                hi.plot(ax=axes[1], color=f'C{i}')

            # draw slow control
            if slow is not None:
                for j, (key, val) in enumerate(slow.items()):
                    v = val.loc[per.period_start:per.period_stop]
                    if len(v) > 0:
                        if xmode in 'datetime':
                            v.index = pd.to_datetime(v.index, unit='s')
                        elif xmode in 'duration':
                            v.index -= run_start
                    v.plot(ax=axes[j+2], color=f'C{i}')

        # draw the rest of the run - current
        cur = current.loc[per.period_stop:self.cycle_stop]

        if len(cur) > 0:
            if xmode in 'datetime':
                cur.index = pd.to_datetime(cur.index, unit='s')
            elif xmode in 'duration':
                cur.index -= run_start

            cur.plot(ax=axes[0], color=f'k')

        # draw the rest of the run - histogram
        hi = hist.loc[per.period_stop:self.cycle_stop]

        if len(hi) > 0:
            if xmode in 'datetime':
                hi.index = pd.to_datetime(hi.index, unit='s')
            elif xmode in 'duration':
                hi.index -= run_start

            hi.plot(ax=axes[1], color=f'k')

        # draw slow control
        if slow is not None:
            for i, (key, val) in enumerate(slow.items()):
                v = val.loc[per.period_stop:self.cycle_stop]
                if len(v) > 0:
                    if xmode in 'datetime':
                        v.index = pd.to_datetime(v.index, unit='s')
                    elif xmode in 'duration':
                        v.index -= run_start
                v.plot(ax=axes[i+2], color=f'k')

    def check_data(self, raise_error=False, quiet=False):
        """Run some checks to determine if the data is ok.

        Args:
            raise_error (bool): if True, raise an error when a check fails
                instead of returning False. Has no effect when ``quiet=True``.
            quiet (bool): if True, suppress all printed messages and exceptions;
                always returns False on failure without side effects.

        Returns:
            bool: True if all checks pass, False otherwise.

        Notes:
            Checks performed:

            * is there BeamlineEpics data (1A and 1U beam currents)?
            * is the cycle duration greater than 0?
            * is at least one valve opened during at least one period?
            * does the sum of period durations fit within the cycle duration?
            * did the 1A beam current stay above the minimum threshold throughout
              the cycle and the 20 seconds before it?

        Example:
            >>> cycle = run[0]
            >>> x = cycle.check_data()
            Run 1846, cycle 0: 1A current dropped below 1.0 uA
            >>> x
            False
        """
        # setup error message
        msg = f'Run {self.run_number}, cycle {self.cycle}:'

        # setup raise or warn
        if quiet:
            def warn(error, message):
                return False
        elif raise_error:
            def warn(error, message):
                raise error(message)
        else:
            def warn(error, message):
                tqdm.write(message)
                return False

        ## overall data quality checks ---------------------------------------

        # beam data exists
        if len(self.beam1a_current_uA) == 0:
            return warn(BeamError, f'{msg} No 1A beam data saved')

        if len(self.beam1u_current_uA) == 0:
            return warn(BeamError, f'{msg} No 1U beam data saved')

        # total duration
        if self.cycle_stop - self.cycle_start <= 0:
            return warn(DataError, f'{msg} Cycle duration nonsensical: {self.cycle_stop - self.cycle_start} s')

        # valve states
        if not self.cycle_param.valve_states.any().any():
            return warn(ValveError, f'{msg} No valves operated')

        # check if period duration exceeds cycle duration
        expected_duration = self.cycle_param.period_durations_s.sum()
        actual_duration = self.cycle_stop - self.cycle_start
        if expected_duration > actual_duration:
            return warn(DataError, f'{msg} cycle duration ({actual_duration:.1f} s) shorter than sum of periods ({expected_duration:.1f} s)')

        # drop cycles where the 1A beam drops to zero during any time in the cycle
        if any(self.beam1a_current_uA < ucndata.DATA_CHECK_THRESH['beam_min_current']):
            return warn(BeamError, f'{msg} 1A current dropped below {ucndata.DATA_CHECK_THRESH["beam_min_current"]} uA')

        # drop cycles where the 1A beam drops to zero within 5 s of the cycle starting
        if self.cycle > 0:
            cyc_last = self._run[self.cycle-1]
            current = cyc_last.beam1a_current_uA
            idx = current.index > self.cycle_start-20
            if any(current.loc[idx] < ucndata.DATA_CHECK_THRESH["beam_min_current"]):
                return warn(BeamError, f'{msg} 1A current dropped below {ucndata.DATA_CHECK_THRESH["beam_min_current"]} uA within 20 seconds of the cycle starting')

        return True

    def draw_cycle_times(self, ax=None, xmode='datetime'):
        """Draw cycle start time as a thick black line and period end times as dashed lines.

        The cycle label is rendered vertically at the cycle start. If the cycle
        is excluded by ``cycle_param.filter``, the label is struck through in red.

        Args:
            ax (plt.Axes): axes to draw into. Uses ``plt.gca()`` when None.
            xmode (str): x-axis time representation. One of:

                * ``'datetime'`` — absolute wall-clock timestamps
                * ``'duration'`` — seconds since the start of the run
                * ``'duration_run'`` — same as ``'duration'``
                * ``'duration_cycle'`` — seconds since this cycle's start
                * ``'epoch'`` — raw Unix epoch seconds

        Returns:
            numpy.ndarray: unique period indices that were drawn (zero-length
                periods are skipped).

        Raises:
            RuntimeError: if ``xmode`` is not one of the accepted values.

        Notes:
            Assumed period layout: 0 - irradiation, 1 - storage, 2 - count.

        Example:
            >>> fig, ax = plt.subplots()
            >>> run[0].draw_cycle_times(ax=ax, xmode='duration_cycle')
            array([0, 1, 2])
        """

        # check input
        if all((xmode not in i for i in ('datetime', 'duration', 'duration_run', 'duration_cycle', 'epoch'))):
            raise RuntimeError('xmode must be one of datetime|duration_run|duration_cycle|epoch')

        # get axis to draw in
        if ax is None:
            ax = plt.gca()

        # run start time
        if xmode in 'duration_run':
            run_start = self._run.cycle_param.cycle_times.loc[0, 'start']
        elif xmode in 'duration_cycle':
            run_start = self.cycle_start
        else:
            run_start = 0

        # draw lines
        non_zero_periods = []

        # get x value
        if xmode in 'datetime':
            start = pd.to_datetime(self.cycle_start, unit='s')
        else:
            start = self.cycle_start - run_start

        # draw
        ax.axvline(start, color='k', ls='-', lw=2)

        for i, per in enumerate(self.get_period()):

            # skip zero length periods
            if per.period_start == per.period_stop:
                continue

            # get x value
            if xmode in 'datetime':
                x = pd.to_datetime(per.period_stop, unit='s')
            else:
                x = per.period_stop - run_start

            # draw
            ax.axvline(x, color=f'C{i}', ls=':', lw=1)
            non_zero_periods.append(i)

        # get cycle text - strikeout if not good
        text = f'Cycle {self.cycle}'

        # check if filtered
        if self.cycle_param.filter is None or self.cycle_param.filter:
            color = 'k'
        else:
            text = '\u0336'.join(text) + '\u0336'
            color = 'r'

        text += ' $\\downarrow$'

        ypos = ax.get_ylim()[1]
        ax.text(start, ypos, text,
                va='top',
                ha='left',
                fontsize='xx-small',
                color=color,
                rotation='vertical',
                clip_on=True,)

        # add periods to legend
        return np.unique(non_zero_periods)

    def get_nhits(self, detector, bin_ms=0):
        """Get the total number of UCN hits recorded in this cycle.

        Delegates to the parent run's ``_get_nhits`` with this cycle's index.
        See that method for caching and performance details.

        Args:
            detector (str): detector to query — ``'Li6'`` or ``'He3'``.
            bin_ms (int): hit-event time resolution in milliseconds.
                When 0, raw hit timestamps are used for maximum precision and a
                per-period histogram is cached keyed on the current period
                boundaries. When > 0, a fixed-bin histogram of that width is
                built and reused across repeated calls with the same value,
                which is faster when period timings are modified frequently.

        Returns:
            int: total number of UCN hit events in this cycle.

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
            >>> cycle = run[0]
            >>> cycle.get_nhits('Li6')
            4321
            >>> cycle.get_nhits('He3', bin_ms=100)
            4289
        """
        return self._run._get_nhits(detector,
                                    cycle=self.cycle,
                                    bin_ms=bin_ms)

    def get_period(self, period=None):
        """Return a ucnperiod (or list of all periods) for this cycle.

        Equivalent to the indexing shorthand ``cycle[period]``. Results are
        cached in ``_perioddict`` so repeated calls for the same period are
        cheap.

        Args:
            period (int | None): zero-based period index. Pass ``None`` or a
                negative integer to retrieve all periods as an ``applylist``.

        Returns:
            ucnperiod | applylist:
                * a single ``ucnperiod`` when ``period >= 0``.
                * an ``applylist`` of all ``ucnperiod`` objects when
                  ``period`` is ``None`` or negative.

        Notes:
            Each ``ucnperiod`` is a time-restricted view; all data frames and
            trees are filtered to the period's [start, stop] window.

        Example:
            >>> cycle = run[0]
            >>> cycle.get_period(0)
            run 1846 (cycle 0, period 0):
              comment            cycle_stop         period_start       shifters           tfile
              cycle              experiment_number  period_stop        start_time         year
              cycle_param        month              run_number         stop_time
              cycle_start        period             run_title          supercycle
            >>> all_periods = cycle.get_period()   # applylist of all periods
            >>> len(all_periods)
            3
        """

        # get all periods
        if period is None or period < 0:
            nperiods = self.cycle_param.nperiods
            return applylist(map(self.get_period, range(nperiods)))
        elif period in self._perioddict.keys():
            return self._perioddict[period]
        else:
            self._perioddict[period] = ucnperiod(self, period)
            return self._perioddict[period]

    def shift_timing(self, dt):
        """Shift every period in this cycle by a constant offset, preserving period durations.

        The cycle start time is advanced by ``dt`` while each period boundary
        is shifted by the same amount, so durations remain unchanged. This may
        create a gap between adjacent cycles.

        Args:
            dt (float): seconds to add to every period start and end time.
                Negative values shift earlier.

        Notes:
            Internally calls ``ucnrun._modify_ptiming`` for each period, which
            resets all cached hit histograms. To avoid redundant histogram
            rebuilds, collect all shift values first and then apply them::

                # compute shifts without rebuilding histograms mid-loop
                dt = [cyc.get_time_shift('Li6', 2, 50) if cyc[2].period_dur > 0 else 0
                      for cyc in run]
                for i, t in enumerate(dt):
                    run[i].shift_timing(t)

        Example:
            >>> # shift cycle 0 forward by 2 seconds
            >>> run[0].shift_timing(2.0)
        """
        for period in self:
            period.modify_timing(dt, 0)
        self[-1].modify_timing(0, dt)
