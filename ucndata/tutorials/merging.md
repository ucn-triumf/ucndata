# Merging Runs

[**Back to Index**](index.md)\
[**Next page: Examples**](examples.md)

## Table of Contents

- [Merging Runs](#merging-runs)
  - [Table of Contents](#table-of-contents)
  - [Brief Examples](#brief-examples)
    - [Merging directly](#merging-directly)
    - [Merging in a list](#merging-in-a-list)
  - [Merging behaviour](#merging-behaviour)

---

Merging is useful if two runs should be treated as if they were the same. For example, if a run is stopped early due to some issue, then restarted once that issue was resolved.

The `ucndata` package provides two functions to help with this:

* [merge]
* [merge_inlist]

The first does the actual merging, whereas the second is a convenience function which merges [ucnrun] items in a list, then returns a new list with that merged run.

## Brief Examples

### Using Read to merge runs

This is perhaps the easiest manner to merge runs. Simply use a `+` between the run number you want to merge as in the following example:

```python
from ucndata import read

# read two runs and merge them
runs = read('1846+1847')

# read a list of runs, some of which are merged, extra spaces are ignored
runs = read([1845, '1846 +1847', '1848'])
```

### Merging directly

First let's load the data and merge, assuming the data is on the default path in settings:
```python
from ucndata import read, merge

runs = read([1846, 1847, 1848])
merged_run = merge(runs)
```

If we run this, we can see that the result shows the runs merged:
```python
>>> merged_run
run 1846+1847+1848:
  comment            month              shifters           tfile
  cycle_param        run_number         start_time         year
  experiment_number  run_title          stop_time
```

### Merging in a list

Lets say we have a list and we don't want to merge all of the files. Here's the example script:
```python
from ucndata import read, merge_inlist

runs = read([1846, 1847, 1848, 1850, 1851, 1853])
merged_runs = merge_inlist(runs, [1847, 1848, 1850])
```

Lets inspect what we have done:

```python
# First let us look at the run numbers in runs, which is in the unmerged state
# Remember that runs is an applylist so this can be done in the following way
>>> runs.run_number
[1846, 1847, 1848, 1850, 1851, 1853]

# In the merged list we see that one run has an array of run numbers, this is the merged run
>>> merged_runs.run_number
[1846, array([1847, 1848, 1850]), 1851, 1853]
```

## Merging behaviour

When merging, runs are first sorted by `run_number`, assuming that this quantity also sorts them in time. Contents which are lists are then concatenated in this order. For `merge_inlist`, the contents of the returned [applylist] are sorted by run number, with the lowest run number acting as the sorting key for the merged run.

Here are the specifics on how the runs are merged, using the `merged_run` object from the [above example](#merging-directly).

#### Header

For the most part, header items are concatenated into a list. For example:

```python
>>> merged_run.comment
array(['Source Storage Lifetime 3rd try',
       'Storage Lifetime between I2 and IV3, IV3 production',
       'Storage Lifetime between I2 and IV3, IV3 production'],
      dtype='<U51')
```

There are a few exceptions.

* `run_number`: becomes a string of the format `run1+run2+...`
* `experiment_number`: if all the same, then just keep the experiment number the same. Otherwise, concatenate with `+` as with the `run_number`
* `cycle_param`: see next section

#### Cycle Parameters

The `cycle_param` dictionary is merged in the following way ([recall the definitions of its entries](./gettingstarted.md#cycle_param)):

* `nperiods`: summed
* `nsupercyc`: summed
* `enable`: if any are `True` then `True`, else `False`. But you probably shouldn't merge runs with mixed sequencer states.
* `inf_cyc_enable`: Same as `enable`
* `cycle`: [concatenated] and [re-indexed]
* `supercycle`: [concatenated] and [re-indexed]
* `valve_states`: Only the value from the first run is kept. A warning is raised if they do not all match.
* `period_end_times`: [concatenated] along the column axis and [re-indexed]
* `period_durations_s`: [concatenated] along the column axis and [re-indexed]
* `ncycles`: summed
* `filter`: [concatenated]
* `cycle_times`: [concatenated] along the index axis and [re-indexed]

#### tfile

Items in the [tfile] object are merged according to their type which can be one of: [ttree], [th1], or [th2]. In all cases, these objects are first converted to pandas [DataFrame]s and [concatenated].

* **[ttree]**: a copy of the concatenated [ttree] [DataFrame] is simply saved to the [tfile].
* **[th1]**:
  * Histogram counts are summed according to their bin (only counts in matching bins are summed)
  * Errors are summed in quadrature, according to their bin
  * `sum` and `entires` properties are summed
  * `name`, `title`, `xlabel`, `ylabel`, `base_class`, `nbins` are kept from the first merged run
* **[th2]**
  * Similar to [th1] but both x and y bins must match

Note that these objects are not converted back, but left as [DataFrame]s, since it is often preferential to work with these objects.



[**Back to Index**](index.md)\
[**Next page: Examples**](examples.md)

[concatenated]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.concat.html#pandas.concat
[re-indexed]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.reset_index.html
[tfile]: ./gettingstarted.md#tfile
[DataFrame]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
[ttree]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md
[th1]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/th1.md
[th2]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/th2.md
[attrdict]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/attrdict.md
[rootloader]: https://github.com/ucn-triumf/rootloader
[ucnrun]: ../docs/ucnrun.md
[ucncycle]: ../docs/ucncycle.md
[ucnperiod]: ../docs/ucnperiod.md
[applylist]: ../docs/applylist.md
[read]: ../docs/read.md
[merge]: ../docs/merge.md#merge
[merge_inlist]: ../docs/merge.md#merge_inlist