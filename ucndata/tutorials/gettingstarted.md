# Getting Started

[**Back to Index**](index.md)\
[**Next Page: Contents of the ucnrun Object**](ucnrun_contents.md)

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
In [1]: from ucndata import ucnrun
In [2]: run = ucnrun(2687)
```

Note that [ucnrun] objects inherit from a [base class](../docs/ucnbase.md). File inspection is easy: in the interpreter, simply type out the loaded run and it will print its contents to screen:

```python
In [3]: run
Out[3]:
run 2687:
  comment            experiment_number  run_number         start_time         year
  cycle_param        month              run_title          stop_time
  epics              path               shifters           tfile
```

The same with the contents of the run. Run contents are explained more [here](ucnrun_contents.md).

## Getting Counts and Values

Here are some common operations on a run to get values of interest:

#### Beam current

The calculation is based on value saved in the BeamlineEpics tree.

```python
In [4] run.beam1u_current_uA
Out [4]:
timestamp
1750164032    0.0000
1750164033    0.0000
1750164034    0.0000
1750164035    0.0000
1750164037    0.0000
               ...
1750164785    0.0000
1750164786    0.0000
1750164787    0.0000
1750164788    0.0000
1750164789    4.9935
Length: 662, dtype: float64
```

#### EPICS values or similar

These are saved as [ttree], [th1], [th2] or [DataFrame] objects.

```python
# get the whole tree
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
run.get_hits_histogram(detector='He3').plot()
```

You need to tell it what detector to use. Detectors are defined in the [ucnbase] file (`DET_NAMES`). We may also want to draw with proper datetimes on the x axis:

```python
run.get_hits_histogram(detector='He3', as_datetime=True).plot()
```


#### Getting Hits and Counts

When creating the [ucnrun] object, there is a

## Periods and Cycles

You can access these via indexing (more on that [here](cycandperiods.md)):

Get cycle #1:
```python
In [5]: run[1]
Out [5]:
run 2687 (cycle 1):
  comment            cycle_stop         path               start_time         year
  cycle              epics              run_number         stop_time
  cycle_param        experiment_number  run_title          supercycle
  cycle_start        month              shifters           tfile
```

Get cycle #1, period #0:
```python
In [6]: run[1,0]
Out[6]:
run 2687 (cycle 1, period 0):
  comment            cycle_stop         path               run_number         stop_time
  cycle              epics              period             run_title          supercycle
  cycle_param        experiment_number  period_start       shifters           tfile
  cycle_start        month              period_stop        start_time         year
```

Get all cycles, period 0:
```python
In [7]: x = run[:,0]
```

Note that the [ucncycle] and [ucnperiod] objects that are returned as a result of these slicing operations also inherit from the same [base class](../docs/ucnbase.md) as [ucnrun]. Thus, they behave very similarly, and everything we've done above can be done on these objects as well, but their data is specific only to that cycle or period.

[**Back to Index**](index.md)\
[**Next Page: Contents of the ucnrun Object**](ucnrun_contents.md)

[DataFrame]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
[ttree]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md
[th1]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/th1.md
[th2]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/th2.md
[attrdict]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/attrdict.md
[rootloader]: https://github.com/ucn-triumf/rootloader
[ucnbase]: ../docs/ucnbase.md
[ucnrun]: ../docs/ucnrun.md
[ucncycle]: ../docs/ucncycle.md
[ucnperiod]: ../docs/ucnperiod.md
[applylist]: ../docs/applylist.md
[settings]: ../docs/settings.md
[read]: ../docs/read.md
[merge]: ../docs/merge.md
