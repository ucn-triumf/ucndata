# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../../ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.get_nhits](#ucnperiodget_nhits)
    - [ucnperiod.is_pileup](#ucnperiodis_pileup)

## ucnperiod

[Show source in ucnperiod.py:13](../../ucnperiod.py#L13)

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

[Show source in ucnperiod.py:113](../../ucnperiod.py#L113)

Get number of ucn hits

#### Arguments

- `detector` *str* - Li6|He3

#### Signature

```python
def get_nhits(self, detector): ...
```

### ucnperiod.is_pileup

[Show source in ucnperiod.py:75](../../ucnperiod.py#L75)

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