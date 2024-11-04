# ucnbase

[Ucndata Index](./README.md#ucndata-index) / ucnbase

> Auto-generated documentation for [ucnbase](../ucnbase.py) module.

- [ucnbase](#ucnbase)
  - [ucnbase](#ucnbase-1)
    - [ucnbase.apply](#ucnbaseapply)
    - [ucnbase.beam\_current\_uA](#ucnbasebeam_current_ua)
    - [ucnbase.beam\_off\_s](#ucnbasebeam_off_s)
    - [ucnbase.beam\_on\_s](#ucnbasebeam_on_s)
    - [ucnbase.copy](#ucnbasecopy)
    - [ucnbase.from\_dataframe](#ucnbasefrom_dataframe)
    - [ucnbase.from\_datetime](#ucnbasefrom_datetime)
    - [ucnbase.get\_hits](#ucnbaseget_hits)
    - [ucnbase.get\_hits\_histogram](#ucnbaseget_hits_histogram)
    - [ucnbase.to\_dataframe](#ucnbaseto_dataframe)
    - [ucnbase.to\_datetime](#ucnbaseto_datetime)

## ucnbase

[Show source in ucnbase.py:13](../ucnbase.py#L13)

UCN run data. Cleans data and performs analysis

#### Arguments

- `run` *int|str* - if int, generate filename with settings.datadir
    elif str then run is the path to the file
- `header_only` *bool* - if true, read only the header

#### Attributes

- `comment` *str* - comment input by users
- `cycle` *int|none* - cycle number, none if no cycle selected
- `cycle_param` *attrdict* - cycle parameters from sequencer settings
- `experiment_number` *str* - experiment number input by users
- `month` *int* - month of run start
- `run_number` *int* - run number
- `run_title` *str* - run title input by users
- `shifter` *str* - experimenters on shift at time of run
- `start_time` *str* - start time of the run
- `stop_time` *str* - stop time of the run
- `supercycle` *int|none* - supercycle number, none if no cycle selected
- `tfile` *tfile* - stores tfile raw readback
- `year` *int* - year of run start

#### Notes

Can access attributes of tfile directly from top-level object
Need to define the values in ucndata.settings if you want non-default
behaviour
Object is indexed as [cycle, period] for easy access to sub time frames

#### Signature

```python
class ucnbase(object): ...
```

### ucnbase.apply

[Show source in ucnbase.py:107](../ucnbase.py#L107)

Apply function to each cycle

#### Arguments

fn_handle (function handle): function to be applied to each cycle

#### Returns

- `np.ndarray` - output of the function

#### Signature

```python
def apply(self, fn_handle): ...
```

### ucnbase.beam_current_uA

[Show source in ucnbase.py:256](../ucnbase.py#L256)

#### Signature

```python
@property
def beam_current_uA(self): ...
```

### ucnbase.beam_off_s

[Show source in ucnbase.py:281](../ucnbase.py#L281)

#### Signature

```python
@property
def beam_off_s(self): ...
```

### ucnbase.beam_on_s

[Show source in ucnbase.py:278](../ucnbase.py#L278)

#### Signature

```python
@property
def beam_on_s(self): ...
```

### ucnbase.copy

[Show source in ucnbase.py:118](../ucnbase.py#L118)

Return a copy of this objet

#### Signature

```python
def copy(self): ...
```

### ucnbase.from_dataframe

[Show source in ucnbase.py:189](../ucnbase.py#L189)

Convert self.tfile contents to rootfile struture types

#### Signature

```python
def from_dataframe(self): ...
```

### ucnbase.from_datetime

[Show source in ucnbase.py:193](../ucnbase.py#L193)

Convert self.tfile contents index to epoch time if dataframe

#### Returns

- `None` - converts in-place

#### Signature

```python
def from_datetime(self): ...
```

### ucnbase.get_hits

[Show source in ucnbase.py:129](../ucnbase.py#L129)

Get times of ucn hits

#### Arguments

- `detector` *str* - one of the keys to settings.DET_NAMES

#### Returns

- `pd.DataFrame` - hits tree as a dataframe, only the values when a hit is registered

#### Signature

```python
def get_hits(self, detector): ...
```

### ucnbase.get_hits_histogram

[Show source in ucnbase.py:149](../ucnbase.py#L149)

Get histogram of UCNHits ttree times

#### Arguments

- `detector` *str* - Li6|He3
- `bin_ms` *int* - histogram bin size in milliseconds

#### Returns

- `tuple` - (bin_centers, histogram counts)

#### Signature

```python
def get_hits_histogram(self, detector, bin_ms=100): ...
```

### ucnbase.to_dataframe

[Show source in ucnbase.py:217](../ucnbase.py#L217)

Convert self.tfile contents to pd.DataFrame

#### Arguments

- `datetime` *bool* - if true, convert all timestamps into datetimes

#### Returns

- `None` - converts in-place

#### Signature

```python
def to_dataframe(self, datetime=False): ...
```

### ucnbase.to_datetime

[Show source in ucnbase.py:234](../ucnbase.py#L234)

Convert self.tfile contents index to datetime objects if dataframe

#### Returns

- `None` - converts in-place

#### Signature

```python
def to_datetime(self): ...
```