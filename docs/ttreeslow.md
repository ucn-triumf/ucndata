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

Unified interface to multiple EPICS slow-control ROOT trees.

Merges several rootloader.ttree objects (e.g. BeamlineEpics, UCN2Epics)
into a single object so callers can access any column without knowing
which underlying tree it lives in. Aggregate statistics (mean, min, max,
std, rms) concatenate results across all trees into a single pd.Series.

#### Attributes

- `_columns` *dict* - maps column name to the source tree name
- `_treenames` *list* - names of all underlying trees
- `_parent` - ucnrun/ucncycle/ucnperiod object that owns the tfile

#### Examples

```python
>>> # Access any EPICS column without specifying the source tree
>>> run.epics.UCN_UGD_ISOCP_RDVOL.mean()
>>> run.epics.mean.  # aggregate mean across all EPICS trees
```

#### Signature

```python
class ttreeslow(ttree):
    def __init__(self, ttree_list, parent=None): ...
```

### ttreeslow.__getitem__

[Show source in ttreeslow.py:78](../ucndata/ttreeslow.py#L78)

Return the data series for a single column from its source tree.

#### Arguments

- `key` *str* - column name to retrieve

#### Returns

- `pd.Series` - time-indexed series for the requested column

#### Signature

```python
def __getitem__(self, key): ...
```

### ttreeslow.columns

[Show source in ttreeslow.py:178](../ucndata/ttreeslow.py#L178)

list[str]: all column names available across all underlying trees.

#### Signature

```python
@property
def columns(self): ...
```

### ttreeslow.filters

[Show source in ttreeslow.py:188](../ucndata/ttreeslow.py#L188)

dict: mapping of tree name to its current filter expression.

#### Signature

```python
@property
def filters(self): ...
```

### ttreeslow.hist1d

[Show source in ttreeslow.py:89](../ucndata/ttreeslow.py#L89)

Return a 1D histogram of a column's data.

#### Arguments

- `column` *str* - column name to histogram; required when the object
    contains more than one column
- `nbins` *int* - number of equally-spaced bins spanning the full data
    range; mutually exclusive with step and edges
- `step` *float* - bin width in data units, spanning the full range;
    mutually exclusive with nbins and edges
- `edges` *array-like* - explicit bin-edge array; mutually exclusive with
    nbins and step

#### Returns

- `rootloader.th1` - histogram object

#### Raises

- `KeyError` - if column is not specified when there are multiple columns,
    or if the specified column does not exist

#### Examples

```python
>>> h = run.epics.hist1d('UCN_UGD_ISOCP_RDVOL', nbins=50)
```

#### Signature

```python
def hist1d(self, column=None, nbins=None, step=None, edges=None): ...
```

### ttreeslow.index

[Show source in ttreeslow.py:193](../ucndata/ttreeslow.py#L193)

dict: mapping of tree name to its current index (pd.Index).

#### Signature

```python
@property
def index(self): ...
```

### ttreeslow.index_name

[Show source in ttreeslow.py:198](../ucndata/ttreeslow.py#L198)

dict: mapping of tree name to its index column name string.

#### Signature

```python
@property
def index_name(self): ...
```

### ttreeslow.max

[Show source in ttreeslow.py:227](../ucndata/ttreeslow.py#L227)

Return the column-wise maximum across all underlying trees.

#### Returns

- `pd.Series` - maximum value for each column, indexed by column name

#### Examples

```python
>>> run.epics.max()
```

#### Signature

```python
def max(self): ...
```

### ttreeslow.mean

[Show source in ttreeslow.py:203](../ucndata/ttreeslow.py#L203)

Return the column-wise mean across all underlying trees.

#### Returns

- `pd.Series` - mean value for each column, indexed by column name

#### Examples

```python
>>> run.epics.mean()
```

#### Signature

```python
def mean(self): ...
```

### ttreeslow.min

[Show source in ttreeslow.py:215](../ucndata/ttreeslow.py#L215)

Return the column-wise minimum across all underlying trees.

#### Returns

- `pd.Series` - minimum value for each column, indexed by column name

#### Examples

```python
>>> run.epics.min()
```

#### Signature

```python
def min(self): ...
```

### ttreeslow.reset

[Show source in ttreeslow.py:126](../ucndata/ttreeslow.py#L126)

Reset all underlying trees and return a fresh ttreeslow copy.

Calls reset.on each source tree (clearing any cached data or filters)
and then constructs a new ttreeslow with the same column mapping.

#### Returns

- [ttreeslow](#ttreeslow) - new instance wrapping the reset trees

#### Examples

```python
>>> run.epics.set_filter('timestamp > 1000')
>>> clean = run.epics.reset. # filters cleared
```

#### Signature

```python
def reset(self): ...
```

### ttreeslow.rms

[Show source in ttreeslow.py:239](../ucndata/ttreeslow.py#L239)

Return the column-wise root-mean-square across all underlying trees.

#### Returns

- `pd.Series` - RMS value for each column, indexed by column name

#### Examples

```python
>>> run.epics.rms()
```

#### Signature

```python
def rms(self): ...
```

### ttreeslow.set_filter

[Show source in ttreeslow.py:153](../ucndata/ttreeslow.py#L153)

Apply a row-selection filter to all underlying trees.

#### Arguments

- `expression` *str* - boolean expression string evaluated against each
    tree's columns (e.g. 'timestamp > 1000')
- `inplace` *bool* - must be True; non-inplace filtering on parent trees
    is not supported

#### Raises

- `RuntimeError` - if inplace is False

#### Examples

```python
>>> run.epics.set_filter('UCN_UGD_ISOCP_RDVOL > 0')
```

#### Signature

```python
def set_filter(self, expression, inplace=True): ...
```

### ttreeslow.set_index

[Show source in ttreeslow.py:144](../ucndata/ttreeslow.py#L144)

Set the index column on all underlying trees.

#### Arguments

- `column` *str* - name of the column to use as the row index

#### Signature

```python
def set_index(self, column): ...
```

### ttreeslow.std

[Show source in ttreeslow.py:251](../ucndata/ttreeslow.py#L251)

Return the column-wise standard deviation across all underlying trees.

#### Returns

- `pd.Series` - standard deviation for each column, indexed by column name

#### Examples

```python
>>> run.epics.std()
```

#### Signature

```python
def std(self): ...
```

### ttreeslow.treenames

[Show source in ttreeslow.py:183](../ucndata/ttreeslow.py#L183)

np.ndarray: unique names of the underlying source trees.

#### Signature

```python
@property
def treenames(self): ...
```