# Run analysis for TCN6A-040: source saturation measurement at varying beam energies
# Derek Fujimoto
# June 2025
from ucndata import ucnrun
import os
import pandas as pd
from scipy.optimize import curve_fit
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime

# settings
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
dirname = '.'
outfile = f'{dirname}/summary.csv'

target_currents = np.array([0.3, 1, 5, 10, 20, 36])

os.makedirs(dirname, exist_ok=True)

# worker fn
def fetch(run, cyclen, last20):
    current = run[cyclen, 0].beam1u_current_uA
    current = current[current > 0]

    output = {}
    output['current'] = current.mean()
    output['counts'] = run[cyclen, 2].get_nhits('Li6')
    output['counts_bkgd'] = run[cyclen, 3].get_nhits('Li6')
    output['run'] = run.run_number
    output['cycle_num'] = cyclen
    output['irradiation_time'] = run.cycle_param.period_durations_s.loc[0, cyclen]
    output['storage_time'] = run.cycle_param.period_durations_s.loc[1, cyclen]
    output['count_time'] = run.cycle_param.period_durations_s.loc[2, cyclen]
    output['bkgd_time'] = run.cycle_param.period_durations_s.loc[3, cyclen]
    output['is_last_20s'] = last20

    return pd.DataFrame(output, index=[0])

def fix_bad_transition(run, cycle, dt, kill_bkgd):
    """Shift bad cycle timings by a constant amount"""

    if kill_bkgd:
        run.modify_timing(cycle, 3, 0, -120)
        run.modify_timing(cycle, 0, 0, dt)
        run.modify_timing(cycle, 1, 0, dt)
        run.modify_timing(cycle, 2, 0, 120)
    else:
        run.modify_timing(cycle, 0, 0, dt)
        run.modify_timing(cycle, 1, 0, dt)
        run.modify_timing(cycle, 2, 0, dt)

# get run data - 6A no foil
def extract():
    """*/120/120"""

    runs = [# 2549, # count rate issues
            # 2550, # low rate
            2546, 2547, 2548, 2551, 2552, 2553, 2554, 2555, 2556, 2557, 2575,
            2576, 2577, 2579, 2580, 2581, 2582, 2584, 2585, 2587, 2588, 2590,
            2592]

    df_list = []

    for runn in tqdm(runs, desc="Runs"):

        run = ucnrun(runn)
        run.set_cycle_filter(run.gen_cycle_filter())

        if runn == 2546:

            # fix bad cycles
            fix_bad_transition(run, 12, 20, False)

            # fixes to filter
            cyc_filter = run.cycle_param.filter
            cyc_filter[4] = False
            cyc_filter[7] = False
            cyc_filter[11] = False
            cyc_filter[16] = False
            run.set_cycle_filter(cyc_filter)

            # fix overal timing issues
            for cyc in run:
                cyc[1].modify_timing(1,1)
                cyc[2].modify_timing(0,1)

        elif runn == 2547:

            # fix bad cycles
            fix_bad_transition(run, 4, 40, False)

        elif runn == 2548:

            # fix bad cycles
            fix_bad_transition(run, 4, -90, False)
            fix_bad_transition(run, 9, 50, True)
            fix_bad_transition(run, 14, -40, True)
            fix_bad_transition(run, 22, 20, False)

            # fixes to filter
            cyc_filter = run.cycle_param.filter
            cyc_filter[4] = True
            cyc_filter[13] = False
            cyc_filter[14] = True
            cyc_filter[21] = False
            cyc_filter[25] = False
            run.set_cycle_filter(cyc_filter)

        elif runn in (2551, 2552, 2553, 2554, 2555, 2556, 2557, 2577, 2580,
                      2581, 2582, 2584, 2585, 2587, 2590):
            pass

        elif runn == 2575:

            # fix bad cycles
            fix_bad_transition(run, 5, -90, False)
            fix_bad_transition(run, 8, 50, False)

            # fixes to filter
            cyc_filter = run.cycle_param.filter
            cyc_filter[0] = True
            run.set_cycle_filter(cyc_filter)

        elif runn == 2576:
            for cyc in run:
                cyc[1].modify_timing(1,1)
                if cyc.cycle in (1, 4):
                    cyc[3].modify_timing(0,1)
                else:
                    cyc[2].modify_timing(0,1)

        elif runn == 2579:

            # fixes to filter
            cyc_filter = run.cycle_param.filter
            cyc_filter[0] = True
            run.set_cycle_filter(cyc_filter)

        elif runn == 2588:

            # fixes to filter
            cyc_filter = run.cycle_param.filter
            cyc_filter[0] = True
            run.set_cycle_filter(cyc_filter)

        # extract counts
        for cyc in run:
            df_list.append(fetch(run, cyc.cycle, False))

        # extract last 20s
        for cyc in run:
            if cyc.cycle_param.period_durations_s[2] > 0:
                run.modify_timing(cyc.cycle, 2, 100, 0)
            elif cyc.cycle_param.period_durations_s[3] > 0:
                run.modify_timing(cyc.cycle, 3, 100, 0)

        for cyc in run:
            df_list.append(fetch(run, cyc.cycle, True))

        df = pd.concat(df_list, axis='index')
        df.to_csv(outfile, index=False)



# load results
df = pd.read_csv(outfile, comment='#')

# get rounded beam currents for grouping - find closest from list
fn = lambda x: target_currents[np.argmin(np.abs(target_currents-x))]
df['current_rounded'] = df['current'].apply(fn)

# pair last 20 sec with corresponding run
df.set_index(['run', 'cycle_num'], inplace=True)
df_last = df.loc[df.is_last_20s]
df = df.loc[~df.is_last_20s]
df['last20_counts'] = df_last['counts']
df['last20_bkgd'] = df_last['counts_bkgd']

# get marked background cycles
df['is_bkgd'] = df['counts_bkgd'] != 0

# round irradiation times to nearest 10 sec
df['irradiation_time'] = (df['irradiation_time']/10).round()*10

# keep only storage time 10s (108/127)
df = df.loc[df.storage_time == 10]

# reset index
df.reset_index(inplace=True)

# correct backgrounds by rounded current (not every run has a background cycle)
for cur, df_cur in df.groupby('current_rounded'):
    for irr, df_irr in df_cur.groupby('irradiation_time'):
        df_dat = df_irr.loc[~df_irr.is_bkgd]
        df_bkg = df_irr.loc[df_irr.is_bkgd]

        # subtract using nearest background
        for i in df_dat.index:
            closest = df_bkg.index[np.argmin(abs(df_bkg.index - i))]
            df.loc[i, 'counts_bkgd'] = df_bkg.loc[closest, 'counts_bkgd']
            df.loc[i, 'last20_bkgd'] = df_bkg.loc[closest, 'last20_bkgd']

# ditch the background calculations
df = df.loc[~df.is_bkgd]

# setup analysis columns
df['factor'] = df.last20_counts / df.last20_bkgd
df['dfactor'] = df.factor * (1/df.last20_counts + 1/df.last20_bkgd)**0.5

df['dbkgd_counts_corr'] = df.factor * df.counts_bkgd * (1/df.counts_bkgd + (df.dfactor/df.factor)**2)**0.5
df['bkgd_counts_corr'] = df.factor * df.counts_bkgd

df['counts_corr'] = df.counts - df.bkgd_counts_corr
df['dcounts_corr'] = (df.counts + df.dbkgd_counts_corr**2)**0.5

# fit function
fitfn = lambda t, amp, tau : amp*(1-np.exp(-t/tau))

currents = []
pars = []
stds = []

# draw and fit
plt.figure()
for cur, df_cur in df.groupby('current_rounded'):

    # draw
    x = df_cur.irradiation_time
    y = df_cur.counts_corr
    dy = df_cur.dcounts_corr
    # y = df_cur.counts
    # dy = df_cur.counts**0.5
    line = plt.errorbar(x, y, dy, fmt='o', fillstyle='none', label=f'{int(cur):d} $\\mu$A')

    # fit
    par, cov = curve_fit(fitfn, x, y, sigma=dy,
                        absolute_sigma=True,
                        p0=(max(y), 1))
    std = np.diag(cov)**0.5

    fitx = np.linspace(min(x), max(x), 100)
    plt.plot(fitx, fitfn(fitx, *par), color=line[0].get_color())

    currents.append(cur)
    pars.append(par)
    stds.append(std)

plt.ylabel('UCN Counts')
plt.xlabel('Irradiation Time (s)')
plt.legend(fontsize='x-small')
plt.tight_layout()
plt.savefig(f'{dirname}/TCN6A_040_fit.pdf')

# draw fit parameters
pars = np.transpose(pars)
stds = np.transpose(stds)


plt.figure()
plt.errorbar(currents, pars[0], stds[0], fmt='o', fillstyle='none')
plt.ylabel('Amplitude')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()
plt.savefig(f'{dirname}/TCN6A_040_amp.pdf')

plt.figure()
plt.errorbar(currents, pars[1], stds[1], fmt='o', fillstyle='none')
plt.ylabel(r'Saturation Time $\tau$ (s)')
plt.xlabel(r'Beam Current ($\mu$A)')
plt.tight_layout()
plt.savefig(f'{dirname}/TCN6A_040_tau.pdf')

# RUN ==================================
# extract()