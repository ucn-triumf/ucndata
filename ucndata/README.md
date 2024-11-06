# UCN DATA

Based on [rootloader], read ROOT files with ucndata, output from [midas2root], and do analysis-common tasks.

The goals of this package are as follows:

* Simplify analyses by organizing data into cycles and periods
* Allow for quick file inspection

## Useful Links

* Full API Documentation [here](docs/README.md).
* Tutorials and Getting Started [here](tutorials/index.md)


## Useful Objects

These are the main workhorses of the ucndata project:

* [applylist](docs/applylist.md) - for working with sets of runs or cycles or periods. Does element-wise attribute access and operators
* [merge](docs/merge.md) - merge runs into a single run
* [merge_inlist](docs/merge.md#merge_inlist) - function for merging runs within a list
* [read](docs/read.md) - convenience function for reading ucnruns from file
* [settings](docs/settings.md) - change behaviour of ucnrun objects
* [ucnrun](docs/ucnrun.md) - workhorse object representing a single run

## Generate documentation

Run the following:

```bash
./gen_documentation.bash
```


[rootloader]: https://github.com/ucn-triumf/rootloader
[midas2root]: https://github.com/ucn-triumf/ucn_detector_analyzer/tree/2024