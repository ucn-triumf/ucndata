# Run analysis for TCN6A-030: source lifetime measurement at 1 uA
# Derek Fujimoto
# June 2025

from ucndata import settings, read, ucnrun
import os
import tools

# settings
settings.datadir = 'test'     # path to root data
settings.cycle_times_mode = 'beamon'# what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
outfile = 'TCN6A_030/summary.csv'   # save counts output
run_numbers = [1846, 1873, 1875]    # example: [1846, '1847+1848']

# check existing runs to skip re-analysis of counts
old = pd.read_csv(outfile, comment='#')
run_numbers = [r for r in run_numbers if r not in old['run']]

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# setup analyzer
ana = tools.Analyzer('lifetime', outfile)

# counts and hits
for run in runs:       
    ana.get_counts(run)
    ana.draw_hits(run)

# fit function to counts vs lifetimes
@tools.prettyprint(r'$p_0 \exp(-t/\tau)$', '$p_0$', r'$\tau$')
def fitfn(t, p0, tau):
    return p0*np.exp(-t/tau)

# get results
df = pd.read_csv(outfile, comment='#')
df.sort_values('storage duration (s)', inplace=True)

# draw counts normalized to 1 uA current
plt.figure()
tools.fit(fitfn,
        df['storage duration (s)'],
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
tools.fit(fitfn,
    df['storage duration (s)'],
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
