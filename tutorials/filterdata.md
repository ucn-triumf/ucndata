# Filtering Data Events

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)

When you load a `ucnrun` the hits trees are stored as rootloader [ttree]. Under the hood, the data is accessed as a [RDataFrame](https://root.cern/doc/master/classROOT_1_1RDataFrame.html). Data can be selected in a custom way using filters. 

## Default Filters

When you load a run, the default filters are a sanity check on the timestamps and to select on UCN hits:

```python
from ucndata import ucnrun

# read a run - note that the ucn_only flag automatically applies a filter to the data to select only UCN hits
run = ucnrun(3200, ucn_only=True)

# let's check the filters on the Li6 hits tree
print(run.tfile.UCNHits_Li6.filters)
# output: ['tUnixTimePrecise > 15e8', 'tIsUCN>0']
```

When you do any operation on this [ttree] it will do that operation only on the rows that satisfy all the filters. If `unc_only=False`, you will see that the `'tIsUCN>0'` filter is now absent. 

## Setting Custom Filters

You can set your own filters using the `set_filter` function. In the following example we will define our own custom cuts on the Li6 data

```python
from ucndata import ucnrun

# read a run - this time we omit the tIsUCN flag, we will set our own
run = ucnrun(3200, ucn_only=False)

# print the number of rows in the tree at this time
print(len(run.tfile.UCNHits_Li6))
# output: 23482378

# apply the cuts to tPSD and tChargeL
# do this in-place so you don't return a copy of the existing tree
# these should be the exact same cuts that were used to determine tIsUCN in the first place
run.tfile.UCNHits_Li6.set_filter('tPSD>0.3', inplace=True)
run.tfile.UCNHits_Li6.set_filter('tChargeL>2000', inplace=True)

# we can now check the number of hits:
print(len(run.tfile.UCNHits_Li6))
# output: 14376279
```

## Removing Filters

Unfortunately the only way to remove filters is to reset the tree then re-add the remaining filters.

```python
from ucndata import ucnrun

# repeat the filters from the last example
run = ucnrun(3200, ucn_only=False)
run.tfile.UCNHits_Li6.set_filter('tPSD>0.3', inplace=True)
run.tfile.UCNHits_Li6.set_filter('tChargeL>2000', inplace=True)

# get the existing filters as a list
filters = run.tfile.UCNHits_Li6.filters

# check filters and operation
print(run.tfile.UCNHits_Li6.filters)
# output: ['tUnixTimePrecise > 15e8', 'tPSD>0.3', 'tChargeL>2000']
print(len(run.tfile.UCNHits_Li6))
# output: 14376279

# now lets reset the tree
run.tfile.UCNHits_Li6 = run.tfile.UCNHits_Li6.reset()

# check filters and operation
print(run.tfile.UCNHits_Li6.filters)
# output: []
print(len(run.tfile.UCNHits_Li6))
# output: 23482378

# re-add some filters, except the last one
for filt in filters[:-1]:
    run.tfile.UCNHits_Li6.set_filter(filt, inplace=True)

# check filters and operation
print(run.tfile.UCNHits_Li6.filters)
# output: ['tUnixTimePrecise > 15e8', 'tPSD>0.3']
print(len(run.tfile.UCNHits_Li6))
# output: 14546775
```

## Cycles and Periods

When cycles or periods are selected, the existing filters from the [ttrees] are copied over, and new filters on the timestamps are added, based on the start and stop times of the cycle or period. 

```python
from ucndata import ucnrun
run = ucnrun(3200)

print(run.tfile.UCNHits_Li6.filters)
# output: ['tUnixTimePrecise > 15e8', 'tIsUCN>0'] 

print(run[0].tfile.UCNHits_Li6.filters)
# output: ['tUnixTimePrecise > 15e8', 'tIsUCN>0', 'tUnixTimePrecise >= 1769320571', 'tUnixTimePrecise < 1769321056']
```

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)

[ttree]: https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md