# Contents of a ucnrun

[**Back to Index**](index.md)\
[**Next Page: Loading Runs Efficiently in an Environment**](read.md)

---

### Table of Contents

- [Contents of a ucnrun](#contents-of-a-ucnrun)
    - [Table of Contents](#table-of-contents)
  - [`cycle_param`](#cycle_param)
  - [`tfile`](#tfile)
  - [`ttree` objects](#ttree-objects)


Recall that when we load our run we have the following header values:

```python
In [1]: from ucndata import ucnrun
In [2]: run = ucnrun(2687)
In [3]: run
Out[3]:
run 2687:
  comment            experiment_number  run_number         start_time         year
  cycle_param        month              run_title          stop_time
  epics              path               shifters           tfile
```

These are defined as follows:

* `comment`: Comment input by users at start of run
* `cycle_param`: Cycle and period parameters and timings
* `epics`: object with all the epics ttree branches for easy access
* `experiment_number`: Experiment number, actually a string
* `month`: Month in which the run was started
* `run_number`: Run number
* `run_title`: A title for the run
* `shifters`: Names of those on shift at the time
* `start_time`: Start time, human-readable
* `stop_time`: Stop time, human-readable (may not be accurate?)
* `tfile`: All file contents which were read
* `year`: Year in which the run was conducted

Most of these variables are simple strings or integers but there are two important attributes you should pay attention to: `cycle_param` and `tfile`.

## `cycle_param`

This object is an [attrdict] defined in the [rootloader] package. This is simply a dictionary whose contents can be accessed either in the normal way, or as an attribute. This allows for tab-completion in the interpreter.

Let's inspect the contents of this attribute:

```python
In [4]: run.cycle_param
Out[4]: attrdict: {'nperiods', 'nsupercyc', 'enable', 'inf_cyc_enable', 'cycle', 'supercycle', 'valve_states', 'period_end_times', 'period_durations_s', 'ncycles', 'filter', 'cycle_times'}
```

These are the various settings and properties of each cycle and period.

* `nperiods`: Number of periods in each cycle
* `nsupercyc`: Number of supercycles contained in the run
* `enable`: Enable status of the sequencer
* `inf_cyc_enable`: Enable status of infinite cycles
* `cycle`: Cycle ID numbers
* `supercycle`: Supercycle ID numbers
* `valve_states`: Valve states in each period and cycle
* `period_end_times`: End time of each period in each cycle in epoch time - used to calculate period timings
* `period_durations_s`: Duration in sections of each period in each cycle (calculated from `period_end_times`)
* `ncycles`: Number of total cycles contained in the run
* `filter`: A list indicating how we should filter cycles. More on that in [filters](filters.md)
* `cycle_time`: The start and end times of each cycle

## `tfile`

This is a [tfile](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/tfile.md) object from the [rootloader] package. It is effectively an [attrdict] with some embellishment for reading root files. This is the object which contains all your data read from the file. Its contents can be either [ttree] objects (again, based on the [attrdict] object) or a pandas [DataFrame]. These can be converted relatively easily. First, inspecting with its contents as [ttree]s:

```python
In [5]: run.tfile
Out[5]:
contents:
    BeamlineEpics            RunTransitions_Li-6      hitsinsequence_he3
    CycleParamTree           SequencerTree            hitsinsequence_li6
    LNDDetectorTree          UCNHits_He3              hitsinsequencecumul_he3
    RunTransitions_He3       UCNHits_Li-6             hitsinsequencecumul_li6
    RunTransitions_He3Det2   header

In [6]: run.tfile.BeamlineEpics
Out[6]:
ttree branches:
    B1UT_CM01_RDCOND        B1U_IV2_STATON          B1U_TPMLEFT_RDVOL
    B1UT_CM02_RDCOND        B1U_PNG0_RDVAC          B1U_TPMRIGHT_RDVOL
    B1UT_LM50_RDLVL         B1U_PNG2_RDVAC          B1U_TPMTOP_RDVOL
    B1UT_PT01_RDPRESS       B1U_Q1_STATON           B1U_WTEMP1_RDTEMP
    B1UT_PT02_RDPRESS       B1U_Q1_VT_RDCUR         B1U_WTEMP2_RDTEMP
    B1UT_PT50_RDPRESS       B1U_Q2_RDCUR            B1U_XCB1_RDCUR
    B1U_B0_RDCUR            B1U_Q2_STATON           B1U_YCB0_RDCUR
    B1U_B0_STATON           B1U_SEPT_RDCUR          B1U_YCB0_STATON
    B1U_BPM2A_RDCUR         B1U_SEPT_STATON         B1U_YCB1_RDCUR
    B1U_BPM2A_RDX           B1U_TGTTEMP1_RDTEMP     B1V_KICK_RDHICUR
    B1U_BPM2A_RDY           B1U_TGTTEMP2_RDTEMP     B1V_KICK_STATON
    B1U_BPM2B_RDCUR         B1U_TNIM2_10MINAVG      B1V_KSM_BONPRD
    B1U_BPM2B_RDX           B1U_TNIM2_10MINTRIP     B1V_KSM_INSEQ
    B1U_BPM2B_RDY           B1U_TNIM2_10SECAVG      B1V_KSM_PREDCUR
    B1U_COL2DOWN_RDTEMP     B1U_TNIM2_10SECTRIP     B1V_KSM_RDBEAMOFF_VAL1
    B1U_COL2LEFT_RDTEMP     B1U_TNIM2_1SECAVG       B1V_KSM_RDBEAMON_VAL1
    B1U_COL2RIGHT_RDTEMP    B1U_TNIM2_1SECTRIP      B1V_KSM_RDFRCTN_VAL1
    B1U_COL2UP_RDTEMP       B1U_TNIM2_5MINAVG       B1V_KSM_RDMODE_VAL1
    B1U_HARP0_RDUPDATE      B1U_TNIM2_RAW           B1_FOIL_ADJCUR
    B1U_HARP2_RDUPDATE      B1U_TPMBOTTOM_RDVOL     timestamp
    B1U_IV0_STATON          B1U_TPMHALO_RDVOL
```

## `ttree` objects

Most of the contents of the `tfile` object in a [ucnrun] are [ttree]s from the [rootloader] package. Because the trees with the UCN hits can be large, we may not be able to load the entire tree into memory. Thus, beware of the `ttree.to_dataframe()` function. While very useful on smaller trees, this can crash your computer if the tree is too large. To avoid this problem, the [ttree] uses [pyroot](https://root.cern/manual/python/) under the hood to compute the key quantities that most users will need. This also implements ROOT's implicit multithreading support to improve performance.

For consistency with most analysis the [ttree] is written to look similar to a pandas [DataFrame]. In actuality, the data is stored in a ROOT [RDataFrame](https://root.cern/doc/master/classROOT_1_1RDataFrame.html) and makes heavy use of the [Filter](https://root.cern/doc/master/classROOT_1_1RDF_1_1RInterface.html#ad6a94ba7e70fc8f6425a40a4057d40a0) function. This allows one to pre-select rows based on a set of conditions. However, it means that for all operations, all rows get evaluated. Thus, if you want to histogram the counts in a particular cycle, first a filter is applied to select UCN hits, then on the timestamps to select the cycle. Then, the entire dataset is evaluated to determine whether the conditions are met. While the process is fast and exceedingly memory-efficient, it can still take a long time for large datasets.

Thus it is more efficient to do this:

```python
run = ucnrun(2575)

```


vs this:

```python
run = ucnrun(2575)

```

To improve efficiency, the [ttree]s try to save any and all results computed at the conclusion of the computation, such that if they are requested a second time, the code returns the alread-computed result. For example:

```python
In [1]: from ucndata import ucnrun
In [2]: import time
In [3]: run = ucnrun(2575)
Run 2575: Cycle time detection mode matched failed
Run 2575: Set cycle times based on li6 detection mode
In [4]: t0=time.time(); run.tfile.UCNHits_Li6.size; print(f'{time.time()-t0:g} s')
10.2543 s
In [5]: t0=time.time(); run.tfile.UCNHits_Li6.size; print(f'{time.time()-t0:g} s')
3.71933e-05 s
```


---

[**Back to Index**](index.md)\
[**Next Page: Loading Runs Efficiently in an Environment**](read.md)


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
