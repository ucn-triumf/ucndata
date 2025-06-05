# Run analysis for TCN6A-020: source saturation measurement at 1 uA
# Derek Fujimoto
# June 2025

import sourcesaturation
from sourcesaturation import get_satur_cnts, fit, draw_hits
from ucndata import settings, read, ucnrun
import os

# settings
settings.datadir = 'test'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
sourcesaturation.detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
outfile = 'TCN6A_020/summary.csv'   # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# counts and hits
for run in runs:
    get_satur_cnts(run, outfile)
    draw_hits(run, outdir=os.path.dirname(outfile))

# get results
df = pd.read_csv(outfile, comment='#')
df.sort_values('production duration (s)', inplace=True)

# draw counts normalized to 1 uA current
plt.figure()
fit(df['production duration (s)'],
    df['counts_norm (1/uA)'],
    df['dcounts_norm (1/uA)'],
    p0 = (1,1),
    err_kwargs = {
        'marker':'o',
        'ls':'none',
        'fillstyle':'none'},
    xlabel = 'Storage Duration (s)',
    ylabel = 'UCN Counts Normalized to 1 uA',
    outfile = 'TCN6A_020/fitpar_counts_norm.csv')

# draw raw counts
plt.figure()
fit(df['production duration (s)'],
    df['counts'],
    df['dcounts'],
    p0 = (1,1),
    err_kwargs = {
        'marker':'o',
        'ls':'none',
        'fillstyle':'none'},
    xlabel = 'Storage Duration (s)',
    ylabel = 'UCN Counts',
    outfile = 'TCN6A_020/fitpar_counts_raw.csv')
