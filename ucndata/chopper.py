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
import matplotlib.pyplot as plt

class crun(ucndata.ucnrun):
    def __init__(self, run, ucn_only=True, chop_time_ch=15):
        super().__init__(run, ucn_only)

        tree = self.tfile['UCNHits_Li6'].reset()
        tree.set_filter(f'tChannel == {chop_time_ch}', inplace=True)
        times = tree.tUnixTimePrecise.to_dataframe().index.values

        self.cycle_param['nframes'] = len(times)
        self.cycle_param['frame_start_times'] = times

        self._nhits_frame = None

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
        tree = self.tfile[self.DET_NAMES[detector]['hits']]

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
            return ucndata.applylist(map(self.get_cycle, range(ncycles)))
        elif cycle in self._cycledict.keys():
            return self._cycledict[cycle]
        else:
            self._cycledict[cycle] = ccycle(self, cycle)
            return self._cycledict[cycle]

    def inspect(self, detector='Li6', bin_ms=100, xmode='duration', slow=None):
        """Draw counts and BL1A current with indicated periods to determine data quality

        Args:
            detector (str): detector from which to get the counts from. Li6|He3
            bin_ms (int): histogram bin size in ms
            xmode (str): datetime|duration|epoch
            slow (list|str): name of slow control tree to add in a separate axis, can be a list of names
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
        """Add an offset to the start times of all frames
            
        Args:
            dt (float): time shift, should not push frames outside the limits of the run    
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
        super().__init__(urun, cycle)

        # trim frame times
        times =  self.cycle_param.frame_start_times
        idx = (times >= self.cycle_start) & (times < self.cycle_stop)
        self.cycle_param.frame_start_times = times[idx]
        self.cycle_param.nframes = len(self.cycle_param.frame_start_times)

    def __getitem__(self, key):
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
        super().__init__(ucycle, period)

        # trim frame times
        times =  self.cycle_param.frame_start_times
        idx = (times >= self.period_start) & (times < self.period_stop)
        self.cycle_param.frame_start_times = times[idx]
        self.cycle_param.nframes = len(self.cycle_param.frame_start_times)

        # frame dict
        self._framedict = {}

    def __len__(self):
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
        """Get number of ucn hits

        Args:
            detector (str): Li6|He3
        """

        return self._run._get_nhits_frame(detector, self.frame_start)
    
    def __repr__(self):
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
