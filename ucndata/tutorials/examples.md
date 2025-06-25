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

Using the default path (`/data3/ucn/root_files`)

```python
from ucndata import ucnrun
runs = ucnrun(2687)
```

Using a custom path
```python
from ucndata import ucnrun
ucnrun.datadir = 'mypath'
runs = ucnrun(2687)
```

Specify the file directly
```python
from ucndata import ucnrun
runs = ucnrun('/path/ucn_run_00002687.root')
```


## Drawing hits histograms

Using the [hits histogram function](../docs/ucnbase.md#ucnbaseget_hits_histogram).

```python
from ucndata import ucnrun
import matplotlib.pyplot as plt
data = ucnrun(2687)

# draw entire run hits, need to pass detector type
hist = data.get_hits_histogram('He3')
hist.plot()

# draw each cycle individually
plt.figure()
for cycle in data:
    cycle.get_hits_histogram('He3').plot(label=f'Cycle {cycle.cycle}')
plt.legend(fontsize='xx-small')
```

## Getting number of hits in each cycle or period

Using the get_counts function for either [cycles](../docs/ucncycle.md#ucncycleget_counts) or [periods](../docs/ucnperiod.md#ucnperiodget_counts)

```python
from ucndata import ucnrun
data = ucnrun(2087)

# counts in each cycle, overall
# note this returns an array that looks like [(x, dx), (x, dx), ...] so useful to transpose
counts = data[:].get_nhits('He3')

# counts in period 2 of each cycle
counts = data[:, 2].get_nhits('He3')
```

## Get list of hits in each cycle or period

We can do the same thing, but get all the data for each hit, without summing or histogramming, using the [get_hits_dataframe](../docs/ucnbase.md#ucnbaseget_hits_dataframe) function. Be careful, this can easily take more memory than your machine is capable of handling.

```python
from ucndata import ucndata
data = read(2687)
hits = data[:].get_hits_dataframe('He3')
```

Lets look at the output
```python
>>> hits[0]
                 tBaseline tChannel tChargeL tChargeS  ...      tPSD tTimeE  tTimeStamp     tUnixTime
tUnixTimePrecise                                       ...
1.750164e+09             0        0    65535    32767  ...  0.500000      0  1937476768  1.750164e+09
1.750164e+09             0        0    65535    32767  ...  0.500000      0    43272024  1.750164e+09
1.750164e+09             0        0    65535    32767  ...  0.500000      0   426009476  1.750164e+09
...
1.750164e+09             0        0    65535    32767  ...  0.500000      0   796146636  1.750164e+09
1.750164e+09             0        0    65535    32767  ...  0.500000      0  1268468856  1.750164e+09
1.750164e+09             0        0    65535    32767  ...  0.500000      0  1648070648  1.750164e+09

[37 rows x 11 columns]

```

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)