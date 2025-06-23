# hitstree

[Ucndata Index](./README.md#ucndata-index) / hitstree

> Auto-generated documentation for [hitstree](../../hitstree.py) module.

- [hitstree](#hitstree)
  - [hitstree](#hitstree-1)
    - [hitstree.__getitem__](#hitstree__getitem__)
    - [hitstree.columns](#hitstreecolumns)
    - [hitstree.filters](#hitstreefilters)
    - [hitstree.get_hits_histogram](#hitstreeget_hits_histogram)
    - [hitstree.index](#hitstreeindex)
    - [hitstree.index_name](#hitstreeindex_name)
    - [hitstree.loc](#hitstreeloc)
    - [hitstree.max](#hitstreemax)
    - [hitstree.mean](#hitstreemean)
    - [hitstree.min](#hitstreemin)
    - [hitstree.reset_columns](#hitstreereset_columns)
    - [hitstree.rms](#hitstreerms)
    - [hitstree.set_filter](#hitstreeset_filter)
    - [hitstree.set_filter_isucn](#hitstreeset_filter_isucn)
    - [hitstree.set_index](#hitstreeset_index)
    - [hitstree.size](#hitstreesize)
    - [hitstree.std](#hitstreestd)
    - [hitstree.to_dataframe](#hitstreeto_dataframe)

## hitstree

[Show source in hitstree.py:13](../../hitstree.py#L13)

Extract ROOT.TTree with lazy operation. Looks like a dataframe in most ways

#### Arguments

- `tree` *str|hitstree* - tree to load
- `filter_string` *str|None* - if not none then pass this to [`RDataFrame.Filter`](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0)
- `columns` *list|None* - list of column names to include in fetch, if None, get all

#### Signature

```python
class hitstree(object):
    def __init__(self, tree, filename=None): ...
```

### hitstree.__getitem__

[Show source in hitstree.py:73](../../hitstree.py#L73)

Fetch a new dataframe with fewer 'columns', as a memory view

#### Signature

```python
def __getitem__(self, key): ...
```

### hitstree.columns

[Show source in hitstree.py:175](../../hitstree.py#L175)

#### Signature

```python
@property
def columns(self): ...
```

### hitstree.filters

[Show source in hitstree.py:178](../../hitstree.py#L178)

#### Signature

```python
@property
def filters(self): ...
```

### hitstree.get_hits_histogram

[Show source in hitstree.py:127](../../hitstree.py#L127)

Return histogram of hit times

#### Arguments

- `nbins` *int* - number of bins, span full range
- `step` *float* - bin spacing, span full range

Pick one or the other

#### Returns

- `np.array` - array of size 2 (bin centers, weights)

#### Signature

```python
def get_hits_histogram(self, nbins=None, step=None): ...
```

### hitstree.index

[Show source in hitstree.py:181](../../hitstree.py#L181)

#### Signature

```python
@property
def index(self): ...
```

### hitstree.index_name

[Show source in hitstree.py:184](../../hitstree.py#L184)

#### Signature

```python
@property
def index_name(self): ...
```

### hitstree.loc

[Show source in hitstree.py:187](../../hitstree.py#L187)

#### Signature

```python
@property
def loc(self): ...
```

### hitstree.max

[Show source in hitstree.py:206](../../hitstree.py#L206)

#### Signature

```python
def max(self): ...
```

### hitstree.mean

[Show source in hitstree.py:211](../../hitstree.py#L211)

#### Signature

```python
def mean(self): ...
```

### hitstree.min

[Show source in hitstree.py:201](../../hitstree.py#L201)

#### Signature

```python
def min(self): ...
```

### hitstree.reset_columns

[Show source in hitstree.py:153](../../hitstree.py#L153)

Include all columns again

#### Signature

```python
def reset_columns(self): ...
```

### hitstree.rms

[Show source in hitstree.py:216](../../hitstree.py#L216)

#### Signature

```python
def rms(self): ...
```

### hitstree.set_filter

[Show source in hitstree.py:162](../../hitstree.py#L162)

#### Signature

```python
def set_filter(self, expression): ...
```

### hitstree.set_filter_isucn

[Show source in hitstree.py:123](../../hitstree.py#L123)

Filter on tIsUCN==1

#### Signature

```python
def set_filter_isucn(self): ...
```

### hitstree.set_index

[Show source in hitstree.py:157](../../hitstree.py#L157)

#### Signature

```python
def set_index(self, column): ...
```

### hitstree.size

[Show source in hitstree.py:190](../../hitstree.py#L190)

#### Signature

```python
@property
def size(self): ...
```

### hitstree.std

[Show source in hitstree.py:221](../../hitstree.py#L221)

#### Signature

```python
def std(self): ...
```

### hitstree.to_dataframe

[Show source in hitstree.py:167](../../hitstree.py#L167)

Return pandas dataframe of the data

#### Signature

```python
def to_dataframe(self): ...
```