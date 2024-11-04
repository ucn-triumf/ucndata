# Getting Started

[**Back to Index**](index.md)\
[**Next Page: Contents of the ucnrun Object**](read.md)

---

The `ucndata` package is based around the [ucnrun] object. This object reads a root file into memory and organizes its contents for easy scripting of future analyses. These root files can be generated with the `midas2root` program, which is a part of the [ucn_detector_analyzer](https://github.com/ucn-triumf/ucn_detector_analyzer/tree/2024) code set.

### Table of Contents

- [Getting Started](#getting-started)
    - [Table of Contents](#table-of-contents)
  - [The Very Basics](#the-very-basics)
  - [Getting Counts and Values](#getting-counts-and-values)
  - [Periods and Cycles](#periods-and-cycles)
  - [Lists of Runs (or cycles or periods)](#lists-of-runs-or-cycles-or-periods)

On this page we quickly work through what will be covered in more detail later in this tutorial.

## The Very Basics

Here is a minimum working example, assuming we have the file `ucn_run_00001846.root` in our current working directory.

```python
In [1]: from ucndata import read
In [2]: run = read('ucn_run_00001846.root')
```

The [read] function returns either a [ucnrun] object or an [applylist] of [ucnrun] objects. Note that [ucnrun] objects inherit from a [base class](../docs/ucnbase.md). File inspection is easy: in the interpreter, simply type out the loaded run and it will print its contents to screen:

```python
In [3]: run
Out[3]:
run 1846:
  comment            month              shifters           tfile
  cycle_param        run_number         start_time         year
  experiment_number  run_title          stop_time
```

The same with the contents of the run. Run contents are explained more [here](ucnrun_contents.md). See also [this page](read.md) for more info on how to read runs efficiently and how this works. Note that by default [read] converts the tfile contents to pandas [DataFrame]s.

## Getting Counts and Values

Here are some common operations on a run to get values of interest:

#### Beam current

The calculation is based on value saved in the BeamlineEpics tree.

```python
In [4] run.beam_current_uA
Out [4]:
timestamp
1572460997    0.0
1572461002    0.0
1572461007    0.0
1572461012    0.0
1572461017    0.0
             ...
1572466463    0.0
1572466468    0.0
1572466473    0.0
1572466478    0.0
1572466479    0.0
Length: 1093, dtype: float64
```

#### EPICS values or similar

These are saved as [ttree], [th1], [th2] or [DataFrame] objects.

```python
# get the whole dataframe
df = run.tfile.BeamlineEpics

# get a single column
df = run.tfile.BeamlineEpics.B1V_KICK_RDHICUR

# this is an equivalent statement should the key contain an inappropriate character
df = run.tfile.BeamlineEpics['B1V_KICK_RDHICUR']

# get the mean value
avg = run.tfile.BeamlineEpics.B1V_KICK_RDHICUR.mean()
```

#### Drawing UCN Hits as a Histogram

Since this is a common operation, this is built into the ucnrun object via the [`get_hits_histogram`](../docs/ucnbase.md#ucnbaseget_hits_histogram) function.

```python
import matplotlib.pyplot as plt
plt.plot(*run.get_hits_histogram(detector='Li6'))
```

You need to tell it what detector to use. Detectors are defined in the [settings] file (`DET_NAMES`).

#### Getting Hits and Counts

There are two versions: "hits" refers to all the data when there is a positive UCN detection. "Counts" refers to the sum of these hits during a specific time window. To get the [DataFrame] of hits:

```python
hits = run.get_hits('Li6')
```

This then produces a [DataFrame] with the following columns, matching the UCN hits tree:

```python
'tUnixTimePrecise', 'tBaseline', 'tChannel', 'tChargeL', 'tChargeS',
'tEntry', 'tIsUCN', 'tLength', 'tPSD', 'tTimeE', 'tTimeStamp',
'tUnixTime'
```

You can only get counts for Cycles or Periods.

## Periods and Cycles

You can access these via indexing (more on that [here](cycandperiods.md)):

Get cycle #5:
```python
In [5]: run[5]
Out [5]:
run 1846 (cycle 5):
  comment            cycle_start        month              shifters           supercycle
  cycle              cycle_stop         run_number         start_time         tfile
  cycle_param        experiment_number  run_title          stop_time          year
```

Get cycle #5, period #0:
```python
In [6]: run[5,0]
Out[6]:
run 1846 (cycle 5, period 0):
  comment            cycle_stop         period_start       shifters           tfile
  cycle              experiment_number  period_stop        start_time         year
  cycle_param        month              run_number         stop_time
  cycle_start        period             run_title          supercycle
```

Get all cycles, period 0:
```python
In [7]: x = run[:,0]
```

Note that the [ucncycle] and [ucnperiod] objects that are returned as a result of these slicing operations also inherit from the same [base class](../docs/ucnbase.md) as [ucnrun]. Thus, they behave very similarly, and everything we've done above can be done on these objects as well, but their data is specific only to that cycle or period.

## Lists of Runs (or cycles or periods)

The [read] function, as with slicing, returns an [applylist]. This list allows one to get properties of the contained objects as if they were properties of the list. [More on that here](applylist.md). To get the cycle number of all cycles:

```python
In [8]: run[:].cycle
Out [8]:
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
```

Or to get the average beam current of period 0:

```python
In [9]: x = run[:, 0].beam_current_uA.mean()
In [10]: x
Out [10]:
[np.float64(0.8348174370252169),
 np.float64(0.907572403550148),
 np.float64(0.9051820337772369),
 np.float64(0.9075725873311361),
 np.float64(0.9051825851202011),
 np.float64(0.9027922203143438),
 np.float64(0.9027920365333557),
 np.float64(0.9035888860623041),
 np.float64(0.9004018505414327),
 np.float64(0.8996049960454305),
 np.float64(0.8980118532975515),
 np.float64(0.827094629406929),
 np.float64(0.8948242564996084),
 np.float64(0.8502016713221868),
 np.float64(0.8494050006071726),
 np.float64(0.8525918622811636),
 np.float64(0.845421110590299)]

# convert to regular floats
In [11]: x.astype(float)
In [12]: x
Out[12]:
[0.8348174370252169,
 0.907572403550148,
 0.9051820337772369,
 0.9075725873311361,
 0.9051825851202011,
 0.9027922203143438,
 0.9027920365333557,
 0.9035888860623041,
 0.9004018505414327,
 0.8996049960454305,
 0.8980118532975515,
 0.827094629406929,
 0.8948242564996084,
 0.8502016713221868,
 0.8494050006071726,
 0.8525918622811636,
 0.845421110590299]
```

[**Back to Index**](index.md)\
[**Next Page: Contents of the ucnrun Object**](ucnrun_contents.md)

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
[settings]: ../docs/settings.md
[read]: ../docs/read.md
[merge]: ../docs/merge.md
