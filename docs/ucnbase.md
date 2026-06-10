# ucnbase

[Ucndata Index](./README.md#ucndata-index) / ucnbase

> Auto-generated documentation for [ucnbase](../ucndata/ucnbase.py) module.

- [ucnbase](#ucnbase)
  - [ucnbase](#ucnbase-1)
    - [ucnbase().apply](#ucnbaseapply)
    - [ucnbase().beam1a_current_uA](#ucnbasebeam1a_current_ua)
    - [ucnbase().beam1u_current_uA](#ucnbasebeam1u_current_ua)
    - [ucnbase().beam_off_s](#ucnbasebeam_off_s)
    - [ucnbase().beam_on_s](#ucnbasebeam_on_s)
    - [ucnbase().get_hits_array](#ucnbaseget_hits_array)
    - [ucnbase().get_hits_histogram](#ucnbaseget_hits_histogram)
    - [ucnbase().inspect](#ucnbaseinspect)
    - [ucnbase().plot_psd](#ucnbaseplot_psd)
    - [ucnbase().trigger_edge](#ucnbasetrigger_edge)

## ucnbase

[Show source in ucnbase.py:19](../ucndata/ucnbase.py#L19)

Base class shared by ucnrun, ucncycle, and ucnperiod.

Provides shared analysis methods and quick-access properties for
Ultra-Cold Neutron (UCN) experimental data loaded from ROOT files.
Not instantiated directly — use ucnrun, ucncycle, or ucnperiod instead.

#### Attributes

- `comment` *str* - comment input by users at the time of the run
- `cycle` *int|None* - cycle index within the run; None at the run level
- `cycle_param` *attrdict* - cycle timing and period structure parameters
- `epics` *ttreeslow* - unified EPICS slow-control interface
- `experiment_number` *str* - experiment number recorded by users
- `month` *int* - month of the run start date
- `run_number` *int* - run number as recorded in the ROOT file header
- `run_title` *str* - run title recorded by users
- `shifter` *str* - experimenter names on shift during the run
- `start_time` *str* - human-readable start time of the run
- `stop_time` *str* - human-readable stop time of the run
- `supercycle` *int|None* - supercycle index; None at the run level
- `tfile` *tfile* - rootloader tfile object holding all ROOT tree data
- `year` *int* - year of the run start date

#### Notes

- Attributes of tfile can be accessed directly from the top-level
  ucnrun, ucncycle, or ucnperiod object via attribute pass-through.
- ucncycle objects additionally expose cycle_start, cycle_stop, and
  cycle_dur (epoch seconds).
- ucnperiod objects additionally expose period_start, period_stop,
  period_dur (epoch seconds), and period (int index).
- Objects support indexing as [cycle] or [cycle, period] for easy
  access to sub-timeframe views.

#### Signature

```python
class ucnbase(object): ...
```

### ucnbase().apply

[Show source in ucnbase.py:102](../ucndata/ucnbase.py#L102)

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

### ucnbase().beam1a_current_uA

[Show source in ucnbase.py:492](../ucndata/ucnbase.py#L492)

Get beamline 1A current in uA (micro amps).

Reads the B1_FOIL_ADJCUR column from BeamlineEpics, which records
the adjusted extraction foil current on BL1A.

#### Returns

- `pd.Series` - indexed by epoch timestamps, current values in uA.

#### Examples

```python
>>> run.beam1a_current_uA
timestamp
1750164000    98.3
1750164005    98.2
1750164010    98.4
dtype: float64
```

#### Signature

```python
@property
def beam1a_current_uA(self): ...
```

### ucnbase().beam1u_current_uA

[Show source in ucnbase.py:517](../ucndata/ucnbase.py#L517)

Get beam current in uA (micro amps)

#### Returns

- `pd.Series` - indexed by timestamps, current in uA

#### Notes

Beam current defined as `B1V_KSM_PREDCUR` * `B1V_KSM_BONPRD`

#### Examples

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

#### Signature

```python
@property
def beam1u_current_uA(self): ...
```

### ucnbase().beam_off_s

[Show source in ucnbase.py:596](../ucndata/ucnbase.py#L596)

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

### ucnbase().beam_on_s

[Show source in ucnbase.py:561](../ucndata/ucnbase.py#L561)

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

### ucnbase().get_hits_array

[Show source in ucnbase.py:119](../ucndata/ucnbase.py#L119)

Get times of ucn hits as a numpy array

#### Arguments

- `detector` *str* - one of the keys to `ucndata.DET_NAMES`

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

### ucnbase().get_hits_histogram

[Show source in ucnbase.py:145](../ucndata/ucnbase.py#L145)

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
def get_hits_histogram(self, detector, bin_ms=10, as_datetime=False): ...
```

### ucnbase().inspect

[Show source in ucnbase.py:226](../ucndata/ucnbase.py#L226)

Draw counts and BL1A current with indicated periods to determine data quality.

Produces a multi-panel figure with the BL1A beam current on the top panel,
UCN hit counts on the second panel, and optional EPICS slow-control channels
in additional panels below. Cycle start times are marked with solid black
vertical lines; period boundaries are marked with dashed coloured lines.

#### Arguments

- `detector` *str* - detector from which to get the counts. Li6|He3
- `bin_ms` *int* - histogram bin size in milliseconds
- `xmode` *str* - x-axis mode — datetime|duration|epoch
- `slow` *list|str* - name(s) of EPICS column(s) to add as extra axes below
    the count panel. Accepts a single column name string or a list of
    column name strings. Must be present in self.epics.columns.

#### Returns

- `np.ndarray` - array of matplotlib Axes objects for the figure panels.

#### Raises

- `RuntimeError` - if xmode is not one of datetime|duration|epoch.
- `KeyError` - if a requested slow-control column is not found in self.epics.
- `RuntimeError` - if slow is not a string or iterable.

#### Examples

```python
# inspect full run
>>> axes = run.inspect('Li6', bin_ms=100, xmode='duration')

# inspect single cycle with extra slow control panel
>>> axes = run[3].inspect('He3', slow='UCN2EpicsTemperature_UCN_He3_TEMP')
```

#### Signature

```python
def inspect(self, detector="Li6", bin_ms=100, xmode="duration", slow=None): ...
```

### ucnbase().plot_psd

[Show source in ucnbase.py:362](../ucndata/ucnbase.py#L362)

Calculate PSD as (QLong-QShort)/QLong and draw as a 3x3 grid of 2D histograms.

One subplot per digitizer channel (channels 0–8). The x-axis is the long-gate
charge QLong, and the y-axis is the pulse-shape discriminant
(QLong - QShort) / QLong. All subplots share the same colour scale.

#### Arguments

- `detector` *str* - Li6|He3, selects which detector hit tree to read
- `cut` *tuple|None* - (QLong, PSD) coordinates of the lower-left corner of a
    rectangular selection box. If not None, a white rectangle is drawn on
    every subplot from this corner to (max_QLong, 1).
- `cmap` *str* - matplotlib colormap name. See
    https://matplotlib.org/stable/users/explain/colors/colormaps.html
    Append "_r" to reverse the colormap direction.

#### Examples

```python
# basic PSD plot for Li6 detector
>>> run.plot_psd('Li6')

# draw with a selection cut at QLong=200, PSD=0.2
>>> run.plot_psd('Li6', cut=(200, 0.2))
```

#### Signature

```python
def plot_psd(self, detector="Li6", cut=None, cmap="RdBu"): ...
```

### ucnbase().trigger_edge

[Show source in ucnbase.py:450](../ucndata/ucnbase.py#L450)

Detect period start time based on a rising or falling edge

#### Arguments

- `detector` *str* - Li6|He3
- `thresh` *float* - calculate cycle start time shift based on edge detection passing through this level
- `bin_ms` *int* - histogram bin size in milliseconds
- `rising` *bool* - if true do rising edge, else do falling edge

#### Returns

- `np.array` - the times at which the rising or falling edge passes through the threshold

#### Examples

```python
>>> dt = [cyc[2].trigger_edge('Li6', 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
```

#### Signature

```python
def trigger_edge(self, detector, thresh, bin_ms=10, rising=True): ...
```