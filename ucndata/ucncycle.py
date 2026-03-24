# Open and analyze UCN data for a one cycle
# Derek Fujimoto
# Oct 2024
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
        return self.cycle_param.nperiods

    def __next__(self):
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
            period_production (int): index of period where the beam should be stable. Enables checks of beam stability
            period_count (int): index of period where we count ucn. Enables checks of data quantity
            period_background (int): index of period where we do not count ucn. Enables checks of background
            raise_error (bool): if true, raise an error if check fails, else return false. Inactive if quiet=True
            quiet (bool): if true don't print or raise exception

        Returns:
            bool: true if check passes, else false.

        Note:

            Checks performed

            * is there BeamlineEpics data?
            * is the cycle duration greater than 0?
            * is at least one valve opened during at least one period?
            * are there counts in each detector?

        Example:
            ```python
            >>> cycle = run[0]
            >>> x = cycle.check_data()
            Run 1846, cycle 0: Beam current dropped to 0.0 uA
            >>> x
            False
            ```
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
        if any(self.beam1a_current_uA < self.DATA_CHECK_THRESH['beam_min_current']):
            return warn(BeamError, f'{msg} 1A current dropped below {self.DATA_CHECK_THRESH["beam_min_current"]} uA')

        # drop cycles where the 1A beam drops to zero within 5 s of the cycle starting
        if self.cycle > 0:
            cyc_last = self._run[self.cycle-1]
            current = cyc_last.beam1a_current_uA
            idx = current.index > self.cycle_start-20
            if any(current.loc[idx] < self.DATA_CHECK_THRESH["beam_min_current"]):
                return warn(BeamError, f'{msg} 1A current dropped below {self.DATA_CHECK_THRESH["beam_min_current"]} uA within 20 seconds of the cycle starting')

        return True

    def draw_cycle_times(self, ax=None, xmode='datetime'):
        """Draw cycle start times as thick black lines, period end times as dashed lines

        Args:
            ax (plt.Axes): axis to draw in, if None, draw in current axes
            xmode (str): datetime|duration|duration_run|duration_cycle|epoch

        Notes:
            Assumed periods:    0 - irradiation
                                1 - storage
                                2 - count
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

        for i, per in enumerate(self):

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
            Getting the hits with resolution_ms=0 requires that you parse the 
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
                                    bin_ms=bin_ms)

    def get_period(self, period=None):
        """Return a copy of this object, but trees are trimmed to only one period.

        Notes:
            * This process converts all objects to dataframes
            * Must be called for a single cycle only
            * Equivalent to indexing style: `cycle[period]`

        Args:
            period (int): period number, if None, get all periods
            cycle (int|None) if cycle not specified then specify a cycle

        Returns:
            run:
                if period > 0: a copy of this object but with data from only one period.
                if period < 0 | None: a list of copies of this object for all periods for a single cycle

        Example:
            ```python
            >>> cycle = run[0]
            >>> cycle.get_period(0)
            run 1846 (cycle 0, period 0):
                comment            cycle_stop         period_start       shifters           tfile
                cycle              experiment_number  period_stop        start_time         year
                cycle_param        month              run_number         stop_time
                cycle_start        period             run_title          supercycle
            ```
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
        """Shift all periods by a constant time, maintaining the period durations.
        This shifts the cycle start time and shortens the cycle, potentially creating gaps between cycles

        Args:
            dt (float): time in seconds to add to each period start/end time

        Example:
            ```python
                # this avoids recomputing the histograms each iteration
                dt = [cyc.get_time_shift('Li6', 2, 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
                for i, t in enumerate(dt):
                    run[i].shift_timing(t)
            ```

        Notes:
            * This function makes use of `ucnrun._modify_ptiming`, which resets all saved histograms and hits
        """
        for period in self:
            period.modify_timing(dt, 0)
        self[-1].modify_timing(0, dt)
