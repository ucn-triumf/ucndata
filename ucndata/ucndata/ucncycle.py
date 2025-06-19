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
from .applylist import applylist
from .ucnbase import ucnbase
from .ucnperiod import ucnperiod
from .tsubfile import tsubfile

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
            elif hasattr(value, 'copy'):
                setattr(self, key, value.copy())
            else:
                setattr(self, key, value)

        # trim cycle parameters
        self.cycle_param.period_durations_s = self.cycle_param.period_durations_s[cycle]
        self.cycle_param.period_end_times = self.cycle_param.period_end_times[cycle]

        self.cycle = cycle
        self.supercycle = supercycle
        self.cycle_start = start
        self.cycle_stop = stop


    def __next__(self):
        # permit iteration over object like it was a list

        #
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
            if key > self.cycle_param.nperiods:
                raise IndexError(f'Run {self.run_number}, cycle {self.cycle}: Index larger than number of periods ({self.cycle_param.nperiods})')

            return self.get_period(key)

        # slice on cycles
        if isinstance(key, slice):
            period = self.get_period()[:self.cycle_param.nperiods]
            return applylist(period[key])

        raise IndexError('Cycles indexable only as a 1-dimensional object')

    def check_data(self, period_production=None, period_count=None, period_background=None,
                   raise_error=False, quiet=False):
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

            If production period specified:

                * beam data exists during production
                * beam doesn't drop too low (`beam_min_current`)
                * beam current stable (`beam_max_current_std`)

            If background period specified:

                * background count rate too high (`max_bkgd_count_rate`)
                * no background counts at all

            If count period specified:

                * check too few counts (`min_total_counts`)
                * does pileup exist? (>`pileup_cnt_per_ms` in the first `pileup_within_first_s`)

        Example:
            ```python
            >>> cycle = run[0]
            >>> x = cycle.check_data(period_production=0)
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
                print(message)
                return False

        ## overall data quality checks ---------------------------------------

        # beam data exists
        if len(self.beam_current_uA) == 0:
            return warn(BeamError, f'{msg} No beam data saved')

        # total duration
        if self.cycle_stop - self.cycle_start <= 0:
            return warn(DataError, f'{msg} Cycle duration nonsensical: {self.cycle_stop - self.cycle_start} s')

        # valve states
        if not self.cycle_param.valve_states.any().any():
            return warn(ValveError, f'{msg} No valves operated')

        # has counts
        det_counts = []
        for det in self.DET_NAMES.keys():
            try:
                det_counts.append(self.tfile[self.DET_NAMES[det]['hits']].tIsUCN.size > 1)
            except KeyError:
                pass

        if not any(det_counts):
            return warn(DataError, f'{msg} No counts detected in any detector')

        # check that proton current is stable
        beam_current = self.tfile.BeamlineEpics.B1V_KSM_PREDCUR
        if beam_current.min() < self.DATA_CHECK_THRESH['beam_min_current']:
            return warn(BeamError, f'{msg} Proton current dropped to {beam_current.min()} uA during full cycle')

        # beam_range = beam_current.max() - beam_current.min()
        # if beam_range > self.DATA_CHECK_THRESH['beam_max_current_std']:
        #     return warn(BeamError, f'{msg} Proton current fluctuated up to {beam_range:.2f} uA during full cycle')

        # check that the cycle duration is at least as long as the period duration sums
        dt_cycle = self.cycle_stop - self.cycle_start
        dt_periods = self.cycle_param.period_durations_s.sum()
        if dt_periods > dt_cycle:
            return warn(DataError, f'{msg} Cycle length ({dt_cycle}) shorter than expected given period duration sum ({dt_periods})')

        ## production period checks ------------------------------------------
        if period_production is not None:
            period = self.get_period(period_production)
            beam_current = period.beam_current_uA.iloc[1:-1]

            # beam data exists during production
            if len(beam_current) == 0:
                return warn(BeamError, f'{msg} No beam data during production period')

            # beam dropped too low
            if beam_current.min() < self.DATA_CHECK_THRESH['beam_min_current']:
                return warn(BeamError, f'{msg} Beam current dropped to {beam_current.min():.2f} uA')

            # # beam current unstable
            # beam_range = beam_current.std()
            # if beam_range > self.DATA_CHECK_THRESH['beam_max_current_std']:
            #     return warn(BeamError, f'{msg} Beam current fluctuated up to {beam_range:.2f} uA')

        ## background period checks ------------------------------------------
        if period_background is not None:

            period = self.get_period(period_background)

            for det in self.DET_NAMES.keys():
                try:
                    counts = period.tfile[self.DET_NAMES[det]['hits']].tIsUCN.sum()
                except KeyError:
                    continue

                # background count rate too high
                # rate = counts / period.cycle_param.period_durations_s
                #if rate / self.DET_BKGD[det] > self.DATA_CHECK_THRESH['max_bkgd_count_rate']:
                #    return warn(DataError, f'{msg} Background count rate in {det} detector is {rate / self.DET_BKGD[det]:.1f} times larger than expected ({self.DET_BKGD[det]} counts/s)')

                ## background counts missing
                #if counts == 0:
                #    return warn(DataError, f'{msg} No detected background counts in {det} detector')

        ## count period checks -----------------------------------------------
        if period_count is not None:

            period = self.get_period(period_count)
            for det in self.DET_NAMES.keys():

                # check too few counts
                try:
                    counts = period.get_counts(det)[0]
                    hits = period.get_hits(det)
                except KeyError:
                    continue

                if counts < self.DATA_CHECK_THRESH['min_total_counts']:
                    return warn(DataError, f'{msg} Too few counts in {det} detector during counting period ({counts} counts)')

                # check if pileup
                if period.is_pileup(det):
                    return warn(DataError, f'{msg} Detected pileup in period {period.period} of detector {det}')

                # check if counts at end are too large

                # get thresholds
                dt = self.DATA_CHECK_THRESH['count_period_last_s_is_bkgd']
                rate_thresh = self.DATA_CHECK_THRESH['max_bkgd_count_rate']*self.DET_BKGD[det]

                # get rate
                t = hits.index.values
                rate = sum(t > max(t)-dt) / dt
                if rate > rate_thresh:
                    return warn(DataError, f'{msg} Count rate ({rate:.1f}) in last {dt} s is over {rate_thresh} in period {period.period} of detector {det}')

        return True

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
        else:
            return ucnperiod(self, period)