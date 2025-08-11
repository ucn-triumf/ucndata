# Open and analyze UCN data for a whole run
# Derek Fujimoto
# June 2024

from rootloader import tfile, ttree, attrdict
from .exceptions import *
from .applylist import applylist
from .ucnbase import ucnbase
from .ttreeslow import ttreeslow
from .ucncycle import ucncycle
from .datetime import to_datetime
import itertools, warnings, os, ROOT

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections.abc import Iterable
from tqdm import tqdm

ROOT.gROOT.SetBatch(1)

# patch warnings
def new_format(message, category, filename, lineno, line):
    filename = os.path.basename(filename)
    return f'\n{filename}:{lineno}: {category.__name__}: {message}\n'

warnings.formatwarning = new_format

class ucnrun(ucnbase):
    """UCN run data. Cleans data and performs analysis

    Args:
        run (int|str): if int, generate filename with self.datadir
            elif str then run is the path to the file
        ucn_only (bool): if true set filter tIsUCN==1 on all hit trees

    Attributes:
        comment (str): comment input by users
        cycle (int|none): cycle number, none if no cycle selected
        cycle_param (attrdict): cycle parameters from sequencer settings
        experiment_number (str): experiment number input by users
        month (int): month of run start
        run_number (int): run number
        run_title (str): run title input by users
        shifter (str): experimenters on shift at time of run
        start_time (str): start time of the run
        stop_time (str): stop time of the run
        supercycle (int|none): supercycle number, none if no cycle selected
        tfile (tfile): stores tfile raw readback
        year (int): year of run start

    Notes:
        * Can access attributes of tfile directly from top-level object
        * Need to define the values if you want non-default behaviour
        * Object is indexed as [cycle, period] for easy access to sub time frames

        Cycle param contents

        `nperiods`: Number of periods in each cycle
        `nsupercyc`: Number of supercycles contained in the run
        `enable`: Enable status of the sequencer
        `inf_cyc_enable`: Enable status of infinite cycles
        `cycle`: Cycle ID numbers
        `supercycle`: Supercycle ID numbers
        `valve_states`: Valve states in each period and cycle
        `period_end_times`: End time of each period in each cycle in epoch time
        `period_durations_s`: Duration in sections of each period in each cycle
        `ncycles`: Number of total cycles contained in the run
        `filter`: A list indicating how we should filter cycles. More on that in [filters](filters.md)
        `cycle_time`: The start and end times of each cycle

    Examples:

        Loading runs
        ```python
        from ucndata import ucnrun, settings
        # load from filename
        ucnrun('/path/to/file/ucn_run_00002684.root')
        # load from run number
        ucnrun.datadir = '/path/to/file/'
        ucnrun(2684)
        ```

        Slicing
        ```python
        from ucndata import ucnrun
        run = ucnrun(2684)
        run[0, 0]   # cycle 0, period 0
        run[:]      # all cycles, no distinction on period
        run[:, 0]   # get all cycles, period 0
        run[0, :]   # cycle 0, all periods
        run[4:7, 2] # cycles 4, 5, 6, period 2
        ```

        Get beam properties
        ```python
        from ucndata import ucnrun
        run = ucnrun(2684)
        run.beam_current_uA # beam current in uA
        run.beam_on_s       # beam duration on in s
        run.beam_off_s      # beam duration off in s
        ```

        Draw hits
        ```python
        import matplotlib.pyplot as plt
        from ucndata import ucnrun
        run = ucnrun(2684)

        # draw all hits in the file
        run.get_hits_histogram('Li6').plot()

        # draw hits in each cycle
        for cycle in run:
            cycle.get_hits_histogram('Li6').plot(label=cycle.cycle)

        # adjust the timing of cycles and periods
        run._modify_ptiming(cycle=0, period=0, dt_start_s=1, dt_start_s=0)

        # inspect the data: draw a figure with hits histogram, beam current, and optional slow control data
        run.inspect('Li6', bin_ms=100, xmode='dur')
        ```
    """

    def __init__(self, run, ucn_only=True):

        # check if copying
        if run is None:
            return

        # make filename from defaults
        elif isinstance(run, (int, float, np.float64, np.int64)):
            filename = os.path.join(self.datadir, f'ucn_run_{int(run):0>8d}.root')

        # fetch from specified path
        elif isinstance(run, str):
            filename = run

        else:
            raise TypeError(f'Unknown input type "{type(run)}" for run')

        self.path = os.path.abspath(filename)

        # read
        self.tfile = tfile(filename, empty_ok=False, quiet=True,
                            key_filter=self.keyfilter)
        head = self.tfile['header'].to_dataframe()

        # reformat header and move to top level
        for k, val in head.items():
            setattr(self, k.replace(' ', '_').lower(), val.loc[0])

        if type(self.run_number) is pd.Series:
            self.run_number = int(float(self.run_number[0]))
        else:
            self.run_number = int(float(self.run_number))

        # set other header items
        date = pd.to_datetime(self.start_time)
        self.year = date.year
        self.month = date.month

        # reformat tfile branch names to remove spaces
        for key in tuple(self.tfile.keys()):
            if ' ' in key or '-' in key:
                self.tfile[key.replace(' ', '_').replace('-','')] = self.tfile[key]
                del self.tfile[key]

        # some trees should be dataframes by default
        for name in self.DATAFRAME_TREES:
            if name in self.tfile.keys():
                self.tfile[name] = self.tfile[name].to_dataframe()
                self.tfile[name].reset_index(inplace=True, drop=True)

        # set cycle parameters
        self._get_cycle_param()

        # get cycle times
        if hasattr(self, 'cycle_param'):
            cycle_failed = False
            if isinstance(self.cycle_times_mode, str):
                self.cycle_times_mode = [self.cycle_times_mode]

            for mode in self.cycle_times_mode:
                try:
                    self.set_cycle_times(mode=mode)
                except (AttributeError, IndexError):
                    warnings.warn(f'Run {self.run_number}: Unable to set cycle times. SequencerTree must exist and have entries.',
                                MissingDataWarning)
                    break
                except (KeyError, CycleError):
                    print(f'Run {self.run_number}: Cycle time detection mode {mode} failed')
                    cycle_failed = True
                else:
                    break

            if cycle_failed:
                print(f'Run {self.run_number}: Set cycle times based on {mode} detection mode')

        # setup tree filters
        for detector in self.DET_NAMES.keys():
            try:
                tree = self.tfile[self.DET_NAMES[detector]['hits']]
            except KeyError:
                continue

            # purge bad timestamps
            tree.set_filter('tUnixTimePrecise > 15e8', inplace=True)

            # filter on ucn hits
            if ucn_only:
                tree.set_filter('tIsUCN>0', inplace=True)

        # make slow control tree
        self.epics = ttreeslow(self.tfile[name] for name in self.EPICS_TREES)

        # store fetched cycles
        self._cycledict = dict()

        # store fetched histogram
        self._hits_hist = {'detector':None,
                           'bin_ms': None,
                           'hist':None}

        # histograms with edges set by period and cycle timings
        self._nhits = None

        # pointer to self for cycles and periods
        self._run = self

    def __next__(self):
        # permit iteration over object like it was a list

        if self._iter_current < self.cycle_param.ncycles:

            # skip elements that should be filtered
            if self.cycle_param.filter is not None:

                # skip
                while not self.cycle_param.filter[self._iter_current]:
                    self._iter_current += 1

                    # end condition
                    if self._iter_current >= self.cycle_param.ncycles:
                        raise StopIteration()

            # iterate
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
            s = f'run {self.run_number}:\n'
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
                key = self.cycle_param.ncycles + key

            if key > self.cycle_param.ncycles:
                raise IndexError(f'Run {self.run_number}: Index larger than number of cycles ({self.cycle_param.ncycles})')

            return self.get_cycle(key)

        # slice on cycles
        if isinstance(key, slice):
            cycles = self.get_cycle()[:self.cycle_param.ncycles]

            # no filter
            if self.cycle_param.filter is None or all(self.cycle_param.filter):
                cyc = cycles[key]

            # yes filter
            else:

                # fetch the filter and slice in the same way as the return value
                cfilter = self.cycle_param.filter[key]

                # fetch cycles and slice, then apply filter
                cyc = np.array(cycles[key])
                cyc = cyc[cfilter]

            return applylist(cyc)

        # slice on periods
        if isinstance(key, tuple):
            cycles = self[key[0]]
            if isinstance(cycles, (np.ndarray, applylist, list)):
                return applylist([c[key[1]] for c in cycles])
            else:
                return cycles[key[1]]

        raise IndexError(f'Run {self.run_number} given an unknown index type ({type(key)})')

    def _get_cycle_param(self):
        # set self.cycle_param dict

        # reformat cycle param tree
        paramtree = self.tfile.CycleParamTree
        self.cycle_param = {'nperiods': paramtree.nPeriods[0],
                            'nsupercyc': paramtree.nSuperCyc[0],
                            'enable': bool(paramtree.enable[0]),
                            'inf_cyc_enable': bool(paramtree.infCyclesEnable[0]),
                            'ncycles': 1
                            }
        self.cycle_param = attrdict(self.cycle_param)

        # cycle filter
        self.cycle_param['filter'] = None

        # setup cycle paramtree array outputs from transition trees
        treelist = []
        for detector in self.DET_NAMES.values():
            if detector['transitions'] in self.tfile.keys():
                treelist.append(self.tfile[detector['transitions']])

        # check if trees exist
        if not treelist:
            warnings.warn(f'Run {self.run_number}: no detector transition tree, cannot fully set up cycle_param', MissingDataWarning)

            # number of cycles, periods
            self.cycle_param['ncycles'] = 1
            self.cycle_param['nperiods'] = 1

            # cycle and supercycle indices
            self.cycle_param['cycle'] = pd.Series([0], index=[0])
            self.cycle_param['supercycle'] = pd.Series([0], index=[0])

            self.cycle_param['cycle'].name = 'cycleIndex'
            self.cycle_param['supercycle'].name = 'superCycleIndex'

            return

        # get longest
        treelen = [len(t) for t in treelist]
        tree = treelist[np.argmax(treelen)]

        # cycle and supercycle indices
        self.cycle_param['cycle'] = tree['cycleIndex'].astype(int)
        self.cycle_param['supercycle'] = tree['superCycleIndex'].astype(int)

        # convert the array in each cell into a dataframe
        def item_to_df(x):
            s = pd.DataFrame(np.array(x).copy(), index=np.arange(len(x))+1)
            return s

        # valve states -------------------------------------------------------
        df = tree[[col for col in tree.columns if 'valveState' in col]]
        col_map = {col:int(col.replace("valveStatePeriod", "")) for col in df.columns}
        df = df.rename(columns=col_map)
        df.columns.name = 'period'
        df.reset_index(inplace=True, drop=True)
        df.index.name = 'cycle_idx'

        # valve states should not change across cycles
        df2 = df.loc[0]
        df2 = pd.concat([item_to_df(df2[period]) for period in df2.index], axis='columns')

        # rename columns and index
        df2.columns = np.arange(len(df2.columns))
        df2.columns.name = 'period'
        df2.index.name = 'valve'
        self.cycle_param['valve_states'] = df2.transpose()

        # period end times ---------------------------------------------------
        df = tree[[col for col in tree.columns if 'cyclePeriod' in col]]
        col_map = {col:int(col.replace("cyclePeriod", "").replace("EndTime", "")) for col in df.columns}

        # rename columns and index
        df = df.rename(columns=col_map)
        df.columns.name = 'period'
        df.index.name = 'cycle'
        self.cycle_param['period_end_times'] = df.transpose()

        # period durations ---------------------------------------------------
        cycle_start = tree.cycleStartTime
        df_diff = df.diff(axis='columns')
        df_diff[0] = df[0] - cycle_start

        self.cycle_param['period_durations_s'] = df_diff.transpose()

        # number of cycles
        self.cycle_param['ncycles'] = len(df.index)

    def _get_nhits(self, detector, cycle=None, period=None):
        # Get number ucn hits

        # Args:
        #     detector (str): Li6|He3
        #     cycle (int): cycle number, if None compute for whole run
        #     period (int): period number, if None compute for whole cycle, if cycle is not also None

        # Notes:
        #     Because of how RDataFrame works it is better to compute a histogram whose bins correspond to the period or cycle start/end times than to set a filter and get the resulting tree size.
        #     The histogram bin quantities is saved as self._nhits or self._nhits_cycle
        #     Both ucncycle and ucnperiod classes call this function to get the counts

        # get hits tree
        tree = self.tfile[self.DET_NAMES[detector]['hits']]

        # get hits for run
        if cycle is None and period is None:
            return tree.size

        else:

            # make hits histogram
            if self._nhits is None:

                # use period and cycle start and end times as bin edges
                edges = []
                for cyclei in range(self.cycle_param.ncycles):

                    # get cycle start and end
                    cycle_start = self.cycle_param.cycle_times.start[cyclei]
                    period_ends = self.cycle_param.period_end_times[cyclei]

                    # shorten periods that extend past the end of the cycle (edge case)
                    if cyclei < self.cycle_param.ncycles-1:
                        next_cycle_start = self.cycle_param.cycle_times.start[cyclei+1]
                    else:
                        next_cycle_start = self.cycle_param.cycle_times.stop.iloc[-1]

                    period_ends[period_ends > next_cycle_start] = next_cycle_start

                    # save to list
                    edges.append(cycle_start)
                    edges.extend(list(period_ends))

                edges = np.append(edges, self.cycle_param.cycle_times.stop.iloc[-1])
                edges = np.append(edges, self.cycle_param.cycle_times.stop.iloc[-1]) # need duplicate end bin for some reason

                self._nhits = tree.hist1d('tUnixTimePrecise', edges=edges).y[1:]

            # get hits for cycle
            if period is None:
                nperiodsp1 = len(self.cycle_param.period_end_times)+1
                return int(self._nhits[cycle*nperiodsp1:(cycle+1)*nperiodsp1].sum())

            # get hits for period
            else:
                return int(self._nhits[cycle*(len(self.cycle_param.period_end_times)+1)+period])

    def _modify_ptiming(self, cycle, period, dt_start_s=0, dt_stop_s=0, update_duration=True):
        # Change start and end times of periods

        # Args:
        #     cycle (int): cycle id number
        #     period (int): period id number
        #     dt_start_s (float): change to the period start time
        #     dt_stop_s (float): change to the period stop time
        #     update_duration (bool): if true, update period durations dataframe

        # Notes:
        #     * as a result of this, cycles may overlap or have gaps
        #     * periods are forced to not overlap and have no gaps
        #     * cannot change cycle end time, but can change cycle start time
        #     * this function resets all saved histgrams and hits

        # get cycle parameters
        cycpar = self.cycle_param

        # start times - prevent unnecessary recursion
        if dt_start_s != 0:

            # adjust cycle start
            if period == 0:
                cycpar.cycle_times.loc[cycle, 'start'] += dt_start_s

            # period start time adjustment
            else:
                cycpar.period_end_times.loc[period-1, cycle] += dt_start_s

            # recursively adjust adjacent size zero periods
            if period-1 > 0 and cycpar.period_durations_s.loc[period-1, cycle] == 0:
                self._modify_ptiming(cycle, period-1,
                                    dt_start_s = dt_start_s,
                                    dt_stop_s  = 0,
                                    update_duration = False)

        # stop times - prevent unnecessary recursion
        if dt_stop_s != 0:

            # period end time adjustment
            cycpar.period_end_times.loc[period, cycle] += dt_stop_s

            # force periods to stay within cycle bounds
            cycend = cycpar.cycle_times.loc[cycle, 'stop']
            perend = cycpar.period_end_times.loc[period, cycle]
            cycpar.period_end_times.loc[period, cycle] = min(perend, cycend)

            # recursively adjust adjacent size zero periods
            try:
                if cycpar.period_durations_s.loc[period+1, cycle] == 0:
                    self._modify_ptiming(cycle, period+1,
                                        dt_start_s = 0,
                                        dt_stop_s  = dt_stop_s,
                                        update_duration = False)

            # period not in durations dataframe
            except KeyError:
                pass

        # adjust period and cycle durations
        if update_duration:

            start = cycpar.cycle_times['start']
            stop = cycpar.cycle_times['stop']

            df = cycpar.period_end_times
            df_diff = df.diff()
            df_diff.loc[0] = df.loc[0] - start
            cycpar.period_durations_s = df_diff

            cycpar.cycle_times.loc[cycle, 'duration (s)'] = (stop-start).loc[0]

        # set in memory
        self.cycle_param = cycpar

        # remove saved cycles to account for updated limits
        if cycle in self._cycledict.keys():
            del self._cycledict[cycle]

        # reset histogram for number of hits
        self._nhits = None

        # reset all saved histograms
        for key in self._hits_hist.keys():
            self._hits_hist[key] = None

    def check_data(self, raise_error=False):
        """Run some checks to determine if the data is ok.

        Args:
            raise_error (bool): if true, raise an error if check fails, else return false

        Returns:
            bool: true if check passes, else false.

        Notes:
            * Do the self.SLOW_TREES exist and have entries?
            * Are there nonzero counts in UCNHits?

        Example:
            ```python
            >>> run.check_data()
            True
            ```
        """

        # check some necessary data trees
        for tree in self.SLOW_TREES:

            msg = None

            # does tree exist?
            if tree not in self.tfile.keys():
                msg = f'Missing ttree "{tree}" in run {self.run_number}'

            # does tree have entries?
            elif len(self.tfile[tree]) == 0:
                msg = f'Zero entries found in "{tree}" ttree in run {self.run_number}'

            # raise error or return
            if msg is not None:
                if raise_error:
                    raise MissingDataError(msg)
                else:
                    print(msg)
                    return False

        for name, det in self.DET_NAMES.items():

            # check for nonzero counts
            if not self.tfile[det['hits']].tIsUCN.any():
                msg = f'No UCN hits in "{name}" ttree in run {self.run_number}'

            # check if sequencer was enabled but no run transitions
            elif any(self.tfile.SequencerTree.sequencerEnabled):

                if len(self.tfile[det['transitions']]) == 0:
                    msg = 'No cycles found in run {self.run_number}, although sequencer was active'

            # raise error or return
            if msg is not None:
                if raise_error:
                    raise MissingDataError(msg)
                else:
                    tqdm.write(msg)
                    return False

        return True

    def draw_cycle_times(self, ax=None, xmode='datetime', do_legend=False):
        """Draw cycle start times as thick black lines, period end times as dashed lines

        Args:
            ax (plt.Axes): axis to draw in, if None, draw in current axes
            xmode (str): datetime|duration|epoch
            do_legend (bool): if true draw legend colors for period numbers

        Notes:
            Assumed periods:    0 - irradiation
                                1 - storage
                                2 - count
        """

        # check input
        if all((xmode not in i for i in ('datetime', 'duration', 'epoch'))):
            raise RuntimeError('xmode must be one of datetime|duration|epoch')

        # get axis to draw in
        if ax is None:
            ax = plt.gca()

        # run start time
        if xmode in 'duration':
            run_start = self.cycle_param.cycle_times.loc[0, 'start']
        else:
            run_start = 0

        # draw lines
        non_zero_periods = []
        for cyc in self.get_cycle():

            # get x value
            if xmode in 'datetime':
                start = pd.to_datetime(cyc.cycle_start, unit='s')
            else:
                start = cyc.cycle_start - run_start

            # draw
            ax.axvline(start, color='k', ls='-', lw=2)

            for i, per in enumerate(cyc):

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
            text = f'Cycle {cyc.cycle}'

            # check if filtered
            if cyc.cycle_param.filter is None or cyc.cycle_param.filter:
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
        if do_legend:
            handles = [mpatches.Patch(color=f'C{period}', label=f'Period {period}') \
                    for period in np.unique(non_zero_periods)]
            ax.legend(handles=handles)

    def gen_cycle_filter(self, quiet=False):
        """Generate filter array for cycles. Use with self.set_cycle_filter to filter cycles.

        Args:
            quiet (bool): if true don't print or raise exception

        Returns:
            np.array(bool): true if keep cycle, false if discard

        Notes:
            calls `ucncycle.check_data` on each cycle

        Example:
            ```python
            >>> run = ucnrun(2575)
            >>> run.gen_cycle_filter()
            Run 2575, cycle 0: 1A current dropped below 0.1 uA
            Run 2575, cycle 1: 1A current dropped below 0.1 uA

            array([False, False,  True,  True,  True,  True,  True,  True,  True,
                    True,  True,  True])
            ```
        """

        cycles = self.get_cycle()
        iterator = tqdm(cycles, desc=f'Run {self.run_number}: Scanning cycles',
                                leave=False,
                                total=self.cycle_param.ncycles)
        cfilter = [c.check_data(quiet=quiet, raise_error=False) for c in iterator]
        return np.array(cfilter)

    def get_cycle(self, cycle=None):
        """Return a copy of this object, but trees are trimmed to only one cycle.

        Note that this process converts all objects to dataframes

        Args:
            cycle (int): cycle number, if None, get all cycles

        Returns:
            ucncycle:
                if cycle > 0:  ucncycle object
                if cycle < 0 | None: a list ucncycle objects for all cycles

        Examples:
            ```python
            # get single cycle
            >>> run.get_cycle(0)
            run 1846 (cycle 0):
                comment            cycle_start        month              shifters           supercycle
                cycle              cycle_stop         run_number         start_time         tfile
                cycle_param        experiment_number  run_title          stop_time          year

            # get all cycles
            >>> len(run.get_cycle())
            17
            ```
        """

        if cycle is None or cycle < 0:
            ncycles = len(self.cycle_param.cycle_times.index)
            return applylist(map(self.get_cycle, range(ncycles)))
        elif cycle in self._cycledict.keys():
            return self._cycledict[cycle]
        else:
            self._cycledict[cycle] = ucncycle(self, cycle)
            return self._cycledict[cycle]

    def inspect(self, detector='Li6', bin_ms=100, xmode='duration', slow=None):
        """Draw counts and BL1A current with indicated periods to determine data quality

        Args:
            detector (str): detector from which to get the counts from. Li6|He3
            bin_ms (int): histogram bin size in ms
            xmode (str): datetime|duration|epoch
            slow (list|str): name of slow control tree to add in a separate axis, can be a list of names
        """

        # check input
        if all((xmode not in i for i in ('datetime', 'duration', 'epoch'))):
            raise RuntimeError('xmode must be one of datetime|duration|epoch')

        # number of rows in figure
        nrows = 2

        # check input
        if slow is not None:
            if isinstance(slow, str):
                if slow not in self.epics.columns:
                    raise KeyError(f'Input slow ("{slow}") not found in tree "epics"')
                slow = [slow]
            elif isinstance(slow, Iterable):
                for s in slow:
                    if s not in self.epics.columns:
                        raise KeyError(f'Input slow ("{slow}") not found in tree "epics"')
            else:
                raise RuntimeError('Input "slow" must be a string or iterable')

            # extra row for slow control
            nrows += len(slow)

        # make figure
        _, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True,
                        layout='constrained', figsize=(8,10))

        # get current and histogram
        current = self.beam1a_current_uA
        current.sort_index(inplace=True)
        hist = self.get_hits_histogram(detector, bin_ms=bin_ms).to_dataframe()
        hist.set_index('tUnixTimePrecise', inplace=True)
        hist = hist['Count']

        # get slow control
        if slow is not None:
            slow = {s:self.epics[s].to_dataframe() for s in slow}

        # run start time
        run_start = self.cycle_param.cycle_times.loc[0, 'start']

        for cyc in self.get_cycle():
            for i, per in enumerate(cyc):

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
            cur = current.loc[per.period_stop:cyc.cycle_stop]

            if len(cur) > 0:
                if xmode in 'datetime':
                    cur.index = pd.to_datetime(cur.index, unit='s')
                elif xmode in 'duration':
                    cur.index -= run_start

                cur.plot(ax=axes[0], color=f'k')

            # draw the rest of the run - histogram
            hi = hist.loc[per.period_stop:cyc.cycle_stop]

            if len(hi) > 0:
                if xmode in 'datetime':
                    hi.index = pd.to_datetime(hi.index, unit='s')
                elif xmode in 'duration':
                    hi.index -= run_start

                hi.plot(ax=axes[1], color=f'k')

            # draw slow control
            if slow is not None:
                for i, (key, val) in enumerate(slow.items()):
                    v = val.loc[per.period_stop:cyc.cycle_stop]
                    if len(v) > 0:
                        if xmode in 'datetime':
                            v.index = pd.to_datetime(v.index, unit='s')
                        elif xmode in 'duration':
                            v.index -= run_start
                    v.plot(ax=axes[i+2], color=f'k')

        # draw vertical markers
        for i, ax in enumerate(axes):
            self.draw_cycle_times(ax=ax, xmode=xmode, do_legend=(i==0))

        # plot elements
        axes[0].set_title(self.run_number,fontsize='x-small')
        axes[0].set_ylabel('BL1A Current (uA)')
        axes[1].set_ylabel(f'UCN Counts/{bin_ms/1000:g}s')

        if slow is not None:
            slow_keys = tuple(slow.keys())
            for i, ax in enumerate(axes[2:]):
                ax.set_ylabel(slow_keys[i].split('_')[-2])

        if xmode in 'datetime':
            axes[-1].set_xlabel('')
        elif xmode in 'duration':
            axes[-1].set_xlabel('Time Since Run Start (s)')
        else:
            axes[-1].set_xlabel('Epoch Time')
        axes[1].set_yscale('log')

    def keyfilter(self, name):
        """Don't load all the data in each file, only that which is needed"""

        name = name.replace(' ', '_').lower()

        # reject some keys based on partial matches
        reject_keys = ('v1725', 'v1720', 'v792', 'tv1725', 'charge', 'edge_diff',
                       'pulse_widths', 'iv2', 'iv3', 'rate')
        for key in reject_keys:
            if key in name:
                return False

        return True

    def set_cycle_filter(self, cfilter=None):
        """Set filter for which cycles to fetch when slicing or iterating

        Args:
            cfilter (None|iterable): list of bool, True if keep cycle, False if reject.
                if None then same as if all True

        Returns:
            None: sets self.cycle_param.filter

        Notes:
            Filter is ONLY applied when fetching cycles as a slice or as an iterator. ucnrun.get_cycle() always returns unfiltered cycles.

            Examples where the filter is applied:
                * run[:]
                * run[3:10]
                * run[:3]
                * for c in run: print(c)

            Examples where the filter is not applied:
                * run[2]
                * run.get_cycle()
                * run.get_cycle(2)

        Example:

            ```python
            # check how many cycles are fetched without filter
            >>> len(run[:])
            17

            # apply a filter
            >>> filter = np.full(17, True)
            >>> filter[2] = False
            >>> run.set_cycle_filter(filter)

            # check that cycle 2 is filtered out
            >>> len(run[:])
            16
            >>> for c in run:
                    print(c.cycle)
            0
            1
            3
            4
            5
            6
            7
            8
            9
            10
            11
            12
            13
            14
            15
            16
            ```
        """

        # check input
        cfilter = np.array(cfilter).astype(bool)

        if len(cfilter) != self.cycle_param.ncycles:
            raise RuntimeError(f'Run {self.run_number}: Length of cycle filter ({len(cfilter)}) does not match expected number of cycles ({self.cycle_param.ncycles})')

        # set
        self.cycle_param.filter = cfilter

        # set for already fetched cycles
        for key, cyc in self._cycledict.items():
            cyc.cycle_param.filter = self.cycle_param.filter[key]

    def set_cycle_times(self, mode):
        """Get start and end times of each cycle from the sequencer and save
        into self.cycle_param.cycle_times

        Run this if you want to change how cycle start times are calculated

        Args:
            mode (str): default|matched|sequencer|he3|li6
                if matched: look for identical timestamps in RunTransitions from detectors
                if sequencer: look for inCycle timestamps in SequencerTree
                if he3: use He3 detector cycle start times
                if li6: use Li6 detector cycle start times

        Returns:
            pd.DataFrame: with columns "start", "stop", "offset" and "duration (s)". Values are in epoch time. Indexed by cycle id. Offset is the difference in detector start times: he3_start-li6_start


        Notes:
            - If run ends before sequencer stop is called, a stop is set to final timestamp.
            - If the sequencer is disabled mid-run, a stop is set when disable ocurrs.
            - If sequencer is not enabled, then make the entire run one cycle
            - For matched mode,
                - set run stops as start of next transition
                - set offset as start_He3 - start_Li6
                - set start/stop/duration based on start_He3
            - If the object reflects a single cycle, return from cycle_start, cycle_stop

        Example:
            ```python
            # this calculates new cycle start and end times based on the selected method
            >>> run.set_cycle_times('li6')
            ```
        """

        # check if single cycle
        if hasattr(self, 'cycle'):
            return pd.DataFrame({'start':[self.cycle_start],
                                 'stop':[self.cycle_stop],
                                 'duration (s)': [self.cycle_stop-self.cycle_start],
                                 'offset (s)': [0.0],
                                 'supercycle': [self.supercycle]},
                                 index=[self.cycle])

        # get mode
        mode = mode.lower()

        # get run end time from control trees - used in matched and detector cycles times
        run_stop = -np.inf
        for treename in self.SLOW_TREES:
            try:
                max_time = self.tfile[treename].index.max()

            # tree not found, skip
            except KeyError:
                continue

            run_stop = max((max_time, run_stop))

        # bad end time
        if np.isinf(run_stop):
            raise MissingDataError(f"Run {self.run_number}: Missing slow control trees, cannot find run end time.")

        # get squencer data
        try:
            df = self.tfile.SequencerTree
        except AttributeError:
            df = None
        else:
            if type(df) == ttree:
                df = df.to_dataframe()

        ## if no sequencer, make the whole run a single cycle
        if df is None or not any(df.sequencerEnabled):

            times = {'start': np.inf,
                     'stop':  -np.inf,
                     'supercycle': [0]}

            # use timestamps from slow control trees to determine timestamps
            for treename in self.SLOW_TREES:

                # check for tree
                if treename not in self.tfile.keys():
                    continue

                # get times
                if isinstance(self.tfile[treename], pd.DataFrame):
                    idx = self.tfile[treename].index
                else:
                    idx = self.tfile[treename].to_dataframe().index

                # find min and max
                times['start'] = [min((idx.min(), times['start']))]
                times['stop']  = [max((idx.max(), times['stop']))]
                break

        ## get matched timesteps from He3 and Li6 RunTransitions
        elif mode in 'matched':
            hestart = self.tfile[self.DET_NAMES['He3']['transitions']].cycleStartTime
            listart = self.tfile[self.DET_NAMES['Li6']['transitions']].cycleStartTime
            scycle = self.tfile[self.DET_NAMES['He3']['transitions']].superCycleIndex

            # drop duplicate timestamps
            hestart = hestart.drop_duplicates()
            listart = listart.drop_duplicates()

            # get all possible pairs and sort by time difference
            pairs = sorted(itertools.product(hestart, listart),
                            key = lambda t: abs(t[0] - t[1]))

            # save output
            matchedhe3 = []
            matchedli6 = []

            # go through all possible pairs
            for pair in pairs:

                # if none of the two start times are already in the matched list, add the pair to the matched list
                if pair[0] not in matchedhe3 and pair[1] not in matchedli6:
                    offset = pair[0] - pair[1]

                    # discard if time difference is too large
                    if abs(offset) > 20:
                        raise CycleError(f'He3 cycle start time ({pair[0]}) too distant from Li6 start ({pair[1]}) in run {self.run_number}')
                    else:
                        matchedhe3.append(pair[0])
                        matchedli6.append(pair[1])

            matchedhe3 = np.sort(matchedhe3)
            matchedli6 = np.sort(matchedli6)

            # warnings for unmatched cycles
            unmatched = [t not in matchedhe3 for t in hestart.values]
            if any(unmatched):
                raise CycleError(f'Found no match to He3 cycles at {hestart.values[unmatched]} in run {self.run_number}')

            unmatched = [t not in matchedhe3 for t in listart.values]
            if any(unmatched):
                raise CycleError(f'Found no match to Li6 cycles at {listart.values[unmatched]} in run {self.run_number}')

            # setup output
            times = {'start': matchedhe3,
                     'duration (s)': np.concatenate((np.diff(matchedhe3), [run_stop])),
                     'offset (s)': matchedhe3-matchedli6}
            times['stop'] = times['start'] + times['duration (s)']
            times['supercycle'] = scycle

        ## get timestamps from sequencer
        elif mode in 'sequencer':

            # if sequencer is not enabled cause a stop transition
            df.inCycle *= df.sequencerEnabled

            # start counting only after first start flag
            df = df.loc[df.loc[df.cycleStarted > 0].index[0]:]

            # get start and end times
            df = df.diff()
            times = {'start': df.index[df.inCycle == 1],
                    'stop': df.index[df.inCycle == -1],
                    'supercycle': 0}

            # check lengths
            if len(times['start']) > len(times['stop']):
                times['stop'].append(df.index[-1])

        ## detector start times
        elif mode in 'he3':

            start = self.tfile[self.DET_NAMES['He3']['transitions']].cycleStartTime
            start = start.drop_duplicates()

            # setup output
            times = {'start': start,
                     'duration (s)': np.diff(np.concatenate((start, [run_stop])))
                    }
            times['stop'] = times['start'] + times['duration (s)']
            times['supercycle'] = self.tfile[self.DET_NAMES['He3']['transitions']].superCycleIndex

        ## detector start times
        elif mode in 'li6':

            start = self.tfile[self.DET_NAMES['Li6']['transitions']].cycleStartTime
            start = start.drop_duplicates()

            # setup output
            times = {'start': start,
                     'duration (s)': np.diff(np.concatenate((start, [run_stop]))),
                    }
            times['stop'] = times['start'] + times['duration (s)']
            times['supercycle'] = 0

        ## bad mode
        else:
            raise RuntimeError(f"Bad mode input {mode}")

        # convert to dataframe
        times = pd.DataFrame(times)
        times['duration (s)'] = times.stop - times.start
        times.index.name = 'cycle'

        # save
        self.cycle_param['cycle_times'] = times
        self.cycle_param['ncycles'] = len(times.index)

        # finish setting up cycle_param
        if 'period_end_times' not in self.cycle_param.keys():
            self.cycle_param['period_end_times'] = pd.DataFrame({0:times.loc[0, 'stop']}, index=[0])
            self.cycle_param['period_end_times'].index.name = 'period'
            self.cycle_param['period_end_times'].columns.name = 'cycle'

        if 'period_durations_s' not in self.cycle_param.keys():
            self.cycle_param['period_durations_s'] = pd.DataFrame({0:times.loc[0, 'duration (s)']}, index=[0])
            self.cycle_param['period_durations_s'].index.name = 'period'
            self.cycle_param['period_durations_s'].columns.name = 'cycle'

        return times
