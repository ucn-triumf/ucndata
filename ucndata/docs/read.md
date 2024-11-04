# Read

[Ucndata Index](./README.md#ucndata-index) / Read

> Auto-generated documentation for [read](../read.py) module.

- [Read](#read)
  - [read](#read)

## read

[Show source in read.py:16](../read.py#L16)

Read out single or multiple UCN run files from ROOT

#### Arguments

- `path` *str|list* - path to file, may include wildcards
    may be a list of paths which may include wildcards
    OR list of ints to specify run numbers
    OR list of mixed ints and strings either of run numbers or of the format 'x+y' to denote merged runs, where x and y are ints
- `as_dataframe` *bool* - if true, convert to dataframes
- `nproc` *int* - number of processors used in read. If <= 0, use total - nproc. If > 0 use nproc.
- `header_only` *bool* - if true, read only the header

#### Examples

```python
# example with run numbers
runs = read([1846, 1847, 1848])

# example with wildcards
runs = read('/path/datadir/ucn_run_000018*')

# example with merged runs and mixed types
runs = read([1846, '1847+1848', '1849', '/path/datadir/ucn_run_0000185*'])
```

#### Returns

- [applylist](./applylist.md#applylist) - sorted by run number, contains ucnrun objects

#### Signature

```python
def read(path, as_dataframe=True, nproc=-1, header_only=False): ...
```