# Draw counts vs current for irradiation times
# Derek Fujimoto
# June 2025

from ucndata import ucnrun
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import os

# worker fn
def fetch(run, df, cycle_num, outdf):

    start = run[cycle_num, 0].period_start
    stop = run[cycle_num, 0].period_stop

    current = run[cycle_num, 0].beam1u_current_uA
    current = current[current > 0]

    ncounts = df.loc[start:stop, 'Count'].sum()

    outdf['current'].append(current.mean())
    outdf['counts'].append(ncounts)
    outdf['run'].append(run.run_number)
    outdf['cycle_count'].append(cycle_num)
    outdf['start'].append(start)
    outdf['stop'].append(stop)


# get run data - 6A no foil
def extract_nofoil():
    """60/0/120"""
    runs = [2530, 2558, 2573, 2578, 2593]

    outdf = {'current': [],
             'counts': [],
             'run': [],
             'cycle_count': [],
             'start': [],
             'stop': [],
            }
    for runn in runs:

        run = ucnrun(runn)

        # get histogram for faster counting
        hist = run.get_hits_histogram('Li6', bin_ms=100)
        df = hist.to_dataframe()
        df.set_index('tUnixTimePrecise', inplace=True)
        df.sort_index(inplace=True)

        if runn == 2530:
            for cyclen in range(17):
                fetch(run, df, cyclen, outdf)

        elif runn==2558:
            for cyclen in range(26):
                fetch(run, df, cyclen, outdf)

        elif runn==2573:
            for cyclen in range(36):
                if cyclen in [2,3,5,23,24]:
                    continue
                fetch(run, df, cyclen, outdf)

        elif runn==2578:
            for cyclen in range(19):
                fetch(run, df, cyclen, outdf)

        elif runn==2593:
            for cyclen in range(10):
                fetch(run, df, cyclen, outdf)

    outdf = pd.DataFrame(outdf)
    outdf.to_csv('irradiation_nofoil.csv', index=False)

# RUN ===============================================

# extract_nofoil()

# draw sim data
plt.figure()

# draw with no foil
df = pd.read_csv('irradiation_nofoil.csv')
x = df.current
y = df.counts.copy()
dy = y**0.5

plt.errorbar(x, y, dy, fmt='o', label='Phase 6A (measured)', color='k', fillstyle='none')

# second axes
ax = plt.gca()
secax = ax.secondary_yaxis('right', functions=(lambda x: x/60/1e6, lambda x: x*60*1e6))

# linear fit
fn = lambda x, a: a*x
par, cov = curve_fit(fn, x, y, sigma=dy, absolute_sigma=True)
std = np.diag(cov)**0.5
fitx = np.linspace(0,40,10)
slope = par[0]
plt.plot(fitx, fn(fitx, *par), color='k')

ax.set_ylabel('UCN Counts / 60 s')
ax.set_xlabel(r'Beam Current ($\mu$A)')
secax.set_ylabel('UCN Count Rate (MHz)')
plt.legend(fontsize='x-small')
plt.tight_layout()
plt.savefig('6A_counts_irradiation.pdf')

# residuals
# plt.figure()
# plt.errorbar(x, fn(x, *par)-y, dy, fmt='ok')