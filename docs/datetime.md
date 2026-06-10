# Datetime

[Ucndata Index](./README.md#ucndata-index) / Datetime

> Auto-generated documentation for [datetime](../ucndata/datetime.py) module.

- [Datetime](#datetime)
  - [from_datetime](#from_datetime)
  - [to_datetime](#to_datetime)

## from_datetime

[Show source in datetime.py:9](../ucndata/datetime.py#L9)

Convert datetime-indexed data back to integer Unix epoch timestamps.

Accepts either a DataFrame/Series (converts its index) or any iterable of
datetime-like values. Timezone-aware inputs are converted to UTC first;
naive inputs are treated as UTC. The result is truncated to whole seconds.

#### Arguments

- `item` *pd.DataFrame|pd.Series|iterable* - data to convert. If a
    DataFrame or Series, the index is replaced with epoch integers and
    the original object is returned; otherwise an array of integers is
    returned.

#### Returns

- `pd.DataFrame|pd.Series|np.ndarray` - input with index (or values)
    replaced by integer Unix epoch timestamps (seconds since 1970-01-01
    UTC).

#### Examples

```python
>>> run = ucnrun(1846)
>>> df = to_datetime(run.tfile.BeamlineEpics.to_dataframe.
>>> df2 = from_datetime(df)
>>> df2
            B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                       ...
1572460997          0.018750           0.00000  ...                  0.0        0.000000
1572461002          0.000000           0.01875  ...                  0.0        2.151400
...
```

```python
>>> all(df2.index == run.tfile.BeamlineEpics.index)
np.True_
```

#### Signature

```python
def from_datetime(item): ...
```



## to_datetime

[Show source in datetime.py:70](../ucndata/datetime.py#L70)

Convert Unix epoch timestamps to timezone-aware datetime objects.

Accepts either a DataFrame/Series (converts its index) or any iterable of
numeric epoch values. Timestamps are interpreted as seconds since
1970-01-01 UTC and then converted to the requested timezone.

#### Arguments

- `item` *pd.DataFrame|pd.Series|iterable* - data to convert. If a
    DataFrame or Series, the index is replaced with datetime values and
    the original object is returned; otherwise an array of datetime
    values is returned.
- `timezone` *str* - IANA timezone name for the output timestamps. Defaults
    to 'America/Vancouver'.

#### Returns

- `pd.DataFrame|pd.Series|pd.DatetimeIndex` - input with index (or values)
    replaced by timezone-aware datetime objects.

#### Examples

```python
>>> run = ucnrun(1846)
>>> to_datetime(run.tfile.BeamlineEpics.to_dataframe.
                   B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                                      ...
2019-10-30 11:43:17-07:00          0.018750           0.00000  ...                  0.0        0.000000
2019-10-30 11:43:22-07:00          0.000000           0.01875  ...                  0.0        2.151400
...
```

```python
>>> to_datetime([1572460997, 1572461002], timezone='UTC')
DatetimeIndex(['2019-10-30 18:43:17+00:00', '2019-10-30 18:43:22+00:00'],
              dtype='datetime64[ns, UTC]', freq=None)
```

#### Signature

```python
def to_datetime(item, timezone="America/Vancouver"): ...
```