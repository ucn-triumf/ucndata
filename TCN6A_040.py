# Run analysis for TCN6A-040: source saturation measurement at varying beam energies
# Derek Fujimoto
# June 2025

from ucndata import settings, read, ucnrun
import os
import tools

# settings
settings.datadir = 'test'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
outfile = 'TCN6A_040/summary.csv'    # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# setup analyzer
ana = tools.Analyzer('saturation', outfile)

# counts and hits
for run in runs:
    ana.get_counts(run)
    ana.draw_hits(run)

# fit function to counts vs production times
@tools.prettyprint(r'$p_0 (1-\exp(-t/\tau))$', '$p_0$', r'$\tau$')
def fitfn(t, p0, tau):
    return p0*(1-np.exp(-t/tau))

# draw counts for each beam energy
df = pd.read_csv(outfile, comment='#')

# round to the nearest mA
df['beam_current_rounded (mA)'] = df['beam_current (mA)'].round()

plt.figure()
for current, g in df.groupby('beam_current_rounded (mA)'):

    tools.fit(fitfn,
        df['production duration (s)'],
        df['counts_norm (1/uA)']*current,
        df['dcounts_norm (1/uA)']*current,
        p0 = (1,1),
        err_kwargs = {
            'marker':'o',
            'ls':'none',
            'fillstyle':'none',
            'label':f'{current} uA'},
        )
plt.xlabel('Production Duration (s)')
plt.ylabel('UCN Counts Normalized to Current Setpoint')
plt.tight_layout()
plt.savefig('TCN6A_040/counts_norm.pdf')
