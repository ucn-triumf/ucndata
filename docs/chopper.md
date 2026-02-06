# Chopper

[Ucndata Index](./README.md#ucndata-index) / Chopper

> Auto-generated documentation for [chopper](../ucndata/chopper.py) module.

- [Chopper](#chopper)
  - [ccycle](#ccycle)
    - [ccycle.get_period](#ccycle.get_period)
  - [cframe](#cframe)
    - [cframe.get_nhits](#cframe.get_nhits)
  - [cperiod](#cperiod)
    - [cperiod.get_frame](#cperiod.get_frame)
  - [crun](#crun)
    - [crun.get_cycle](#crun.get_cycle)
    - [crun.inspect](#crun.inspect)
    - [crun.offset_frames](#crun.offset_frames)

## ccycle

[Show source in chopper.py:235](../ucndata/chopper.py#L235)

#### Signature

```python
class ccycle(ucndata.ucncycle):
    def __init__(self, urun, cycle): ...
```

### ccycle.get_period

[Show source in chopper.py:289](../ucndata/chopper.py#L289)

Return a copy of this object, but trees are trimmed to only one period.

#### Notes

* This process converts all objects to dataframes
* Must be called for a single cycle only
* Equivalent to indexing style: `cycle[period]`

#### Arguments

- `period` *int* - period number, if None, get all periods
cycle (int|None) if cycle not specified then specify a cycle

#### Returns

run:
    if period > 0: a copy of this object but with data from only one period.
    if period < 0 | None: a list of copies of this object for all periods for a single cycle

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

[Show source in chopper.py:392](../ucndata/chopper.py#L392)

#### Signature

```python
class cframe(ucndata.ucnbase):
    def __init__(self, uperiod, frame): ...
```

### cframe.get_nhits

[Show source in chopper.py:427](../ucndata/chopper.py#L427)

Get number of ucn hits

#### Arguments

- `detector` *str* - Li6|He3

#### Signature

```python
def get_nhits(self, detector): ...
```



## cperiod

[Show source in chopper.py:331](../ucndata/chopper.py#L331)

#### Signature

```python
class cperiod(ucndata.ucnperiod):
    def __init__(self, ucycle, period): ...
```

### cperiod.get_frame

[Show source in chopper.py:380](../ucndata/chopper.py#L380)

#### Signature

```python
def get_frame(self, frame=None): ...
```



## crun

[Show source in chopper.py:14](../ucndata/chopper.py#L14)

#### Signature

```python
class crun(ucndata.ucnrun):
    def __init__(self, run, ucn_only=True, chop_time_ch=15): ...
```

### crun.get_cycle

[Show source in chopper.py:122](../ucndata/chopper.py#L122)

Return a copy of this object, but trees are trimmed to only one cycle.

Note that this process converts all objects to dataframes

#### Arguments

- `cycle` *int* - cycle number, if None, get all cycles

#### Returns

ucncycle:
    if cycle > 0:  ucncycle object
    if cycle < 0 | None: a list ucncycle objects for all cycles

#### Examples

```python
# get single cycle
>>> run.get_cycle(0)
run 1846 (cycle 0):
    comment            cycle_start        month              shifters           supercycle
    cycle              cycle_stop         run_number         start_time         tfile
    cycle_param        experiment_number  run_title          stop_time          year

# get all cycles
>>> len(run.get_cycle.
17
```

#### Signature

```python
def get_cycle(self, cycle=None): ...
```

### crun.inspect

[Show source in chopper.py:159](../ucndata/chopper.py#L159)

Draw counts and BL1A current with indicated periods to determine data quality

#### Arguments

- `detector` *str* - detector from which to get the counts from. Li6|He3
- `bin_ms` *int* - histogram bin size in ms
- `xmode` *str* - datetime|duration|epoch
- `slow` *list|str* - name of slow control tree to add in a separate axis, can be a list of names

#### Signature

```python
def inspect(self, detector="Li6", bin_ms=100, xmode="duration", slow=None): ...
```

### crun.offset_frames

[Show source in chopper.py:200](../ucndata/chopper.py#L200)

Add an offset to the start times of all frames

#### Arguments

- `dt` *float* - time shift, should not push frames outside the limits of the run

#### Signature

```python
def offset_frames(self, dt): ...
```