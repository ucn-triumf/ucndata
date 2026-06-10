# Base class for ucnrun, ucncycle, and ucnperiod
# Derek Fujimoto
# Oct 2024

import ucndata
from rootloader import ttree
from .exceptions import *
from .datetime import to_datetime
from .applylist import applylist
import ucndata.constants as const
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from tqdm import tqdm
from collections.abc import Iterable
import matplotlib.patches as mpatches

class ucnbase(object):
    """Base class shared by `ucnrun`, `ucncycle`, and `ucnperiod`.

    Provides shared analysis methods and quick-access properties for
    Ultra-Cold Neutron (UCN) experimental data loaded from ROOT files.
    Not instantiated directly — use `ucnrun`, `ucncycle`, or `ucnperiod` instead.

    Attributes:
        comment (str): comment input by users at the time of the run
        cycle (int|None): cycle index within the run; `None` at the run level
        cycle_param (attrdict): cycle timing and period structure parameters
        epics (ttreeslow): unified EPICS slow-control interface
        experiment_number (str): experiment number recorded by users
        month (int): month of the run start date
        run_number (int): run number as recorded in the ROOT file header
        run_title (str): run title recorded by users
        shifter (str): experimenter names on shift during the run
        start_time (str): human-readable start time of the run
        stop_time (str): human-readable stop time of the run
        supercycle (int|None): supercycle index; `None` at the run level
        tfile (tfile): rootloader tfile object holding all ROOT tree data
        year (int): year of the run start date

    Notes:
        - Attributes of `tfile` can be accessed directly from the top-level
          `ucnrun`, `ucncycle`, or `ucnperiod` object via attribute pass-through.
        - `ucncycle` objects additionally expose `cycle_start`, `cycle_stop`, and
          `cycle_dur` (epoch seconds).
        - `ucnperiod` objects additionally expose `period_start`, `period_stop`,
          `period_dur` (epoch seconds), and `period` (int index).
        - Objects support indexing as `[cycle]` or `[cycle, period]` for easy
          access to sub-timeframe views.
    """

    def __iter__(self):
        """Initialize iteration over cycles (`ucnrun`) or periods (`ucncycle`).

        Returns:
            ucnbase: self, with internal iteration counter reset to zero.
        """
        # setup iteration
        self._iter_current = 0
        return self

    def _get_beam_duration(self, on=True):
        # Get beam on/off durations

        # get needed info
        cycle_times = self.cycle_param.cycle_times

        try:
            beam = self.tfile.BeamlineEpics
        except AttributeError:
            raise MissingDataError("No saved ttree named BeamlineEpics")

        # setup storage
        beam_dur = []
        epics_val = 'B1V_KSM_RDBEAMON_VAL1' if on else 'B1V_KSM_RDBEAMOFF_VAL1'

        # get as dataframe
        if isinstance(beam, ttree):
            beam = beam[epics_val].to_dataframe()

        # get durations closest to cycle start time
        for start in cycle_times.start:

            start_times = abs(beam.index.values - start)
            durations = beam.values*const.beam_bucket_duration_s
            idx = np.argmin(start_times)
            beam_dur.append(durations[idx])

        out = pd.Series(beam_dur, index=cycle_times.index)
        out.index.name = cycle_times.index.name

        if len(out) == 1:
            return float(out.values[0])

        # select single cycle
        if hasattr(self, 'cycle'):
            out = out[self.cycle]

        return out

    def apply(self, fn_handle):
        """Apply function to each cycle

        Args:
            fn_handle (function handle): function to be applied to each cycle

        Returns:
            applylist: output of the function

        Example:
            ```python
            >>> run.apply(lambda x: x.cycle)
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
            ```
        """
        return applylist([fn_handle(c) for c in self])

    def get_hits_array(self, detector):
        """Get times of ucn hits as a numpy array

        Args:
            detector (str): one of the keys to `ucndata.DET_NAMES`

        Returns:
            np.array: array of timestamps corresponding to an UCN hit. Note that this returns all events in the case where `ucn_only=False`

        Example:
            ```python
            >>> run.get_hits_array('Li6')
            array([1.75016403e+09, 1.75016405e+09, 1.75016405e+09, ...,
                   1.75016479e+09, 1.75016479e+09, 1.75016479e+09])
            ```
        """

        # check input
        if detector not in ucndata.DET_NAMES.keys():
            raise KeyError(f'Detector input "{detector}" not one of {tuple(ucndata.DET_NAMES.keys())}')

        # get the tree
        tree = self.tfile[ucndata.DET_NAMES[detector]['hits']]

        return tree.tUnixTimePrecise.to_dataframe().index.values

    def get_hits_histogram(self, detector, bin_ms=10, as_datetime=False):
        """Get histogram of UCNHits ttree times

        Args:
            detector (str): `Li6`|`He3`
            bin_ms (int): histogram bin size in milliseconds
            as_datetime (bool): if true, convert `bin_centers` to datetime objects

        Returns:
            rootloader.th1: histogram object

        Example:
            ```python
            >>> run.get_hits_histogram('He3')
            TH1D: "HisttUnixTimePrecise", 557053 entries, sum = 557053.0

            # quick plotting with timestamps
            >>> run.get_hits_histogram('He3', as_datetime=True).plot()

            # get result as a dataframe
            >>> run.get_hits_histogram('He3').to_dataframe()
                    tUnixTimePrecise  Count  Count error
            0         1.750164e+09    0.0     0.000000
            1         1.750164e+09    1.0     1.000000
            2         1.750164e+09    0.0     0.000000
            3         1.750164e+09    0.0     0.000000
            4         1.750164e+09    0.0     0.000000
            ...                ...    ...          ...
            7528      1.750165e+09    0.0     0.000000
            7529      1.750165e+09    0.0     0.000000
            7530      1.750165e+09  415.0    20.371549
            7531      1.750165e+09  507.0    22.516660
            7532      1.750165e+09  509.0    22.561028

            [7533 rows x 3 columns]
            ```
        """

        # check input
        if detector not in ucndata.DET_NAMES.keys():
            raise KeyError(f'Detector input "{detector}" not one of {tuple(ucndata.DET_NAMES.keys())}')

        # get data
        tree = self._run.tfile[ucndata.DET_NAMES[detector]['hits']]

        # histogram
        hist = tree.hist1d('tUnixTimePrecise', step=bin_ms/1000)

        # make a copy
        hist = hist.copy()

        # trim axes
        if hasattr(self, 'frame_start'):
            start = self.frame_start
            stop = self.frame_stop
        elif hasattr(self, 'period_start'):
            start = self.period_start
            stop = self.period_stop
        elif hasattr(self, 'cycle_start'):
            start = self.cycle_start
            stop = self.cycle_stop
        else:
            start = 0
            stop = 0

        if start > 0:
            idx = (hist.x >= start) & (hist.x < stop)
            hist.x = hist.x[idx]
            hist.y = hist.y[idx]
            hist.dy = hist.dy[idx]
            hist.sum = np.sum(hist.y)
            hist.entries = int(hist.sum)
            hist.nbins = len(hist.x)


        # to datetime
        if as_datetime:
            hist.x = to_datetime(hist.x)

        return hist

    def inspect(self, detector='Li6', bin_ms=100, xmode='duration', slow=None):
        """Draw counts and BL1A current with indicated periods to determine data quality.

        Produces a multi-panel figure with the BL1A beam current on the top panel,
        UCN hit counts on the second panel, and optional EPICS slow-control channels
        in additional panels below. Cycle start times are marked with solid black
        vertical lines; period boundaries are marked with dashed coloured lines.

        Args:
            detector (str): detector from which to get the counts. `Li6`|`He3`
            bin_ms (int): histogram bin size in milliseconds
            xmode (str): x-axis mode — `datetime`|`duration`|`epoch`
            slow (list|str): name(s) of EPICS column(s) to add as extra axes below
                the count panel. Accepts a single column name string or a list of
                column name strings. Must be present in `self.epics.columns`.

        Returns:
            np.ndarray: array of matplotlib Axes objects for the figure panels.

        Raises:
            RuntimeError: if `xmode` is not one of `datetime`|`duration`|`epoch`.
            KeyError: if a requested slow-control column is not found in `self.epics`.
            RuntimeError: if `slow` is not a string or iterable.

        Example:
            ```python
            # inspect full run
            >>> axes = run.inspect('Li6', bin_ms=100, xmode='duration')

            # inspect single cycle with extra slow control panel
            >>> axes = run[3].inspect('He3', slow='UCN2EpicsTemperature_UCN_He3_TEMP')
            ```
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

        # period
        if hasattr(self, 'period'):
            type = 'Period'
            run_start = self.period_start
            raise NotImplementedError('Inspect for periods not yet implemented')
        
        # cycle
        elif hasattr(self, 'cycle'):
            type = 'Cycle'
            run_start = self.cycle_start
            self._inspect_draw(current, hist, run_start, axes, xmode, slow)
            
            # draw vertical markers
            if xmode in 'duration':
                xmode = 'duration_cycle'
            for i, ax in enumerate(axes):
                non_zero_periods = self.draw_cycle_times(ax=ax, xmode=xmode)

            # title is run, cycle number
            axes[0].set_title(f'run {self.run_number}, cycle {self.cycle}',
                              fontsize='x-small')

        # full run
        else:
            type = 'Run'
            run_start = self.cycle_param.cycle_times.loc[0, 'start']

            # draw each cycle
            for cyc in self.get_cycle():
                cyc._inspect_draw(current, hist, run_start, axes, xmode, slow)

            # draw vertical markers
            for i, ax in enumerate(axes):
                non_zero_periods = self.get_cycle().draw_cycle_times(ax=ax, xmode=xmode)
            non_zero_periods = np.concat(non_zero_periods)

            # title is run number
            axes[0].set_title(f'run {self.run_number}',
                              fontsize='x-small')

        # plot elements
        axes[0].set_ylabel('BL1A Current (uA)')
        axes[1].set_ylabel(f'UCN Counts/{bin_ms/1000:g}s')

        if slow is not None:
            slow_keys = tuple(slow.keys())
            for i, ax in enumerate(axes[2:]):
                ax.set_ylabel(slow_keys[i].split('_')[-2])

        if xmode in 'datetime':
            axes[-1].set_xlabel('')
        elif xmode in 'duration' or xmode in 'duration_cycle' or xmode in 'duration_run':
            axes[-1].set_xlabel(f'Time Since {type} Start (s)')
        else:
            axes[-1].set_xlabel('Epoch Time')
        axes[1].set_yscale('log')

        # legend
        handles = [mpatches.Patch(color=f'C{period}', label=f'Period {period}') \
                   for period in sorted(np.unique(non_zero_periods))]
        axes[0].legend(handles=handles, loc='upper right') 

        return axes

    def plot_psd(self, detector='Li6', cut=None, cmap='RdBu'):
        """Calculate PSD as `(QLong-QShort)/QLong` and draw as a 3x3 grid of 2D histograms.

        One subplot per digitizer channel (channels 0–8). The x-axis is the long-gate
        charge `QLong`, and the y-axis is the pulse-shape discriminant
        `(QLong - QShort) / QLong`. All subplots share the same colour scale.

        Args:
            detector (str): `Li6`|`He3`, selects which detector hit tree to read
            cut (tuple|None): `(QLong, PSD)` coordinates of the lower-left corner of a
                rectangular selection box. If not `None`, a white rectangle is drawn on
                every subplot from this corner to `(max_QLong, 1)`.
            cmap (str): matplotlib colormap name. See
                https://matplotlib.org/stable/users/explain/colors/colormaps.html
                Append `"_r"` to reverse the colormap direction.

        Example:
            ```python
            # basic PSD plot for Li6 detector
            >>> run.plot_psd('Li6')

            # draw with a selection cut at QLong=200, PSD=0.2
            >>> run.plot_psd('Li6', cut=(200, 0.2))
            ```
        """

        # get the data from the tree
        tree = self.tfile[ucndata.DET_NAMES[detector]['hits']].reset()
        tree.set_filter("tUnixTimePrecise > 15e8", inplace=True)

        # calculate new psd
        tree.set_filter("tChargeL > 0", inplace=True)
        tree.set_filter("tChargeL < 5e3", inplace=True)

        # Li detector figures
        fig, axes = plt.subplots(nrows=3, ncols=3, sharex=True, sharey=True,
                                layout='constrained',
                                figsize=(10,8))
        axes = np.concat(axes)

        hist_edges = []
        max_chargeL = tree.tChargeL.max()

        # histogram
        for i in tqdm(range(9), desc='Generating Histograms', leave=False):

            # hist single channel
            treech = tree.set_filter(f'tChannel=={i}')
            hist = treech.hist2d('tChargeL', 'tPSD', xstep=5, ystep=0.01)

            # reconstruct histogram edges
            xedge = hist.x
            yedge = hist.y

            xedge = np.append(xedge, xedge[-1] + xedge[1]-xedge[0])
            yedge = np.append(yedge, yedge[-1] + yedge[1]-yedge[0])

            xedge -= (xedge[1]-xedge[0])/2
            yedge -= (yedge[1]-yedge[0])/2

            # save
            hist_edges.append((hist.z, xedge, yedge))

        # get max
        max_bin_count = np.max([np.max(h[0]) for h in hist_edges])


        # draw
        for i in range(9):
            ax = axes[i]
            hist, xbins, ybins = hist_edges[i]
            c = ax.pcolormesh(xbins, ybins, hist,
                              cmap=cmap,
                              vmin=0, vmax=max_bin_count/10)
            if i in (2, 5, 8):
                plt.gcf().colorbar(c, ax=ax)
            ax.set_title(f'CH {i}', fontsize='x-small')

            if cut is not None:
                dx = max_chargeL - cut[0]
                dy = 1 - cut[1]
                rec = Rectangle(cut, dx, dy, color='white', fc='none', lw=1)
                ax.add_patch(rec)

        fig.suptitle(f'Run {self.run_number}')
        fig.supxlabel(r'$Q_{\mathrm{Long}}$')
        fig.supylabel(r'$(Q_{\mathrm{Long}}-Q_{\mathrm{Short}})/Q_{\mathrm{Long}}$')

    def trigger_edge(self, detector, thresh, bin_ms=10, rising=True):
        """Detect period start time based on a rising or falling edge
        Args:
            detector (str): `Li6`|`He3`
            thresh (float): calculate cycle start time shift based on edge detection passing through this level
            bin_ms (int): histogram bin size in milliseconds
            rising (bool): if true do rising edge, else do falling edge

        Returns:
            np.array: the times at which the rising or falling edge passes through the threshold

        Example:
            ```python
            >>> dt = [cyc[2].trigger_edge('Li6', 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
            ```
        """
        searched = 1 if rising else -1

        # get histogram
        hist = self.get_hits_histogram(detector, bin_ms=bin_ms)
        t = hist.x
        n = hist.y

        # check that the histo has data
        if len(t) == 0:
            raise RuntimeError('Histogram has no data')

        # edge detection using convolution
        # https://stackoverflow.com/questions/50365310/python-rising-falling-edge-oscilloscope-like-trigger
        sign = n >= thresh
        pos = np.where(np.convolve(sign, [1, -1]) == searched)[0]

        # check that positions are found
        if len(pos) == 0:
            raise RuntimeError(f'No position from trigger edge found (thresh = {thresh}, hits min = {np.min(n)}, hits max = {np.max(n)}, bin_ms = {bin_ms})')

        # trim positions which are too long
        pos[pos == len(sign)] -= 1

        return t[pos]

    # quick access properties
    @property
    def beam1a_current_uA(self):
        """Get beamline 1A current in uA (micro amps).

        Reads the `B1_FOIL_ADJCUR` column from `BeamlineEpics`, which records
        the adjusted extraction foil current on BL1A.

        Returns:
            pd.Series: indexed by epoch timestamps, current values in uA.

        Example:
            ```python
            >>> run.beam1a_current_uA
            timestamp
            1750164000    98.3
            1750164005    98.2
            1750164010    98.4
            dtype: float64
            ```
        """
        if type(self.tfile.BeamlineEpics) is pd.DataFrame:
            return self.tfile.BeamlineEpics.B1_FOIL_ADJCUR.copy()
        else:
            return self.tfile.BeamlineEpics.B1_FOIL_ADJCUR.to_dataframe()

    @property
    def beam1u_current_uA(self):
        """Get beam current in uA (micro amps)

        Returns:
            pd.Series: indexed by timestamps, current in uA

        Notes:
            Beam current defined as `B1V_KSM_PREDCUR` * `B1V_KSM_BONPRD`

        Example:
            ```python
            >>> run.beam1u_current_uA
            timestamp
            1572460997    0.0
            1572461002    0.0
            1572461007    0.0
            1572461012    0.0
            1572461017    0.0
                        ...
            1572466463    0.0
            1572466468    0.0
            1572466473    0.0
            1572466478    0.0
            1572466479    0.0
            Length: 1093, dtype: float64
            ```
        """

        # PREDCUR is the predicted current in beamline 1U.
        # PREDCUR is calculated by using the beamline 1V extraction foil current
        # (the current as it leaves the cyclotron) and multiplid by the fraction
        # of beam that is going to the 1U beamline (as opposed to 1A beamline).
        # So if the extraction foil current is 100uA and we are kicking 1 bucket
        # out of 10 buckets to 1U, then PREDCUR will be 10uA

        # BONPRD is a bool, which indicates if there is beam down 1U

        df = self.tfile.BeamlineEpics[['B1V_KSM_PREDCUR', 'B1V_KSM_BONPRD']]
        df = df.to_dataframe()

        # current in the 1U beamline
        return df.B1V_KSM_PREDCUR * df.B1V_KSM_BONPRD

    @property
    def beam_on_s(self):
        """Get the beam-on duration in seconds for each cycle as given by `B1V_KSM_RDBEAMON_VAL1`

        Returns:
            pd.Series: indexed by cycle number, beam-on duration in s

        Example:

            ```python
            >>> run.beam_on_s
            cycle
            0     59.999284
            1     59.999284
            2     59.999284
            3     59.999284
            4     59.999284
            5     59.999284
            6     59.999284
            7     59.999284
            8     59.999284
            9     59.999284
            10    59.999284
            11    59.999284
            12    59.999284
            13    59.999284
            14    59.999284
            15    59.999284
            16    59.999284
            dtype: float64
            ```
        """

        return self._get_beam_duration(on=True)

    @property
    def beam_off_s(self):
        """Get the beam-off duration in seconds for each cycle as given by `B1V_KSM_RDBEAMOFF_VAL1`

        Returns:
            pd.Series: indexed by cycle number, beam-off duration in s

        Example:

            ```python
            >>> run.beam_off_s
            cycle
            0     229.999918
            1     229.999918
            2     229.999918
            3     229.999918
            4     229.999918
            5     229.999918
            6     229.999918
            7     229.999918
            8     229.999918
            9     229.999918
            10    229.999918
            11    229.999918
            12    229.999918
            13    229.999918
            14    229.999918
            15    229.999918
            16    229.999918
            dtype: float64
            ```
        """
        return self._get_beam_duration(on=False)


