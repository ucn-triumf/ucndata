# ucnbase

[Ucndata Index](./README.md#ucndata-index) / ucnbase

> Auto-generated documentation for [ucnbase](../ucndata/ucnbase.py) module.

- [ucnbase](#ucnbase)
  - [ucnbase](#ucnbase-1)
    - [ucnbase.apply](#ucnbaseapply)
    - [ucnbase.beam1a_current_uA](#ucnbasebeam1a_current_ua)
    - [ucnbase.beam1u_current_uA](#ucnbasebeam1u_current_ua)
    - [ucnbase.beam_off_s](#ucnbasebeam_off_s)
    - [ucnbase.beam_on_s](#ucnbasebeam_on_s)
    - [ucnbase.get_hits_array](#ucnbaseget_hits_array)
    - [ucnbase.get_hits_histogram](#ucnbaseget_hits_histogram)
    - [ucnbase.plot_psd](#ucnbaseplot_psd)

## ucnbase

[Show source in ucnbase.py:16](../ucndata/ucnbase.py#L16)

#### Attributes

- `datadir` - path to the directory which contains the root files: '/data3/ucn/root_files'

- `timezone` - timezone for datetime conversion: 'America/Vancouver'

- `cycle_times_mode` - cycle times finding mode order: ['matched', 'li6', 'he3', 'sequencer', 'beamon']

- `tree_filter` - filter what trees and branches to load in each file. If unspecified then load the whole tree
  treename: (filter, columns). See [rootloader documentation](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md#ttree-1) for details: {}

- `DET_NAMES` - detector tree names: {'He3': {'hits': 'UCNHits_He3', 'hits_orig': 'UCNHits_He3', 'charge': 'He3_Charge', 'rate': 'He3_Rate', 'transitions': 'RunTransitions_He3', 'hitsseq': 'hitsinsequence_he3', 'hitsseqcumul': 'hitsinsequencecumul_he3'}, 'Li6': {'hits': 'UCNHits_Li6', 'hits_orig': 'UCNHits_Li-6', 'charge': 'Li6_Charge', 'rate': 'Li6_Rate', 'transitions': 'RunTransitions_Li6', 'hitsseq': 'hitsinsequence_li6', 'hitsseqcumul': 'hitsinsequencecumul_li6'}}

- `DATAFRAME_TREES` - make these trees dataframes, ok since they're small - also resets the index: ('CycleParamTree', 'RunTransitions_He3', 'RunTransitions_Li6')

- `SLOW_TREES` - needed slow control trees: for checking data quality: ('BeamlineEpics', 'SequencerTree', 'LNDDetectorTree')

- `EPICS_TREES` - EPICS trees to group into a single slow control tree: ['BeamlineEpics', 'UCN2EpPha5Last', 'UCN2EpicsPhase2B', 'UCN2EpPha5Oth', 'UCN2EpicsPhase3', 'UCN2EpPha5Pre', 'UCN2EpicsPressures', 'UCN2EpPha5Tmp', 'UCN2EpicsTemperature', 'UCN2Epics', 'UCN2Pur', 'UCN2EpicsOthers']

- `DATA_CHECK_THRESH` - data thresholds for checking data: {'beam_min_current': 0.1, 'pileup_cnt_per_ms': 10, 'pileup_within_first_s': 1}


UCN run data. Cleans data and performs analysis

#### Arguments

- `run` *int|str* - if int, generate filename with self.datadir
    elif str then run is the path to the file
- `header_only` *bool* - if true, read only the header

#### Attributes

- `comment` *str* - comment input by users
- `cycle` *int|none* - cycle number, none if no cycle selected
- `cycle_param` *attrdict* - cycle parameters
- `experiment_number` *str* - experiment number input by users
- `month` *int* - month of run start
- `run_number` *int* - run number
- `run_title` *str* - run title input by users
- `shifter` *str* - experimenters on shift at time of run
- `start_time` *str* - start time of the run
- `stop_time` *str* - stop time of the run
- `supercycle` *int|none* - supercycle number, none if no cycle selected
- `tfile` *tfile* - stores tfile raw readback
- `year` *int* - year of run start

#### Notes

Can access attributes of tfile directly from top-level object
Need to redefine the values if you want non-default
behaviour
Object is indexed as [cycle, period] for easy access to sub time frames

#### Signature

```python
class ucnbase(object): ...
```

### ucnbase.apply

[Show source in ucnbase.py:141](../ucndata/ucnbase.py#L141)

Apply function to each cycle

#### Arguments

fn_handle (function handle): function to be applied to each cycle

#### Returns

- [applylist](./applylist.md#applylist) - output of the function

#### Examples

```python
>>> run.apply(lambda x: x.cycle)
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
```

#### Signature

```python
def apply(self, fn_handle): ...
```

### ucnbase.beam1a_current_uA

[Show source in ucnbase.py:344](../ucndata/ucnbase.py#L344)

Get beamline 1A current in uA (micro amps)

#### Returns

- `pd.Series` - indexed by timestamps, current in uA

#### Signature

```python
@property
def beam1a_current_uA(self): ...
```

### ucnbase.beam1u_current_uA

[Show source in ucnbase.py:358](../ucndata/ucnbase.py#L358)

Get beam current in uA (micro amps)

#### Returns

- `pd.Series` - indexed by timestamps, current in uA

#### Notes

Beam current defined as `B1V_KSM_PREDCUR` * `B1V_KSM_BONPRD`

#### Examples

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

#### Signature

```python
@property
def beam1u_current_uA(self): ...
```

### ucnbase.beam_off_s

[Show source in ucnbase.py:437](../ucndata/ucnbase.py#L437)

Get the beam-off duration in seconds for each cycle as given by `B1V_KSM_RDBEAMOFF_VAL1`

#### Returns

- `pd.Series` - indexed by cycle number, beam-off duration in s

#### Examples

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

#### Signature

```python
@property
def beam_off_s(self): ...
```

### ucnbase.beam_on_s

[Show source in ucnbase.py:402](../ucndata/ucnbase.py#L402)

Get the beam-on duration in seconds for each cycle as given by `B1V_KSM_RDBEAMON_VAL1`

#### Returns

- `pd.Series` - indexed by cycle number, beam-on duration in s

#### Examples

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

#### Signature

```python
@property
def beam_on_s(self): ...
```

### ucnbase.get_hits_array

[Show source in ucnbase.py:158](../ucndata/ucnbase.py#L158)

Get times of ucn hits as a numpy array

#### Arguments

- `detector` *str* - one of the keys to `self.DET_NAMES`

#### Returns

- `np.array` - array of timestamps corresponding to an UCN hit. Note that this returns all events in the case where ucn_only=False

#### Examples

```python
>>> run.get_hits_array('Li6')
array([1.75016403e+09, 1.75016405e+09, 1.75016405e+09, ...,
       1.75016479e+09, 1.75016479e+09, 1.75016479e+09])
```

#### Signature

```python
def get_hits_array(self, detector): ...
```

### ucnbase.get_hits_histogram

[Show source in ucnbase.py:184](../ucndata/ucnbase.py#L184)

Get histogram of UCNHits ttree times

#### Arguments

- `detector` *str* - Li6|He3
- `bin_ms` *int* - histogram bin size in milliseconds
- `as_datetime` *bool* - if true, convert bin_centers to datetime objects

#### Returns

- `rootloader.th1` - histogram object

#### Examples

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

#### Signature

```python
def get_hits_histogram(self, detector, bin_ms=100, as_datetime=False): ...
```

### ucnbase.plot_psd

[Show source in ucnbase.py:272](../ucndata/ucnbase.py#L272)

Calculate PSD as (QLong-QShort)/QLong, draw as a grid, 2D histograms

#### Arguments

- `detector` *str* - Li6|He3, select from which detector the data comes from
- `cut` *tuple* - lower left corner of box cut (QLong, PSD). If not none then draw
- `cmap` *str* - [matplotlib color map](https://matplotlib.org/stable/users/explain/colors/colormaps.html) To reverse the order of the colormap append "_r" to the end of the string

#### Signature

```python
def plot_psd(self, detector="Li6", cut=None, cmap="RdBu"): ...
```