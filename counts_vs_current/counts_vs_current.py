# Draw counts vs current for measurements and simulation
# Derek Fujimoto
# June 2025

from ucndata import ucnrun
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import os

# simulation data
sim = pd.DataFrame({'current': [1, 5.5, 8.16, 11, 16.12, 22, 24.08, 32.04, 36.6, 40, ],
                    # 'PENTrack (Sidhu)': [2.45e6, np.nan, 2.00e7, np.nan,3.49e7, np.nan,4.39e7,5.00e7, np.nan,5.27e7],
                    'LD2, D2O Correction': [3.85e4, np.nan, 3.14e5, np.nan, 5.48e5, np.nan, 6.90e5, 7.86e5, np.nan, 8.28e5,],
                    'Isopure Fill Correction':[3.25e4, np.nan, 2.65e5, np.nan, 4.63e5, np.nan, 5.82e5, 6.63e5, np.nan, 6.99e5,],
                    'HePak':[3.00e4, np.nan, 2.45e5, np.nan, 4.28e5, np.nan, 5.38e5, 6.13e5, np.nan, 6.46e5, ]})
sim.set_index('current', inplace=True)

# get run data - 6A with foil
def extract_withfoil(draw=False):
    runs = [2666] # 2663, 2665,

    df = {'current': [],
          'counts': [],
          'background': [],
          'run': [],
          'cycle_count': [],
          'cycle_bkgd': []}
    for runn in runs:

        run = ucnrun(runn)

        if runn == 2663:
            run.modify_timing(0,2,1,0)
            run.modify_timing(1,1,1,0)
            fetch(run, 0, 1, 1, df, draw)

        elif runn == 2665:
            run.modify_timing(0,2,1,0)
            fetch(run, 0, 1, 1, df, draw)

        if runn == 2666:
            fetch(run, 0, 1, 1, df, draw)

            run.modify_timing(8,3,0,-120)
            fetch(run, 9, 8, 3, df, draw)

        df = pd.DataFrame(df)
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

# worker fn
def fetch(run, countc, bkdgc, bkdgp, df, draw=False):
    current = run[countc,0].beam1u_current_uA
    current = current[current > 0]
    df['current'].append(current.mean())
    df['counts'].append(run[countc,2].get_nhits('Li6'))
    df['background'].append(run[bkdgc, bkdgp].get_nhits('Li6'))
    df['run'].append(run.run_number)
    df['cycle_count'].append(countc)
    df['cycle_bkgd'].append(bkdgc)

    # get last 20s of the background and cycle
    run.modify_timing(countc, 2, 100, 0)
    run.modify_timing(bkdgc, bkdgp, 100, 0)

    df['cycle_last_20s'].append(run[countc,2].get_nhits('Li6'))
    df['bkgd_last_20s'].append(run[bkdgc, bkdgp].get_nhits('Li6'))

    # undo modify
    run.modify_timing(countc, 2, -100, 0)
    run.modify_timing(bkdgc, bkdgp, -100, 0)

    if draw:
        hist = run[countc,2].get_hits_histogram('Li6', bin_ms=1000)
        histb = run[bkdgc,bkdgp].get_hits_histogram('Li6', bin_ms=1000)

        hist.x -= hist.x[0]
        histb.x -= histb.x[0]

        plt.figure()
        hist.plot(ax=plt.gca(), color='k', label='Count period')
        histb.plot(ax=plt.gca(), color='r', label='Background period')

        histb.y *= df['cycle_last_20s'][-1]/df['bkgd_last_20s'][-1]
        histb.plot(ax=plt.gca(), color='g', label='Background rescaled')

        plt.xlabel('Time since period start (s)', fontsize='medium')
        plt.ylabel('UCN Counts')
        plt.yscale('linear')
        plt.legend(fontsize='xx-small')
        plt.title(f'Run {run.run_number}, cycle {countc}, bkgd cycle {bkdgc}', fontsize='x-small')
        plt.tight_layout()
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/r{run.run_number}_c{countc}_b{bkdgc}.pdf')
        plt.pause(1)

# get run data - 6A no foil
def extract_nofoil_0storage(draw=False):
    """60/0/120"""
    runs = [2530, 2558, 2573, 2578, 2593]

    df = {'current': [],
          'counts': [],
          'background': [],
          'run': [],
          'cycle_count': [],
          'cycle_bkgd': [],
          'cycle_last_20s': [],
          'bkgd_last_20s': []}
    for runn in runs:

        run = ucnrun(runn)

        if runn == 2530:
            run.modify_timing(1,1,0,-40)
            fetch(run, 0, 1, 1, df, draw)

            run.modify_timing(9,1,0,-40)
            fetch(run, 8, 9, 1, df, draw)

            fetch(run, 16, 9, 1, df, draw)

        elif runn==2558:
            fetch(run, 0, 1, 1, df, draw)
            fetch(run, 9, 10, 1, df, draw)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 18, 17, 3, df, draw)

        elif runn==2573:
            fetch(run, 0, 1, 1, df, draw)
            fetch(run, 9, 10, 1, df, draw)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 18, 17, 3, df, draw)

            fetch(run, 27, 28, 1, df, draw)

        elif runn==2578:
            fetch(run, 0, 1, 1, df, draw)

            run.modify_timing(9,2,1,1)
            run.modify_timing(8,3,1,1)
            run.modify_timing(8,3,0,-120)
            fetch(run, 9, 8, 3, df, draw)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 18, 17, 3, df, draw)

        elif runn==2593:
            fetch(run, 0, 1, 1, df, draw)

            run.modify_timing(9,2,1,1)
            run.modify_timing(8,3,1,1)
            run.modify_timing(8,3,0,-120)
            fetch(run, 9, 8, 3, df, draw)

    df = pd.DataFrame(df)
    df.to_csv('nofoil_0s.csv', index=False)

# extract_withfoil(True)
# extract_nofoil_10storage()
# extract_nofoil_0storage(True)

# draw sim data
plt.figure()
markers = 'xs^'
for col, m in zip(sim.columns, markers):
    sim[col].plot(marker=m, fillstyle='none', ls='none', label=col)

# draw with no foil
df = pd.read_csv('nofoil_0s.csv')
x = df.current
y = df.counts.copy()
by = df.background.copy()
dy = y**0.5
dby = by**0.5

# rescale the background
by_last = df.bkgd_last_20s
y_last = df.cycle_last_20s

dby_last = by_last**0.5
dy_last = y_last**0.5

factor = y_last / by_last
dfactor = factor * ((dby_last/by_last)**2 + (dy_last/y_last)**2)**0.5

dby = factor*by * ((dby/by)**2 + (dfactor/factor)**2)**0.5
by *= factor

# backgground subtraction
dy = (dy**2+dby**2)**0.5
y -= by

df['counts_corr'] = y
df['dcounts_corr'] = dy

plt.errorbar(x, y, dy, fmt='o', label='Phase 6A (measured)', color='k', fillstyle='none')

# linear fit
fn = lambda x, a: a*x
par, cov = curve_fit(fn, x, y, sigma=dy, absolute_sigma=True)
std = np.diag(cov)**0.5
fitx = np.linspace(0,40,10)
plt.plot(fitx, fn(fitx, *par), color='k')

# get with foil data
df_foil = pd.read_csv('withfoil.csv')

xf = df_foil.current
yf = df_foil.counts.copy()
byf = df_foil.background.copy()
dyf = y**0.5
dbyf = by**0.5

dyf = (dy**2+dby**2)**0.5
yf -= by

df_foil['counts_corr'] = yf
df_foil['dcounts_corr'] = dyf

idx = df.current < 2
scaling_factor = df_foil.counts_corr.mean()/df.loc[idx, 'counts_corr'].mean()
dscaling_factor = scaling_factor*((df_foil.counts_corr.std()/df_foil.counts_corr.mean())**2 + \
                    (df.loc[idx, 'counts_corr'].std()/df.loc[idx, 'counts_corr'].mean())**2)**0.5

central_slope = par[0] * scaling_factor
dcentral_slope = par[0] * scaling_factor * ((std[0]/par[0])**2 + (dscaling_factor/scaling_factor)**2)**0.5

plt.fill_between(fitx, fn(fitx, central_slope-dcentral_slope), fn(fitx, central_slope+dcentral_slope),
                color='gray', alpha=0.2, label='Phase 6A (rescaled for foil)')

plt.ylabel('UCN Counts / 120 s')
plt.xlabel(r'Beam Current ($\mu$A)')
plt.legend(fontsize='x-small')
plt.tight_layout()
plt.savefig('6A_counts.pdf')