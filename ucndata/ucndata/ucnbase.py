# Base class for ucnrun, ucncycle, and ucnperiod
# Derek Fujimoto
# Oct 2024

from rootloader import ttree
from .exceptions import *
from . import settings
from .datetime import to_datetime
from .applylist import applylist
import ucndata.constants as const
import numpy as np
import pandas as pd

class ucnbase(object):
    """UCN run data. Cleans data and performs analysis

    Args:
        run (int|str): if int, generate filename with settings.datadir
            elif str then run is the path to the file
        header_only (bool): if true, read only the header

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
        Can access attributes of tfile directly from top-level object
        Need to define the values in ucndata.settings if you want non-default
        behaviour
        Object is indexed as [cycle, period] for easy access to sub time frames
    """

    def __iter__(self):
        # setup iteration
        self._iter_current = 0
        return self

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
            beam = beam.to_dataframe()

        # get durations closest to cycle start time
        for start in cycle_times.start:

            start_times = abs(beam.index.values - start)
            durations = beam[epics_val].values*const.beam_bucket_duration_s
            idx = np.argmin(start_times)
            beam_dur.append(durations[idx])

        out = pd.Series(beam_dur, index=cycle_times.index)
        out.index.name = cycle_times.index.name

        if len(out) == 1:
            return float(out.values[0])
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

    def from_dataframe(self):
        """Convert self.tfile contents to rootfile struture types

        Returns:
            None: acts in-place

        Example:

            ```python
                >>> run = ucnrun(1846)

                # convert to dataframe
                >>> run.to_dataframe()
                >>> type(run.tfile.BeamlineEpics)
                pandas.core.frame.DataFrame

                # convert back
                >>> run.from_dataframe()
                >>> type(run.tfile.BeamlineEpics)
                rootloader.ttree.ttree
            ```
        """
        self.tfile.from_dataframe()

    def get_hits(self, detector):
        """Get times of ucn hits

        Args:
            detector (str): one of the keys to `settings.DET_NAMES`

        Returns:
            pd.DataFrame: hits tree as a dataframe, only the values when a hit is registered

        Example:
            ```python
            >>> run.get_hits('Li6')
                             tBaseline tChannel tChargeL tChargeS  ...      tPSD tTimeE  tTimeStamp     tUnixTime
            tUnixTimePrecise                                       ...
            4.072601e-02             0        2     3613     2126  ...  0.411560      0   260181502  4.072601e-02
            1.572461e+09             0        3     4796     3185  ...  0.335876      0   883762351  1.572461e+09
            1.572461e+09             0        3    40777    26278  ...  0.355591      0   746477328  1.572461e+09
            1.572461e+09             0        1     6386     3663  ...  0.426392      0   862122800  1.572461e+09
            1.572461e+09             0        4     4328     2246  ...  0.481079      0   694451573  1.572461e+09
            ...                    ...      ...      ...      ...  ...       ...    ...         ...           ...
            1.572466e+09             0        2     6076     3536  ...  0.418030      0  1993850662  1.572466e+09
            1.572466e+09             0        5     4027     1845  ...  0.541870      0    41459150  1.572466e+09
            1.572466e+09             0        4     6475     2903  ...  0.551636      0   517358805  1.572466e+09
            1.572466e+09             0        7     3836     2604  ...  0.321167      0   536381628  1.572466e+09
            1.572466e+09             0        4     5751     3028  ...  0.473511      0   851762669  1.572466e+09

            [242540 rows x 11 columns]
            ```
        """

        # get the tree
        hit_tree = self.tfile[settings.DET_NAMES[detector]['hits']] # maybe should be a copy?
        if type(hit_tree) is not pd.DataFrame:
            hit_tree = hit_tree.to_dataframe()

        # get times only when a hit is registered
        hit_tree = hit_tree.loc[hit_tree.tIsUCN.astype(bool)]

        return hit_tree

    def get_hits_histogram(self, detector, bin_ms=100, as_datetime=False):
        """Get histogram of UCNHits ttree times

        Args:
            detector (str): Li6|He3
            bin_ms (int): histogram bin size in milliseconds
            as_datetime (bool): if true, convert bin_centers to datetime objects

        Returns:
            tuple: (bin_centers, histogram counts)

        Example:
            ```python
            >>> run.get_hits_histogram('Li6')
            (array([1.57246100e+09, 1.57246100e+09, 1.57246100e+09, ...,
                    1.57246647e+09, 1.57246647e+09, 1.57246647e+09]),
            array([1, 0, 0, ..., 0, 0, 0]))

            # quick plotting with timestamps
            >>> import matplotlib.pyplot as plt
            >>> plt.plot(*run.get_hits_histogram('Li6', as_datetime=True))
            ```
        """

        # get data
        df = self.tfile[settings.DET_NAMES[detector]['hits']].copy()

        # to dataframe
        if not isinstance(df, pd.DataFrame):
            df = df.to_dataframe()

        # get new index
        index_col = df.index.name
        df.reset_index(inplace=True)

        # get timesteps for which there is an ucn
        times = df.index[df.tIsUCN.values.astype(bool)].values
        times = np.sort(times)

        # purge bad timestamps
        idx = df[index_col] > 15e8
        if any(idx):
            df = df.loc[idx]

        # combine timestamps which are identical
        df = df.groupby(index_col).sum()

        # get histogram bin edges
        bins = np.arange(times.min(), times.max()+bin_ms/1000, bin_ms/1000)
        bins -= bin_ms/1000/2

        # histogram
        hist, bins = np.histogram(times, bins=bins)
        bin_centers = (bins[1:] + bins[:-1])/2

        # to datetime
        if as_datetime:
            bin_centers = to_datetime(bin_centers)

        return (bin_centers, hist)

    def to_dataframe(self):
        """Convert self.tfile contents to pd.DataFrame

        Returns:
            None: converts in-place

        Example:

            ```python
                >>> run = ucnrun(1846)

                # check loaded type
                >>> type(run.tfile.BeamlineEpics)
                rootloader.ttree.ttree

                # convert
                >>> run.to_dataframe()
                >>> type(run.tfile.BeamlineEpics)
                pandas.core.frame.DataFrame
            ```
        """

        # convert to dataframes
        self.tfile.to_dataframe()

    # quick access properties
    @property
    def beam_current_uA(self):
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

        if type(self.tfile.BeamlineEpics) is pd.DataFrame:
            df = self.tfile.BeamlineEpics
        else:
            df = self.tfile.BeamlineEpics.to_dataframe()

        # PREDCUR is the predicted current in beamline 1U.
        # PREDCUR is calculated by using the beamline 1V extraction foil current
        # (the current as it leaves the cyclotron) and multiplid by the fraction
        # of beam that is going to the 1U beamline (as opposed to 1A beamline).
        # So if the extraction foil current is 100uA and we are kicking 1 bucket
        # out of 10 buckets to 1U, then PREDCUR will be 10uA
        predcur = df.B1V_KSM_PREDCUR

        # BONPRD is a bool, which indicates if there is beam down 1U
        bonprd = df.B1V_KSM_BONPRD

        # current in the 1U beamline
        return predcur*bonprd

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
