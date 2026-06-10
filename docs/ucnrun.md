# ucnrun

[Ucndata Index](./README.md#ucndata-index) / ucnrun

> Auto-generated documentation for [ucnrun](../ucndata/ucnrun.py) module.

- [ucnrun](#ucnrun)
  - [ucnrun](#ucnrun-1)
    - [ucnrun.__getitem__](#ucnrun__getitem__)
    - [ucnrun.__len__](#ucnrun__len__)
    - [ucnrun.__next__](#ucnrun__next__)
    - [ucnrun.__repr__](#ucnrun__repr__)
    - [ucnrun._set_period_times](#ucnrun_set_period_times)
    - [ucnrun._set_valve_states](#ucnrun_set_valve_states)
    - [ucnrun.check_data](#ucnruncheck_data)
    - [ucnrun.gen_cycle_filter](#ucnrungen_cycle_filter)
    - [ucnrun.get_cycle](#ucnrunget_cycle)
    - [ucnrun.keyfilter](#ucnrunkeyfilter)
    - [ucnrun.set_cycle_filter](#ucnrunset_cycle_filter)
    - [ucnrun.set_cycle_times_crude](#ucnrunset_cycle_times_crude)
    - [ucnrun.set_cycle_times_precise](#ucnrunset_cycle_times_precise)
  - [new_format](#new_format)

## ucnrun

[Show source in ucnrun.py:27](../ucndata/ucnrun.py#L27)

UCN run data. Cleans data and performs analysis

#### Arguments

- `run` *int|str* - if int, generate filename with DATADIR
    elif str then run is the path to the file
- `ucn_only` *bool* - if true set filter tIsUCN==1 on all hit trees
- `use_precise_cycles` *bool* - if true attempt to use precise cycle times.
    First, check if the RunTransition_Li6 tree has precise times in it (precise times found from midas2root).
    If not, then check if there are any hits in hardware cycle start channel on the digitizer.
    If not, raise a warning
    Default inputs are listed as ucndata.DEFAULT_CYCLE_TIMES_PRECISE

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
- ``filter`` - A list of booleans indicating how we should filter cycles. More on that in [the tutorial](https://github.com/ucn-triumf/ucndata/blob/main/tutorials/filter.md)
- ``cycle_time`` - The start and end times of each cycle

#### Examples

Loading runs

```python
from ucndata import ucnrun, settings
import ucndata
# load from filename
ucnrun('/pa../ucndata/file/ucn_run_00002684.root')
# load from run number
ucndata.DATADIR = '/pa../ucndata/file/'
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
    def __init__(self, run, ucn_only=True, use_precise_cycles=True): ...
```

#### See also

- [ucnbase](./ucnbase.md#ucnbase)

### ucnrun.__getitem__

[Show source in ucnrun.py:283](../ucndata/ucnrun.py#L283)

Return cycle(s) or period(s) using index/slice notation.

Supported index forms:

- ``run[i]`` — single integer: return cycle *i* as a [ucncycle](./ucncycle.md#ucncycle).
- ``run[i, j]`` — two-element tuple: return period *j* of cycle *i*.
- ``run[slice]`` / ``run[array]`` — slice or array: return an
  [applylist](./applylist.md#applylist) of cycles.  The cycle filter is applied when a slice
  or array index is used (but not for a plain integer index).
- ``run[slice, j]`` — slice of cycles then period *j* of each.

Negative integer indices are supported and wrap around like standard
Python lists.

#### Arguments

- `key` *int|tuple|slice|np.ndarray|list* - index specifying which
    cycle(s) and optionally which period to return.

#### Returns

- `ucncycle|ucnperiod|applylist` - a single cycle/period, or a list of
    them when a slice/array index is given.

#### Raises

- `IndexError` - if a single integer index exceeds the number of cycles,
    or if *key* is of an unrecognised type.

#### Examples

```python
>>> run[0]           # first cycle
>>> run[-1]          # last cycle
>>> run[0, 1]        # period 1 of cycle 0
>>> run[:]           # all cycles as an applylist
>>> run[:, 0]        # period 0 of every cycle
>>> run[2:5]         # cycles 2, 3, 4
```

#### Signature

```python
def __getitem__(self, key): ...
```

### ucnrun.__len__

[Show source in ucnrun.py:361](../ucndata/ucnrun.py#L361)

Return the total number of cycles in the run (unfiltered).

#### Returns

- `int` - value of ``cycle_param.ncycles``.

#### Signature

```python
def __len__(self): ...
```

### ucnrun.__next__

[Show source in ucnrun.py:212](../ucndata/ucnrun.py#L212)

Return next cycle during iteration, respecting the cycle filter.

#### Returns

- [ucncycle](./ucncycle.md#ucncycle) - the next cycle in iteration order.

#### Raises

- `StopIteration` - when all cycles (or all unfiltered cycles) have
    been yielded.

#### Signature

```python
def __next__(self): ...
```

### ucnrun.__repr__

[Show source in ucnrun.py:246](../ucndata/ucnrun.py#L246)

Return a human-readable summary of top-level public attributes.

Attributes are sorted case-insensitively and laid out in columns that
fit the current terminal width.

#### Returns

- `str` - multi-line string listing all public attributes, prefixed with
    the run number.

#### Signature

```python
def __repr__(self): ...
```

### ucnrun._set_period_times

[Show source in ucnrun.py:600](../ucndata/ucnrun.py#L600)

Compute and store period durations and end times from CycleParamTree.

Reads the 'Duration'-prefixed columns from CycleParamTree, trims them to
the declared nPeriods and nCycles, tiles the pattern across all cycles in
the run, then derives cumulative period end times from the cycle start
times already stored in ``cycle_param.cycle_times``.

Updates ``cycle_param`` with:
    period_durations_s (DataFrame): duration in seconds, indexed by
        period (rows) and cycle (columns).
    period_end_times (DataFrame): epoch end time of each period,
        same index/column layout as period_durations_s.
    nperiods (int): number of periods per cycle.
    ncycles (int): total number of cycles in the run.
    nsupercycles (int): number of supercycles.
    ncycles_per_supercycle (int): cycles per supercycle from CycleParamTree.
    cycle (np.ndarray): per-cycle index within its supercycle.
    supercycle (Series): supercycle index for each cycle.

#### Signature

```python
def _set_period_times(self): ...
```

### ucnrun._set_valve_states

[Show source in ucnrun.py:571](../ucndata/ucnrun.py#L571)

Read valve-state columns from CycleParamTree and store in cycle_param.

Parses the 'Valve'-prefixed columns of the CycleParamTree, extracts the
valve number from each column name, and stores the result as a DataFrame
in ``self.cycle_param['valve_states']`` with axes named 'period' (rows)
and 'valve' (columns).

#### Signature

```python
def _set_valve_states(self): ...
```

### ucnrun.check_data

[Show source in ucnrun.py:675](../ucndata/ucnrun.py#L675)

Run some checks to determine if the data is ok.

#### Arguments

- `raise_error` *bool* - if true, raise an error if check fails, else return false

#### Returns

- `bool` - true if check passes, else false.

#### Notes

* Do the ucndata.SLOW_TREES exist and have entries?
* Are there nonzero counts in UCNHits?

#### Examples

```python
>>> run = ucnrun(2684)
>>> run.check_data()
True
>>> run.check_data(raise_error=True)  # raises MissingDataError if checks fail
```

#### Signature

```python
def check_data(self, raise_error=False): ...
```

### ucnrun.gen_cycle_filter

[Show source in ucnrun.py:738](../ucndata/ucnrun.py#L738)

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
>>> run.set_cycle_filter(run.gen_cycle_filter(quiet=True))
```

#### Signature

```python
def gen_cycle_filter(self, quiet=False): ...
```

### ucnrun.get_cycle

[Show source in ucnrun.py:767](../ucndata/ucnrun.py#L767)

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
>>> run = ucnrun(1846)
>>> run.get_cycle(0)       # returns ucncycle for cycle 0
>>> len(run.get_cycle.   # returns applylist of all cycles
17
```

#### Signature

```python
def get_cycle(self, cycle=None): ...
```

### ucnrun.keyfilter

[Show source in ucnrun.py:796](../ucndata/ucnrun.py#L796)

Decide whether a ROOT tree key should be loaded from the file.

Called by ``tfile`` during file open to skip trees that are not needed
for UCN analysis (e.g. raw digitiser waveform trees). The name is
compared case-insensitively after spaces are replaced with underscores.

#### Arguments

- `name` *str* - ROOT tree key name as it appears in the file.

#### Returns

- `bool` - True if the tree should be loaded, False if it should be
    skipped.

#### Signature

```python
def keyfilter(self, name): ...
```

### ucnrun.set_cycle_filter

[Show source in ucnrun.py:822](../ucndata/ucnrun.py#L822)

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
>>> run = ucnrun(2684)
>>> len(run[:])        # all 17 cycles before filtering
17
>>> cfilter = np.full(17, True)
>>> cfilter[2] = False
>>> run.set_cycle_filter(cfilter)
>>> len(run[:])        # cycle 2 is now excluded
16
>>> [c.cycle for c in run]
[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
```

#### Signature

```python
def set_cycle_filter(self, cfilter=None): ...
```

### ucnrun.set_cycle_times_crude

[Show source in ucnrun.py:872](../ucndata/ucnrun.py#L872)

Get start and end times of each cycle from the sequencer and save
into self.cycle_param.cycle_times.

Reads cycleStarted timestamps from SequencerTree. Call this to reset
cycle timing after set_cycle_times_precise.or to re-derive from scratch.

#### Raises

- `DataError` - if SequencerTree is absent from the ROOT file.

#### Notes

- Cycle stop times are derived from the start of the next cycle;
  the last cycle stops at the final SequencerTree timestamp.
- Sets cycle_param.is_precise_timing to False.

#### Examples

```python
>>> run = ucnrun(2684)
>>> run.set_cycle_times_precise. # upgrade to precise timing
>>> run.set_cycle_times_crude.   # revert to sequencer-derived timing
```

#### Signature

```python
def set_cycle_times_crude(self): ...
```

### ucnrun.set_cycle_times_precise

[Show source in ucnrun.py:923](../ucndata/ucnrun.py#L923)

Replace crude cycle start times with hardware-timestamped precise times.

Reads hardware-trigger hit timestamps on the specified TV1725 input hw_channel.
These timestamps have sub-millisecond precision compared to the sequencer-derived
crude cycle times. The function aligns the precise timestamps against the existing
crude cycle grid, back-extrapolates if the first trigger was missed, and linearly
interpolates over any gaps where the hardware signal was not recorded.

After a successful call, ``cycle_param`` is updated as follows:

- ``cycle_param.cycle_times`` and ``cycle_param.period_end_times`` are
  replaced with their precise counterparts.
- ``cycle_param.is_precise_timing`` is set to ``True``.

The updated ``cycle_times`` DataFrame gains one extra column relative
to the crude version:

- ``is_measured`` (bool): ``True`` if the start time came directly from
  a recorded hardware hit; ``False`` if it was back-extrapolated or
  interpolated from the average precise cycle duration.

If no precise timestamps are found on the requested hw_channel the function
returns immediately without modifying ``cycle_param``.

#### Arguments

- `hw_channel` *int* - TV1725 input channel carrying the hardware
    cycle-start signal. Default is 10.
- `detector` *str* - Li6 | He3, select between RunTransition_* trees

#### Notes

The average precise cycle duration is estimated from inter-hit
differences that agree with the crude average to within 5 seconds,
so the crude timing must already be a reasonable first approximation.

#### Examples

```python
>>> run = ucnrun(2684)
>>> run.set_cycle_times_precise.          # use defaults
>>> run.set_cycle_times_precise(hw_channel=10, detector='Li6')
>>> run.cycle_param.is_precise_timing
True
>>> run.cycle_param.cycle_times['is_measured']  # True where hardware hit was recorded
```

#### Signature

```python
def set_cycle_times_precise(self, hw_channel=10, detector="Li6"): ...
```



## new_format

[Show source in ucnrun.py:21](../ucndata/ucnrun.py#L21)

#### Signature

```python
def new_format(message, category, filename, lineno, line): ...
```