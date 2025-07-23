# Check how the backgrounds change over time with the Li6 data
# Derek Fujimoto
# Jul 2025

from ucndata import ucnrun
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
from iminuit import Minuit
from iminuit.cost import LeastSquares
import os
from glob import glob

os.makedirs('hists', exist_ok=True)
os.makedirs('fits', exist_ok=True)

# worker fn - extract data from run
def fetch(run, bkdgc, bkdgp):
    current = run[bkdgc,0].beam1u_current_uA
    current = current[current > 0]
    current = current.mean()

    # get background histogram
    hist = run[bkdgc, bkdgp].get_hits_histogram('Li6', bin_ms=1000)
    hist = hist.to_dataframe()
    hist.drop(columns=['Count error'], inplace=True)
    hist.set_index('tUnixTimePrecise', inplace=True)
    hist.sort_index(inplace=True)

    # save histogram to file
    filename = f'hists/{run.run_number}_{bkdgc}_{bkdgp}_histogram.csv'
    with open(filename, 'w') as fid:
        fid.write('\n'.join(['# UCN Hits histogram',
                             f'# Run {run.run_number}',
                             f'# Cycle {bkdgc}',
                             f'# Period {bkdgp}',
                             f'# Background data',
                             f'# Bin size: 1000 ms',
                             f'# Current: {current}',
                             ]))
        fid.write('\n')
    hist.to_csv(filename, mode='a')

# get run data - 6A no foil
def extract_nofoil():
    """60/0/120"""
    runs = [2530, 2558, 2573, 2578, 2593]

    for runn in runs:

        run = ucnrun(runn)

        if runn == 2530:
            run.modify_timing(1,1,0,-40)
            fetch(run, 1, 1)

            run.modify_timing(9,1,0,-40)
            fetch(run, 9, 1)

            fetch(run, 9, 1)

        elif runn==2558:
            fetch(run, 1, 1)
            fetch(run, 10, 1)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 17, 3)

        elif runn==2573:
            fetch(run, 1, 1)
            fetch(run, 10, 1)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 17, 3)
            fetch(run, 28, 1)

        elif runn==2578:
            fetch(run, 1, 1)

            run.modify_timing(9,2,1,1)
            run.modify_timing(8,3,1,1)
            run.modify_timing(8,3,0,-120)
            fetch(run, 8, 3)

            run.modify_timing(18,2,1,1)
            run.modify_timing(17,3,1,1)
            run.modify_timing(17,3,0,-120)
            fetch(run, 17, 3)

        elif runn==2593:
            fetch(run, 1, 1)

            run.modify_timing(9,2,1,1)
            run.modify_timing(8,3,1,1)
            run.modify_timing(8,3,0,-120)
            fetch(run, 8, 3)

# extract_nofoil()

# fit function
fn = lambda t, amp, frac, tau1, tau2, off: amp*(frac*np.exp(-t/tau1) + (1-frac)*np.exp(-t/tau2))+off

fitpar = {'amp': [],
          'frac':[],
          'tau1':[],
          'tau2':[],
          'off':[],
          'damp': [],
          'dfrac':[],
          'dtau1':[],
          'dtau2':[],
          'doff':[],
          'current':[],
          'current_rounded':[],
          'run': [],
          'cycle': [],
          'period': [],
          }


currents = {1: plt.subplots()[1],
            5: plt.subplots()[1],
            11: plt.subplots()[1],
            22: plt.subplots()[1],
            37: plt.subplots()[1],
            }

# fit backgrounds
for filen in glob('hists/*.csv'):

    # read file header
    with open(filen, 'r') as fid:
        line = '#'
        header = []
        while line[0] == '#':
            header.append(line)
            line = fid.readline()
    header = header[1:]

    # get header info
    run = int(header[1].split(' ')[-1])
    cyc = int(header[2].split(' ')[-1])
    per = int(header[3].split(' ')[-1])
    current = float(header[-1].split(':')[-1].strip())
    current_rounded = int(np.round(current))

    # get file contents
    df = pd.read_csv(filen, comment='#')

    idx = df.Count > 0
    df = df.loc[idx]

    x = df.tUnixTimePrecise.values
    x -= x[0]
    y = df.Count.values
    dy = y**0.5

    # fit
    ls = LeastSquares(x, y, dy, fn)
    m = Minuit(ls, amp=max(y), frac=0.01, tau1=0.1, tau2=10, off=0)
    m.limits['frac'] = [0, 1]
    m.limits['amp'] = [0, np.inf]
    m.limits['tau1'] = [0, 1000]
    m.limits['tau2'] = [0, 1000]
    print(m.migrad())
    par = np.array(m.values)
    std = np.array(m.errors)

    # draw
    ax = currents[current_rounded]
    line = ax.plot(x, y, label=f'run {run} cycle {cyc} period {per}')
    ax.plot(x, fn(x, *par), color=line[0].get_color(), ls='--')
    ax.set_xlabel('Time Elapsed (s)')
    ax.set_ylabel('UCN Counts / 1000 ms')
    ax.set_title(f'{current_rounded} $\\mu$A')
    plt.figure(ax.get_figure().number)
    plt.legend(fontsize='xx-small')
    plt.tight_layout()
    plt.savefig(f'figures/{current_rounded}uA.pdf')

    # save results
    for i, name in enumerate(['amp', 'frac', 'tau1', 'tau2', 'off']):
        fitpar[name].append(par[i])
        fitpar['d'+name].append(std[i])
    fitpar['current'].append(current)
    fitpar['current_rounded'].append(current_rounded)
    fitpar['run'].append(run)
    fitpar['cycle'].append(cyc)
    fitpar['period'].append(per)

# sort tau1 vs tau2
fitpar = pd.DataFrame(fitpar)
for i in fitpar.index:
    if fitpar.loc[i, 'tau1'] > fitpar.loc[i, 'tau2']:
        fitpar.loc[i, 'tau1'], fitpar.loc[i, 'tau2'] = fitpar.loc[i, 'tau2'], fitpar.loc[i, 'tau1']
        fitpar.loc[i, 'frac'] = 1 - fitpar.loc[i, 'frac']

# save fit results
fitpar.to_csv('fit_results.csv', index=False)

for cur, ax in currents.items():
    plt.figure(ax.get_figure().number)
    plt.savefig(f'fits/{cur}.pdf')


# plot fit results - amplitude
name = 'amp'
x = fitpar['current']
y = fitpar[name]
dy = fitpar[f'd{name}']

plt.figure()
plt.errorbar(x, y, dy, fmt='o', fillstyle='none')
plt.ylabel('Amplitude')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()

# plot fit results - tau1
name = 'tau1'
x = fitpar['current']
y = fitpar[name]
dy = fitpar[f'd{name}']

plt.figure()
plt.errorbar(x, y, dy, fmt='o', fillstyle='none')
# plt.plot(x, y, 'o', fillstyle='none')
plt.ylabel(r'Short $\tau$')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()

# plot fit results - tau2
name = 'tau2'
x = fitpar['current']
y = fitpar[name]
dy = fitpar[f'd{name}']

plt.figure()
plt.errorbar(x, y, dy, fmt='o', fillstyle='none')
plt.ylabel(r'Long $\tau$')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()

# plot fit results - frac
name = 'frac'
x = fitpar['current']
y = fitpar[name]
dy = fitpar[f'd{name}']

plt.figure()
plt.errorbar(x, y, dy, fmt='o', fillstyle='none')
plt.ylabel(r'Fraction Short $\tau$')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()

# plot fit results - frac
name = 'off'
x = fitpar['current']
y = fitpar[name]
dy = fitpar[f'd{name}']

plt.figure()
plt.errorbar(x, y, dy, fmt='o', fillstyle='none')
plt.ylabel(r'Constant Offset')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()