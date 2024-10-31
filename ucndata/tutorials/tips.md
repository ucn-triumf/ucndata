# Tips and FAQ

[**Back to Index**](index.md)

## Table of Contents

- [Tips and FAQ](#tips-and-faq)
  - [Table of Contents](#table-of-contents)
  - [Converting epoch times to timestamps](#converting-epoch-times-to-timestamps)


## Converting epoch times to timestamps

There are many ways to do this, but pandas offers a nice way to convert arrays of epoch times through the [`pd.to_datetime`](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.to_datetime.html) function. Below are some examples showing its use.

Here's a useful function to convert an array of epoch times to datetimes:

```python
from datetime import datetime
import pandas as pd
import numpy as np

def to_datetime(times, unit='s', timezone='America/Vancouver'):
    """Convert array of epoch times into datetime objects

    Args:
        times (iterable): some array or list of floats, epoch times, assumed utc time
        unit (str): the unit of the times. default: 's'
        timezone (str): which time zone to convert into. default: 'America/Vancouver'

    Returns:
        np.ndarray: of datetime objects
    """

    # lets use pandas
    # utc means that the timetamps are timezone-aware
    # unit='s' is the default for our MIDAS system
    s = pd.to_datetime(times, unit=unit, utc=True)

    # set timezone
    s = s.tz_convert(timezone)

    # convert to numpy array
    return s.to_numpy()
```

Here is perhaps the easiest if it's the index of a pandas [DataFrame]:

```python
from ucndata import ucnrun
import pandas as pd

# assume I have some dataframe with an index which is composed of epoch times
# for example:
run = ucnrun(1846)
df = run.tfile.BeamlineEpics.to_dataframe()

# convert the index - note that this is different from the above function that I defined
idx_converted = pd.to_datetime(df.index, unit='s', utc=True)

# set as new index
df.index = idx_converted

# set timezone
df = df.tz_convert('America/Vancouver')
```

Here's another version of this where we also preserve the epoch times as a new column in the [DataFrame]:

```python
from ucndata import ucnrun
import pandas as pd

# assume I have some dataframe with an index which is composed of epoch times
# for example:
run = ucnrun(1846)
df = run.tfile.BeamlineEpics.to_dataframe()

# reset index
col = df.index.name
df.reset_index(inplace=True)

# convert the column
df['timestamps'] = pd.to_datetime(df[col], unit='s', utc=True)

# set as new index
df.set_index('timestamps', inplace=True)

# set timezone
df = df.tz_convert('America/Vancouver')
```

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