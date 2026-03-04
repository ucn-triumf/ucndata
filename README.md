# ucndata


<a href="https://pypi.org/project/ucndata/" alt="PyPI Version"><img src="https://img.shields.io/pypi/v/ucndata?label=PyPI%20Version"/></a>
<a href="https://github.com/ucn-triumf/ucndata/commits/master" alt="Commits"><img src="https://img.shields.io/github/last-commit/ucn-triumf/ucndata"/></a>

<img src="https://img.shields.io/pypi/format/ucndata?label=PyPI%20Format"/> <img src="https://img.shields.io/github/languages/code-size/ucn-triumf/ucndata"/> <img src="https://img.shields.io/pypi/l/ucndata"/>

This repository defines the `ucndata` package and a few scripts which utilize this package to analyze UCN ROOT files.

The `ucndata` package contained within has been installed system-wide on `daq04`. You will therefore be able to import it from any directory.

## ucndata quick links

* [Installation](tutorials/installation.md)
* [Getting Started](tutorials/gettingstarted.md)
* [Tutorial](tutorials/index.md)
* [Full API reference](docs/README.md)

## Quick API Reference

These are the main workhorses of the ucndata project:

* [ucnbase](docs/ucnbase.md) - base class for the following:
* [ucnrun](docs/ucnrun.md) - workhorse object representing a single run
* [ucncycle](docs/ucncycle.md) - workhorse object representing a single cycle within a run
* [ucnperiod](docs/ucnperiod.md) - workhorse object representing a single period within a cycle

But these can also be useful:

* [the chopper module](docs/chopper.md) - redefinition for working with chopper data
* [applylist](docs/applylist.md) - for working with sets of runs or cycles or periods. Does element-wise attribute access and operators
* [datetime](docs/datetime.md) - convert timestamps to datetime objects and back

## rootloader API

[rootloader] is a custom package which facilitates the reading of ROOT files in a more pythonic way than is provided by generic PyROOT. In general it attempts to make the various ROOT objects (histograms, trees) look like pandas dataframes. When you are looking at the contents of `ucnrun.tfile` you are looking at the [`rootloader.tfile`](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/tfile.md#tfile) object. Here are the reference for some of the more commonly found [rootloader] objects: 

* [`ttree`](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/ttree.md#ttree)
* [`th1`](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/th1.md#th1)
* [`tfile`](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/tfile.md#tfile)
* [`tdirectory`](https://github.com/ucn-triumf/rootloader/blob/main/docs/rootloader/tdirectory.md#tdirectory)

[rootloader]:https://github.com/ucn-triumf/rootloader