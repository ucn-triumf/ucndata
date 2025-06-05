# Run analysis for TCN6A-040: source saturation measurement at varying beam energies
# Derek Fujimoto
# June 2025

import sourcesaturation
from sourcesaturation import get_satur_cnts, fit, draw_hits
from ucndata import settings, read, ucnrun
import os

# settings
settings.datadir = 'root_files'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
sourcesaturation.detector = 'Li6'   # detector to use when getting counts [Li6|He3]
outfile = 'TCN6A_040/summary.csv'    # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# counts and hits
for run in runs:
    get_satur_cnts(run, outfile, periods)
    draw_hits(run, outdir=os.path.dirname(outfile))

# draw counts for each beam energy
df = pd.read_csv(outfile, comment='#')

# round to the nearest mA
df['beam_current_rounded (mA)'] = df['beam_current (mA)'].round()

plt.figure()
for current, g in df.groupby('beam_current_rounded (mA)'):

    fit(df['production duration (s)'],
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
