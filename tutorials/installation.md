# Installation

[**Back to Index**](index.md)\
[**Next Page: Getting Started**](gettingstarted.md)

---

This analysis package relies on relatively few prerequisites. The main one is that [ROOT must be installed](https://root.cern/install/) with PyROOT functionality. Note that ROOT must have been compiled with the same version of python that you will be using for your analysis.


## Simplest method

Install from the [python package index (PyPI)](https://pypi.org/project/ucndata/):

```bash
pip install ucndata
```

To update to the latest version after initial installation, run:

```bash
pip install --upgrade ucndata
```

## Developer method

1. Clone this repository

```bash
git clone https://github.com/ucn-triumf/ucndata.git
```

2. Go to the `ucndata` directory

```bash
cd ucndata
```

3. Install ucndata system-wide

```bash
pip install -e .
```

To update you will then only need to pull this repository.

You're ready to get started and can import `ucndata` from anywhere on your system. Any edits made to the files will be updated immediately without any further actions.

---

[**Back to Index**](index.md)\
[**Next Page: Getting Started**](gettingstarted.md)
