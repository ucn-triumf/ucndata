# Run analysis for TCN6A-050: source lifetime measurement at varying beam energies
# Time signature: 60/*/120
# Derek Fujimoto
# July 2025
from ucndata import ucnrun
import os
from scipy.optimize import curve_fit
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm


# settings
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
outfile = 'summary.csv'    # save counts output

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

        # check that the irradiation time is 60 s
        if cyc.cycle_param.period_durations_s.loc[0] != 60:
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): Irradiation period not 60s ({cyc.cycle_param.period_durations_s.loc[0]} s)')
            continue


        # drop cycles where the 1A beam drops to zero during any time in the cycle
        if any(cyc.beam1a_current_uA < 0.1):
            filt.append(False)
            tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): 1A current dropped below 0.1 uA')
            continue

        # drop cycles where the 1A beam drops to zero within 5 s of the cycle starting
        if cyc.cycle > 0:
            cyc_last = run[cyc.cycle-1]
            current = cyc_last.beam1a_current_uA
            idx = current.index > cyc.cycle_start-20
            if any(current.loc[idx] < 0.1):
                filt.append(False)
                tqdm.write(f'Run {run.run_number} (cycle {cyc.cycle}): 1A current dropped below 0.1 uA within 20 seconds of the cycle starting')
                continue

        filt.append(True)
    return filt

# worker fn
def fetch(run, cyclen, periodn, is_background, draw=False):
    current = run[cyclen, 0].beam1u_current_uA
    current = current[current > 0]

    output = {}
    output['current'] = current.mean()
    output['counts'] = run[cyclen,periodn].get_nhits('Li6')
    output['run'] = run.run_number
    output['cycle_num'] = cyclen
    output['period_num'] = periodn
    output['is_background'] = is_background
    output['storage_time'] = run.cycle_param.period_durations_s.loc[1, cyclen]

    # get last 20s counts
    run.modify_timing(cyclen, periodn, 100, 0)
    output['counts_last_20s'] = run[cyclen,periodn].get_nhits('Li6')
    run.modify_timing(cyclen, periodn, -100, 0)

    if draw:
        hist = run[cyclen, periodn].get_hits_histogram('Li6', bin_ms=1000)
        hist.x -= hist.x[0]

        plt.figure()
        hist.plot(ax=plt.gca(), color='k', label='Count period')

        plt.xlabel('Time since period start (s)', fontsize='medium')
        plt.ylabel('UCN Counts')
        plt.yscale('linear')
        plt.legend(fontsize='xx-small')
        plt.title(f'Run {run.run_number}, cycle {cyclen}, period {periodn}', fontsize='x-small')
        plt.tight_layout()
        os.makedirs('figures', exist_ok=True)
        plt.savefig(f'figures/r{run.run_number}_c{cyclen}_p{periodn}.pdf')
        plt.pause(1)

    # return
    return pd.DataFrame(output, index=[0])

# get run data - 6A no foil
def extract():
    """60/*/120"""
    runs = [2548, 2575, 2581, 2588, # saturation measurements - just get 60s beam on
            2558, 2573, 2578, 2593, 2594, 2608]

    df_list = []

    for runn in tqdm(runs, desc="Runs"):

        run = ucnrun(runn)
        run.set_cycle_filter(cycle_filter(run))

        if runn == 2548:
            run.modify_timing(11, 1, 1, 0)
            run.modify_timing(11, 2, 1, 1)
            run.modify_timing(12, 1, 1, 0)
            run.modify_timing(12, 3, 1, 1)
            df_list.append(fetch(run, 11, 2, False))
            df_list.append(fetch(run, 12, 3, True))

        elif runn == 2575:
            df_list.append(fetch(run, 10, 2, False))
            df_list.append(fetch(run, 11, 2, False))
            df_list.append(fetch(run, 9,  3, True))

        elif runn == 2581:
            run.modify_timing(0, 1, 1, 0)
            run.modify_timing(0, 2, 1, 1)
            run.modify_timing(2, 1, 1, 0)
            run.modify_timing(2, 2, 1, 1)
            run.modify_timing(3, 1, 1, 0)
            run.modify_timing(3, 2, 1, 1)
            run.modify_timing(1, 1, 1, 0)
            run.modify_timing(1, 3, 1, 1)
            df_list.append(fetch(run, 0, 2, False))
            df_list.append(fetch(run, 2, 2, False))
            df_list.append(fetch(run, 3, 2, False))
            df_list.append(fetch(run, 1, 3, True))

        elif runn == 2588:
            df_list.append(fetch(run, 2, 2, False))
            df_list.append(fetch(run, 3, 2, False))
            df_list.append(fetch(run, 5, 2, False))
            df_list.append(fetch(run, 4, 3, True))

        elif runn == 2558:

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in [8, 17]:
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm([8, 17], desc='background'):

                # trim to 120 s
                run.modify_timing(i, 3, 0, -120)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        elif runn == 2573:

            bkgd_cycles = (8, 17, 26, 35)

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in bkgd_cycles:
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm(bkgd_cycles, desc='background'):

                # trim to 120 s
                run.modify_timing(i, 3, 0, -120)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        elif runn == 2578:

            bkgd_cycles = (8, 17)

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in bkgd_cycles:

                    if cyc.cycle > 0:
                        run.modify_timing(cyc.cycle, 1, 1, 0)
                        run.modify_timing(cyc.cycle, 2, 1, 1)   # shift 1s - bad timing?
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm(bkgd_cycles, desc='background'):

                # trim to 120 s
                run.modify_timing(i, 2, 1, 1)   # shift 1s - bad timing?
                run.modify_timing(i, 3, 0, -120)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        elif runn == 2593:

            bkgd_cycles = (8, )

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in bkgd_cycles:

                    if cyc.cycle == 9:
                        run.modify_timing(cyc.cycle, 1, 1, 0)
                        run.modify_timing(cyc.cycle, 2, 1, 1)   # shift 1s - bad timing?
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm(bkgd_cycles, desc='background'):

                # trim to 120 s
                run.modify_timing(i, 3, 0, -120)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        elif runn == 2594:

            bkgd_cycles = (8, )

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in bkgd_cycles:
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm(bkgd_cycles, desc='background'):

                # trim to 120 s
                run.modify_timing(i, 3, 0, -120)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        elif runn == 2608:

            bkgd_cycles = (8, 17)

            # get cycle counts
            storage_times = []
            for cyc in run:
                if cyc.cycle not in bkgd_cycles:
                    if cyc.cycle <= 6 or cyc.cycle == 9 or cyc.cycle >=16:
                        run.modify_timing(cyc.cycle, 1, 1, 0)
                        run.modify_timing(cyc.cycle, 2, 1, 1)
                    df_list.append(fetch(run, cyc.cycle, 2, False))
                    storage_times.append(df_list[-1]['storage_time'])

            # get backgrounds
            storage_times = np.unique(storage_times)
            for i in tqdm(bkgd_cycles, desc='background'):

                # trim to 120 s
                run.modify_timing(i, 3, 0, -120)
                if cyc.cycle == 17:
                    run.modify_timing(cyc.cycle, 3, 1, 1)

                for time in tqdm(storage_times, desc='storage times'):
                    # shift window
                    run.modify_timing(i, 3, time, time)
                    run.modify_timing(i, 1, -time, 0)

                    # get data
                    df_list.append(fetch(run, i, 3, True))

                    # shift back
                    run.modify_timing(i, 1, time, 0)
                    run.modify_timing(i, 3, -time, -time)

        df = pd.concat(df_list, axis='index')
        df.to_csv(outfile, index=False)

# get data
df = pd.read_csv(outfile, comment='#')
df['current_rounded'] = df.current.round()

dfb = df.loc[df.is_background]
df = df.loc[~df.is_background]

dfb.set_index(['run','storage_time','current_rounded', 'cycle_num'], inplace=True)
dfb.sort_index(inplace=True)


# background corrections
df.loc[:, 'counts_corrected'] = np.nan
df.loc[:, 'dcounts_corrected'] = np.nan
df.loc[:, 'factor'] = np.nan
df.loc[:, 'dfactor'] = np.nan

for i in df.index:

    row = df.loc[i]

    # get closest background
    bkgd = dfb.loc[row.run, row.storage_time, row.current_rounded, :]
    bcyc = list(np.abs(bkgd.index - row.cycle_num))
    idx_best = bcyc.index(min(bcyc))
    idx_best = bkgd.index[idx_best]
    bkgd = bkgd.loc[idx_best]

    # rescale by last 20s
    factor = row.counts_last_20s / bkgd.counts_last_20s
    dfactor = factor * (1/row.counts_last_20s + 1/bkgd.counts_last_20s)**0.5

    bkgd['dcounts'] = factor * bkgd.counts * (1/bkgd.counts + (dfactor/factor)**2)**0.5
    bkgd.counts *= factor

    # background subtraction
    df.loc[i, 'counts_corrected'] = row.counts - bkgd.counts
    df.loc[i, 'dcounts_corrected'] = (row.counts + bkgd.dcounts**2)**0.5
    df.loc[i, 'factor'] = factor
    df.loc[i, 'dfactor'] = dfactor

# fit function
fn = lambda x, tau, amp: amp*np.exp(-x/tau)
pars = []
stds = []
curs = []
chisq = []

# draw
plt.figure()
for cur, g in df.groupby('current_rounded'):
    g.sort_values('storage_time', inplace=True)

    idx = g.storage_time <50

    x = g.storage_time
    y = g.counts_corrected
    dy = g.dcounts_corrected

    # fit
    par, cov = curve_fit(fn, x[idx], y[idx], sigma=dy[idx], absolute_sigma=True, p0=(1, max(y)))
    std = np.diag(cov)**0.5

    pars.append(par)
    stds.append(std)
    curs.append(cur)

    # draw
    line = plt.errorbar(x, y, dy, fmt='o', fillstyle='none', label=f'{cur:g} $\\mu$A')

    fitx = np.linspace(min(x), max(x), 1000)
    plt.plot(fitx, fn(fitx, *par), color=line[0].get_color())

    # chisq
    chisq.append(np.sum(((y-fn(x,*par))/dy)**2)/(len(x)-2))

plt.legend(fontsize='x-small')
plt.xlabel('Storage Time (s)')
plt.ylabel('UCN Counts')
plt.yscale('log')
plt.tight_layout()
plt.savefig('TCN6A_050_fit.pdf')

# make outputs arrays
pars = np.array(pars)
stds = np.array(stds)

# draw storage lifetimes
plt.figure()
plt.errorbar(curs, pars[:, 0], stds[:, 0], fmt='o', fillstyle='none')
plt.ylabel('Storage Lifetime (s)')
plt.xlabel('Beam Current ($\\mu$A)')
plt.tight_layout()
plt.savefig('TCN6A_050_tau.pdf')

# draw amp
plt.figure()
plt.errorbar(curs, pars[:, 1], stds[:, 1], fmt='o', fillstyle='none')
plt.ylabel('UCN Counts at Time Zero')
plt.xlabel('Beam Current ($\\mu$A)')
plt.tight_layout()
plt.savefig('TCN6A_050_amp.pdf')

# draw chisq
plt.figure()
plt.plot(curs, chisq, 'o', fillstyle='none')
plt.ylabel('$\\chi^2$/DOF')
plt.xlabel('Beam Current ($\\mu$A)')
plt.tight_layout()
