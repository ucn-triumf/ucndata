# Tips and FAQ

[**Back to Index**](index.md)

## Table of Contents

- [Tips and FAQ](#tips-and-faq)
  - [Table of Contents](#table-of-contents)
  - [Converting epoch times to timestamps](#converting-epoch-times-to-timestamps)


## Converting epoch times to timestamps

There are many ways to do this, but pandas offers a nice way to convert arrays of epoch times through the [`pd.to_datetime`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html) function. However, to simplify this I have included a [datetime](../docs/datetime.md) module which is able to translate to and from datetime objects:

First, some setup:
```python
from ucndata import read, to_datetime, from_datetime
run = read(1846)
df = run.tfile.BeamlineEpics.copy()
```

If we look at `df`, we see that the index is an epoch time:
```python
In [2]: df
Out [2]:
            B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                       ...
1572460997          0.018750           0.00000  ...                  0.0        0.000000
1572461002          0.000000           0.01875  ...                  0.0        2.151400
1572461007          0.021875           0.01250  ...                  0.0        2.151400
1572461012          0.012500           0.00000  ...                  0.0        2.151400
1572461017          0.000000           0.00000  ...                  0.0        2.151400
...                      ...               ...  ...                  ...             ...
1572466463          0.000000           0.01250  ...                  0.0       38.294899
1572466468          0.000000           0.00000  ...                  0.0       38.294899
1572466473          0.018750           0.00000  ...                  0.0       37.864700
1572466478          0.034375           0.00000  ...                  0.0       37.864700
1572466479          0.000000           0.01250  ...                  0.0       38.294899

[1093 rows x 49 columns]
```

We can convert the [DataFrame], the module knows to convert only in the index:

```python
In [3]: to_datetime(df)
Out [3]:
                           B1UT_CM01_RDCOND  B1UT_CM02_RDCOND  ...  B1V_KSM_RDMODE_VAL1  B1_FOIL_ADJCUR
timestamp                                                      ...
2019-10-30 11:43:17-07:00          0.018750           0.00000  ...                  0.0        0.000000
2019-10-30 11:43:22-07:00          0.000000           0.01875  ...                  0.0        2.151400
2019-10-30 11:43:27-07:00          0.021875           0.01250  ...                  0.0        2.151400
2019-10-30 11:43:32-07:00          0.012500           0.00000  ...                  0.0        2.151400
2019-10-30 11:43:37-07:00          0.000000           0.00000  ...                  0.0        2.151400
...                                     ...               ...  ...                  ...             ...
2019-10-30 13:14:23-07:00          0.000000           0.01250  ...                  0.0       38.294899
2019-10-30 13:14:28-07:00          0.000000           0.00000  ...                  0.0       38.294899
2019-10-30 13:14:33-07:00          0.018750           0.00000  ...                  0.0       37.864700
2019-10-30 13:14:38-07:00          0.034375           0.00000  ...                  0.0       37.864700
2019-10-30 13:14:39-07:00          0.000000           0.01250  ...                  0.0       38.294899

[1093 rows x 49 columns]
```

We can also convert the index directly:

```python
In [4]: to_datetime(df.index)
Out [4]:
array(['2019-10-30T18:43:17.000000000', '2019-10-30T18:43:22.000000000',
       '2019-10-30T18:43:27.000000000', ...,
       '2019-10-30T20:14:33.000000000', '2019-10-30T20:14:38.000000000',
       '2019-10-30T20:14:39.000000000'], dtype='datetime64[ns]')
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