# ucnrun

[Ucndata Index](./README.md#ucndata-index) / ucnrun

> Auto-generated documentation for [ucnrun](../ucndata/ucnrun.py) module.

- [ucnrun](#ucnrun)
  - [ucnrun](#ucnrun-1)
    - [ucnrun.check_data](#ucnruncheck_data)
    - [ucnrun.draw_cycle_times](#ucnrundraw_cycle_times)
    - [ucnrun.gen_cycle_filter](#ucnrungen_cycle_filter)
    - [ucnrun.get_cycle](#ucnrunget_cycle)
    - [ucnrun.inspect](#ucnruninspect)
    - [ucnrun.keyfilter](#ucnrunkeyfilter)
    - [ucnrun.set_cycle_filter](#ucnrunset_cycle_filter)
    - [ucnrun.set_cycle_times](#ucnrunset_cycle_times)
  - [new_format](#new_format)

## ucnrun

[Show source in ucnrun.py:30](../ucndata/ucnrun.py#L30)

UCN run data. Cleans data and performs analysis

#### Arguments

- `run` *int|str* - if int, generate filename with self.datadir
    elif str then run is the path to the file
- `header_only` *bool* - if true, read only the header
- `ucn_only` *bool* - if true set filter tIsUCN==1 on all hit trees

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
* Need to define the values if you want non-default behaviour
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
ucnrun('/pa../ucndata/file/ucn_run_00002684.root')
# load from run number
ucnrun.datadir = '/pa../ucndata/file/'
ucnrun(2684)
```

Slicing

```python
from ucndata import ucnrun
run = ucnrun(2684)
run[0, 0]   # cycle 0, period 0
run[:]      # all cycles, no distinction on period
run[:, 0]   # get all cycles, period 0
run[0, :]   # cycle 0, all periods
run[4:7, 2] # cycles 4, 5, 6, period 2
```

Get beam properties

```python
from ucndata import ucnrun
run = ucnrun(2684)
run.beam_current_uA # beam current in uA
run.beam_on_s       # beam duration on in s
run.beam_off_s      # beam duration off in s
```

Draw hits

```python
import matplotlib.pyplot as plt
from ucndata import ucnrun
run = ucnrun(2684)

# draw all hits in the file
run.get_hits_histogram('Li6').plot()

# draw hits in each cycle
for cycle in run:
    cycle.get_hits_histogram('Li6').plot(label=cycle.cycle)

# adjust the timing of cycles and periods
run._modify_ptiming(cycle=0, period=0, dt_start_s=1, dt_start_s=0)

# inspect the data: draw a figure with hits histogram, beam current, and optional slow control data
run.inspect('Li6', bin_ms=100, xmode='dur')
```

#### Signature

```python
class ucnrun(ucnbase):
    def __init__(self, run, header_only=False, ucn_only=True): ...
```

#### See also

- [ucnbase](./ucnbase.md#ucnbase)

### ucnrun.check_data

[Show source in ucnrun.py:562](../ucndata/ucnrun.py#L562)

Run some checks to determine if the data is ok.

#### Arguments

- `raise_error` *bool* - if true, raise an error if check fails, else return false

#### Returns

- `bool` - true if check passes, else false.

#### Notes

* Do the self.SLOW_TREES exist and have entries?
* Are there nonzero counts in UCNHits?

#### Examples

```python
>>> run.check_data()
True
```

#### Signature

```python
def check_data(self, raise_error=False): ...
```

### ucnrun.draw_cycle_times

[Show source in ucnrun.py:625](../ucndata/ucnrun.py#L625)

Draw cycle start times as thick black lines, period end times as dashed lines

#### Arguments

- `ax` *plt.Axes* - axis to draw in, if None, draw in current axes
- `xmode` *str* - datetime|duration|epoch
- `do_legend` *bool* - if true draw legend colors for period numbers

#### Notes

- `Assumed` *periods* - 0 - irradiation
                    1 - storage
                    2 - count

#### Signature

```python
def draw_cycle_times(self, ax=None, xmode="datetime", do_legend=False): ...
```

### ucnrun.gen_cycle_filter

[Show source in ucnrun.py:709](../ucndata/ucnrun.py#L709)

Generate filter array for cycles. Use with self.set_cycle_filter to filter cycles.

#### Arguments

- `quiet` *bool* - if true don't print or raise exception

#### Returns

- `np.array(bool)` - true if keep cycle, false if discard

#### Notes

calls `ucncycle.check_data` on each cycle

#### Examples

```python
>>> run = ucnrun(2575)
>>> run.gen_cycle_filter()
Run 2575, cycle 0: 1A current dropped below 0.1 uA
Run 2575, cycle 1: 1A current dropped below 0.1 uA

array([False, False,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True])
```

#### Signature

```python
def gen_cycle_filter(self, quiet=False): ...
```

### ucnrun.get_cycle

[Show source in ucnrun.py:740](../ucndata/ucnrun.py#L740)

Return a copy of this object, but trees are trimmed to only one cycle.

Note that this process converts all objects to dataframes

#### Arguments

- `cycle` *int* - cycle number, if None, get all cycles

#### Returns

ucncycle:
    if cycle > 0:  ucncycle object
    if cycle < 0 | None: a list ucncycle objects for all cycles

#### Examples

```python
# get single cycle
>>> run.get_cycle(0)
run 1846 (cycle 0):
    comment            cycle_start        month              shifters           supercycle
    cycle              cycle_stop         run_number         start_time         tfile
    cycle_param        experiment_number  run_title          stop_time          year

# get all cycles
>>> len(run.get_cycle.
17
```

#### Signature

```python
def get_cycle(self, cycle=None): ...
```

### ucnrun.inspect

[Show source in ucnrun.py:777](../ucndata/ucnrun.py#L777)

Draw counts and BL1A current with indicated periods to determine data quality

#### Arguments

- `detector` *str* - detector from which to get the counts from. Li6|He3
- `bin_ms` *int* - histogram bin size in ms
- `xmode` *str* - datetime|duration|epoch
- `slow` *list|str* - name of slow control tree to add in a separate axis, can be a list of names

#### Signature

```python
def inspect(self, detector="Li6", bin_ms=100, xmode="duration", slow=None): ...
```

### ucnrun.keyfilter

[Show source in ucnrun.py:919](../ucndata/ucnrun.py#L919)

Don't load all the data in each file, only that which is needed

#### Signature

```python
def keyfilter(self, name): ...
```

### ucnrun.set_cycle_filter

[Show source in ucnrun.py:933](../ucndata/ucnrun.py#L933)

Set filter for which cycles to fetch when slicing or iterating

#### Arguments

- `cfilter` *None|iterable* - list of bool, True if keep cycle, False if reject.
    if None then same as if all True

#### Returns

- `None` - sets self.cycle_param.filter

#### Notes

Filter is ONLY applied when fetching cycles as a slice or as an iterator. ucnrun.get_cycle.always returns unfiltered cycles.

Examples where the filter is applied:
    * run[:]
    * run[3:10]
    * run[:3]
    * for c in run: print(c)

Examples where the filter is not applied:
    * run[2]
    * run.get_cycle()
    * run.get_cycle(2)

#### Examples

```python
# check how many cycles are fetched without filter
>>> len(run[:])
17

# apply a filter
>>> filter = np.full(17, True)
>>> filter[2] = False
>>> run.set_cycle_filter(filter)

# check that cycle 2 is filtered out
>>> len(run[:])
16
>>> for c in run:
        print(c.cycle)
0
1
3
4
5
6
7
8
9
10
11
12
13
14
15
16
```

#### Signature

```python
def set_cycle_filter(self, cfilter=None): ...
```

### ucnrun.set_cycle_times

[Show source in ucnrun.py:1006](../ucndata/ucnrun.py#L1006)

Get start and end times of each cycle from the sequencer and save
into self.cycle_param.cycle_times

Run this if you want to change how cycle start times are calculated

#### Arguments

- `mode` *str* - default|matched|sequencer|he3|li6|beamon
    - `if` *matched* - look for identical timestamps in RunTransitions from detectors
    - `if` *sequencer* - look for inCycle timestamps in SequencerTree
    - `if` *he3* - use He3 detector cycle start times
    - `if` *li6* - use Li6 detector cycle start times
    - `if` *beamon* - use rise of beam current to determine start time

#### Returns

- `pd.DataFrame` - with columns "start", "stop", "offset" and "duration (s)". Values are in epoch time. Indexed by cycle id. Offset is the difference in detector start times: he3_start-li6_start

#### Notes

- If run ends before sequencer stop is called, a stop is set to final timestamp.
- If the sequencer is disabled mid-run, a stop is set when disable ocurrs.
- If sequencer is not enabled, then make the entire run one cycle
- For matched mode,
    - set run stops as start of next transition
    - set offset as start_He3 - start_Li6
    - set start/stop/duration based on start_He3
- If the object reflects a single cycle, return from cycle_start, cycle_stop

#### Examples

```python
# this calculates new cycle start and end times based on the selected method
>>> run.set_cycle_times('li6')
```

#### Signature

```python
def set_cycle_times(self, mode): ...
```



## new_format

[Show source in ucnrun.py:24](../ucndata/ucnrun.py#L24)

#### Signature

```python
def new_format(message, category, filename, lineno, line): ...
```