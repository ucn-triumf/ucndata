# ucnbase

[Ucndata Index](./README.md#ucndata-index) / ucnbase

> Auto-generated documentation for [ucnbase](../../ucnbase.py) module.

- [ucnbase](#ucnbase)
  - [ucnbase](#ucnbase-1)
    - [ucnbase.apply](#ucnbaseapply)
    - [ucnbase.beam1a_current_uA](#ucnbasebeam1a_current_ua)
    - [ucnbase.beam1u_current_uA](#ucnbasebeam1u_current_ua)
    - [ucnbase.beam_off_s](#ucnbasebeam_off_s)
    - [ucnbase.beam_on_s](#ucnbasebeam_on_s)
    - [ucnbase.get_hits_dataframe](#ucnbaseget_hits_dataframe)
    - [ucnbase.get_hits_histogram](#ucnbaseget_hits_histogram)
    - [ucnbase.get_nhits](#ucnbaseget_nhits)

## ucnbase

[Show source in ucnbase.py:16](../../ucnbase.py#L16)

#### Attributes

- `datadir` - path to the directory which contains the root files: '/data3/ucn/root_files'

- `timezone` - timezone for datetime conversion: 'America/Vancouver'

- `cycle_times_mode` - cycle times finding mode order: ['matched', 'li6', 'he3', 'sequencer', 'beamon']

- `tree_filter` - filter what trees and branches to load in each file. If unspecified then load the whole tree
  treename: (filter, columns). See [rootloader documentation](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md#ttree-1) for details: {}

- `DET_NAMES` - detector tree names: {'He3': {'hits': 'UCNHits_He3', 'hits_orig': 'UCNHits_He3', 'charge': 'He3_Charge', 'rate': 'He3_Rate', 'transitions': 'RunTransitions_He3', 'hitsseq': 'hitsinsequence_he3', 'hitsseqcumul': 'hitsinsequencecumul_he3'}, 'Li6': {'hits': 'UCNHits_Li6', 'hits_orig': 'UCNHits_Li-6', 'charge': 'Li6_Charge', 'rate': 'Li6_Rate', 'transitions': 'RunTransitions_Li6', 'hitsseq': 'hitsinsequence_li6', 'hitsseqcumul': 'hitsinsequencecumul_li6'}}

- `DATAFRAME_TREES` - make these trees dataframes, ok since they're small - also resets the index: ('CycleParamTree', 'RunTransitions_He3', 'RunTransitions_Li6')

- `SLOW_TREES` - needed slow control trees: for checking data quality: ('BeamlineEpics', 'SequencerTree', 'LNDDetectorTree')

- `DATA_CHECK_THRESH` - data thresholds for checking data: {'beam_min_current': 0.1, 'beam_max_current_std': 0.2, 'max_bkgd_count_rate': 4, 'count_period_last_s_is_bkgd': 5, 'min_total_counts': 20, 'pileup_cnt_per_ms': 10, 'pileup_within_first_s': 1}

- `DET_BKGD` - default detector backgrounds - from 2019: {'Li6': 80, 'Li6_err': 0.009, 'He3': 0.0349, 'He3_err': 0.0023}


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

[Show source in ucnbase.py:144](../../ucnbase.py#L144)

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

[Show source in ucnbase.py:307](../../ucnbase.py#L307)

Get beamline 1A current in uA (micro amps)

#### Returns

- `pd.Series` - indexed by timestamps, current in uA

#### Signature

```python
@property
def beam1a_current_uA(self): ...
```

### ucnbase.beam1u_current_uA

[Show source in ucnbase.py:321](../../ucnbase.py#L321)

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

[Show source in ucnbase.py:400](../../ucnbase.py#L400)

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

[Show source in ucnbase.py:365](../../ucnbase.py#L365)

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

### ucnbase.get_hits_dataframe

[Show source in ucnbase.py:161](../../ucnbase.py#L161)

Get times of ucn hits as a pandas dataframe

#### Arguments

- `detector` *str* - one of the keys to `self.DET_NAMES`

#### Returns

- `pd.DataFrame` - hits tree as a dataframe, only the values when a hit is registered

#### Examples

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

#### Signature

```python
def get_hits_dataframe(self, detector): ...
```

### ucnbase.get_hits_histogram

[Show source in ucnbase.py:200](../../ucnbase.py#L200)

Get histogram of UCNHits ttree times

#### Arguments

- `detector` *str* - Li6|He3
- `bin_ms` *int* - histogram bin size in milliseconds
- `as_datetime` *bool* - if true, convert bin_centers to datetime objects

#### Returns

- `rootloader.th1` - histogram object

#### Examples

```python
>>> run.get_hits_histogram('Li6')
(array([1.57246100e+09, 1.57246100e+09, 1.57246100e+09, ...,
        1.57246647e+09, 1.57246647e+09, 1.57246647e+09]),
array([1, 0, 0, ..., 0, 0, 0]))

# quick plotting with timestamps
>>> import matplotlib.pyplot as plt
>>> plt.plot(*run.get_hits_histogram('Li6', as_datetime=True))
```

#### Signature

```python
def get_hits_histogram(self, detector, bin_ms=100, as_datetime=False): ...
```

### ucnbase.get_nhits

[Show source in ucnbase.py:240](../../ucnbase.py#L240)

Get number of ucn hits

#### Signature

```python
def get_nhits(self, detector): ...
```