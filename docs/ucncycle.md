# ucncycle

[Ucndata Index](./README.md#ucndata-index) / ucncycle

> Auto-generated documentation for [ucncycle](../ucndata/ucncycle.py) module.

- [ucncycle](#ucncycle)
  - [ucncycle](#ucncycle-1)
    - [ucncycle().check_data](#ucncyclecheck_data)
    - [ucncycle().draw_cycle_times](#ucncycledraw_cycle_times)
    - [ucncycle().get_nhits](#ucncycleget_nhits)
    - [ucncycle().get_period](#ucncycleget_period)
    - [ucncycle().shift_timing](#ucncycleshift_timing)

## ucncycle

[Show source in ucncycle.py:19](../ucndata/ucncycle.py#L19)

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

### ucncycle().check_data

[Show source in ucncycle.py:257](../ucndata/ucncycle.py#L257)

Run some checks to determine if the data is ok.

#### Arguments

- `raise_error` *bool* - if True, raise an error when a check fails
    instead of returning False. Has no effect when ``quiet=True``.
- `quiet` *bool* - if True, suppress all printed messages and exceptions;
    always returns False on failure without side effects.

#### Returns

- `bool` - True if all checks pass, False otherwise.

#### Notes

Checks performed:

* is there BeamlineEpics data (1A and 1U beam currents)?
* is the cycle duration greater than 0?
* is at least one valve opened during at least one period?
* does the sum of period durations fit within the cycle duration?
* did the 1A beam current stay above the minimum threshold throughout
  the cycle and the 20 seconds before it?

#### Examples

```python
>>> cycle = run[0]
>>> x = cycle.check_data()
Run 1846, cycle 0: 1A current dropped below 1.0 uA
>>> x
False
```

#### Signature

```python
def check_data(self, raise_error=False, quiet=False): ...
```

### ucncycle().draw_cycle_times

[Show source in ucncycle.py:338](../ucndata/ucncycle.py#L338)

Draw cycle start time as a thick black line and period end times as dashed lines.

The cycle label is rendered vertically at the cycle start. If the cycle
is excluded by ``cycle_param.filter``, the label is struck through in red.

#### Arguments

- `ax` *plt.Axes* - axes to draw into. Uses ``plt.gca()`` when None.
- `xmode` *str* - x-axis time representation. One of:

* ``'datetime'`` — absolute wall-clock timestamps
* ``'duration'`` — seconds since the start of the run
* ``'duration_run'`` — same as ``'duration'``
* ``'duration_cycle'`` — seconds since this cycle's start
* ``'epoch'`` — raw Unix epoch seconds

#### Returns

- `numpy.ndarray` - unique period indices that were drawn (zero-length
    periods are skipped).

#### Raises

- `RuntimeError` - if ``xmode`` is not one of the accepted values.

#### Notes

Assumed period layout: 0 - irradiation, 1 - storage, 2 - count.

#### Examples

```python
>>> fig, ax = plt.subplots()
>>> run[0].draw_cycle_times(ax=ax, xmode='duration_cycle')
array([0, 1, 2])
```

#### Signature

```python
def draw_cycle_times(self, ax=None, xmode="datetime"): ...
```

### ucncycle().get_nhits

[Show source in ucncycle.py:438](../ucndata/ucncycle.py#L438)

Get the total number of UCN hits recorded in this cycle.

Delegates to the parent run's ``_get_nhits`` with this cycle's index.
See that method for caching and performance details.

#### Arguments

- `detector` *str* - detector to query — ``'Li6'`` or ``'He3'``.
- `bin_ms` *int* - hit-event time resolution in milliseconds.
    When 0, raw hit timestamps are used for maximum precision and a
    per-period histogram is cached keyed on the current period
    boundaries. When > 0, a fixed-bin histogram of that width is
    built and reused across repeated calls with the same value,
    which is faster when period timings are modified frequently.

#### Returns

- `int` - total number of UCN hit events in this cycle.

#### Notes

With ``bin_ms=0`` the hit histogram is cached against the current
period boundaries. Modifying timings invalidates the cache and
forces a rebuild on the next call. To avoid per-iteration rebuilds,
finish all timing modifications before calling ``get_nhits``

```python
# slow — rebuilds histogram every iteration
hits = []
for cycle in run:
    cycle[1].modify_timing(1)
    hits.append(cycle[1].get_nhits('Li6'))

# fast — histogram built once after all modifications
for cycle in run:
    cycle[1].modify_timing(1)
hits = run[:, 1].get_nhits('Li6')
```

#### Examples

```python
>>> cycle = run[0]
>>> cycle.get_nhits('Li6')
4321
>>> cycle.get_nhits('He3', bin_ms=100)
4289
```

#### Signature

```python
def get_nhits(self, detector, bin_ms=0): ...
```

### ucncycle().get_period

[Show source in ucncycle.py:484](../ucndata/ucncycle.py#L484)

Return a ucnperiod (or list of all periods) for this cycle.

Equivalent to the indexing shorthand ``cycle[period]``. Results are
cached in ``_perioddict`` so repeated calls for the same period are
cheap.

#### Arguments

period (int | None): zero-based period index. Pass ``None`` or a
    negative integer to retrieve all periods as an [applylist](./applylist.md#applylist).

#### Returns

ucnperiod | applylist:
    * a single [ucnperiod](./ucnperiod.md#ucnperiod) when ``period >= 0``.
    * an [applylist](./applylist.md#applylist) of all [ucnperiod](./ucnperiod.md#ucnperiod) objects when
      ``period`` is ``None`` or negative.

#### Notes

Each [ucnperiod](./ucnperiod.md#ucnperiod) is a time-restricted view; all data frames and
trees are filtered to the period's [start, stop] window.

#### Examples

```python
>>> cycle = run[0]
>>> cycle.get_period(0)
run 1846 (cycle 0, period 0):
  comment            cycle_stop         period_start       shifters           tfile
  cycle              experiment_number  period_stop        start_time         year
  cycle_param        month              run_number         stop_time
  cycle_start        period             run_title          supercycle
>>> all_periods = cycle.get_period()   # applylist of all periods
>>> len(all_periods)
3
```

#### Signature

```python
def get_period(self, period=None): ...
```

### ucncycle().shift_timing

[Show source in ucncycle.py:528](../ucndata/ucncycle.py#L528)

Shift every period in this cycle by a constant offset, preserving period durations.

The cycle start time is advanced by ``dt`` while each period boundary
is shifted by the same amount, so durations remain unchanged. This may
create a gap between adjacent cycles.

#### Arguments

- `dt` *float* - seconds to add to every period start and end time.
    Negative values shift earlier.

#### Notes

Internally calls ``ucnrun._modify_ptiming`` for each period, which
resets all cached hit histograms. To avoid redundant histogram
rebuilds, collect all shift values first and then apply them

```python
# compute shifts without rebuilding histograms mid-loop
dt = [cyc.get_time_shift('Li6', 2, 50) if cyc[2].period_dur > 0 else 0
      for cyc in run]
for i, t in enumerate(dt):
    run[i].shift_timing(t)
```

#### Examples

```python
>>> # shift cycle 0 forward by 2 seconds
>>> run[0].shift_timing(2.0)
```

#### Signature

```python
def shift_timing(self, dt): ...
```