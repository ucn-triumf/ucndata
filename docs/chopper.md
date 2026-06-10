# Chopper

[Ucndata Index](./README.md#ucndata-index) / Chopper

> Auto-generated documentation for [chopper](../ucndata/chopper.py) module.

- [Chopper](#chopper)
  - [ccycle](#ccycle)
    - [ccycle.__getitem__](#ccycle()__getitem__)
    - [ccycle.get_period](#ccycle()get_period)
  - [cframe](#cframe)
    - [cframe.__repr__](#cframe()__repr__)
    - [cframe.get_nhits](#cframe()get_nhits)
  - [cperiod](#cperiod)
    - [cperiod.__getitem__](#cperiod()__getitem__)
    - [cperiod.__len__](#cperiod()__len__)
    - [cperiod.get_frame](#cperiod()get_frame)
  - [crun](#crun)
    - [crun.__getitem__](#crun()__getitem__)
    - [crun.get_cycle](#crun()get_cycle)
    - [crun.get_tof](#crun()get_tof)
    - [crun.inspect](#crun()inspect)
    - [crun.offset_frames](#crun()offset_frames)

## ccycle

[Show source in chopper.py:373](../ucndata/chopper.py#L373)

#### Signature

```python
class ccycle(ucndata.ucncycle):
    def __init__(self, urun, cycle): ...
```

### ccycle.__getitem__

[Show source in chopper.py:392](../ucndata/chopper.py#L392)

Return period(s) or frame(s) via index or slice notation.

Supports integer indexing, slices, and two-element tuples of the form
(period, frame). Negative integers are resolved relative to the total
period count. When cycle_param.filter is set, filtered-out periods are
excluded from slice results.

#### Arguments

- `key` *int|slice|tuple* - index into this cycle.
    * int — return a single cperiod.
    * slice — return an applylist of cperiod objects.
    * (period, frame) — return frame(s) within period(s).

#### Returns

- `cperiod|cframe|applylist` - the requested object or list of objects.

#### Raises

- `IndexError` - if the integer index exceeds the number of periods, or
    if the key type is not supported.

#### Examples

```python
>>> per = cycle[0]          # first period
>>> pers = cycle[0:2]       # first two periods as applylist
>>> fr = cycle[0, 1]        # frame 1 of period 0
```

#### Signature

```python
def __getitem__(self, key): ...
```

### ccycle.get_period

[Show source in chopper.py:461](../ucndata/chopper.py#L461)

Return a cperiod for the requested period, or all periods.

Trees are time-restricted to the requested period; this process
converts all ROOT objects to dataframes on first access. Results are
cached in self._perioddict so repeated calls are cheap. The last
period is dropped if it contains no data.

#### Notes

* This process converts all objects to dataframes.
* Must be called on a single cycle object, not on applylist.
* Equivalent to indexing style: ``cycle[period]``.

#### Arguments

- `period` *int|None* - period index (0-based). Pass None or a negative
    integer to get all periods. Defaults to None.

#### Returns

- `cperiod|applylist` - a single cperiod when period >= 0, or an
    applylist of cperiod objects for all periods when period is
    None or negative.

#### Examples

```python
>>> cycle = run[0]
>>> cycle.get_period(0)
run 1846 (cycle 0, period 0):
    comment            cycle_stop         period_start       shifters           tfile
    cycle              experiment_number  period_stop        start_time         year
    cycle_param        month              run_number         stop_time
    cycle_start        period             run_title          supercycle
```

#### Signature

```python
def get_period(self, period=None): ...
```



## cframe

[Show source in chopper.py:619](../ucndata/chopper.py#L619)

#### Signature

```python
class cframe(ucndata.ucnbase):
    def __init__(self, uperiod, frame): ...
```

### cframe.__repr__

[Show source in chopper.py:682](../ucndata/chopper.py#L682)

Return a human-readable summary of the frame's public attributes.

Attributes are sorted case-insensitively and laid out in columns sized
to fit the current terminal width.

#### Returns

- `str` - multi-line string showing run number, cycle, period, frame
    index, and all public attribute names.

#### Signature

```python
def __repr__(self): ...
```

### cframe.get_nhits

[Show source in chopper.py:664](../ucndata/chopper.py#L664)

Get the number of UCN hits recorded in this chopper frame.

Delegates to the parent crun._get_nhits_frame, which bins hits by
frame start time on first call and caches the result.

#### Arguments

- `detector` *str* - detector name. One of 'Li6' or 'He3'.

#### Returns

- `int` - number of UCN hits in this frame for the given detector.

#### Examples

```python
>>> frame.get_nhits('Li6')
42
```

#### Signature

```python
def get_nhits(self, detector): ...
```



## cperiod

[Show source in chopper.py:506](../ucndata/chopper.py#L506)

#### Signature

```python
class cperiod(ucndata.ucnperiod):
    def __init__(self, ucycle, period): ...
```

### cperiod.__getitem__

[Show source in chopper.py:550](../ucndata/chopper.py#L550)

Return frame(s) via integer index or slice.

Negative integers are resolved relative to the total frame count.

#### Arguments

- `key` *int|slice* - index into this period's frames.
    * int — return a single cframe.
    * slice — return an applylist of cframe objects.

#### Returns

- `cframe|applylist` - the requested frame or list of frames.

#### Raises

- `IndexError` - if the integer index exceeds the number of frames, or
    if a non-integer/non-slice key is given.

#### Examples

```python
>>> fr = period[0]       # first frame
>>> frs = period[0:3]    # first three frames as applylist
```

#### Signature

```python
def __getitem__(self, key): ...
```

### cperiod.__len__

[Show source in chopper.py:529](../ucndata/chopper.py#L529)

Return the number of chopper frames in this period.

#### Returns

- `int` - number of frames (cycle_param.nframes).

#### Signature

```python
def __len__(self): ...
```

### cperiod.get_frame

[Show source in chopper.py:590](../ucndata/chopper.py#L590)

Return a cframe for the requested frame, or all frames.

Trees are time-restricted to the requested chopper frame. Results are
cached in self._framedict so repeated calls are cheap.

#### Arguments

- `frame` *int|None* - frame index (0-based). Pass None or a negative
    integer to get all frames. Defaults to None.

#### Returns

- `cframe|applylist` - a single cframe when frame >= 0, or an applylist
    of cframe objects for all frames when frame is None or negative.

#### Examples

```python
>>> period.get_frame(0)          # first frame
>>> len(period.get_frame.      # total number of frames
```

#### Signature

```python
def get_frame(self, frame=None): ...
```



## crun

[Show source in chopper.py:13](../ucndata/chopper.py#L13)

#### Signature

```python
class crun(ucndata.ucnrun):
    def __init__(self, run, ucn_only=True, chop_time_ch=15): ...
```

### crun.__getitem__

[Show source in chopper.py:51](../ucndata/chopper.py#L51)

Return cycle(s), period(s), or frame(s) via index or slice notation.

Supports integer indexing, slices, and tuples of up to three elements
corresponding to (cycle, period, frame) dimensions. Negative integers
are resolved relative to the total cycle count. When cycle_param.filter
is set, filtered-out cycles are excluded from slice results.

#### Arguments

- `key` *int|slice|tuple* - index into the run hierarchy.
    * int — return a single ccycle.
    * slice — return an applylist of ccycle objects.
    * (cycle, period) — return period(s) within cycle(s).
    * (cycle, period, frame) — return frame(s) within period(s).

#### Returns

- `ccycle|cperiod|cframe|applylist` - the requested object or list of
    objects matching the given index.

#### Raises

- `IndexError` - if the integer index exceeds the number of cycles, or
    if the key type is not supported.

#### Examples

```python
>>> cyc = run[0]            # single cycle
>>> cycs = run[0:3]         # first three cycles as applylist
>>> per = run[0, 1]         # period 1 of cycle 0
>>> fr = run[0, 1, 2]       # frame 2 of period 1 of cycle 0
```

#### Signature

```python
def __getitem__(self, key): ...
```

### crun.get_cycle

[Show source in chopper.py:174](../ucndata/chopper.py#L174)

Return a ccycle for the requested cycle, or all cycles.

Trees are time-restricted to the requested cycle via tsubfile; this
process converts all ROOT objects to dataframes on first access.
Results are cached in self._cycledict so repeated calls are cheap.

#### Arguments

- `cycle` *int|None* - cycle index (0-based). Pass None or a negative
    integer to get all cycles. Defaults to None.

#### Returns

- `ccycle|applylist` - a single ccycle when cycle >= 0, or an applylist
    of ccycle objects for all cycles when cycle is None or negative.

#### Examples

```python
>>> run.get_cycle(0)
run 1846 (cycle 0):
    comment            cycle_start        month              shifters           supercycle
    cycle              cycle_stop         run_number         start_time         tfile
    cycle_param        experiment_number  run_title          stop_time          year
```

```python
>>> len(run.get_cycle.
17
```

#### Signature

```python
def get_cycle(self, cycle=None): ...
```

### crun.get_tof

[Show source in chopper.py:209](../ucndata/chopper.py#L209)

Compute a time-of-flight histogram over all good cycles.

Each neutron hit time is expressed relative to the most recent chopper
opening (channel 15 pulse), producing a ToF value. Bad cycles excluded
by cycle_param.filter are removed before histogramming.

#### Arguments

- `bin_ms` *float* - histogram bin width in milliseconds. Defaults to 1.

#### Returns

- `tuple` - (bin_edges, counts) where bin_edges is a np.ndarray of
    length N+1 and counts is a np.ndarray of length N.

#### Examples

```python
>>> edges, hist = run.get_tof(bin_ms=1)
>>> import matplotlib.pyplot as plt
>>> plt.stairs(hist, edges)
```

#### Signature

```python
def get_tof(self, bin_ms=1): ...
```

### crun.inspect

[Show source in chopper.py:272](../ucndata/chopper.py#L272)

Draw counts and BL1A current with shaded chopper frames to assess data quality.

Calls the parent ucnrun.inspect and then overlays alternating grey
shading for each chopper frame so the frame structure is visible
alongside the rate and beam-current traces.

#### Arguments

- `detector` *str* - detector to histogram. One of 'Li6' or 'He3'.
    Defaults to 'Li6'.
- `bin_ms` *int* - histogram bin width in milliseconds. Defaults to 100.
- `xmode` *str* - x-axis units. One of 'datetime', 'duration', or
    'epoch'. Defaults to 'duration'.
- `slow` *list|str|None* - slow-control channel name(s) to plot on an
    additional axis. Defaults to None.

#### Returns

- `list` - matplotlib Axes objects created by the parent inspect call.

#### Examples

```python
>>> run.inspect(detector='Li6', bin_ms=50, xmode='datetime')
```

#### Signature

```python
def inspect(self, detector="Li6", bin_ms=100, xmode="duration", slow=None): ...
```

### crun.offset_frames

[Show source in chopper.py:326](../ucndata/chopper.py#L326)

Shift all chopper frame start times by a constant offset.

Updates frame_start_times at the run, cycle, and period levels, and
resets the cached nhits-per-frame histogram so it is recomputed on the
next access.

#### Arguments

- `dt` *float* - time shift in seconds. Positive values shift frames
    forward in time.

#### Raises

- `ValueError` - if the shift would produce frame start times below zero
    or beyond the end of the run.

#### Examples

```python
>>> run.offset_frames(0.001)   # shift all frames forward by 1 ms
```

#### Signature

```python
def offset_frames(self, dt): ...
```