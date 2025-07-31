# ucncycle

[Ucndata Index](./README.md#ucndata-index) / ucncycle

> Auto-generated documentation for [ucncycle](../ucndata/ucncycle.py) module.

- [ucncycle](#ucncycle)
  - [ucncycle](#ucncycle-1)
    - [ucncycle.check_data](#ucncyclecheck_data)
    - [ucncycle.get_nhits](#ucncycleget_nhits)
    - [ucncycle.get_period](#ucncycleget_period)
    - [ucncycle.shift_timing](#ucncycleshift_timing)

## ucncycle

[Show source in ucncycle.py:14](../ucndata/ucncycle.py#L14)

View for the data from a single UCN cycle

#### Notes

Any changes to the data frame affects all periods (for the time steps
contained in that period) and the containing run

#### Arguments

- `urun` *ucnrun* - object to pull cycle from
- `cycle` *int* - cycle number

#### Signature

```python
class ucncycle(ucnbase):
    def __init__(self, urun, cycle): ...
```

#### See also

- [ucnbase](./ucnbase.md#ucnbase)

### ucncycle.check_data

[Show source in ucncycle.py:121](../ucndata/ucncycle.py#L121)

Run some checks to determine if the data is ok.

#### Arguments

- `period_production` *int* - index of period where the beam should be stable. Enables checks of beam stability
- `period_count` *int* - index of period where we count ucn. Enables checks of data quantity
- `period_background` *int* - index of period where we do not count ucn. Enables checks of background
- `raise_error` *bool* - if true, raise an error if check fails, else return false. Inactive if quiet=True
- `quiet` *bool* - if true don't print or raise exception

#### Returns

- `bool` - true if check passes, else false.

#### Notes

Checks performed

* is there BeamlineEpics data?
* is the cycle duration greater than 0?
* is at least one valve opened during at least one period?
* are there counts in each detector?

#### Examples

```python
>>> cycle = run[0]
>>> x = cycle.check_data()
Run 1846, cycle 0: Beam current dropped to 0.0 uA
>>> x
False
```

#### Signature

```python
def check_data(self, raise_error=False, quiet=False): ...
```

### ucncycle.get_nhits

[Show source in ucncycle.py:204](../ucndata/ucncycle.py#L204)

Get number of ucn hits

#### Arguments

- `detector` *str* - Li6|He3

#### Signature

```python
def get_nhits(self, detector): ...
```

### ucncycle.get_period

[Show source in ucncycle.py:212](../ucndata/ucncycle.py#L212)

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

### ucncycle.shift_timing

[Show source in ucncycle.py:251](../ucndata/ucncycle.py#L251)

Shift all periods by a constant time, maintaining the period durations.
This shifts the cycle start time and shortens the cycle, potentially creating gaps between cycles

#### Arguments

- `dt` *float* - time in seconds to add to each period start/end time

#### Examples

```python
# this avoids recomputing the histograms each iteration
dt = [cyc.get_time_shift('Li6', 2, 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
for i, t in enumerate(dt):
    run[i].shift_timing(t)
```

#### Notes

* This function makes use of `ucnrun._modify_ptiming`, which resets all saved histograms and hits

#### Signature

```python
def shift_timing(self, dt): ...
```