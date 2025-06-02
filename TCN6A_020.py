# Run analysis for TCN6A-020: source saturation measurement at 1 uA
# Derek Fujimoto
# June 2025

from sourcesaturation import get_satur_cnts, draw_counts, draw_hits
from ucndata import settings, read, ucnrun
import os

# settings
settings.datadir = 'root_files'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
outfile = 'TCN6A_020/results.csv'   # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# periods settings
periods = {'production':  0,
           'count':       1,
           'background':  0}

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# counts and hits
for run in runs:
    get_satur_cnts(run, outfile, periods)
    draw_hits(run)
    draw_counts(run.run_number, outfile)

# draw all counts
draw_counts(None, outfile)