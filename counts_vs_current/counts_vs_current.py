# Draw counts vs current for measurements and simulation
# Derek Fujimoto
# June 2025

from ucndata import ucnrun
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# simulation data
sim = pd.DataFrame({'current': [1, 5.5, 8.16, 11, 16.12, 22, 24.08, 32.04, 36.6, 40, ],
                    # 'PENTrack (Sidhu)': [2.45e6, np.nan, 2.00e7, np.nan,3.49e7, np.nan,4.39e7,5.00e7, np.nan,5.27e7],
                    'LD2, D2O Correction': [3.85e4, np.nan, 3.14e5, np.nan, 5.48e5, np.nan, 6.90e5, 7.86e5, np.nan, 8.28e5,],
                    'Isopure Fill Correction':[3.25e4, np.nan, 2.65e5, np.nan, 4.63e5, np.nan, 5.82e5, 6.63e5, np.nan, 6.99e5,],
                    'HePak':[3.00e4, np.nan, 2.45e5, np.nan, 4.28e5, np.nan, 5.38e5, 6.13e5, np.nan, 6.46e5, ]})
sim.set_index('current', inplace=True)

# get run data - 6A with foil
def extract_withfoil():
    runs = [2666] # 2663, 2665,

    withfoil = {'current': [],
                'counts': [],
                'background': []}
    for runn in runs:

        run = ucnrun(runn)

        # if runn == 2663:
        #     run.modify_timing(0,2,1,0)
        #     run.modify_timing(1,1,1,0)
        #     withfoil['current'].append(run[0,0].beam1u_current_uA.mean())
        #     withfoil['counts'].append(run[0,2].get_nhits('Li6'))
        #     withfoil['background'].append(run[1,1].get_nhits('Li6'))

        # elif runn == 2665:
        #     run.modify_timing(0,2,1,0)
        #     withfoil['current'].append(run[0,0].beam1u_current_uA.mean())
        #     withfoil['counts'].append(run[0,2].get_nhits('Li6'))
        #     withfoil['background'].append(run[1,1].get_nhits('Li6'))

        if runn == 2666:
            withfoil['current'].append(run[0,0].beam1u_current_uA.mean())
            withfoil['counts'].append(run[0,2].get_nhits('Li6'))
            withfoil['background'].append(run[1,1].get_nhits('Li6'))

            run.modify_timing(8,3,0,-120)
            withfoil['current'].append(run[9,0].beam1u_current_uA.mean())
            withfoil['counts'].append(run[9,2].get_nhits('Li6'))
            withfoil['background'].append(run[8,3].get_nhits('Li6'))

        df = pd.DataFrame(withfoil)
        df.to_csv('withfoil.csv', index=False)

# get run data - 6A no foil
def extract_nofoil_10storage():
    """100/10/120"""
    runs = [2548,2551,2549,2575,2579,2585]

    df = {'current': [],
          'counts': [],
          'background': []}
    for runn in runs:

        run = ucnrun(runn)

        if runn == 2548:
            current = run[0,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[0,2].get_nhits('Li6'))
            df['background'].append(run[1,3].get_nhits('Li6'))

            current = run[2,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[2,2].get_nhits('Li6'))
            df['background'].append(run[3,3].get_nhits('Li6'))

        elif runn == 2551:

            current = run[0,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[0,2].get_nhits('Li6'))
            df['background'].append(run[1,3].get_nhits('Li6'))

            current = run[2,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[2,2].get_nhits('Li6'))
            df['background'].append(run[1,3].get_nhits('Li6'))

        elif runn == 2549:
            current = run[0,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[0,2].get_nhits('Li6'))
            df['background'].append(run[1,3].get_nhits('Li6'))

            current = run[2,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[2,2].get_nhits('Li6'))
            df['background'].append(run[1,3].get_nhits('Li6'))

        elif runn == 2575:
            current = run[0,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[0,2].get_nhits('Li6'))
            df['background'].append(run[4,3].get_nhits('Li6'))

            current = run[2,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[2,2].get_nhits('Li6'))
            df['background'].append(run[4,3].get_nhits('Li6'))

            current = run[3,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[3,2].get_nhits('Li6'))
            df['background'].append(run[4,3].get_nhits('Li6'))

        elif runn == 2579:
            for i in [5,6,9,11,12]:
                current = run[i,0].beam1u_current_uA
                current = current[current > 0]
                df['current'].append(current.mean())
                df['counts'].append(run[i,2].get_nhits('Li6'))
                df['background'].append(run[10,3].get_nhits('Li6'))

        elif runn == 2585:
            for i in [0,2,3]:
                current = run[i,0].beam1u_current_uA
                current = current[current > 0]
                df['current'].append(current.mean())
                df['counts'].append(run[i,2].get_nhits('Li6'))
                df['background'].append(run[1,3].get_nhits('Li6'))

    df = pd.DataFrame(df)
    df.to_csv('nofoil.csv', index=False)

# get run data - 6A no foil
def extract_nofoil_0storage():
    """60/0/120"""
    runs = [2530, 2558, 2573, 2578, 2593]

    df = {'current': [],
          'counts': [],
          'background': [],
          'run': [],
          'cycle_count': [],
          'cycle_bkgd': []}
    for runn in runs:

        run = ucnrun(runn)

        if runn == 2530:

            i=0
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            run.modify_timing(1,1,0,-40)
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=8
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            run.modify_timing(9,1,0,-40)
            df['background'].append(run[9,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=16
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[9,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(9)

        elif runn==2558:
            i=0
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=9
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=18
            run.modify_timing(i,2,1,1)
            run.modify_timing(i-1,3,1,1)
            run.modify_timing(i-1,3,0,-120)
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i-1,3].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i-1)

        elif runn==2573:
            i=0
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=9
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=18
            run.modify_timing(i,2,1,1)
            run.modify_timing(i-1,3,1,1)
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            run.modify_timing(i-1,3,0,-120)
            df['background'].append(run[i-1,3].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i-1)

            i=27
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

        elif runn==2578:
            i=0
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=9
            run.modify_timing(i,2,1,1)
            run.modify_timing(i-1,3,1,1)
            run.modify_timing(i-1,3,0,-120)
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i-1,3].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i-1)

            i=18
            run.modify_timing(i,2,1,1)
            run.modify_timing(i-1,3,1,1)
            run.modify_timing(i-1,3,0,-120)
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i-1,3].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i-1)

        elif runn==2593:
            i=0
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i+1,2].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i+1)

            i=9
            run.modify_timing(i,2,1,1)
            run.modify_timing(i-1,3,1,1)
            run.modify_timing(i-1,3,0,-120)
            current = run[i,0].beam1u_current_uA
            current = current[current > 0]
            df['current'].append(current.mean())
            df['counts'].append(run[i,2].get_nhits('Li6'))
            df['background'].append(run[i-1,3].get_nhits('Li6'))
            df['run'].append(run.run_number)
            df['cycle_count'].append(i)
            df['cycle_bkgd'].append(i-1)

    df = pd.DataFrame(df)
    df.to_csv('nofoil_0s.csv', index=False)

# extract_withfoil()
# extract_nofoil_10storage()
# extract_nofoil_0storage()

# draw sim data
plt.figure()
markers = 'xs^'
for col, m in zip(sim.columns, markers):
    sim[col].plot(marker=m, fillstyle='none', ls='none', label=col)

# draw with no foil
df = pd.read_csv('nofoil_0s.csv')
x = df.current
y = df.counts
by = df.background
dy = y**0.5
dby = by**0.5

dy = (dy**2+dby**2)**0.5
y -= by

plt.errorbar(x, y, dy, fmt='o', label='Phase 6A (measured)', color='k', fillstyle='none')

# linear fit
fn = lambda x, a: a*x
par, cov = curve_fit(fn, x, y, sigma=dy, absolute_sigma=True)
fitx = np.linspace(0,40,10)
plt.plot(fitx, fn(fitx, *par), color='k')


plt.ylabel('UCN Counts / 120 s')
plt.xlabel(r'Beam Current ($\mu$A)')
# plt.yscale('log')
plt.legend(fontsize='x-small')
plt.tight_layout()
plt.savefig('6A_counts.pdf')