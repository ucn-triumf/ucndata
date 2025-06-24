# He3 lifetime measurements
# Derek Fujimoto
# June 2025

from ucndata import ucnrun
from tqdm import tqdm
import pandas as pd
import numpy as np
from datetime import datetime
import os
from iminuit import Minuit
from iminuit.cost import LeastSquares

# settings
run_numbers = [2688, 2689]
dirname = 'TCN6A_150_10'
ucnrun.cycle_times_mode = ['li6'] # force detection mode
filename_summary = f'{dirname}/summary.csv'

# make output dir
os.makedirs(dirname, exist_ok=True)

# define filter on good/bad cycles
def cycle_filter(run):
    """Determine if a cycle should be kept or not"""
    filt = []
    iterator = tqdm(run,
                    desc=f'Run {run.run_number}: Scanning cycles',
                    leave=False,
                    total=run.cycle_param.ncycles)

    for cyc in iterator:

        # check if period duration exceeds cycle duration
        expected_duration = cyc.cycle_param.period_durations_s.sum()
        actual_duration = cyc.cycle_stop - cyc.cycle_start
        if expected_duration > actual_duration:
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): cycle duration shorter than sum of periods')
            continue

        # drop cycles where the 1A beam drops to zero during any time in the cycle
        if any(cyc.beam1a_current_uA < 0.1):
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): 1A current dropped below 0.1 uA')
            continue

        # check that there are hits in the count or background periods
        hits = cyc[2].get_nhits('He3')
        hitsb = cyc[3].get_nhits('He3')
        if hits == 0 and hitsb == 0:
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): No counts in both counting period and background period')
            continue

        filt.append(True)
    return filt

# extract run info and counts
def extract(save_diagnostic=False):

    # save results
    with open(filename_summary, 'w') as fid:
        fid.write('\n'.join(['# TCN6A-150-10 (Lifetime measurment)',
                            '# He3 detector',
                            '# 10 seconds irradiation',
                            '# 120 seconds counting',
                            '# 10 uA',
                            '# Derek Fujimoto',
                            f'# This file written {datetime.now()}',
                            ]))
        fid.write('\n')

    # extract run info
    for r in tqdm(run_numbers, desc='Extracting run info'):

        # get runs and filter on cycles
        run = ucnrun(r)
        run.set_cycle_filter(cycle_filter(run))

        # adjust timings
        if r == 2688:

            for c in range(4):
                # beam end times
                run.modify_timing(cycle=c, period=0, dt_start_s=0, dt_stop_s=1)

                # counting end times
                run.modify_timing(cycle=c, period=2, dt_start_s=1.5, dt_stop_s=4)

            # fix cycle 0
            run.modify_timing(cycle=0, period=0, dt_start_s=0, dt_stop_s=-0.9)

        elif r == 2689:
            for c in range(5):
                # counting end times
                run.modify_timing(cycle=c, period=2, dt_start_s=0, dt_stop_s=4)

        # save inspect figure
        if save_diagnostic:
            run.inspect('He3', bin_ms=100, xmode='dur')
            plt.savefig(f'{dirname}/run_{r}_inspect.pdf')

        # extract results
        get_dbeam_current = lambda b: b.std()/np.sqrt(b.size)
        df = pd.DataFrame({'run': r,
                        'cycle': [cyc.cycle for cyc in run],
                        'counts': [cyc[2].get_nhits('He3') for cyc in run],
                        'counts_bkgd': [cyc[3].get_nhits('He3') for cyc in run],
                        'irr_s': [cyc[0].period_stop - cyc[0].period_start for cyc in run],
                        'storage_s': [cyc[1].period_stop - cyc[1].period_start for cyc in run],
                        'count_s': [cyc[2].period_stop - cyc[2].period_start for cyc in run],
                        'bkgd_s': [cyc[3].period_stop - cyc[2].period_start for cyc in run],
                        'beam1a_current_uA': [cyc[0].beam1a_current_uA.mean() for cyc in run],
                        'dbeam1a_current_uA': [get_dbeam_current(cyc[0].beam1a_current_uA) for cyc in run],
                        'beam1u_current_uA': [cyc[0].beam1u_current_uA.mean() for cyc in run],
                        'dbeam1u_current_uA': [get_dbeam_current(cyc[0].beam1u_current_uA) for cyc in run],
                        })

        # write to file
        if r == run_numbers[0]:
            df.to_csv(filename_summary, mode='a', index=False, header=True)
        else:
            df.to_csv(filename_summary, mode='a', index=False, header=False)

# def analyze():
if True:
    # draw results
    df = pd.read_csv(filename_summary, comment='#')

    # count errors
    df['dcounts'] = df.counts**0.5
    df['dcounts_bkgd'] = df.counts_bkgd**0.5

    # normalize to 10 uA
    df.dcounts = 10*df.counts/df.beam1u_current_uA * ((df.dcounts/df.counts)**2 + (df.dbeam1u_current_uA/df.beam1u_current_uA)**2)**0.5
    df.counts *= 10/df.beam1u_current_uA

    # drop background measurements and get data
    df_bkgd = df.loc[df['bkgd_s'] > 200]
    df = df.loc[df['bkgd_s'] < 200]
    x, y, dy = df.storage_s, df.counts, df.dcounts

    # background corrections
    bk_mean = df_bkgd.mean()
    bk_std = df_bkgd.std()/np.sqrt(len(df_bkgd))

    bk_counts = bk_mean.counts_bkgd * bk_mean.bkgd_s/df.count_s
    dbk_counts = bk_mean.dcounts_bkgd

    y -= bk_counts
    dy = (dy**2 + dbk_counts**2)**0.5

    # fit
    fitfn = lambda t, amp, tau: amp*np.exp(-t/tau)
    cost = LeastSquares(x=x, y=y, yerror=dy, model=fitfn)
    m = Minuit(cost, amp=max(y), tau=1)
    print(m.migrad())

    # draw
    plt.errorbar(x, y, dy, fmt='o', fillstyle='none', color='k', ecolor='k')
    fitx = np.linspace(min(x), max(x), 100)
    plt.plot(fitx, fitfn(fitx, **m.values.to_dict()), color='r')

    plt.xlabel('Valve Delay Time (s)')
    plt.ylabel('UCN Hits')
    plt.yscale('log')
    plt.tight_layout()

    # print stats
    for parname in ['amp', 'tau']:
        print(f'{parname} = {m.values[parname]} +/- {m.errors[parname]}')

    print(f'Chisq/ndof: {m.fval/m.ndof}')
    plt.savefig(f'{dirname}/{dirname}.pdf')
