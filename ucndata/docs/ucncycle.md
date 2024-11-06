# ucncycle

[Ucndata Index](./README.md#ucndata-index) / ucncycle

> Auto-generated documentation for [ucncycle](../../ucncycle.py) module.

- [ucncycle](#ucncycle)
  - [ucncycle](#ucncycle-1)
    - [ucncycle.check_data](#ucncyclecheck_data)
    - [ucncycle.get_counts](#ucncycleget_counts)
    - [ucncycle.get_period](#ucncycleget_period)
    - [ucncycle.get_rate](#ucncycleget_rate)

## ucncycle

[Show source in ucncycle.py:24](../../ucncycle.py#L24)

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

[Show source in ucncycle.py:108](../../ucncycle.py#L108)

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

If production period specified:

* beam data exists during production
* beam doesn't drop too low (`beam_min_current`)
* beam current stable (`beam_max_current_std`)

If background period specified:

* background count rate too high (`max_bkgd_count_rate`)
* no background counts at all

If count period specified:

* check too few counts (`min_total_counts`)
* does pileup exist? (>`pileup_cnt_per_ms` in the first `pileup_within_first_s`)

#### Examples

```python
>>> cycle = run[0]
>>> x = cycle.check_data(period_production=0)
Run 1846, cycle 0: Beam current dropped to 0.0 uA
>>> x
False
```

#### Signature

```python
def check_data(
    self,
    period_production=None,
    period_count=None,
    period_background=None,
    raise_error=False,
    quiet=False,
): ...
```

### ucncycle.get_counts

[Show source in ucncycle.py:243](../../ucncycle.py#L243)

Get counts for a/each period

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES
- `period` *None|int* - if None get for entire cycle
                    elif < 0 get for each period
                    elif >=0 get for that period
- `bkgd` *float|None* - background counts
- `dbkgd(float|None)` - error in background counts
- `norm` *float|None* - normalize to this value
- `dnorm` *float|None* - error in normalization

#### Returns

- `tuple` - (value, error) number of hits

#### Examples

```python
>>> cycle = run[0]

# counts for full cycle
>>> cycle.get_counts('Li6')
(25397, np.float64(159.3643623900902))

# counts for all periods
>>> cycle.get_counts('Li6', -1)
(array([  352,     5, 24720]),
 array([ 18.76166304,   2.23606798, 157.22595206]))

# counts for single period (in this case period 0)
>>> cycle.get_counts('Li6', 0)
(np.int64(352), np.float64(18.76166303929372))
```

#### Signature

```python
def get_counts(
    self, detector, period=None, bkgd=None, dbkgd=None, norm=None, dnorm=None
): ...
```

### ucncycle.get_period

[Show source in ucncycle.py:325](../../ucncycle.py#L325)

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

### ucncycle.get_rate

[Show source in ucncycle.py:361](../../ucncycle.py#L361)

Get count rate for each period

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES
- `bkgd` *float|None* - background counts
- `dbkgd(float|None)` - error in background counts
- `norm` *float|None* - normalize to this value
- `dnorm` *float|None* - error in normalization

#### Returns

- [applylist](./applylist.md#applylist) - count rate each period and error
    [(period0_value, period0_error),
     (period1_value, period1_error),
     ...
    ]

#### Examples

```python
>>> cycle = run[0]
>>> cycle.get_rate('Li6')
[(np.float64(5.783333333333333), np.float64(0.3104656001699526)),
 (np.float64(4.0), np.float64(1.4142135623730951)),
 (np.float64(247.07), np.float64(1.5718460484411316))]
```

#### Signature

```python
def get_rate(self, detector, bkgd=None, dbkgd=None, norm=None, dnorm=None): ...
```