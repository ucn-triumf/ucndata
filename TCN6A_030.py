# Run analysis for TCN6A-030: source lifetime measurement at 1 uA
# Derek Fujimoto
# June 2025

from storagelifetime import get_storage_cnts, get_lifetime, get_global_lifetime, draw_hits
from ucndata import settings, read, ucnrun
import os

# settings
settings.datadir = 'root_files'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
outfile = 'TCN6A_030/results.csv'   # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# periods settings
periods = {'production':  0,
        'storage':     1,
        'count':       2,
        'background':  1}

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# counts and hits
for run in runs:
    get_storage_cnts(run)
    draw_hits(run)

# calculate lifetimes for each run
for run in run_numbers:
    get_lifetime(run, outfile, fitfn)

# get global lifetime
par, std = get_global_lifetime(outfile, fitfn)
