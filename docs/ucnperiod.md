# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../ucndata/ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.get_nhits](#ucnperiodget_nhits)
    - [ucnperiod.is_pileup](#ucnperiodis_pileup)
    - [ucnperiod.modify_timing](#ucnperiodmodify_timing)

## ucnperiod

[Show source in ucnperiod.py:13](../ucndata/ucnperiod.py#L13)

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

### ucnperiod.get_nhits

[Show source in ucnperiod.py:116](../ucndata/ucnperiod.py#L116)

Get number of ucn hits

#### Arguments

- `detector` *str* - Li6|He3

#### Returns

- `int` - number of events

#### Notes

Getting the hits requires that you parse the entire tree, so to
speed this up, a histogram is created where the bin edges are
set to the period and cycle start/end times. This histogram is
cached as `self._nhits` so future requests of the number of hits is
fast. However, if you modify the start/end times of the periods,
this histogram is no longer accurate and so must be recomputed.
This happens automatically, but rebuilding the histogram adds to
your runtime. Thus the following works, but is slow:

```python
hits = []
for cycle in run:
    cycle[1].modify_timing(1)
    hits.append(cycle[1].get_nhits('Li6')) // hits histogram recomputed every loop
```

Whereas the following is much faster but does the same thing:

```python
for cycle in run:
    cycle[1].modify_timing(1)
hits = run[:, 1].get_nhits('Li6') // hits histogram recomputed only once
```

#### Signature

```python
def get_nhits(self, detector): ...
```

### ucnperiod.is_pileup

[Show source in ucnperiod.py:78](../ucndata/ucnperiod.py#L78)

Check if pileup may be an issue in this period.

Histograms the first `pileup_within_first_s` seconds of data in 1 ms bins and checks if any of those bins are greater than the `pileup_cnt_per_ms` threshold.

#### Arguments

- `detector` *str* - one of the keys to self.DET_NAMES

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

[Show source in ucnperiod.py:152](../ucndata/ucnperiod.py#L152)

Change start and end times of period

#### Arguments

- `dt_start_s` *float* - change to the period start time
- `dt_stop_s` *float* - change to the period stop time

#### Notes

* as a result of this, cycles may overlap or have gaps
* periods are forced to not overlap and have no gaps
* cannot change cycle end time, but can change cycle start time
* this function resets all saved histgrams and hits

#### Signature

```python
def modify_timing(self, dt_start_s=0, dt_stop_s=0): ...
```