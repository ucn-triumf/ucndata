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
    - [ttreeslow.max](#ttreeslowmax)
    - [ttreeslow.mean](#ttreeslowmean)
    - [ttreeslow.min](#ttreeslowmin)
    - [ttreeslow.reset](#ttreeslowreset)
    - [ttreeslow.rms](#ttreeslowrms)
    - [ttreeslow.set_filter](#ttreeslowset_filter)
    - [ttreeslow.set_index](#ttreeslowset_index)
    - [ttreeslow.std](#ttreeslowstd)
    - [ttreeslow.treenames](#ttreeslowtreenames)

## ttreeslow

[Show source in ttreeslow.py:9](../ucndata/ttreeslow.py#L9)

#### Signature

```python
class ttreeslow(ttree):
    def __init__(self, ttree_list, parent=None): ...
```

### ttreeslow.__getitem__

[Show source in ttreeslow.py:45](../ucndata/ttreeslow.py#L45)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### ttreeslow.columns

[Show source in ttreeslow.py:97](../ucndata/ttreeslow.py#L97)

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

[Show source in ttreeslow.py:49](../ucndata/ttreeslow.py#L49)

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
def hist1d(self, column=None, nbins=None, step=None, edges=None): ...
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

### ttreeslow.max

[Show source in ttreeslow.py:119](../ucndata/ttreeslow.py#L119)

#### Signature

```python
def max(self): ...
```

### ttreeslow.mean

[Show source in ttreeslow.py:113](../ucndata/ttreeslow.py#L113)

#### Signature

```python
def mean(self): ...
```

### ttreeslow.min

[Show source in ttreeslow.py:116](../ucndata/ttreeslow.py#L116)

#### Signature

```python
def min(self): ...
```

### ttreeslow.reset

[Show source in ttreeslow.py:75](../ucndata/ttreeslow.py#L75)

Make a new set of trees

#### Signature

```python
def reset(self): ...
```

### ttreeslow.rms

[Show source in ttreeslow.py:122](../ucndata/ttreeslow.py#L122)

#### Signature

```python
def rms(self): ...
```

### ttreeslow.set_filter

[Show source in ttreeslow.py:86](../ucndata/ttreeslow.py#L86)

Set a filter on the dataframe to select a subset of the data

#### Signature

```python
def set_filter(self, expression, inplace=True): ...
```

### ttreeslow.set_index

[Show source in ttreeslow.py:81](../ucndata/ttreeslow.py#L81)

Set the index column name

#### Signature

```python
def set_index(self, column): ...
```

### ttreeslow.std

[Show source in ttreeslow.py:125](../ucndata/ttreeslow.py#L125)

#### Signature

```python
def std(self): ...
```

### ttreeslow.treenames

[Show source in ttreeslow.py:100](../ucndata/ttreeslow.py#L100)

#### Signature

```python
@property
def treenames(self): ...
```