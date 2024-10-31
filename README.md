# UCNanalysis

This repository defines the [ucndata] package and a few scripts which utilize this package to analyze data from the 2024 run.

## ucndata quick links

* [Installation](ucndata/tutorials/installation.md)
* [Getting Started](ucndata/tutorials/gettingstarted.md)
* [Tutorial](ucndata/tutorials/index.md)
* [Full API reference](ucndata/docs/README.md)

## Quick API Reference

These are the main workhorses of the ucndata project:

* [applylist](ucndata/docs/applylist.md) - for working with sets of runs or cycles or periods. Does element-wise attribute access and operators
* [merge](ucndata/docs/merge.md#merge) - function for merging runs into a single run
* [merge_inlist](ucndata/docs/merge.md#merge_inlist) - function for merging runs within a list
* [read](ucndata/docs/read.md) - convenience function for reading ucnruns from file
* [settings](ucndata/docs/settings.md) - change behaviour of ucnrun objects
* [ucnrun](ucndata/docs/ucnrun.md) - workhorse object representing a single run



## storagelifetime.py

This script takes storage-lifetime experiments with three periods per cycle (irradiation, storage, counting) that were performed without a monitor detector available during irradiation.
It takes the counts in either the He3 or the Li6 detector (whichever was used for counting) and determines the storage lifetime in two ways:
1. Subtract a fixed background rate and divide the background-corrected detector counts by the average beam current for ach cycle. Plot against duration of the storage period. A single-exponential fit determines the storage lifetime.
2. Plot the uncorrected and unnormalized counts against duration of the storage period and fit a single-exponential with background.

Results are saved to the storagelifetime directory.

[ucndata]: ucndata/README.md