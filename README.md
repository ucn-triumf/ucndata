# UCNanalysis

This repository defines the [ucndata] package and a few scripts which utilize this package to analyze data from the 2025 run.

The `ucndata` package contained within has been installed system-wide on `daq04`. You will therefore be able to import it from any directory.

## ucndata quick links

* [Installation](ucndata/tutorials/installation.md)
* [Getting Started](ucndata/tutorials/gettingstarted.md)
* [Tutorial](ucndata/tutorials/index.md)
* [Full API reference](ucndata/docs/README.md)

## Quick API Reference

These are the main workhorses of the ucndata project:

* [applylist](ucndata/docs/applylist.md) - for working with sets of runs or cycles or periods. Does element-wise attribute access and operators
* [datetime](ucndata/docs/datetime.md) - convert timestamps to datetime objects and back
* [ucnbase](ucndata/docs/ucnbase.md) - base class for the following:
  * [ucnrun](ucndata/docs/ucnrun.md) - workhorse object representing a single run
  * [ucncycle](ucndata/docs/ucncycle.md) - workhorse object representing a single cycle within a run
  * [ucnperiod](ucndata/docs/ucnperiod.md) - workhorse object representing a single period within a cycle

[ucndata]: ucndata/README.md
