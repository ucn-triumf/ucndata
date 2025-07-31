# applylist

[Ucndata Index](./README.md#ucndata-index) / applylist

> Auto-generated documentation for [applylist](../ucndata/applylist.py) module.

- [applylist](#applylist)
  - [applylist](#applylist-1)
    - [applylist.apply](#applylistapply)
    - [applylist.astype](#applylistastype)
    - [applylist.transpose](#applylisttranspose)

## applylist

[Show source in applylist.py:7](../ucndata/applylist.py#L7)

A list object with the following enhancements:

* An apply function: like in pandas, apply takes a function handle and applies it to every element in the list. This acts recursively, if the list has a depth of more than 1
* Element access: accessing attributes, if not an attribute of the applylist, instead try to fetch attributes of the contained objects. The same for functions. This also works recursively.
* Numpy-like array slicing: slicing with a np.ndarray first converts this object to an array, then does the slice, then converts back. This allows slicing on arrays of indices for re-ordering or booleans for selection based on criteria
* Arithmetic works element-wise as in numpy arrays

#### Examples

```python
>>> # Slicing
>>> x = applylist(range(10))
>>> print(x[3:7])
[3, 4, 5, 6]
```

```python
>>> # Element access
>>> x = applylist([ucnrun(1846), ucnrun(1847)])
>>> print(x.run_number)
[1846, 1847]
>>> print(x.beam_current_uA.mean.
[np.float64(0.16612837637441483), np.float64(0.18927602913972205)]
```

```python
>>> # Arithmetic and comparisons
>>> x = applylist([1,2,3])
>>> print(x*2)
[np.int64(2), np.int64(4), np.int64(6)]
>>> print(x>2)
[np.False_, np.False_, np.True_]
```

#### Signature

```python
class applylist(list): ...
```

### applylist.apply

[Show source in applylist.py:121](../ucndata/applylist.py#L121)

Apply function to each element contained, similar to pandas functionality

#### Arguments

fn (function handle): function to apply to each element
- `inplace` *bool* - if false return a copy, else act in-place

#### Returns

- `ucnarray|None` - depending on the value of inplace

#### Examples

```python
>>> # With return value
>>> x = applylist(np.arange(5))
>>> y = x.apply(lambda a: a**2)
>>> print(x)
[np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4)]
>>> print(y)
[np.int64(0), np.int64(1), np.int64(4), np.int64(9), np.int64(16)]
```

```python
>>> # Inplace
>>> x = applylist(np.arange(5))
>>> x.apply(lambda a: a**2, inplace=True)
>>> print(x)
[np.int64(0), np.int64(1), np.int64(4), np.int64(9), np.int64(16)]
```

#### Signature

```python
def apply(self, fn, inplace=False): ...
```

### applylist.astype

[Show source in applylist.py:100](../ucndata/applylist.py#L100)

Convert datatypes in self to typecast

#### Arguments

- `typecase` *type* - type to convert to

#### Returns

None, works in-place

#### Examples

```python
>>> x = applylist(np.arange(5))
>>> print(x)
[np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4)]
>>> x.astype(int)
>>> print(x)
[0, 1, 2, 3, 4]
```

#### Signature

```python
def astype(self, typecast): ...
```

### applylist.transpose

[Show source in applylist.py:162](../ucndata/applylist.py#L162)

Transpose by conversion to np.array and back

#### Arguments

None

#### Returns

- [applylist](#applylist) - transposed

#### Examples

```python
>>> x = applylist([[1,2,3], [4,5,6]])
>>> print(x)
[[1, 2, 3], [4, 5, 6]]
>>> print(x.transpose.
[array([1, 4]), array([2, 5]), array([3, 6])]
```

#### Signature

```python
def transpose(self): ...
```