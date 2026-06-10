# tsubfile

[Ucndata Index](./README.md#ucndata-index) / tsubfile

> Auto-generated documentation for [tsubfile](../ucndata/tsubfile.py) module.

- [tsubfile](#tsubfile)
  - [tsubfile](#tsubfile-1)

## tsubfile

[Show source in tsubfile.py:10](../ucndata/tsubfile.py#L10)

Time-bounded wrapper around a rootloader.tfile object.

Acts like a tfile but silently filters any DataFrame or ttree whose index
is a time axis, returning only rows whose timestamp falls within [start, stop].
Non-time-indexed data is returned unchanged. Accessed values are cached in
the internal _items dict to avoid redundant filtering on repeated access.

#### Arguments

- `tfileobj` *tfile* - rootloader tfile object to wrap
- `start` *int* - inclusive start of the allowed epoch time range (seconds)
- `stop` *int* - inclusive end of the allowed epoch time range (seconds)

#### Examples

```python
>>> # Wrap an open run's tfile to the time window of one cycle
>>> sub = tsubfile(run.tfile, cycle_start, cycle_stop)
>>> sub['He3'].head()   # only rows within [cycle_start, cycle_stop]
```

#### Signature

```python
class tsubfile(tfile):
    def __init__(self, tfileobj, start, stop): ...
```