# Datetime

[Ucndata Index](./README.md#ucndata-index) / Datetime

> Auto-generated documentation for [datetime](../ucndata/datetime.py) module.

- [Datetime](#datetime)
  - [from_datetime](#from_datetime)
  - [to_datetime](#to_datetime)

## from_datetime

[Show source in datetime.py:9](../ucndata/datetime.py#L9)

Convert to epoch time

#### Arguments

- `item` *pd.DataFrame|iterable* - if dataframe, convert the index, else convert the array

#### Returns

pd.DataFrame|np.array

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
1572461007          0.021875           0.01250  ...                  0.0        2.151400
1572461012          0.012500           0.00000  ...                  0.0        2.151400
1572461017          0.000000           0.00000  ...                  0.0        2.151400
...                      ...               ...  ...                  ...             ...
1572466463          0.000000           0.01250  ...                  0.0       38.294899
1572466468          0.000000           0.00000  ...                  0.0       38.294899
1572466473          0.018750           0.00000  ...                  0.0       37.864700
1572466478          0.034375           0.00000  ...                  0.0       37.864700
1572466479          0.000000           0.01250  ...                  0.0       38.294899

[1093 rows x 49 columns]

# check that conversion worked
>>> all(df2.index == run.tfile.BeamlineEpics.index)
np.True_
```

#### Signature

```python
def from_datetime(item): ...
```



## to_datetime

[Show source in datetime.py:74](../ucndata/datetime.py#L74)

Convert to datetime objects

#### Arguments

- `item` *pd.DataFrame|iterable* - if dataframe, convert the index, else convert the array

#### Returns

pd.DataFrame|np.array

#### Examples

```python
>>> run = ucnrun(1846)
>>> to_datetime(run.tfile.BeamlineEpics.to_dataframe.
                   B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                                      ...
2019-10-30 11:43:17-07:00          0.018750           0.00000  ...                  0.0        0.000000
2019-10-30 11:43:22-07:00          0.000000           0.01875  ...                  0.0        2.151400
2019-10-30 11:43:27-07:00          0.021875           0.01250  ...                  0.0        2.151400
2019-10-30 11:43:32-07:00          0.012500           0.00000  ...                  0.0        2.151400
2019-10-30 11:43:37-07:00          0.000000           0.00000  ...                  0.0        2.151400
...                                     ...               ...  ...                  ...             ...
2019-10-30 13:14:23-07:00          0.000000           0.01250  ...                  0.0       38.294899
2019-10-30 13:14:28-07:00          0.000000           0.00000  ...                  0.0       38.294899
2019-10-30 13:14:33-07:00          0.018750           0.00000  ...                  0.0       37.864700
2019-10-30 13:14:38-07:00          0.034375           0.00000  ...                  0.0       37.864700
2019-10-30 13:14:39-07:00          0.000000           0.01250  ...                  0.0       38.294899

[1093 rows x 49 columns]
```

#### Signature

```python
def to_datetime(item): ...
```