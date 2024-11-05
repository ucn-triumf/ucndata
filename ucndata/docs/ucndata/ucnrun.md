# ucnrun

[Ucndata Index](../README.md#ucndata-index) / [Ucndata](./index.md#ucndata) / ucnrun

> Auto-generated documentation for [ucndata.ucnrun](../../ucndata/ucnrun.py) module.

- [ucnrun](#ucnrun)
  - [ucnrun](#ucnrun-1)
    - [ucnrun().check_data](#ucnrun()check_data)
    - [ucnrun().gen_cycle_filter](#ucnrun()gen_cycle_filter)
    - [ucnrun().get_cycle](#ucnrun()get_cycle)
    - [ucnrun().set_cycle_filter](#ucnrun()set_cycle_filter)
    - [ucnrun().set_cycle_times](#ucnrun()set_cycle_times)

## ucnrun

[Show source in ucnrun.py:27](../../ucndata/ucnrun.py#L27)

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

* Can access attributes of tfile directly from top-level object
* Need to define the values in ucndata.settings if you want non-default
behaviour
* Object is indexed as [cycle, period] for easy access to sub time frames

Cycle param contents

- ``nperiods`` - Number of periods in each cycle
- ``nsupercyc`` - Number of supercycles contained in the run
- ``enable`` - Enable status of the sequencer
- ``inf_cyc_enable`` - Enable status of infinite cycles
- ``cycle`` - Cycle ID numbers
- ``supercycle`` - Supercycle ID numbers
- ``valve_states`` - Valve states in each period and cycle
- ``period_end_times`` - End time of each period in each cycle in epoch time
- ``period_durations_s`` - Duration in sections of each period in each cycle
- ``ncycles`` - Number of total cycles contained in the run
- ``filter`` - A list indicating how we should filter cycles. More on that in [filters](filters.md)
- ``cycle_time`` - The start and end times of each cycle

#### Examples

Loading runs

```python
from ucndata import ucnrun, settings
# load from filename
ucnrun('/path/to/file/ucn_run_00001846.root')
# load from run number
settings.datadir = '/path/to/file/'
ucnrun(1846)
```

Slicing

```python
from ucndata import ucnrun
run = ucnrun(1846)
run[0, 0]   # cycle 0, period 0
run[:]      # all cycles, no distinction on period
run[:, 0]   # get all cycles, period 0
run[0, :]   # cycle 0, all periods
run[4:7, 2] # cycles 4, 5, 6, period 2
```

Get beam properties

```python
from ucndata import ucnrun
run = ucnrun(1846)
run.beam_current_uA # beam current in uA
run.beam_on_s       # beam duration on in s
run.beam_off_s      # beam duration off in s
```

Draw hits

```python
import matplotlib.pyplot as plt
from ucndata import ucnrun
run = ucnrun(1846)

# draw all hits in the file
plt.plot(*run.get_hits_histogram('Li6'))

# draw hits in each cycle (some differences due to binning)
for cycle in run:
    plt.plot(*cycle.get_hits_histogram('Li6'))
```

Get hits as a pandas dataframe

```python
from ucndata import ucnrun
run = ucnrun(1846)
hits = run.get_hits('Li6')
```

#### Signature

```python
class ucnrun(ucnbase):
    def __init__(self, run, header_only=False): ...
```

### ucnrun().check_data

[Show source in ucnrun.py:331](../../ucndata/ucnrun.py#L331)

Run some checks to determine if the data is ok.

#### Arguments

- `raise_error` *bool* - if true, raise an error if check fails, else return false

#### Returns

- `bool` - true if check passes, else false.

Checks:
    Do the settings.SLOW_TREES exist and have entries?
    Are there nonzero counts in UCNHits?

#### Signature

```python
def check_data(self, raise_error=False): ...
```

### ucnrun().gen_cycle_filter

[Show source in ucnrun.py:388](../../ucndata/ucnrun.py#L388)

Generate filter array for cycles. Use with self.set_cycle_filter to filter cycles.

#### Arguments

- `period_production` *int* - index of period where the beam should be stable. Enables checks of beam stability
- `period_count` *int* - index of period where we count ucn. Enables checks of data quantity
- `period_background` *int* - index of period where we do not count ucn. Enables checks of background
- `quiet` *bool* - if true don't print or raise exception

#### Returns

- `np.array` - of bool, true if keep cycle, false if discard

#### Notes

calls ucncycle.check_data on each cycle

#### Signature

```python
def gen_cycle_filter(
    self, period_production=None, period_count=None, period_background=None, quiet=False
): ...
```

### ucnrun().get_cycle

[Show source in ucnrun.py:413](../../ucndata/ucnrun.py#L413)

Return a copy of this object, but trees are trimmed to only one cycle.

Note that this process converts all objects to dataframes

#### Arguments

- `cycle` *int* - cycle number, if None, get all cycles

#### Returns

ucncycle:
    if cycle > 0:  ucncycle object
    if cycle < 0 | None: a list ucncycle objects for all cycles

#### Signature

```python
def get_cycle(self, cycle=None): ...
```

### ucnrun().set_cycle_filter

[Show source in ucnrun.py:433](../../ucndata/ucnrun.py#L433)

Set filter for which cycles to fetch when slicing or iterating

#### Notes

Filter is ONLY applied when fetching cycles as a slice or as an iterator. ucnrun.get_cycle() always returns unfiltered cycles.

Examples where the filter is applied:
    * run[:]
    * run[3:10]
    * run[:3]
    * for c in run: print(c)

Examples where the filter is not applied:
    * run[2]
    * run.get_cycle()
    * run.get_cycle(2)

#### Arguments

- `cfilter` *None|iterable* - list of bool, True if keep cycle, False if reject.
    if None then same as if all True

#### Returns

- `None` - sets self.cycle_param.filter

#### Signature

```python
def set_cycle_filter(self, cfilter=None): ...
```

### ucnrun().set_cycle_times

[Show source in ucnrun.py:467](../../ucndata/ucnrun.py#L467)

Get start and end times of each cycle from the sequencer and save
into self.cycle_param.cycle_times

Run this if you want to change how cycle start times are calculated

#### Arguments

- `mode` *str* - default|matched|sequencer|he3|li6
    - `if` *matched* - look for identical timestamps in RunTransitions from detectors
    - `if` *sequencer* - look for inCycle timestamps in SequencerTree
    - `if` *he3* - use He3 detector cycle start times
    - `if` *li6* - use Li6 detector cycle start times

#### Notes

- If run ends before sequencer stop is called, a stop is set to final timestamp.
- If the sequencer is disabled mid-run, a stop is set when disable ocurrs.
- If sequencer is not enabled, then make the entire run one cycle
- For matched mode,
    - set run stops as start of next transition
    - set offset as start_He3 - start_Li6
    - set start/stop/duration based on start_He3
- If the object reflects a single cycle, return from cycle_start, cycle_stop

#### Returns

- `pd.DataFrame` - with columns "start", "stop", "offset" and "duration (s)". Values are in epoch time. Indexed by cycle id. Offset is the difference in detector start times: he3_start-li6_start

#### Signature

```python
def set_cycle_times(self, mode="default"): ...
```