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
ucnrun.datadir = '/mnt/ucndata/' # comment out if on daq04
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
dirname = 'TCN6A_040'
filename_summary = f'{dirname}/summary.csv'

target_currents = np.array([0.3, 1, 5, 10, 20, 36])

# runs
run_numbers = [ # 2549, # count rate issues
                # 2550, # low rate
                2551,
                2552,
                2553,
                2554,
                2555,
                2556,
                2557,
                2575,
                2576,
                2577,
                2579,
                2580,
                2581,
                2582,
                2584,
                2585,
                2587,
                2588,
                2590,
                2592]

os.makedirs(dirname, exist_ok=True)

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

        # drop cycles where the 1A beam drops to zero during production
        if any(cyc[0].beam1a_current_uA < 0.1):
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): 1A current dropped below 0.1 uA during irradiation')
            continue

        # check that there are hits in the count period
        hits = cyc[2].get_hits('Li6')
        hitsb = cyc[3].get_hits('Li6')
        if hits.empty and hitsb.empty:
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): No counts in both counting period and background period')
            continue

        # use background if counting period is empty
        if hits.empty:
            count_cyc = cyc[3]
        else:
            count_cyc = cyc[2]

        # check for bad cycle definitions: rate close to irradiation rate at start of count
        # note that irr counts comes in bunches for some reason
        _, irr_hits = cyc[0].get_hits_histogram('Li6', bin_ms=100)
        _, cnt_hits = count_cyc.get_hits_histogram('Li6', bin_ms=100)
        irr_rate = irr_hits.max()/0.1
        cnt_rate = cnt_hits.max()/0.1

        if cnt_rate/irr_rate > 0.7:
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): Starting count rate ({int(cnt_rate):d} Hz) more than 70% of irradiation rate ({int(irr_rate):d} Hz)')
            continue

        filt.append(True)
    return filt

def inspect_all():
    for r in run_numbers:
        run = ucnrun(r)
        run.set_cycle_filter(cycle_filter(run))
        run.inspect_beam()
        plt.pause(1)
        input()
        plt.close()

# extract counts from runs
def extract_counts():

    # setup output file
    header = ['# TCN6A-040 runs processed for backgrounds and counts',
              '# Derek Fujimoto',
             f'# {datetime.now()}']

    with open(filename_summary, 'w') as fid:
        fid.write('\n'.join(header))
        fid.write('\n')

    # extract
    write_cols_names = True
    for n in tqdm(run_numbers, desc='Parsing runs', leave=False):

        # read
        run = ucnrun(n)
        run.to_dataframe()

        # apply cycle filter
        run.set_cycle_filter(cycle_filter(run))

        # get IV001 status - determine if background cycle
        is_background = [cyc[2].tfile.UCN2EpPha5Tmp.UCN2_ISO_IV001_STATON.mean() for cyc in run]
        is_background = ~(np.array(is_background)>0)

        # get count cycle
        counts = run[:,2].get_counts('Li6')

        # get cycles that are not background and background
        bkgd_cyc = [cyc for is_bkgd, cyc in zip(is_background, run) if is_bkgd]
        cnt_cyc = [cyc for is_bkgd, cyc in zip(is_background, run) if not is_bkgd]

        # skip if no background and count
        if not bkgd_cyc or not cnt_cyc:
            tqdm.write(f'Skipping run {n}, no background or count cycle present')
            continue

        # get average hits during backgrounds - weighted mean
        counts, err = np.array([bk[3].get_counts('Li6') for bk in bkgd_cyc]).transpose()
        bk_mean = np.average(counts, weights=1/err**2)
        bk_std = 1/np.sum(1/err**2)**0.5

        # get average beam current during background cycles
        bk_currents = [bk[0].beam_current_uA for bk in bkgd_cyc]
        bk_currents = pd.concat(bk_currents)


        # get hits during counting periods
        cnt, err = np.array([c[2].get_counts('Li6') for c in cnt_cyc]).transpose()

        # make output dataframe
        df = pd.DataFrame({
                        'run': run.run_number,
                        'cycle': [c.cycle for c in cnt_cyc],
                        'counts': cnt,
                        'dcounts': err,
                        'counts_bkgd': bk_mean,
                        'dcounts_bkgd': bk_std,
                        'irr_time_s': [c.cycle_param.period_durations_s[0] for c in cnt_cyc],
                        'store_time_s': [c.cycle_param.period_durations_s[1] for c in cnt_cyc],
                        'count_time_s': [c.cycle_param.period_durations_s[2] for c in cnt_cyc],
                        'beam_uA': [c[0].beam_current_uA.mean() for c in cnt_cyc],
                        'dbeam_uA': [c[0].beam_current_uA.std() for c in cnt_cyc],
                        'beam_uA_bkgd': bk_currents.mean(),
                        'dbeam_uA_bkgd': bk_currents.std(),
                        'cycle_start': [c.cycle_start for c in cnt_cyc],
                        })

        # write
        df.to_csv(filename_summary, mode='a', index=False, header=write_cols_names)
        write_cols_names = False

# load results
df = pd.read_csv(filename_summary, comment='#')

# get rounded beam currents for grouping - find closest from list
fn = lambda x: target_currents[np.argmin(np.abs(target_currents-x))]
df['beam_rounded_uA'] = df['beam_uA'].apply(fn)

# get background-subtracted counts
df['counts_corr'] = df.counts - df.counts_bkgd
df['dcounts_corr'] = (df.dcounts**2 + df.dcounts_bkgd**2)**0.5

# drop bad cycles
df.drop(df.index[df.counts_corr < 0], inplace=True)

# fit function
fitfn = lambda t, amp, tau : amp*(1-np.exp(-t/tau))

# draw
plt.figure()
currents = []
pars = []
stds = []

for current, g in df.groupby('beam_rounded_uA'):

    # draw
    line = plt.errorbar(g.irr_time_s, g.counts_corr, g.dcounts_corr,
                fmt='o', label=f'{int(current):d} $\\mu$A',
                fillstyle='none')

    # fit
    par, cov = curve_fit(fitfn, g.irr_time_s, g.counts_corr,
                         sigma=g.dcounts_corr,
                         absolute_sigma=True,
                         p0=(g.counts_corr.max(), 1))
    std = np.diag(cov)**0.5

    fitx = np.linspace(g.irr_time_s.min(), g.irr_time_s.max(), 100)
    plt.plot(fitx, fitfn(fitx, *par), color=line[0].get_color())

    currents.append(current)
    pars.append(par)
    stds.append(std)

plt.ylabel('UCN Counts')
plt.xlabel('Irradiation Time (s)')
plt.legend(fontsize='x-small')
plt.tight_layout()
plt.savefig(f'{dirname}/{dirname}_fit.pdf')

# draw fit parameters
pars = np.transpose(pars)
stds = np.transpose(stds)


plt.figure()
plt.errorbar(currents, pars[0], stds[0], fmt='o', fillstyle='none')
plt.ylabel('Amplitude')
plt.xlabel(r'Current ($\mu$A)')
plt.tight_layout()
plt.savefig(f'{dirname}/{dirname}_amp.pdf')

plt.figure()
plt.errorbar(currents, pars[1], stds[1], fmt='o', fillstyle='none')
plt.ylabel(r'Saturation Time $\tau$ (s)')
plt.xlabel(r'Beam Current ($\mu$A)')
plt.tight_layout()
plt.savefig(f'{dirname}/{dirname}_tau.pdf')

# RUN ==================================
# extract_counts()