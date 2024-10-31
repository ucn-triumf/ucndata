# Examples

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)

Here we present some examples of simple usage, mostly focusing on things not already covered in the rest of the tutorial.

## Table of Contents

- [Examples](#examples)
  - [Table of Contents](#table-of-contents)
  - [Reading Files](#reading-files)
  - [Drawing hits histograms](#drawing-hits-histograms)
  - [Getting number of hits in each cycle or period](#getting-number-of-hits-in-each-cycle-or-period)
  - [Get list of hits in each cycle or period](#get-list-of-hits-in-each-cycle-or-period)

---

## Reading Files

```python
from ucndata import read, settings

settings.datadir = '/path/to/root_files'
runs = read([1846, 1847, 1848])
```

## Drawing hits histograms

Using the [hits histogram function](../docs/ucnbase.md#ucnbaseget_hits_histogram).

```python
from ucndata import read, settings
import matplotlib.pyplot as plt
settings.datadir = '/path/to/root_files'

data = read(1846)

# draw entire run hits, need to pass detector type
plt.plot(*data.get_hits_histogram('Li6'))

# draw each cycle individually
plt.figure()
for cycle in data:
    plt.plot(*cycle.get_hits_histogram('Li6'), label=f'Cycle {cycle.cycle}')
plt.legend(fontsize='xx-small')
```

## Getting number of hits in each cycle or period

Using the get_counts function for either [cycles](../docs/ucncycle.md#ucncycleget_counts) or [periods](../docs/ucnperiod.md#ucnperiodget_counts)

```python
from ucndata import read, settings
settings.datadir = '/path/to/root_files'

data = read(1846)

# counts in each cycle, overall
# note this returns an array that looks like [(x, dx), (x, dx), ...] so useful to transpose
counts, count_err = data[:].get_counts('Li6').transpose()

# counts in period 0 of each cycle
counts, count_err = data[:, 0].get_counts('Li6').transpose()

# lets use those counts in period 0 as background counts and subtract it from another period
# the background counts are passed as a list and are broadcast across the list
result = data[:, 2].get_counts('Li6', bkgd=counts, dbkgd=count_err)
counts2, counts2_err = result.transpose()
```

## Get list of hits in each cycle or period

We can do the same thing, but get all the data for each hit, without summing or histogramming, using the [get_hits](../docs/ucnbase.md#ucnbaseget_hits) function:

```python
from ucndata import read, settings
settings.datadir = '/path/to/root_files'

data = read(1846)

hits = data[:].get_hits('Li6')
```

Lets look at the output
```python
>>> hits[0]
                 tBaseline tChannel tChargeL tChargeS  tEntry tIsUCN tLength      tPSD  tTimeE  tTimeStamp     tUnixTime
tUnixTimePrecise
1.572462e+09             0        0     4151     2399    7392      1       0  0.422058       0  1740808338  1.572462e+09
1.572462e+09             0        7     6962     4098    7393      1       0  0.411377       0  1741174495  1.572462e+09
1.572462e+09             0        7     4925     2274    7397      1       0  0.538330       0  1775598081  1.572462e+09
1.572462e+09             0        5     5984     2557    7398      1       0  0.572754       0  1782866912  1.572462e+09
1.572462e+09             0        7     6050     2782    7404      1       0  0.540161       0  1815743551  1.572462e+09
...                    ...      ...      ...      ...     ...    ...     ...       ...     ...         ...           ...
1.572462e+09             0        1     5424     2510   39943      1       0  0.537231       0   187622428  1.572462e+09
1.572462e+09             0        1     4999     3008   39970      1       0  0.398254       0   734846517  1.572462e+09
1.572462e+09             0        2     3915     2269   39972      1       0  0.420410       0   772926231  1.572462e+09
1.572462e+09             0        1     5741     2474   39978      1       0  0.569092       0   873705149  1.572462e+09
1.572462e+09             0        2     7849     3801   39984      1       0  0.515747       0   946840691  1.572462e+09

[25397 rows x 11 columns]
```

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)