# Tips and FAQ

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