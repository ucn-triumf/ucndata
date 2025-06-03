# Run analysis for TCN6A-040: source saturation measurement at varying beam energies
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
outfile = 'TCN6A_040/results.csv'   # save counts output
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

# draw counts for each beam energy
df = pd.read_csv(outfile, comment='#')

# round to the nearest mA
df['beam_current (mA)'] = df['beam_current (mA)'].round()

plt.figure()
ax = plt.gca()
for current in df['beam_current (mA)'].unique():
    draw_counts(df.loc[df['beam_current (mA)'] == current],
                ax = ax,
                marker='o',
                fillstyle='none',
                label=f'{current} mA')
plt.tight_layout()

# TODO: determine what the saturation time is!