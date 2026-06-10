# Open and analyze UCN data for a whole run
# Derek Fujimoto
# June 2024

import ROOT
ROOT.gROOT.SetBatch(1)
from rootloader import tfile, ttree, attrdict
from .exceptions import *
from .applylist import applylist
from .ucnbase import ucnbase
from .ttreeslow import ttreeslow
from .ucncycle import ucncycle
import warnings, os, re

import numpy as np
import pandas as pd
from tqdm import tqdm

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
        use_precise_cycles (bool): if true attempt to use precise cycle times. 
            First, check if the RunTransition_Li6 tree has precise times in it (precise times found from midas2root). 
            If not, then check if there are any hits in hardware cycle start channel on the digitizer.
            If not, raise a warning

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
        `filter`: A list of booleans indicating how we should filter cycles. More on that in [the tutorial](https://github.com/ucn-triumf/ucndata/blob/main/tutorials/filter.md)
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

    def __init__(self, run, ucn_only=True, use_precise_cycles=True):

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

        # set cycle parameters
        self.cycle_param = attrdict({'filter': None})
        self._set_valve_states()
        
        # get crude cycle times
        self.set_cycle_times_crude()

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
        self.epics = ttreeslow((self.tfile[name] for name in self.EPICS_TREES 
                                if name in self.tfile.keys()), parent=self)
        
        # store fetched cycles
        self._cycledict = dict()

        # store fetched histogram for binned data
        # detector: (resolution_ms, hits rootloader.hist1d)
        self._hits_hist = {}

        # histograms with edges set by period and cycle timings
        # detector: (bin_ms, hits np.ndarray)
        self._nhits = {}

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

        # slice on periods
        elif isinstance(key, tuple) and len(key) == 2:
            cycles = self[key[0]]
            if isinstance(cycles, (np.ndarray, applylist, list)):
                return applylist([c[key[1]] for c in cycles])
            else:
                return cycles[key[1]]
        
        # slice on cycles
        elif isinstance(key, (slice, np.ndarray, list, tuple, applylist)):
            cycles = self.get_cycle()[:self.cycle_param.ncycles]

            # no filter
            if self.cycle_param.filter is None or all(self.cycle_param.filter):
                cyc = cycles[key]

            # yes filter
            else:

                # fetch the filter and slice in the same way as the return value
                cfilter = self.cycle_param.filter[key]

                # fetch cycles and slice, then apply filter
                cyc = cycles[key]
                cyc = cyc[cfilter]

            return applylist(cyc)

        raise IndexError(f'Run {self.run_number} given an unknown index type ({type(key)})')

    def __len__(self):
        return self.cycle_param.ncycles

    def _get_nhits(self, detector, cycle=None, period=None, bin_ms=0):
        # Get number ucn hits

        # Args:
        #     detector (str): Li6|He3
        #     cycle (int): cycle number, if None compute for whole run
        #     period (int): period number, if None compute for whole cycle, if cycle is not also None
        #     bin_ms (int): hit timing resolution in milliseconds. If 0, use hit tree timings

        # Notes:
        #     Because of how RDataFrame works it is better to compute a histogram whose bins correspond to the period or cycle start/end times than to set a filter and get the resulting tree size.
        #     The histogram bin quantities is saved as self._nhits
        #     Both ucncycle and ucnperiod classes call this function to get the counts

        # get hits tree
        tree = self.tfile[self.DET_NAMES[detector]['hits']]

        # get hits for run
        if cycle is None and period is None:
            return tree.size

        # check _nhits bin_ms to see if we need to regenerate the histogram
        if detector in self._nhits.keys() and self._nhits[detector][0] != bin_ms:
            del self._nhits[detector]
            self._get_nhits(detector, 
                            cycle=cycle, 
                            period=period, 
                            bin_ms=bin_ms)

        # make hits histogram for periods and cycles
        elif detector not in self._nhits.keys():

            # use period and cycle start and end times as bin edges for _nhits
            edges = []
            for cyclei in range(self.cycle_param.ncycles):

                cycle_start = self.cycle_param.cycle_times.start[cyclei].copy()
                period_ends = self.cycle_param.period_end_times[cyclei].copy()

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

            # discard duplicate edges - this drop counts for zero length periods, 
            # we re-insert these after
            edges = np.unique(edges)

            # use resolution tree to generate the hits histogram
            if bin_ms > 0:

                # check if hits histogram exists and has the correct information
                if detector in self._hits_hist.keys() and \
                    self._hits_hist[detector][0] == bin_ms:
                    hist = self._hits_hist[detector][1]

                # generate the hits histogram from binned data
                else:
                    tree = self.tfile[self.DET_NAMES[detector]['hits']]
                    hist = tree.hist1d('tUnixTimePrecise', step=bin_ms/1000)
                    self._hits_hist[detector] = (bin_ms, hist)

                # make _nhits histogram based on _hits_hist histogram
                times = hist.x
                counts = hist.y
                
                # get the array of hits, histogrammed for each period
                hits, _ = np.histogram(times, bins=edges, weights=counts)
                
            # hits from raw events
            else:
                # first bin is hits before first edge - ie before cycle start
                hits = tree.hist1d('tUnixTimePrecise', edges=edges).y[1:]

            # rebuild hits array with zero counts for zero length periods
            dur = self.cycle_param.period_durations_s.values.transpose() # durations[cycle,period]
            idx = 0 # index in the hits array to copy for non-zero durations

            # build list of number of hits for each period
            nhits = []
            for cyci in range(dur.shape[0]):
                for peri in range(dur.shape[1]):

                    # non-zero duration, add hits from historgram
                    # index exceeds hits len if run ended before last cycle finished
                    if dur[cyci,peri] > 0 and idx < len(hits):
                        nhits.append(hits[idx])
                        idx += 1
                    
                    # zero duration add zero counts
                    else:
                        nhits.append(0)
                    
                # end of cycle hits after last period
                if idx < len(hits):
                    nhits.append(hits[idx])
                    idx += 1

            # convert to np array and save as tuple
            self._nhits[detector] = (bin_ms, np.array(nhits))

        # get hits for cycle
        if period is None:
            nperiodsp1 = len(self.cycle_param.period_end_times)+1
            return int(self._nhits[detector][1][cycle*nperiodsp1:(cycle+1)*nperiodsp1].sum())

        # get hits for period
        else:
            return int(self._nhits[detector][1][cycle*(len(self.cycle_param.period_end_times)+1)+period])

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
        self._nhits = {}

    def _set_valve_states(self):
        """"""
        # get tree as dataframe
        df = self.tfile.CycleParamTree
        df = df[[col for col in df.columns if 'Valve' in col]]
        
        if isinstance(df, ttree):
            df = df.to_dataframe()

        # valve states -------------------------------------------------------
        df = df[[col for col in df.columns if 'Valve' in col]]
        col_map = {col:int(re.sub(r'\D', '', col)) for col in df.columns}
        df = df.rename(columns=col_map)
        df.reset_index(inplace=True, drop=True)
        df.columns.name = 'valve'
        df.index.name = 'period'

        self.cycle_param['valve_states'] = df

    def _set_period_times(self):
        """Set period durations and end times based on cycle start times"""

        # get tree as dataframe
        dur = self.tfile.CycleParamTree
        dur = dur[[col for col in dur.columns if 'Duration' in col]]
        
        if isinstance(dur, ttree):
            dur = dur.to_dataframe()

        # get period durations ----------------------------------------------
        dur = dur.rename(columns={col:int(re.sub(r'\D', '', col)) for col in dur.columns})
        dur = dur.reindex(sorted(dur.columns), axis=1)
        
        # drop all-zero columns
        dur = dur.loc[:, dur.sum(axis=0)>0]

        # expand for all cycles
        dur = pd.concat([dur]*max((1, self.cycle_param.ncycles//len(dur.columns))),
                       axis='columns')
        dur.columns = np.arange(len(dur.columns))
        
        # trim missing cycles
        dur = dur[self.cycle_param.cycle_times.index]
    
        dur.index.name = 'period'
        dur.columns.name = 'cycle'

        self.cycle_param['period_durations_s'] = dur

        # get period end times ----------------------------------------------
        
        # get cycle start times
        start = self.cycle_param.cycle_times.start.values

        # sum
        ends = dur.cumsum()
        for i, st in enumerate(start):
            ends.loc[:, i] += st

        self.cycle_param['period_end_times'] = ends
        self.cycle_param['nperiods'] = len(ends.index)

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
                    msg = f'No cycles found in run {self.run_number}, although sequencer was active'

            # raise error or return
            if msg is not None:
                if raise_error:
                    raise MissingDataError(msg)
                else:
                    tqdm.write(msg)
                    return False

        return True

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

    def set_cycle_times_crude(self):
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
            >>> run.set_cycle_times_crude('li6')
            ```
        """

        # check for sequencer tree, if not then single cycle run
        if not hasattr(self.tfile, 'SequencerTree'):
            raise DataError('Missing SequencerTree. Cannot set crude cycle times')
        
        # get cycle start times from sequencer tree
        tree = self.tfile.SequencerTree.set_filter('cycleStarted != 0')
        start = tree.timestamp.values.astype(float)
        run_stop = self.tfile.SequencerTree.timestamp.max()

        # get number of cycles per supercycle
        ncycles = self.tfile.CycleParamTree.nCycles.values[0]

        # get run durations
        duration = np.diff(np.concatenate((start, [run_stop])))
        times = {'start': start,
                'duration (s)': duration,
                'stop': start + duration,
                }

        # convert to dataframe
        times = pd.DataFrame(times)
        times.index.name = 'cycle'

        # set supercycle id
        times['supercycle'] = times.index // ncycles

        # save
        self.cycle_param['cycle_times'] = times
        self.cycle_param['cycle'] = times.index % ncycles
        self.cycle_param['supercycle'] = times['supercycle']
        self.cycle_param['ncycles'] = len(times.index)
        self.cycle_param['nsupercycle'] = len(times['supercycle'].unique())
        self.cycle_param['is_precise_timing'] = False

        # update period times
        self._set_period_times()

        # reset cycle dict
        self._cycledict = {}

    def set_cycle_times_precise(self, hw_channel=10, detector='Li6'):
        """Replace crude cycle start times with hardware-timestamped precise times.

        Reads hardware-trigger hit timestamps on the specified TV1725 input hw_channel. 
        These timestamps have sub-millisecond precision compared to the sequencer-derived 
        crude cycle times. The function aligns the precise timestamps against the existing 
        crude cycle grid, back-extrapolates if the first trigger was missed, and linearly
        interpolates over any gaps where the hardware signal was not recorded.

        After a successful call, ``cycle_param`` is updated as follows:

        - ``cycle_param.cycle_times`` and ``cycle_param.period_end_times`` are
          replaced with their precise counterparts.
        - ``cycle_param.is_precise_timing`` is set to ``True``.

        The updated ``cycle_times`` DataFrame gains one extra column relative
        to the crude version:

        - ``is_measured`` (bool): ``True`` if the start time came directly from
          a recorded hardware hit; ``False`` if it was back-extrapolated or
          interpolated from the average precise cycle duration.

        If no precise timestamps are found on the requested hw_channel the function
        returns immediately without modifying ``cycle_param``.

        Args:
            hw_channel (int): TV1725 input channel carrying the hardware
                cycle-start signal. Default is 10.
            detector (str): Li6 | He3, select between RunTransition_* trees

        Note:
            The average precise cycle duration is estimated from inter-hit
            differences that agree with the crude average to within 5 seconds,
            so the crude timing must already be a reasonable first approximation.
        """

        # check if already precise times
        if self.cycle_param.is_precise_timing:
            warnings.warn(f'Run {self.run_number} is already precise timing')
            return

        # crude cycle times
        ctimes = self.cycle_param.cycle_times.start.values

        # get the detector transition tree times, hopefully they are precise times (will check later)
        if f'RunTransitions_{detector}' not in self.tfile.keys():
            raise KeyError(f'RunTransitions_{detector} not found in tfile')

        tree = self.tfile[f'RunTransitions_{detector}']
        ptimes = np.sort(tree.cycleStartTime.to_array())

        # run transitions are crude times: find the times from the hit tree
        if len(ptimes) == len(ctimes) and all(ptimes == ctimes):
            tree = self.tfile.UCNHits_Li6.reset()
            tree.set_filter(f'tChannel == {hw_channel}', inplace=True)
            ptimes = tree.tUnixTimePrecise.to_array()
            ptimes = np.sort(ptimes)

        # check if any precise times
        if len(ptimes) == 0:
            warnings.warn(f'No cycle start time hits detected in channel {hw_channel}',
                          MissingDataWarning)
            return
        
        # average crude cycle duration
        cdur = np.mean(np.diff(ctimes))

        # get average precise cycle duration for one cycle
        diff = np.diff(ptimes)
        filtered_diff = diff[abs(diff - cdur) < 5]  # cycle durations should be within 5 seconds
        if len(filtered_diff) == 0:
            warnings.warn(f'Run {self.run_number}: no precise cycle diffs within 5 s of crude duration; cannot set precise timing.', MissingDataWarning)
            return
        pdur = np.mean(filtered_diff)

        # setup new values
        new_times = []
        is_measured = []

        # check that the first precise timestamp was recorded, if not back-extrapolate
        npre_cycles = 0
        if abs(ctimes[0] - ptimes[0]) > pdur/2:
            npre_cycles = abs(int(np.round((ctimes[0] - ptimes[0])/pdur)))
            is_measured = [False] * npre_cycles
            new_times = [ptimes[0] - pdur * i for i in range(npre_cycles, 0, -1)]

        # get additional number of cycles to insert
        ncycles = np.round(diff/pdur) - 1 

        # interpolate missing values
        i = -1
        for i, n in enumerate(ncycles):
            t = ptimes[i]
            new_times.append(t)
            is_measured.append(True)

            while n > 0:
                t += pdur
                new_times.append(t)
                is_measured.append(False)
                n -= 1
                
        if len(ptimes) > i+1:
            new_times.append(ptimes[i+1])
            is_measured.append(True)

        # forward-extrapolate for any cycles after the last hardware trigger
        t = new_times[-1]
        for _ in range(len(ctimes) - len(new_times)):
            t += pdur
            new_times.append(t)
            is_measured.append(False)

        # add run stop time
        run_stop = self.tfile.SequencerTree.timestamp.max()
        durations = np.concat((np.diff(new_times), [run_stop - new_times[-1]]))

        # setup cycle times
        cycle_times = self.cycle_param.cycle_times.copy()
        cycle_times['is_measured'] = is_measured
        cycle_times['duration (s)'] = durations
        cycle_times['start'] = new_times
        cycle_times['stop'] = np.array(new_times) + durations

        # copy dicts
        self.cycle_param.cycle_times = cycle_times
        self.cycle_param['is_precise_timing'] = True

        # update period timings
        self._set_period_times()
        
        # reset cycle dict
        self._cycledict = {}
