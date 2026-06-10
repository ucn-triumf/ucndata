# Cycles and Periods

[**Back to Index**](index.md)\
[**Next Page: Filtering Cycles**](filter.md)

---

Each run which uses the sequencer makes use of many cycles, each of which is composed of up to 10 periods. Each period has a set of valves open or closed for a fixed amount of time. Each cycle can have different period settings, but each supercycle reflects a repetition of the full cycle set. It is therefore prudent to access the data for each cycles and period in the run in an easy manner.

## Table of Contents

* [Basics](#basics-and-introduction)
* [Slicing and indexing](#slicing-and-indexing)
* [Determining cycle start and end times](#cycle-start-and-end-times)

## Basics and Introduction

The overarching concept is to access the entire contents of the data set in a new object each time a cycle or period is accessed. These new objects, [ucncycle] and [ucnperiod] respectively, each keep track of their own timings and identity but do not copy the contents of [tfile]. Rather, when the user attempts to access the contents of [tfile] the [ucncycle] or [ucnperiod] object instead fetches only part of the contents as needed. Thus, no large copying of data is needed, improving run times significantly. This means, however, that modifying data in [ucncycle] or [ucnperiod] objects may modify the data elsewhere, since this is a shared property. Otherwise, each of the [ucncycle] or [ucnperiod] objects behave for the most part the same as the containing [ucnrun] object.

A simple example of usage:

```python
In [0]: from ucndata import ucnrun
In [1]: run = ucnrun(2687)

In [2]: run.get_cycle(0)
Out[2]:
run 2687 (cycle 0):
  comment            cycle_stop         path               start_time         year
  cycle              epics              run_number         stop_time
  cycle_param        experiment_number  run_title          supercycle
  cycle_start        month              shifters           tfile
```

As you can see the cycle knows it's cycle 0, and will tell the user as such. It also gains the attributes

* `cycle_start`: the start time of the cycle in epoch time
* `cycle_stop`: the stop time of the cycle in epoch time
* `cycle`: the cycle id index

However its contents are now restricted to the time frame associated with that cycle:

```python
In [3]: run.get_cycle(0).tfile.BeamlineEpics
Out[3]:
ttree branches:
    B1UT_CM01_RDCOND        B1U_COL2RIGHT_RDTEMP    B1U_TNIM2_10MINAVG      B1U_YCB0_RDCUR
    B1UT_CM02_RDCOND        B1U_COL2UP_RDTEMP       B1U_TNIM2_10MINTRIP     B1U_YCB0_STATON
    B1UT_LM50_RDLVL         B1U_HARP0_RDUPDATE      B1U_TNIM2_10SECAVG      B1U_YCB1_RDCUR
    B1UT_PT01_RDPRESS       B1U_HARP2_RDUPDATE      B1U_TNIM2_10SECTRIP     B1V_KICK_RDHICUR
    B1UT_PT02_RDPRESS       B1U_IV0_STATON          B1U_TNIM2_1SECAVG       B1V_KICK_STATON
    B1UT_PT50_RDPRESS       B1U_IV2_STATON          B1U_TNIM2_1SECTRIP      B1V_KSM_BONPRD
    B1U_B0_RDCUR            B1U_PNG0_RDVAC          B1U_TNIM2_5MINAVG       B1V_KSM_INSEQ
    B1U_B0_STATON           B1U_PNG2_RDVAC          B1U_TNIM2_RAW           B1V_KSM_PREDCUR
    B1U_BPM2A_RDCUR         B1U_Q1_STATON           B1U_TPMBOTTOM_RDVOL     B1V_KSM_RDBEAMOFF_VAL1
    B1U_BPM2A_RDX           B1U_Q1_VT_RDCUR         B1U_TPMHALO_RDVOL       B1V_KSM_RDBEAMON_VAL1
    B1U_BPM2A_RDY           B1U_Q2_RDCUR            B1U_TPMLEFT_RDVOL       B1V_KSM_RDFRCTN_VAL1
    B1U_BPM2B_RDCUR         B1U_Q2_STATON           B1U_TPMRIGHT_RDVOL      B1V_KSM_RDMODE_VAL1
    B1U_BPM2B_RDX           B1U_SEPT_RDCUR          B1U_TPMTOP_RDVOL        B1_FOIL_ADJCUR
    B1U_BPM2B_RDY           B1U_SEPT_STATON         B1U_WTEMP1_RDTEMP       timestamp
    B1U_COL2DOWN_RDTEMP     B1U_TGTTEMP1_RDTEMP     B1U_WTEMP2_RDTEMP
    B1U_COL2LEFT_RDTEMP     B1U_TGTTEMP2_RDTEMP     B1U_XCB1_RDCUR
```

Similarly, once a cycle is fetched, one can then access the periods within with [`ucncycle.get_period()`](../docs/ucndata.md#ucncycle). One can fetch all the cycles/periods by passing no parameter (or None) to the function.

## Slicing and Indexing

Since accessing the cycle and period views of the [ucnrun] are such a common thing to need in an analysis, the [ucnrun] object can be indexed as if it were a 2-dimensional array. The indexing follows the scheme of `[cycle, period]` and employs slicing. Thus,

```python
# the following statement
run.get_cycle(0)

# is equivalent to
run[0]
```

Similarly, fetching the entire cycle list is easily reduced:

```python
# the following statement
run.get_cycle()

# is equivalent to
run[:]
```

While this doesn't yet seem to be too beneficial, the true advantage comes when we want to start fetching periods:

```python
# the following statement
run.get_cycle(0).get_period(0)

# is equivalent to
run[0, 0]
```

And more so when we want to get a list of all the periods and cycles:

```python
# the following statements
list_of_cycles = []
for i in range(run.cycle_param.ncycles):
    list_of_periods = []
    for j in range(run.cycle_param.nperiods):
        list_of_periods.append(run.get_cycle(i).get_period(j))
    list_of_cycles.append(list_of_periods)

# is equivalent to
list_of_cycles = run[:, :]
```

All the usual slicing rules and syntax apply. Some examples:

```python
run[0, :]       # fetch all periods from cycle 0
run[:, 0]       # fetch period 0 from all cycles
run[2:5]        # fetch cycles 2, 3, and 4
run[2:5, 0]     # fetch period 0 from cycles 2, 3, and 4
run[2:5, :2]    # fetch periods 0 and 1 from cycles 2, 3, and 4
```

You can also treat the [ucnrun] object as an iterator for notational simplicity:

```python
for cycle in run:
    print(cycle)
```

## Cycle Start and End Times

Cycle timing is determined in two stages: a **crude** pass that runs automatically on load, and an optional **precise** pass that you call manually when sub-millisecond accuracy matters.

### Crude timing (automatic)

When a [ucnrun] object is created, `__init__` immediately calls [`set_cycle_times_crude()`](../docs/ucndata.md#ucnrunset_cycle_times_crude), which derives cycle start and end times from `SequencerTree.cycleStarted` timestamps. The result is stored in `cycle_param.cycle_times` and used by all subsequent cycle/period indexing.

If the sequencer is absent, a `DataError` is raised.

To re-run crude timing after loading (e.g. to reset after precise timing):

```python
run.set_cycle_times_crude()
```

`cycle_param.cycle_times` is updated in-place and `cycle_param.is_precise_timing` is set to `False`.

### Precise timing (automatic)

By default, [`set_cycle_times_precise()`](../docs/ucndata.md#ucnrunset_cycle_times_precise) is called automatically during `ucnrun.__init__` (controlled by `use_precise_cycles=True`). No manual call is needed for most analyses.

First, it checks whether `RunTransitions_Li6` already contains precise timestamps (as written by `midas2root`). If not, it falls back to reading raw hardware-trigger hits on a dedicated TV1725 digitizer channel (default channel 10). Either way, the resulting timestamps have sub-millisecond precision compared to the sequencer-derived crude times.

To disable precise timing at load time:

```python
run = ucnrun(2687, use_precise_cycles=False)
```

To re-run with a non-default channel after loading (e.g. if the default channel had no signal):

```python
run.set_cycle_times_precise(hw_channel=8)
```

Note: `set_cycle_times_precise()` will warn and return early if `cycle_param.is_precise_timing` is already `True`. Call `set_cycle_times_crude()` first to reset to crude timing before re-running with different parameters.

The function aligns hardware timestamps against the existing crude cycle grid:

* If the first hardware trigger was missed, it back-extrapolates from the average precise cycle duration.
* Gaps where the trigger was not recorded are filled by linear interpolation.
* After the last trigger, remaining cycles are forward-extrapolated.

After a successful call `cycle_param` is updated as follows:

| Attribute | Contents |
|---|---|
| `cycle_param.cycle_times` | Replaced with precise values |
| `cycle_param.period_end_times` | Replaced with precise values |
| `cycle_param.is_precise_timing` | Set to `True` |

The `cycle_times` DataFrame also gains an `is_measured` column: `True` if the start time came from a recorded hardware hit, `False` if it was extrapolated or interpolated. You can use this to flag cycles whose start time is estimated rather than directly measured.

If no hardware triggers are found on the requested channel the function returns without modifying `cycle_param`, so crude timing remains in effect.

---

[**Back to Index**](index.md)\
[**Next Page: Filtering Cycles**](filter.md)

[tfile]: #tfile
[DataFrame]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
[ttree]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md
[attrdict]:https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/attrdict.md
[rootloader]: https://github.com/ucn-triumf/rootloader
[ucnrun]: ../docs/ucnrun.md
[ucncycle]: ../docs/ucncycle.md
[ucnperiod]: ../docs/ucnperiod.md
[applylist]: ../docs/applylist.md
[read]: ../docs/read.md
[merge]: ../docs/merge.md
