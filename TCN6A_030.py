# Run analysis for TCN6A-030: source lifetime measurement at 1 uA
# Derek Fujimoto
# June 2025

import storagelifetime
from storagelifetime import get_storage_cnts, draw_hits, fit
from ucndata import settings, read, ucnrun
import os

# settings
settings.datadir = 'test'     # path to root data
settings.cycle_times_mode = 'beamon'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
storagelifetime.detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
outfile = 'TCN6A_030/counts.csv'   # save counts output
run_numbers = [1846, 1873, 1875]   # example: [1846, '1847+1848']

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
    get_storage_cnts(run, periods, outfile)
    draw_hits(run, outdir=os.path.dirname(outfile))

# get results
df = pd.read_csv(outfile, comment='#')
df.sort_values('storage duration (s)', inplace=True)

# draw counts normalized to 1 uA current
plt.figure()
fit(df['storage duration (s)'],
    df['counts_norm (1/uA)'],
    df['dcounts_norm (1/uA)'],
    p0 = (1,1),
    err_kwargs = {
        'marker':'o',
        'ls':'none',
        'fillstyle':'none'},
    xlabel = 'Storage Duration (s)',
    ylabel = 'UCN Counts Normalized to 1 uA',
    outfile = 'TCN6A_030/fit_counts_norm.csv')

# draw raw counts
plt.figure()
fit(df['storage duration (s)'],
    df['counts'],
    df['dcounts'],
    p0 = (1,1),
    err_kwargs = {
        'marker':'o',
        'ls':'none',
        'fillstyle':'none'},
    xlabel = 'Storage Duration (s)',
    ylabel = 'UCN Counts',
    outfile = 'TCN6A_030/fit_counts_raw.csv')
