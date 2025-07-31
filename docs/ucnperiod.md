# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../ucndata/ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.get_nhits](#ucnperiodget_nhits)
    - [ucnperiod.get_start_edge](#ucnperiodget_start_edge)
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

[Show source in ucnperiod.py:114](../ucndata/ucnperiod.py#L114)

Get number of ucn hits

#### Arguments

- `detector` *str* - Li6|He3

#### Signature

```python
def get_nhits(self, detector): ...
```

### ucnperiod.get_start_edge

[Show source in ucnperiod.py:122](../ucndata/ucnperiod.py#L122)

Detect period start time based on a rising or falling edge

#### Arguments

- `detector` *str* - Li6|He3
- `thresh` *float* - calculate cycle start time shift based on edge detection passing through this level
- `bin_ms` *int* - histogram bin size in milliseconds
- `rising` *bool* - if true do rising edge, else do falling edge

#### Returns

- `float` - the change in the times in seconds, after applying the const_offset

#### Examples

```python
dt = [cyc[2].get_start_edge('Li6', 50) if cyc[2].period_dur > 0 else 0 for cyc in run]
```

#### Signature

```python
def get_start_edge(self, detector, thresh, bin_ms=10, rising=True): ...
```

### ucnperiod.is_pileup

[Show source in ucnperiod.py:76](../ucndata/ucnperiod.py#L76)

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

[Show source in ucnperiod.py:157](../ucndata/ucnperiod.py#L157)

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