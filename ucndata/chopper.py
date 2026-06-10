# Chopper data analysis
# Chopper times are split into frames, with the frame start times injected into 
# channel 15 of the Li6 digitizer
#
# Derek Fujimoto
# Jan 2025

import ucndata
import os
import numpy as np
import pandas as pd

class crun(ucndata.ucnrun):
    def __init__(self, run, ucn_only=True, chop_time_ch=15):
        """Load a UCN run file and extract chopper frame timing.

        Extends ucnrun by reading chopper opening times from a dedicated
        Li6 digitizer channel and storing them as frame start times in
        cycle_param. Frame times are clipped to the maximum cycle stop time.

        Args:
            run (int|str): run number or path to ROOT file.
            ucn_only (bool): if True, keep only UCN-flagged hits; otherwise
                keep all detector hits. Defaults to True.
            chop_time_ch (int): Li6 digitizer channel whose hits mark chopper
                opening times. Defaults to 15.

        Notes:
            * `self.cycle_param.frame_start_times` are trimmed to be less
              than the maximum cycle stop time found by
              `self.cycle_param.cycle_times.stop.max()`
        """
        super().__init__(run, ucn_only)

        tree = self.tfile['UCNHits_Li6'].reset()
        tree.set_filter(f'tChannel == {chop_time_ch}', inplace=True)
        times = tree.tUnixTimePrecise.to_dataframe().index.values

        # ensure frames are within the bounds of the run
        stop_time = self.cycle_param.cycle_times.stop.max()
        times = times[times < stop_time]

        # save values
        self.cycle_param['nframes'] = len(times)
        self.cycle_param['frame_start_times'] = times
        self.chop_time_ch = chop_time_ch
        self._ucn_only = ucn_only

        self._nhits_frame = None

    def __getitem__(self, key):
        """Return cycle(s), period(s), or frame(s) via index or slice notation.

        Supports integer indexing, slices, and tuples of up to three elements
        corresponding to (cycle, period, frame) dimensions. Negative integers
        are resolved relative to the total cycle count. When cycle_param.filter
        is set, filtered-out cycles are excluded from slice results.

        Args:
            key (int|slice|tuple): index into the run hierarchy.
                * int — return a single ccycle.
                * slice — return an applylist of ccycle objects.
                * (cycle, period) — return period(s) within cycle(s).
                * (cycle, period, frame) — return frame(s) within period(s).

        Returns:
            ccycle|cperiod|cframe|applylist: the requested object or list of
                objects matching the given index.

        Raises:
            IndexError: if the integer index exceeds the number of cycles, or
                if the key type is not supported.

        Example:
            >>> cyc = run[0]            # single cycle
            >>> cycs = run[0:3]         # first three cycles as applylist
            >>> per = run[0, 1]         # period 1 of cycle 0
            >>> fr = run[0, 1, 2]       # frame 2 of period 1 of cycle 0
        """
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

            return ucndata.applylist(cyc)

        # slice on periods and frames
        if isinstance(key, tuple):

            # slice or single
            cycles = self[key[0]]

            # get frames 
            if len(key) > 2:
                if isinstance(cycles, (np.ndarray, ucndata.applylist, list)):
                    outlist = []
                    for cyc in cycles:

                        periods = cyc[key[1]]
                        if isinstance(periods, (np.ndarray, ucndata.applylist, list)):
                            innerlist = ucndata.applylist([per[key[2]] for per in periods])
                        else:
                            innerlist = periods[key[2]]
                        outlist.append(innerlist)
                        
                    return ucndata.applylist(outlist)            
                else:
                    return cycles[(key[1], key[2])]
                            
            # cycles and periods only
            else:
                if isinstance(cycles, (np.ndarray, ucndata.applylist, list)):
                    return ucndata.applylist([c[key[1]] for c in cycles])
                else:
                    return cycles[key[1]]

        raise IndexError(f'Run {self.run_number} given an unknown index type ({type(key)})')

    def _get_nhits_frame(self, detector, frame_time=None):

        # get hits tree
        tree = self.tfile[ucndata.DET_NAMES[detector]['hits']]

        # get hits for run
        if frame_time is None:
            return tree.size

        else:

            # make hits histogram
            if self._nhits_frame is None:

                # use frame start times as edges
                edges = self.cycle_param.frame_start_times
                runstop = self.cycle_param.period_end_times.max().max()
                edges = np.concat((edges, [runstop]))
                self._nhits_frame = tree.hist1d('tUnixTimePrecise', edges=edges).to_dataframe()
                self._nhits_frame['tUnixTimePrecise'] = edges[:-1]
                self._nhits_frame.set_index('tUnixTimePrecise', inplace=True)
                self._nhits_frame = self._nhits_frame.loc[:, 'Count']

            # get hits for frame
            try:
                return self._nhits_frame[frame_time]
            except KeyError:
                raise KeyError(f'Frame with timestamp {frame_time} does not exist in crun._nhits_frame')

    def get_cycle(self, cycle=None):
        """Return a ccycle for the requested cycle, or all cycles.

        Trees are time-restricted to the requested cycle via tsubfile; this
        process converts all ROOT objects to dataframes on first access.
        Results are cached in self._cycledict so repeated calls are cheap.

        Args:
            cycle (int|None): cycle index (0-based). Pass None or a negative
                integer to get all cycles. Defaults to None.

        Returns:
            ccycle|applylist: a single ccycle when cycle >= 0, or an applylist
                of ccycle objects for all cycles when cycle is None or negative.

        Example:
            >>> run.get_cycle(0)
            run 1846 (cycle 0):
                comment            cycle_start        month              shifters           supercycle
                cycle              cycle_stop         run_number         start_time         tfile
                cycle_param        experiment_number  run_title          stop_time          year

            >>> len(run.get_cycle())
            17
        """

        if cycle is None or cycle < 0:
            ncycles = len(self.cycle_param.cycle_times.index)
            return ucndata.applylist(map(self.get_cycle, range(ncycles)))
        elif cycle in self._cycledict.keys():
            return self._cycledict[cycle]
        else:
            self._cycledict[cycle] = ccycle(self, cycle)
            return self._cycledict[cycle]

    def get_tof(self, bin_ms=1):
        """Compute a time-of-flight histogram over all good cycles.

        Each neutron hit time is expressed relative to the most recent chopper
        opening (channel 15 pulse), producing a ToF value. Bad cycles excluded
        by cycle_param.filter are removed before histogramming.

        Args:
            bin_ms (float): histogram bin width in milliseconds. Defaults to 1.

        Returns:
            tuple: (bin_edges, counts) where bin_edges is a np.ndarray of
                length N+1 and counts is a np.ndarray of length N.

        Example:
            >>> edges, hist = run.get_tof(bin_ms=1)
            >>> import matplotlib.pyplot as plt
            >>> plt.stairs(hist, edges)
        """

        # get only Li6 detector timing entries
        tree = self.tfile.UCNHits_Li6.reset()

        # get hits
        times, chans, isUCN = tree[['tUnixTimePrecise','tChannel', 'tIsUCN']].values
        tof = times.copy()

        # get chopper rate
        idx = np.where(chans==15)[0]
        chop_rate = np.mean(np.diff(times[idx]))

        # get tof
        for i0, i1 in zip(idx[:-1], idx[1:]):
            tof[i0:i1] -= tof[i0]

        # get only ucn hits
        if self._ucn_only:
            tof = tof[isUCN.astype(bool)]
            times = times[isUCN.astype(bool)]

        # get only Li6 detector hits
        else:
            times = times[chans < 10]
            tof = tof[chans < 10]

        # remove bad cycles
        if self.cycle_param.filter is not None:
            idx_keep = np.full(len(tof), False)
            for cycle in self:
                if cycle.cycle_param.filter:
                    idx_keep += (times >= cycle.cycle_start) & (times < cycle.cycle_stop) 
            tof = tof[idx_keep]
            times = times[idx_keep]

        # make histogram edges
        bin_s = bin_ms/1000
        edges = np.arange(0, (chop_rate//bin_s + 1) *  bin_s, bin_s)

        # get histogram
        hist, bins = np.histogram(tof[(tof > 0) & (tof < chop_rate)], bins=edges)

        return (bins, hist)

    def inspect(self, detector='Li6', bin_ms=100, xmode='duration', slow=None):
        """Draw counts and BL1A current with shaded chopper frames to assess data quality.

        Calls the parent ucnrun.inspect and then overlays alternating grey
        shading for each chopper frame so the frame structure is visible
        alongside the rate and beam-current traces.

        Args:
            detector (str): detector to histogram. One of 'Li6' or 'He3'.
                Defaults to 'Li6'.
            bin_ms (int): histogram bin width in milliseconds. Defaults to 100.
            xmode (str): x-axis units. One of 'datetime', 'duration', or
                'epoch'. Defaults to 'duration'.
            slow (list|str|None): slow-control channel name(s) to plot on an
                additional axis. Defaults to None.

        Returns:
            list: matplotlib Axes objects created by the parent inspect call.

        Example:
            >>> run.inspect(detector='Li6', bin_ms=50, xmode='datetime')
        """
        
        # run parent inspect
        axes = super().inspect(detector=detector, 
                               bin_ms=bin_ms, 
                               xmode=xmode, 
                               slow=slow)
        
        # adjust frame units 
        times = self.cycle_param.frame_start_times.copy()
        if xmode in 'datetime':
            times = pd.to_datetime(times, unit='s')
        elif xmode in 'duration':
            times -= self.cycle_param.cycle_times.loc[0, 'start']

        # draw
        alpha_list = [0.25, 0.05]
        for ax in axes:

            ylim = ax.get_ylim()

            # fill alternating colours
            for i in range(len(times)-1):
                start = times[i]
                stop = times[i+1]
                alpha = alpha_list[i%2]

                ax.fill_between((start, stop), *ylim, color='grey', 
                                alpha=alpha, zorder=0)
            
            # reset y limits
            ax.set_ylim(*ylim)

    def offset_frames(self, dt):
        """Shift all chopper frame start times by a constant offset.

        Updates frame_start_times at the run, cycle, and period levels, and
        resets the cached nhits-per-frame histogram so it is recomputed on the
        next access.

        Args:
            dt (float): time shift in seconds. Positive values shift frames
                forward in time.

        Raises:
            ValueError: if the shift would produce frame start times below zero
                or beyond the end of the run.

        Example:
            >>> run.offset_frames(0.001)   # shift all frames forward by 1 ms
        """

        # offset
        times = self.cycle_param.frame_start_times + dt

        # limits checking
        if any(times < 0):
            raise ValueError('This operation would create frames with negative start times')
        if any(self.cycle_param.cycle_times.stop.max() - times < 0):
            raise ValueError('This operation would create frames starting after the end of the run')

        # set at run level
        self.cycle_param.frame_start_times = times

        # update saved cycles
        for cycle in self._cycledict.values():
            idx = (times >= cycle.cycle_start) & (times < cycle.cycle_stop)
            cycle.cycle_param.frame_start_times = times[idx]
            cycle.cycle_param.nframes = len(cycle.cycle_param.frame_start_times)

            # update saved periods
            for period in cycle._perioddict.values():
                idx = (times >= period.period_start) & (times < period.period_stop)
                period.cycle_param.frame_start_times = times[idx]
                period.cycle_param.nframes = len(period.cycle_param.frame_start_times)
                period._framedict = {}

        # reset histogram for number of hits
        self._nhits_frame = None

class ccycle(ucndata.ucncycle):
    def __init__(self, urun, cycle):
        """Create a time-restricted view of a single cycle with chopper frames.

        Calls the ucncycle constructor and then trims frame_start_times to only
        those frames whose start time falls within [cycle_start, cycle_stop).

        Args:
            urun (crun): parent crun object containing the full run data.
            cycle (int): 0-based cycle index.
        """
        super().__init__(urun, cycle)

        # trim frame times
        times =  self.cycle_param.frame_start_times
        idx = (times >= self.cycle_start) & (times < self.cycle_stop)
        self.cycle_param.frame_start_times = times[idx]
        self.cycle_param.nframes = len(self.cycle_param.frame_start_times)

    def __getitem__(self, key):
        """Return period(s) or frame(s) via index or slice notation.

        Supports integer indexing, slices, and two-element tuples of the form
        (period, frame). Negative integers are resolved relative to the total
        period count. When cycle_param.filter is set, filtered-out periods are
        excluded from slice results.

        Args:
            key (int|slice|tuple): index into this cycle.
                * int — return a single cperiod.
                * slice — return an applylist of cperiod objects.
                * (period, frame) — return frame(s) within period(s).

        Returns:
            cperiod|cframe|applylist: the requested object or list of objects.

        Raises:
            IndexError: if the integer index exceeds the number of periods, or
                if the key type is not supported.

        Example:
            >>> per = cycle[0]          # first period
            >>> pers = cycle[0:2]       # first two periods as applylist
            >>> fr = cycle[0, 1]        # frame 1 of period 0
        """
        # get period or frame based on slicing indexes

        # get a single key
        if isinstance(key, (np.integer, int)):

            if key < 0:
                key = self.cycle_param.nperiods + key

            if key > self.cycle_param.nperiods:
                raise IndexError(f'Run {self.run_number}: Index larger than number of periods ({self.cycle_param.nperiods})')

            return self.get_period(key)

        # slice on frames
        elif isinstance(key, tuple):
            periods = self[key[0]]
            if isinstance(periods, (np.ndarray, ucndata.applylist, list)):
                return ucndata.applylist([c[key[1]] for c in periods])
            else:
                return periods[key[1]]

        # slice on periods
        elif isinstance(key, slice):
            periods = self.get_period()[:self.cycle_param.nperiods]

            # no filter
            if self.cycle_param.filter is None or all(self.cycle_param.filter):
                cyc = periods[key]

            # yes filter
            else:

                # fetch the filter and slice in the same way as the return value
                cfilter = self.cycle_param.filter[key]

                # fetch cycles and slice, then apply filter
                cyc = np.array(periods[key])
                cyc = cyc[cfilter]

            return ucndata.applylist(cyc)

        raise IndexError(f'Run {self.run_number} given an unknown index type ({type(key)})')

    def get_period(self, period=None):
        """Return a cperiod for the requested period, or all periods.

        Trees are time-restricted to the requested period; this process
        converts all ROOT objects to dataframes on first access. Results are
        cached in self._perioddict so repeated calls are cheap. The last
        period is dropped if it contains no data.

        Notes:
            * This process converts all objects to dataframes.
            * Must be called on a single cycle object, not on applylist.
            * Equivalent to indexing style: ``cycle[period]``.

        Args:
            period (int|None): period index (0-based). Pass None or a negative
                integer to get all periods. Defaults to None.

        Returns:
            cperiod|applylist: a single cperiod when period >= 0, or an
                applylist of cperiod objects for all periods when period is
                None or negative.

        Example:
            >>> cycle = run[0]
            >>> cycle.get_period(0)
            run 1846 (cycle 0, period 0):
                comment            cycle_stop         period_start       shifters           tfile
                cycle              experiment_number  period_stop        start_time         year
                cycle_param        month              run_number         stop_time
                cycle_start        period             run_title          supercycle
        """

        # get all periods
        if period is None or period < 0:
            nperiods = self.cycle_param.nperiods
            periods = ucndata.applylist(map(self.get_period, range(nperiods)))
            if len(periods[-1]) == 0:
                return periods[:-1]
            return periods
        elif period in self._perioddict.keys():
            return self._perioddict[period]
        else:
            self._perioddict[period] = cperiod(self, period)
            return self._perioddict[period]

class cperiod(ucndata.ucnperiod):
    def __init__(self, ucycle, period):
        """Create a time-restricted view of a single period with chopper frames.

        Calls the ucnperiod constructor and then trims frame_start_times to
        only those frames whose start time falls within [period_start,
        period_stop). Initialises an empty _framedict cache.

        Args:
            ucycle (ccycle): parent ccycle object containing the cycle data.
            period (int): 0-based period index within the cycle.
        """
        super().__init__(ucycle, period)

        # trim frame times
        times =  self.cycle_param.frame_start_times
        idx = (times >= self.period_start) & (times < self.period_stop)
        self.cycle_param.frame_start_times = times[idx]
        self.cycle_param.nframes = len(self.cycle_param.frame_start_times)

        # frame dict
        self._framedict = {}

    def __len__(self):
        """Return the number of chopper frames in this period.

        Returns:
            int: number of frames (cycle_param.nframes).
        """
        return self.cycle_param.nframes

    def __next__(self):
        # permit iteration over object like it was a list

        # iterate
        if self._iter_current < self.cycle_param.nframes:
            fr = self[self._iter_current]
            self._iter_current += 1
            return fr

        # end of iteration
        else:
            raise StopIteration()

    def __getitem__(self, key):
        """Return frame(s) via integer index or slice.

        Negative integers are resolved relative to the total frame count.

        Args:
            key (int|slice): index into this period's frames.
                * int — return a single cframe.
                * slice — return an applylist of cframe objects.

        Returns:
            cframe|applylist: the requested frame or list of frames.

        Raises:
            IndexError: if the integer index exceeds the number of frames, or
                if a non-integer/non-slice key is given.

        Example:
            >>> fr = period[0]       # first frame
            >>> frs = period[0:3]    # first three frames as applylist
        """
        # get cycle or period based on slicing indexes

        # get a single key
        if isinstance(key, (np.integer, int)):
            if key < 0:
                key = self.cycle_param.nframes + key

            if key > self.cycle_param.nframes:
                raise IndexError(f'Run {self.run_number}, cycle {self.cycle}, period {self.period}: Index larger than number of frames ({self.cycle_param.nframes})')

            return self.get_frame(key)

        # slice on cycles
        if isinstance(key, slice):
            fr = self.get_frame()[:self.cycle_param.nframes]
            return ucndata.applylist(fr[key])

        raise IndexError('Periods indexable only as a 1-dimensional object')

    def get_frame(self, frame=None):
        """Return a cframe for the requested frame, or all frames.

        Trees are time-restricted to the requested chopper frame. Results are
        cached in self._framedict so repeated calls are cheap.

        Args:
            frame (int|None): frame index (0-based). Pass None or a negative
                integer to get all frames. Defaults to None.

        Returns:
            cframe|applylist: a single cframe when frame >= 0, or an applylist
                of cframe objects for all frames when frame is None or negative.

        Example:
            >>> period.get_frame(0)          # first frame
            >>> len(period.get_frame())      # total number of frames
        """
        # get all frames
        if frame is None or frame < 0:
            nframes = self.cycle_param.nframes
            return ucndata.applylist(map(self.get_frame, range(nframes)))
        
        elif frame in self._framedict.keys():
            return self._framedict[frame]
        else:
            self._framedict[frame] = cframe(self, frame)
            return self._framedict[frame]

class cframe(ucndata.ucnbase):
    def __init__(self, uperiod, frame):
        """Create a time-restricted view of a single chopper frame.

        Copies all attributes from the parent cperiod, replacing tfile with a
        tsubfile restricted to [frame_start, frame_stop) and rebuilding the
        epics interface for the new time window. If the period contains no
        frames, all time attributes are set to None.

        Args:
            uperiod (cperiod): parent cperiod object containing the period data.
            frame (int): 0-based frame index within the period.
        """
        # frame doesn't exist
        if uperiod.cycle_param.nframes == 0:
            self.frame = None
            self.frame_start = None
            self.frame_stop = None
            self.frame_dur = None
            return 

        # get start and stop time
        start = uperiod.cycle_param.frame_start_times[frame]
        if frame < uperiod.cycle_param.nframes-1:      
            stop = uperiod.cycle_param.frame_start_times[frame+1]
        else:
            stop = uperiod.period_stop

        # copy data
        for key, value in uperiod.__dict__.items():
            if key == 'tfile':
                setattr(self, key, ucndata.tsubfile.tsubfile(value, start, stop))
            elif key == 'epics':
                setattr(self, key, ucndata.ttreeslow(value, self))
            elif hasattr(value, 'copy'):
                setattr(self, key, value.copy())
            else:
                setattr(self, key, value)

        # trim cycle parameters
        self.frame = frame
        self.frame_start = start
        self.frame_stop = stop
        self.frame_dur = stop-start

    def get_nhits(self, detector):
        """Get the number of UCN hits recorded in this chopper frame.

        Delegates to the parent crun._get_nhits_frame, which bins hits by
        frame start time on first call and caches the result.

        Args:
            detector (str): detector name. One of 'Li6' or 'He3'.

        Returns:
            int: number of UCN hits in this frame for the given detector.

        Example:
            >>> frame.get_nhits('Li6')
            42
        """
        return self._run._get_nhits_frame(detector, self.frame_start)
    
    def __repr__(self):
        """Return a human-readable summary of the frame's public attributes.

        Attributes are sorted case-insensitively and laid out in columns sized
        to fit the current terminal width.

        Returns:
            str: multi-line string showing run number, cycle, period, frame
                index, and all public attribute names.
        """
        klist = [d for d in self.__dict__.keys() if d[0] != '_']
        if klist:

            # sort without caps
            klist.sort(key=lambda x: x.lower())
            
            # get number of columns based on terminal size
            maxsize = max([len(k) for k in klist]) + 2
            terminal_width = os.get_terminal_size().columns
            ncolumns = int(np.floor(terminal_width / maxsize))
            ncolumns = min((ncolumns, len(klist)))

            # split into chunks
            needed_len = int(np.ceil(len(klist) / ncolumns)*ncolumns) - len(klist)
            klist = np.concatenate((klist, np.full(needed_len, '')))
            klist = np.array_split(klist, ncolumns)

            # print
            cyc_str = f' (cycle {self.cycle}, period {self.period}, frame {self.frame})'
            s = f'run {self.run_number}{cyc_str}:\n'
            for key in zip(*klist):
                s += '  '
                s += ''.join(['{0: <{1}}'.format(k, maxsize) for k in key])
                s += '\n'
            return s
        else:
            return self.__class__.__name__ + "()"
