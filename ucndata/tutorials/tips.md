# Tips and FAQ

[**Back to Index**](index.md)

## Table of Contents

- [Tips and FAQ](#tips-and-faq)
  - [Table of Contents](#table-of-contents)
  - [Converting epoch times to timestamps](#converting-epoch-times-to-timestamps)


## Converting epoch times to timestamps

There are many ways to do this. Here is perhaps the easiest:

```python
from ucndata import ucnrun
import pandas as pd

# assume I have some dataframe with an index which is composed of epoch times
# for example
run = ucnrun(1846)
df = run.tfile.BeamlineEpics.to_dataframe()

# convert the index
idx_converted = pd.to_datetime(df.index, unit='s')

# set as new index
df.index = idx_converted

# set timezone
df = df.tz_localize('UTC').tz_convert('America/Vancouver')
```

Here's another version of this where we also preserve the epoch times as a new column in the dataframe:

```python
from ucndata import ucnrun
import pandas as pd

# assume I have some dataframe with an index which is composed of epoch times
# for example
run = ucnrun(1846)
df = run.tfile.BeamlineEpics.to_dataframe()

# reset index
col = df.index.name
df.reset_index(inplace=True)

# convert the column
df['timestamps'] = pd.to_datetime(df[col], unit='s')

# set as new index
df.set_index('timestamps', inplace=True)

# set timezone
df = df.tz_localize('UTC').tz_convert('America/Vancouver')
```

[**Back to Index**](index.md)