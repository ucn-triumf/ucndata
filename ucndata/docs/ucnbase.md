# ucnbase

[Ucndata Index](./README.md#ucndata-index) / ucnbase

> Auto-generated documentation for [ucnbase](../../ucnbase.py) module.

- [ucnbase](#ucnbase)
  - [ucnbase](#ucnbase-1)
    - [ucnbase.apply](#ucnbaseapply)
    - [ucnbase.beam_current_uA](#ucnbasebeam_current_ua)
    - [ucnbase.beam_off_s](#ucnbasebeam_off_s)
    - [ucnbase.beam_on_s](#ucnbasebeam_on_s)
    - [ucnbase.from_dataframe](#ucnbasefrom_dataframe)
    - [ucnbase.get_hits](#ucnbaseget_hits)
    - [ucnbase.get_hits_histogram](#ucnbaseget_hits_histogram)
    - [ucnbase.to_dataframe](#ucnbaseto_dataframe)

## ucnbase

[Show source in ucnbase.py:15](../../ucnbase.py#L15)

UCN run data. Cleans data and performs analysis

#### Arguments

- `run` *int|str* - if int, generate filename with settings.datadir
    elif str then run is the path to the file
- `header_only` *bool* - if true, read only the header

#### Attributes

- `comment` *str* - comment input by users
- `cycle` *int|none* - cycle number, none if no cycle selected
- `cycle_param` *attrdict* - cycle parameters from sequencer settings
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
Need to define the values in ucndata.settings if you want non-default
behaviour
Object is indexed as [cycle, period] for easy access to sub time frames

#### Signature

```python
class ucnbase(object): ...
```

### ucnbase.apply

[Show source in ucnbase.py:109](../../ucnbase.py#L109)

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

### ucnbase.beam_current_uA

[Show source in ucnbase.py:271](../../ucnbase.py#L271)

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
def beam_current_uA(self): ...
```

### ucnbase.beam_off_s

[Show source in ucnbase.py:354](../../ucnbase.py#L354)

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

[Show source in ucnbase.py:319](../../ucnbase.py#L319)

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

### ucnbase.from_dataframe

[Show source in ucnbase.py:126](../../ucnbase.py#L126)

Convert self.tfile contents to rootfile struture types

#### Returns

- `None` - acts in-place

#### Examples

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

#### Signature

```python
def from_dataframe(self): ...
```

### ucnbase.get_hits

[Show source in ucnbase.py:150](../../ucnbase.py#L150)

Get times of ucn hits

#### Arguments

- `detector` *str* - one of the keys to [DET_NAMES](./settings.md#det_names)

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
def get_hits(self, detector): ...
```

### ucnbase.get_hits_histogram

[Show source in ucnbase.py:190](../../ucnbase.py#L190)

Get histogram of UCNHits ttree times

#### Arguments

- `detector` *str* - Li6|He3
- `bin_ms` *int* - histogram bin size in milliseconds
- `as_datetime` *bool* - if true, convert bin_centers to datetime objects

#### Returns

- `tuple` - (bin_centers, histogram counts)

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

### ucnbase.to_dataframe

[Show source in ucnbase.py:245](../../ucnbase.py#L245)

Convert self.tfile contents to pd.DataFrame

#### Returns

- `None` - converts in-place

#### Examples

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

#### Signature

```python
def to_dataframe(self): ...
```