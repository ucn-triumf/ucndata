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