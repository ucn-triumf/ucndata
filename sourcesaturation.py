# Get source saturation
# Derek Fujimoto
# Nov 2024

from ucndata import settings, read, ucnrun
from tools import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from iminuit import Minuit
from iminuit.cost import LeastSquares
import os
from datetime import datetime
from fitting import global_fitter

# settings
# settings.datadir = 'root_files'     # path to root data
settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer]
settings.DET_NAMES.pop('He3')       # don't check He3 detector data
detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
filename = 'sourcesaturation/saturation.csv'      # save counts output
run_numbers = [1846]   # example: [1846, '1847+1848']

# periods settings
periods = {'production':  0,
           'count':       1,
           'background':  0}

def get_satur_cnts(run, filename, periods):
    """Get counts needed for a source saturation calculation for a single run.
    Save this to file.

    Args:
        r (ucnrun): run data
        f (str): name of file to save at the end
        periods (dict): specify which periods are for which purpose (production, count, background)

    Returns:
        pd.DataFrame: with counts needed for calculation
    """

    # print status
    print(f'Run {run.run_number} ' + '='*40 )

    # filter cycles
    run.set_cycle_filter(run.gen_cycle_filter(period_production=periods['production'],
                                              period_count=periods['count'],
                                              period_background=periods['background']))

    # get beam current and means
    beam_currents = run[:, periods['production']].beam_current_uA

    dbeam_currents = beam_currents.std()
    beam_currents = beam_currents.mean()

    # get production durations and associated counts
    production_duration = run[:, periods['production']].cycle_param.period_durations_s
    counts_bkgd = run[:, periods['background']].get_counts(detector)
    counts_bkgd = counts_bkgd.transpose()

    counts = run[:, periods['count']].get_counts(detector,
                                        bkgd=counts_bkgd[0],
                                        dbkgd=counts_bkgd[1],
                                        norm=beam_currents,
                                        dnorm=dbeam_currents)

    # make into a dataframe
    df = pd.DataFrame({'run': run.run_number,
                       'experiment': run.experiment_number,
                       'production duration (s)': production_duration,
                       'counts (1/uA)': counts[:, 0],
                       'bkgd (counts)': counts_bkgd[0],
                       'normalization (uA)': beam_currents,
                       'dcounts (1/uA)': counts[:, 1],
                       'dbkgd (counts)': counts_bkgd[1],
                       'dnormalization (uA)': dbeam_currents,
                       })

    # save file
    if filename:
        dirname = os.path.dirname(filename)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # read file if exists
        try:
            df_old = pd.read_csv(filename, comment='#')
        except FileNotFoundError:
            df_old = pd.DataFrame()

        # remove data from this run
        else:
            idx = df_old['run'] != run.run_number
            df_old = df_old.loc[idx]

        # add this to the old data
        df = pd.concat((df, df_old), axis='index')

        # write to file
        header = ['# Normalized counts and production times for saturation measurement',
                  '# Written by sourcesaturation.py',
                  f'# Last updated: {str(datetime.now())}']
        with open(filename, 'w') as fid:
            fid.write('\n'.join(header))
            fid.write('\n')
        df.to_csv(filename, index=False, mode='a')

    return df

def draw_counts(run, filename):
    """Draw and fit counts for a run

    Args:
        run (int): run number to fit and draw.
        filename (str): path to file with the counts (output of get_satur_cnts)
        fitfn (fn handle|None): if none, don't do fit. else fit this function
        p0 (iterable): initial fit paramters
    """

    # get data
    df = pd.read_csv(filename, comment='#', index_col=0)
    if run is not None:
        if isinstance(df.index.dtype, str):
            run = str(run)
        df = df.loc[run]
    else:
        run = 'all'

    # get data
    df.sort_values('production duration (s)', inplace=True)
    production_duration = df['production duration (s)'].values
    counts = df['counts (1/uA)'].values
    dcounts = df['dcounts (1/uA)'].values

    # draw data
    plt.figure()
    plt.errorbar(production_duration, counts, dcounts, fmt='.')
    plt.yscale('log')
    plt.xlabel('Production Duration (s)')
    plt.ylabel('Normalized Number of Counts (uA$^{-1}$)')
    plt.title(f'Run {run}: background-subtracted and normalized by beam current',
              fontsize='xx-small')
    plt.tight_layout()

    # get save location
    dirname = os.path.dirname(filename)
    dirname = dirname if dirname else '.'

    # save results - figure
    plt.savefig(os.path.join(dirname, f'{df.iloc[0]["experiment"]}_run{run}_counts.pdf'))

def draw_hits(run):
    """Draw hits histogram for each run

    Args:
        run (ucnrun): run data
    """

    plt.figure(figsize=(6,6))

    # force iteration over all cycles
    for i in range(run.cycle_param.ncycles):

        # get cycle and check if it passed filter
        cycle = run[i]
        is_good = run.cycle_param.filter[i]

        # plot histogram
        bins, hist = cycle.get_hits_histogram(detector, as_datetime=True)
        line = plt.plot(bins, hist, label=f'Cycle {cycle.cycle}',
                        color=None if is_good else 'k')

        # get cycle text - strikeout if not good
        text = f'Cycle {cycle.cycle}'
        if not is_good:
            text = '\u0336'.join(text) + '\u0336'
        plt.text(bins[0], -1, text,
                 va='top',
                 ha='left',
                 fontsize='xx-small',
                 color=line[0].get_color(),
                 rotation='vertical')

    # plot elements
    plt.ylabel('Number of Hits')
    plt.ylim(-30, None)
    plt.xticks(rotation=90)
    plt.gca().tick_params(axis='x', which='major', labelsize='x-small')
    plt.tight_layout()

    # save file
    savefile = os.path.dirname(filename)
    savefile = os.path.join(savefile, f'{run.experiment_number}_run{run.run_number}_hits.pdf')
    plt.savefig(savefile)

# RUN ============================================

if __name__ == "__main__":

    # setup runs
    runs = read(run_numbers)
    if isinstance(runs, ucnrun):
        runs = [runs]

    # counts and hits
    for run in runs:
        get_satur_cnts(run, filename, periods)
        draw_hits(run)
        draw_counts(run.run_number, filename)

    # draw all counts
    draw_counts(None, filename)