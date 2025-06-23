# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../../ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.is_pileup](#ucnperiodis_pileup)

## ucnperiod

[Show source in ucnperiod.py:21](../../ucnperiod.py#L21)

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

### ucnperiod.is_pileup

[Show source in ucnperiod.py:83](../../ucnperiod.py#L83)

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