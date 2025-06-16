# Run analysis for TCN6A-040: source saturation measurement at varying beam energies
# Derek Fujimoto
# June 2025
from ucndata import read, ucnrun
import os
import tools
from scipy.optimize import curve_fit
import pandas as pd
import numpy as np
from tqdm import tqdm

# settings
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
outfile = 'TCN6A_040/summary.csv'    # save counts output

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

os.makedirs('TCN6A_040', exist_ok=True)

def cycle_filter(run):
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
df_list = []
for n in run_numbers:

    # read
    run = ucnrun(n)
    run.to_dataframe()

    # apply cycle filter
    run.set_cycle_filter(cycle_filter(run))

    # get counts from cycles
    counts = run[:,2].get_counts('Li6')

    # get IV001 status
    is_background = [cyc[2].tfile.UCN2EpPha5Tmp.UCN2_ISO_IV001_STATON.mean() for cyc in run]
    is_background = np.array(is_background)>0




    break

