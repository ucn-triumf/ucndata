# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../ucndata/ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.__repr__](#ucnperiod__repr__)
    - [ucnperiod.get_nhits](#ucnperiodget_nhits)
    - [ucnperiod.is_pileup](#ucnperiodis_pileup)
    - [ucnperiod.modify_timing](#ucnperiodmodify_timing)

## ucnperiod

[Show source in ucnperiod.py:14](../ucndata/ucnperiod.py#L14)

Stores the data from a single UCN period from a single cycle

#### Arguments

- `ucycle` *ucncycle* - object to pull period from
- `period` *int* - period number

#### Signature

```python
class ucnperiod(ucnbase):
    def __init__(self, ucycle, period): ...
```

#### See also

- [ucnbase](./ucnbase.md#ucnbase)

### ucnperiod.__repr__

[Show source in ucnperiod.py:61](../ucndata/ucnperiod.py#L61)

Return a human-readable string listing all public attributes in columns.

The column count is derived from the current terminal width. The header
line includes the run number, cycle index, and period index.

#### Returns

- `str` - formatted multi-column attribute listing, e.g.
    ``"run 1846 (cycle 0, period 1):\n  attr1  attr2  ..."``.

#### Signature

```python
def __repr__(self): ...
```

### ucnperiod.get_nhits

[Show source in ucnperiod.py:134](../ucndata/ucnperiod.py#L134)

Get the total number of UCN hits recorded in this period.

Delegates to the parent run's ``_get_nhits`` with this cycle and period
index. See that method for full caching and performance details.

#### Arguments

- `detector` *str* - detector to query — ``'Li6'`` or ``'He3'``.
- `bin_ms` *int* - hit-event time resolution in milliseconds.
    When 0, raw hit timestamps are used for maximum precision and a
    per-period histogram is cached keyed on the current period
    boundaries. When > 0, a fixed-bin histogram of that width is
    built and reused across repeated calls with the same value,
    which is faster when period timings are modified frequently.

#### Returns

- `int` - total number of UCN hit events in this period.

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
>>> period = run[0, 1]
>>> period.get_nhits('Li6')
1204
>>> period.get_nhits('He3', bin_ms=100)
1197
```

#### Signature

```python
def get_nhits(self, detector, bin_ms=0): ...
```

### ucnperiod.is_pileup

[Show source in ucnperiod.py:99](../ucndata/ucnperiod.py#L99)

Check if pileup may be an issue in this period.

Histograms the first `pileup_within_first_s` seconds of data in 1 ms bins and checks if any of those bins are greater than the `pileup_cnt_per_ms` threshold.

#### Arguments

- `detector` *str* - one of the keys to ucndata.DET_NAMES

#### Returns

- `bool` - true if pileup detected

#### Examples

```python
>>> p = run[0, 0]
>>> p.is_pileup('Li6')
False
```

#### Signature

```python
def is_pileup(self, detector): ...
```

### ucnperiod.modify_timing

[Show source in ucnperiod.py:181](../ucndata/ucnperiod.py#L181)

Change the start and/or end time of this period.

Adjusts ``period_start`` by ``dt_start_s`` and ``period_stop`` by
``dt_stop_s``, then propagates the change back into the parent run via
``ucnrun._modify_ptiming`` so that the run-level ``cycle_param`` and
the [tsubfile](./tsubfile.md#tsubfile) window stay consistent.

#### Arguments

- `dt_start_s` *float* - seconds to add to the period start time.
    Negative values move the boundary earlier.
- `dt_stop_s` *float* - seconds to add to the period stop time.
    Negative values move the boundary earlier.

#### Returns

None

#### Notes

* Adjacent periods are forced to remain contiguous (no overlap,
  no gap), so changing one boundary shifts the neighbouring period
  boundary accordingly.
* The cycle end time cannot be changed; only the cycle start time
  can be shifted (by adjusting period 0's start).
* All cached hit histograms are reset after the timing change.

#### Examples

```python
>>> period = run[0, 1]
>>> period.modify_timing(dt_start_s=2.0, dt_stop_s=-1.0)
```

#### Signature

```python
def modify_timing(self, dt_start_s=0, dt_stop_s=0): ...
```