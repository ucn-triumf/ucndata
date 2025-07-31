# ttreeslow

[Ucndata Index](./README.md#ucndata-index) / ttreeslow

> Auto-generated documentation for [ttreeslow](../ucndata/ttreeslow.py) module.

- [ttreeslow](#ttreeslow)
  - [ttreeslow](#ttreeslow-1)
    - [ttreeslow.__getitem__](#ttreeslow__getitem__)
    - [ttreeslow.columns](#ttreeslowcolumns)
    - [ttreeslow.filters](#ttreeslowfilters)
    - [ttreeslow.hist1d](#ttreeslowhist1d)
    - [ttreeslow.index](#ttreeslowindex)
    - [ttreeslow.index_name](#ttreeslowindex_name)
    - [ttreeslow.reset](#ttreeslowreset)
    - [ttreeslow.reset_columns](#ttreeslowreset_columns)
    - [ttreeslow.set_filter](#ttreeslowset_filter)
    - [ttreeslow.set_index](#ttreeslowset_index)
    - [ttreeslow.size](#ttreeslowsize)
    - [ttreeslow.to_dataframe](#ttreeslowto_dataframe)
    - [ttreeslow.to_dict](#ttreeslowto_dict)

## ttreeslow

[Show source in ttreeslow.py:7](../ucndata/ttreeslow.py#L7)

#### Signature

```python
class ttreeslow(ttree):
    def __init__(self, ttree_list): ...
```

### ttreeslow.__getitem__

[Show source in ttreeslow.py:27](../ucndata/ttreeslow.py#L27)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### ttreeslow.columns

[Show source in ttreeslow.py:100](../ucndata/ttreeslow.py#L100)

#### Signature

```python
@property
def columns(self): ...
```

### ttreeslow.filters

[Show source in ttreeslow.py:103](../ucndata/ttreeslow.py#L103)

#### Signature

```python
@property
def filters(self): ...
```

### ttreeslow.hist1d

[Show source in ttreeslow.py:31](../ucndata/ttreeslow.py#L31)

Return histogram of column

#### Arguments

- `column` *str* - column name, needed if more than one column
- `nbins` *int* - number of bins, span full range
- `step` *float* - bin spacing, span full range

Pick one or the other

#### Returns

rootloader.th1

#### Signature

```python
def hist1d(self, column=None, nbins=None, step=None): ...
```

### ttreeslow.index

[Show source in ttreeslow.py:106](../ucndata/ttreeslow.py#L106)

#### Signature

```python
@property
def index(self): ...
```

### ttreeslow.index_name

[Show source in ttreeslow.py:109](../ucndata/ttreeslow.py#L109)

#### Signature

```python
@property
def index_name(self): ...
```

### ttreeslow.reset

[Show source in ttreeslow.py:57](../ucndata/ttreeslow.py#L57)

Make a new set of trees

#### Signature

```python
def reset(self): ...
```

### ttreeslow.reset_columns

[Show source in ttreeslow.py:62](../ucndata/ttreeslow.py#L62)

Include all columns again

#### Signature

```python
def reset_columns(self): ...
```

### ttreeslow.set_filter

[Show source in ttreeslow.py:78](../ucndata/ttreeslow.py#L78)

Set a filter on the dataframe to select a subset of the data

#### Signature

```python
def set_filter(self, expression, inplace=False): ...
```

### ttreeslow.set_index

[Show source in ttreeslow.py:70](../ucndata/ttreeslow.py#L70)

Set the index column name

#### Signature

```python
def set_index(self, column): ...
```

### ttreeslow.size

[Show source in ttreeslow.py:112](../ucndata/ttreeslow.py#L112)

#### Signature

```python
@property
def size(self): ...
```

### ttreeslow.to_dataframe

[Show source in ttreeslow.py:88](../ucndata/ttreeslow.py#L88)

#### Signature

```python
def to_dataframe(self): ...
```

### ttreeslow.to_dict

[Show source in ttreeslow.py:91](../ucndata/ttreeslow.py#L91)

#### Signature

```python
def to_dict(self): ...
```