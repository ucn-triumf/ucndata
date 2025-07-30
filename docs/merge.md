# Merge

[Ucndata Index](./README.md#ucndata-index) / Merge

> Auto-generated documentation for [merge](../../merge.py) module.

- [Merge](#merge)
  - [merge](#merge)
  - [merge_inlist](#merge_inlist)

## merge

[Show source in merge.py:13](../../merge.py#L13)

Merge a list of ucndata objects into a single object

#### Arguments

- `ucnlist` *list* - iterable of ucndata objects

#### Examples

```python
>>> merge([ucnrun(i) for i in (1846, 1847)])
```

#### Returns

- [ucnrun](./ucnrun.md#ucnrun) - single object with all data inside of it

#### Signature

```python
def merge(ucnlist): ...
```



## merge_inlist

[Show source in merge.py:194](../../merge.py#L194)

Merge runs within a list and return a new list with the merged objects

#### Arguments

- `ucnlist` *list* - iterable of ucndata objects
- `mergeruns` *list* - iterable of run numbers to merge

#### Examples

```python
>>> x = [ucnrun(r) for r in (1846, 1847, 1848)]
>>> y = merge_inlist(x, (1846, 1847))
    # y now contains two entries: merged 1846+1847 and 1848
```

#### Returns

- [applylist](./applylist.md#applylist) - of ucnruns, some are merged, as indicated

#### Signature

```python
def merge_inlist(ucnlist, mergeruns): ...
```