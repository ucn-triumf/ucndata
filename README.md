# UCNanalysis

This repository defines the [ucndata] package and a few scripts which utilize this package to analyze data from the 2024 run.

The `ucndata` package contained within has been installed system-wide on daq04. You will therefore be able to import it from any directory.

## ucndata quick links

* [Installation](ucndata/tutorials/installation.md)
* [Getting Started](ucndata/tutorials/gettingstarted.md)
* [Tutorial](ucndata/tutorials/index.md)
* [Full API reference](ucndata/docs/README.md)

## Quick API Reference

These are the main workhorses of the ucndata project:

* [applylist](ucndata/docs/applylist.md) - for working with sets of runs or cycles or periods. Does element-wise attribute access and operators
* [read](ucndata/docs/read.md) - convenience function for reading ucnruns from file
* [settings](ucndata/docs/settings.md) - change behaviour of ucnrun objects
* [datetime](ucndata/docs/datetime.md) - convert timestamps to datetime objects and back
* [ucnbase](ucndata/docs/ucnbase.md) - base class for the following:
  * [ucnrun](ucndata/docs/ucnrun.md) - workhorse object representing a single run
  * [ucncycle](ucndata/docs/ucncycle.md) - workhorse object representing a single cycle within a run
  * [ucnperiod](ucndata/docs/ucnperiod.md) - workhorse object representing a single period within a cycle

## storagelifetime.py

This script takes storage-lifetime experiments with three periods per cycle (irradiation, storage, counting) that were performed without a monitor detector available during irradiation.
It takes the counts in the Li6 detector and determines the storage lifetime in the following way:

Subtract the background rate (irradiation period) and divide the background-corrected detector counts by the average beam current for each cycle. Plot against duration of the storage period. A single-exponential fit determines the storage lifetime. Fitting routine is Minuit. This is executed in two contexts:

1. On a run-by-run basis
2. With a global fit: shared lifetime but variable scaling coefficient

Results are saved to the `storagelifetime` directory:

1. Figures as pdfs
2. A csv file with the storage lifetimes and counts
3. A csv file with the fit parameters and errors

## sourcesaturation.py

This script takes source saturation experiments with two periods per cycle (irradiation, counting) that were performed without a monitor detector available during irradiation.
It takes the counts in the Li6 detector and subtracts the background rate, then divides by the average beam current for each cycle. Plot against duration of the irradiation period.

Results are saved to the `sourcesaturation` directory:

1. Figures as pdfs
2. A csv file with the irradiation durations and counts

[ucndata]: ucndata/README.md
