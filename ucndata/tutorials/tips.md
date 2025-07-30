# Tips and FAQ

[**Back to Index**](index.md)

## Table of Contents

- [Tips and FAQ](#tips-and-faq)
  - [Table of Contents](#table-of-contents)
  - [Writing Efficient Code](#writing-efficient-code)
    - [Rootloader's ttree uses RDataFrames](#rootloaders-ttree-uses-rdataframes)
    - [Some important consequences of RDataFrames](#some-important-consequences-of-rdataframes)
    - [Efficiently Modifying period timings and getting hits](#efficiently-modifying-period-timings-and-getting-hits)
  - [Mounting Data Drives](#mounting-data-drives)
  - [Converting epoch times to timestamps](#converting-epoch-times-to-timestamps)


## Writing Efficient Code

### Rootloader's ttree uses RDataFrames
The UCN hits trees can be quite large. To speed up processing and to make efficient use of computing resources, ucndata uses [ROOT]'s [RDataFrame] object. This is a high-level representation of a TTree and is utilized by [rootloader]'s [ttree] object to do all computation. In addition, the [ttree] also implements [ROOT]'s implicit multithreading package to speed up processing. In general, here's how all computations work:

* Set some [filters](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0) on the [RDataFrame]. These allow one to select rows of the [RDataFrame] based on some condition. Typical filters include things like `tIsUCN == 1` to select only UCN hits, or conditions on timestamps to select rows based on periods or cycles.
* Run one of the standard [built-in computations](https://root.cern/doc/master/classROOT_1_1RDataFrame.html#cheatsheet). Typically this includes [making histograms](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#af5b79eb05f2ec0b730ec3b378a2d9ef9) or [counting number of entries](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#a876bfce418c82a93caf2b143c9c08704), or [getting some stats](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#a18471e559710b960777f2f803d6904ba).
* ucndata is written such that if a quantity is computed, it is stored to avoid needing to recompute that quantity. We are careful to avoid the case where the data is updated but the stored values are not such that old data is fetched accidentally.

### Some important consequences of RDataFrames

* [RDataFrame]s are extremely well parallelized and are very efficient at computing results from its contents, using almost no RAM in the process.
* [RDataFrame] makes no assumptions on the ordering of the data, and instead uses the filters as a means to extract subsets of data. This means that every computation first checks EVERY row of the entire [ttree], to see if it passes the set filters. Thus a naive count of the number of events for a single period of a single cycle would take an equal amount of time as counting the total number of events in the whole file. If you then wanted to find the number of hits in each period, this would get expensive quickly.
* To circumvent this, when counting hits from any [period](../docs/ucnperiod.md#ucnperiodget_nhits) or [cycle](../docs/ucncycle.md#ucncycleget_nhits), that function instead calls the [equivalent from ucnrun](../docs/ucnrun.md#ucnrunget_nhits), which makes a histogram whose edges correspond to the cycle and period timings. Once called, this histogram is saved for future use. Thus we always calculate the number of hits for all periods at once, and for future calls we retrieve the saved values.
* If modifying the timings of [periods](../docs/ucnperiod.md#ucnperiodmodify_timing), this resets the saved hits histogram since it would no longer be accurate. Thus it would have to be recomputed.

### Efficiently Modifying period timings and getting hits


In the below, we modify the timing of period 0 in each cycle and get the number of hits in that period. This structure is bad, because at every iteration we reset the saved hits histogram (due to modifying the timings). Thus we need to re-run the calculation each iteration of the loop.
```python
from ucnrun import ucnrun

run = ucnrun(2575)
hits = []
for cycle in run:
  cycle[0].modify_timing(0, 1)            # modify period 0 timing
  hits.append(cycle[0].get_nhits('Li6'))  # get n hits
```

The below shows a better version of the above. We modify all the timings at once, then recalculate the number of UCN hits in each period on the first iteration of the second `for` loop, after which we only need retrieve the values from the saved histogram.
```python
from ucnrun import ucnrun

run = ucnrun(2575)
hits = []
for cycle in run:
  cycle[0].modify_timing(0, 1)            # modify period 0 timing

for cycle in run:
  hits.append(cycle[0].get_nhits('Li6'))  # get n hits
```

## Mounting Data Drives

The data is stored here: `ucn@daq01.ucn.triumf.ca:/data3/ucn/root_files`. This directory is also mounted on `daq04` at the same path. If you also want drive-mounted access to enable your machine to access the data as if you were on `daq04` or `daq01`, you need only run the following command after asking Thomas Linder for the needed permissions to mount:

```bash
sudo mount daq01.ucn.triumf.ca:/data3 /data3
```

This should NFS mount the drive on your machine using the same path structure, enabling ucndata to work as written out of the box. Note that when a file is first used, the NFS mount structure seems to first download the file, then ROOT goes to work. Once the file is downloaded it need not be downloaded on subsequent uses, unless the directory is unmounted in the intervening time. Depending on your internet connection this download process can be an initially long bottleneck, but gets better on reanalysis. 

## Converting epoch times to timestamps

There are many ways to do this, but pandas offers a nice way to convert arrays of epoch times through the [`pd.to_datetime`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html) function. However, to simplify this I have included a [datetime](../docs/datetime.md) module which is able to translate to and from datetime objects:

First, some setup:
```python
from ucndata import ucnrun, to_datetime, from_datetime
run = ucnrun(2687)
df = run.tfile.BeamlineEpics.to_dataframe()
```

If we look at `df`, we see that the index is an epoch time:
```python
In [2]: df
Out [2]:
            B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                       ...
1750164032          0.000000          0.000000  ...                  0.0       99.870003
1750164033          0.000000          0.000000  ...                  0.0       99.870003
...                      ...               ...  ...                  ...             ...
1750164788          0.000000          0.000000  ...                  0.0       98.953796
1750164789          0.000000          0.000000  ...                  0.0       99.870003

[662 rows x 61 columns]
```

We can convert the [DataFrame], the module knows to convert only in the index:

```python
In [3]: to_datetime(df)
Out [3]:
                           B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                                      ...
2025-06-17 05:40:32-07:00          0.000000          0.000000  ...                  0.0       99.870003
2025-06-17 05:40:33-07:00          0.000000          0.000000  ...                  0.0       99.870003
...                                     ...               ...  ...                  ...             ...
2025-06-17 05:53:08-07:00          0.000000          0.000000  ...                  0.0       98.953796
2025-06-17 05:53:09-07:00          0.000000          0.000000  ...                  0.0       99.870003

[662 rows x 61 columns]

```

We can also convert the index directly:

```python
In [4]: to_datetime(df.index)
Out [4]:
DatetimeIndex(['2025-06-17 05:40:32-07:00', '2025-06-17 05:40:33-07:00',
               '2025-06-17 05:40:34-07:00', '2025-06-17 05:40:35-07:00',
               ...
               '2025-06-17 05:53:06-07:00', '2025-06-17 05:53:07-07:00',
               '2025-06-17 05:53:08-07:00', '2025-06-17 05:53:09-07:00'],
              dtype='datetime64[ns, America/Vancouver]', name='timestamp', length=662, freq=None)

```

Similarly the `from_datetime` will convert back to epoch_times.


[**Back to Index**](index.md)

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
[RDataFrame]: https://root.cern/doc/master/classROOT_1_1RDataFrame.html
[ROOT]: https://root.cern/