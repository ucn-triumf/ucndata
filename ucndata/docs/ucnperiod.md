# ucnperiod

[Ucndata Index](./README.md#ucndata-index) / ucnperiod

> Auto-generated documentation for [ucnperiod](../../ucnperiod.py) module.

- [ucnperiod](#ucnperiod)
  - [ucnperiod](#ucnperiod-1)
    - [ucnperiod.get_counts](#ucnperiodget_counts)
    - [ucnperiod.get_rate](#ucnperiodget_rate)
    - [ucnperiod.is_pileup](#ucnperiodis_pileup)

## ucnperiod

[Show source in ucnperiod.py:22](../../ucnperiod.py#L22)

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

### ucnperiod.get_counts

[Show source in ucnperiod.py:84](../../ucnperiod.py#L84)

Get sum of ucn hits

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES
- `bkgd` *float|None* - background counts
- `dbkgd(float|None)` - error in background counts
- `norm` *float|None* - normalize to this value
- `dnorm` *float|None* - error in normalization

#### Returns

- `tuple` - (count, error) number of hits

#### Examples

```python
>>> p = run[0,0]
>>> p.get_counts('Li6')
(347, np.float64(18.627936010197157))
```

#### Signature

```python
def get_counts(self, detector, bkgd=None, dbkgd=None, norm=None, dnorm=None): ...
```

### ucnperiod.get_rate

[Show source in ucnperiod.py:191](../../ucnperiod.py#L191)

Get sum of ucn hits per unit time of period

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES
- `bkgd` *float|None* - background counts
- `dbkgd(float|None)` - error in background counts
- `norm` *float|None* - normalize to this value
- `dnorm` *float|None* - error in normalization

#### Returns

- `tuple` - (count rate, error)

#### Examples

```python
>>> p = run[0,0]
>>> p.get_rate('Li6')
(np.float64(5.783333333333333), np.float64(0.3104656001699526))
```

#### Signature

```python
def get_rate(self, detector, bkgd=None, dbkgd=None, norm=None, dnorm=None): ...
```

### ucnperiod.is_pileup

[Show source in ucnperiod.py:153](../../ucnperiod.py#L153)

Check if pileup may be an issue in this period.

Histograms the first `pileup_within_first_s` seconds of data in 1 ms bins and checks if any of those bins are greater than the `pileup_cnt_per_ms` threshold. Set these settings in the [settings.py](../settings.py) file.

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES

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