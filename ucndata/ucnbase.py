# Base class for ucnrun, ucncycle, and ucnperiod
# Derek Fujimoto
# Oct 2024

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

class ucnbase(object):
    """UCN run data. Cleans data and performs analysis

    Args:
        run (int|str): if int, generate filename with self.datadir
            elif str then run is the path to the file
        header_only (bool): if true, read only the header

    Attributes:
        comment (str): comment input by users
        cycle (int|none): cycle number, none if no cycle selected
        cycle_param (attrdict): cycle parameters
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
        Can access attributes of tfile directly from top-level object
        Need to redefine the values if you want non-default
        behaviour
        Object is indexed as [cycle, period] for easy access to sub time frames
    """

    # path to the directory which contains the root files
    datadir = "/data3/ucn/root_files"

    # timezone for datetime conversion
    timezone = 'America/Vancouver'

    # cycle times finding mode order
    cycle_times_mode = ['matched', 'li6', 'he3', 'sequencer', 'beamon']

    # filter what trees and branches to load in each file. If unspecified then load the whole tree
    # treename: (filter, columns). See [rootloader documentation](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md#ttree-1) for details
    tree_filter = {}

    # detector tree names
    DET_NAMES = {'He3':{'hits':         'UCNHits_He3',
                        'hits_orig':    'UCNHits_He3', # as saved in the root file
                        'charge':       'He3_Charge',
                        'rate':         'He3_Rate',
                        'transitions':  'RunTransitions_He3',
                        'hitsseq':      'hitsinsequence_he3',
                        'hitsseqcumul': 'hitsinsequencecumul_he3',
                        },
                 'Li6':{'hits':         'UCNHits_Li6',
                        'hits_orig':    'UCNHits_Li-6', # as saved in the root file
                        'charge':       'Li6_Charge',
                        'rate':         'Li6_Rate',
                        'transitions':  'RunTransitions_Li6',
                        'hitsseq':      'hitsinsequence_li6',
                        'hitsseqcumul': 'hitsinsequencecumul_li6',
                        },
                }

    # make these trees dataframes, ok since they're small - also resets the index
    DATAFRAME_TREES = ('CycleParamTree', 'RunTransitions_He3', 'RunTransitions_Li6')

    # needed slow control trees: for checking data quality
    SLOW_TREES = ('BeamlineEpics', 'SequencerTree', 'LNDDetectorTree')

    # EPICS trees to group into a single slow control tree
    EPICS_TREES = [ 'BeamlineEpics',        'UCN2EpPha5Last',   'UCN2EpicsPhase2B',
                    'UCN2EpPha5Oth',        'UCN2EpicsPhase3',  'UCN2EpPha5Pre',
                    'UCN2EpicsPressures',   'UCN2EpPha5Tmp',    'UCN2EpicsTemperature',
                    'UCN2Epics',            'UCN2Pur',          'UCN2EpicsOthers',
                  ]

    # data thresholds for checking data
    DATA_CHECK_THRESH = {'beam_min_current': 0.1, # uA
                         'pileup_cnt_per_ms': 10, # if larger than this, then pileup and delete
                         'pileup_within_first_s': 1, # time frame for pileup in each period
                        }

    def __iter__(self):
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
            detector (str): one of the keys to `self.DET_NAMES`

        Returns:
            np.array: array of timestamps corresponding to an UCN hit. Note that this returns all events in the case where ucn_only=False

        Example:
            ```python
            >>> run.get_hits_array('Li6')
            array([1.75016403e+09, 1.75016405e+09, 1.75016405e+09, ...,
                   1.75016479e+09, 1.75016479e+09, 1.75016479e+09])
            ```
        """

        # check input
        if detector not in self.DET_NAMES.keys():
            raise KeyError(f'Detector input "{detector}" not one of {tuple(self.DET_NAMES.keys())}')

        # get the tree
        tree = self.tfile[self.DET_NAMES[detector]['hits']]

        return tree.tUnixTimePrecise.to_dataframe().index.values

    def get_hits_histogram(self, detector, bin_ms=100, as_datetime=False):
        """Get histogram of UCNHits ttree times

        Args:
            detector (str): Li6|He3
            bin_ms (int): histogram bin size in milliseconds
            as_datetime (bool): if true, convert bin_centers to datetime objects

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
        if detector not in self.DET_NAMES.keys():
            raise KeyError(f'Detector input "{detector}" not one of {tuple(self.DET_NAMES.keys())}')

        # check precomputed data
        if self._run._hits_hist['detector'] == detector and \
           self._run._hits_hist['bin_ms'] == bin_ms:

            hist = self._run._hits_hist['hist']

        else:
            # get data
            tree = self._run.tfile[self.DET_NAMES[detector]['hits']]

            # histogram
            hist = tree.hist1d('tUnixTimePrecise', step=bin_ms/1000)
            self._run._hits_hist['detector'] = detector
            self._run._hits_hist['bin_ms'] = bin_ms
            self._run._hits_hist['hist'] = hist

        # make a copy
        hist = hist.copy()

        # trim axes
        if hasattr(self, 'period_start'):
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

    def plot_psd(self, detector='Li6', cut=None, cmap='RdBu'):
        """Calculate PSD as (QLong-QShort)/QLong, draw as a grid, 2D histograms

        Args:
            detector (str): Li6|He3, select from which detector the data comes from
            cut (tuple): lower left corner of box cut (QLong, PSD). If not none then draw
            cmap (str): [matplotlib color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) To reverse the order of the colormap append "_r" to the end of the string
        """

        # get the data from the tree
        tree = self.tfile[self.DET_NAMES[detector]['hits']].reset()
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
            detector (str): Li6|He3
            thresh (float): calculate cycle start time shift based on edge detection passing through this level
            bin_ms (int): histogram bin size in milliseconds
            rising (bool): if true do rising edge, else do falling edge

        Returns:
            np.array: the times at which the rising or falling edge passes through the threshold

        Example:
            ```python
                dt = [cyc[2].get_start_edge('Li6', 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
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
            return None

        # trim positions which are too long
        pos[pos == len(sign)] -= 1

        return t[pos]

    # quick access properties
    @property
    def beam1a_current_uA(self):
        """Get beamline 1A current in uA (micro amps)

        Returns:
            pd.Series: indexed by timestamps, current in uA
        """
        if type(self.tfile.BeamlineEpics) is pd.DataFrame:
            df = self.tfile.BeamlineEpics
        else:
            df = self.tfile.BeamlineEpics.to_dataframe()

        return df.B1_FOIL_ADJCUR

    @property
    def beam1u_current_uA(self):
        """Get beam current in uA (micro amps)

        Returns:
            pd.Series: indexed by timestamps, current in uA

        Notes:
            Beam current defined as `B1V_KSM_PREDCUR` * `B1V_KSM_BONPRD`

        Example:
            ```python
            >>> run.beam_current_uA
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


