# Datetime

[Ucndata Index](./README.md#ucndata-index) / Datetime

> Auto-generated documentation for [datetime](../datetime.py) module.

- [Datetime](#datetime)
  - [from_datetime](#from_datetime)
  - [to_datetime](#to_datetime)

## from_datetime

[Show source in datetime.py:9](../datetime.py#L9)

Convert to epoch time

#### Arguments

- `item` *pd.DataFrame|iterable* - if dataframe, convert the index, else convert the array

#### Returns

pd.DataFrame|np.array

#### Signature

```python
def from_datetime(item): ...
```



## to_datetime

[Show source in datetime.py:47](../datetime.py#L47)

Convert to datetime objects

#### Arguments

- `item` *pd.DataFrame|iterable* - if dataframe, convert the index, else convert the array

#### Returns

pd.DataFrame|np.array

#### Signature

```python
def to_datetime(item): ...
```