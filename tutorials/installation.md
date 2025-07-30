# Installation

[**Back to Index**](index.md)\
[**Next Page: Getting Started**](gettingstarted.md)

---

This analysis package relies on relatively few prerequisites. The main one is that [ROOT must be installed](https://root.cern/install/) with PyROOT functionality. Note that ROOT must have been compiled with the same version of python that you will be using for your analysis.

You should install ucndata on your python path. Here is the full installation steps

1. Clone this repository

```bash
git clone https://github.com/ucn-triumf/UCNanalysis.git
```

2. Switch to the correct branch

```bash
git checkout 2025
```

3. Go to the `ucndata` directory

```bash
cd UCNanalysis/ucndata
```

4. Install ucndata system-wide

```bash
pip install -e .
```

To update you will then only need to pull this repository.

You're ready to get started and can import `ucndata` from anywhere on your system.

---

[**Back to Index**](index.md)\
[**Next Page: Getting Started**](gettingstarted.md)
