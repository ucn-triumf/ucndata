# Loading Runs

[**Back to Index**](index.md)\
[**Next Page: Accessing Cycles and Periods**](cycandperiods.md)

---

## Run Specification

There are two main ways to specify which run to load:

1. Pass a filename
2. Pass a run number

The latter is convenient and useful for making readable analysis scripts:

```python
from ucndata import ucnrun

# we want to go from this:
run = ucnrun('/data3/ucn/root_files/ucn_run_00002050.root')

# to this:
run = ucnrun(2050)
```

The way to do this is to set the default path:

```python
from ucndata import ucnrun

# redefine class variable
ucnrun.datadir = '/data3/ucn/root_files'

# now this works
run = ucnrun(2050)
```

By default, the data directory is `/data3/ucn/root_files`, which should be the case on the `daq01.ucn.triumf.ca` and `daq04.ucn.triumf.ca` machines.

This automatically parallelizes the reading and should decrease runtimes significantly. By default this also converts all [tfile] entries to [DataFrame]s. This returns an [applylist] which allows for easy processing of files.

## Efficient Loading

We don't need to load all the data in the root file. This can slow the loading process by quite a bit. The `settings` file also defines the function `keyfilter` which tells the rootloader which objects to read into memory. The default is as follows:

```python
def keyfilter(name):
    """Don't load all the data in each file, only that which is needed"""

    name = name.replace(' ', '_').lower()

    # reject some keys based on partial matches
    reject_keys = ('v1725', 'v1720', 'v792', 'tv1725', 'charge', 'edge_diff',
                   'pulse_widths', 'iv2', 'iv3')
    for key in reject_keys:
        if key in name:
            return False

    return True
```

It takes as input the key name for a given tree or histogram and returns a boolean which determines if the object should be read out or not.

One can define this in the same way as with the data directory:

```python
from ucndata import ucnrun

# this function loads all the data in the file
ucnrun.keyfilter = lambda x: True
```

Note that by default empty trees and histograms are not loaded into memory.

---

[**Back to Index**](index.md)\
[**Next Page: Accessing Cycles and Periods**](cycandperiods.md)

[tfile]: gettingstarted.md#tfile
[DataFrame]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
[ttree]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md
[attrdict]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/attrdict.md
[rootloader]: https://github.com/ucn-triumf/rootloader
[ucnrun]: ../docs/ucnrun.md
[ucncycle]: ../docs/ucncycle.md
[ucnperiod]: ../docs/ucnperiod.md
[applylist]: ../docs/applylist.md
[read]: ../docs/read.md
[merge]: ../docs/merge.md
