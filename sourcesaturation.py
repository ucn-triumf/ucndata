# Get source saturation
# Derek Fujimoto
# Nov 2024

from ucndata import settings, read, ucnrun
from tools import *
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

def get_satur_cnts(run, outfile, periods):
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
                       'beam_current (uA)': beam_currents,
                       'dcounts (1/uA)': counts[:, 1],
                       'dbkgd (counts)': counts_bkgd[1],
                       'dbeam_current (uA)': dbeam_currents,
                       })

    # save file
    if outfile:
        dirname = os.path.dirname(outfile)
        if dirname:
            os.makedirs(dirname, exist_ok=True)

        # read file if exists
        try:
            df_old = pd.read_csv(outfile, comment='#')
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
        with open(outfile, 'w') as fid:
            fid.write('\n'.join(header))
            fid.write('\n')
        df.to_csv(outfile, index=False, mode='a')

    return df

def draw_counts(df, ax=None, **error_kwargs):
    """Draw and fit counts for a run

    Args:
        df (pd.DataFrame): dataframe with the data. Must have columns from output of get_satur_cnts
        ax (plt.Axis): axes to draw in
        error_kwargs: passed to plt.errorbar
    """

    # get data
    df.sort_values('production duration (s)', inplace=True)
    production_duration = df['production duration (s)'].values
    counts = df['counts (1/uA)'].values
    dcounts = df['dcounts (1/uA)'].values

    # get axes
    if ax is None:
        plt.figure()
        ax = plt.gca()

    # draw data
    ax.errorbar(production_duration, counts, dcounts)
    ax.set_yscale('log')
    ax.set_xlabel('Production Duration (s)')
    ax.set_ylabel('Number of Counts Normalized to Beam Current (uA$^{-1}$)')
    plt.tight_layout()

def draw_hits(run, outdir='.'):
    """Draw hits histogram for each run

    Args:
        run (ucnrun): run data
        outdir (str): directory in which to save figure
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
    savefile = os.path.join(outdir, f'{run.experiment_number}_run{run.run_number}_hits.pdf')
    plt.savefig(savefile)