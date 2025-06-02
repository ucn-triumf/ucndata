# Get storage lifetime
# Derek Fujimoto
# Oct 2024

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

# fit function to counts vs lifetimes
@prettyprint(r'$p_0 \exp(-t/\tau)$', '$p_0$', r'$\tau$')
def fitfn(t, p0, tau):
    return p0*np.exp(-t/tau)

def get_storage_cnts(run, periods, outfile):
    """Get counts needed for a storage lifetime calculation for a single run.
    Save this to file.

    Args:
        r (ucnrun): run data to calculate lifetime for
        periods (dict): specify which periods are for which purpose (production, storage,count, background)

    Returns:
        pd.DataFrame: with counts needed for lifetime calculation
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

    # get storage durations and associated counts
    storage_duration = run[:, periods['storage']].cycle_param.period_durations_s
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
                       'storage duration (s)': storage_duration,
                       'counts (1/uA)': counts[:, 0],
                       'bkgd (counts)': counts_bkgd[0],
                       'normalization (uA)': beam_currents,
                       'dcounts (1/uA)': counts[:, 1],
                       'dbkgd (counts)': counts_bkgd[1],
                       'dnormalization (uA)': dbeam_currents,
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
        header = ['# Normalized counts and storage times for lifetime measurement',
                  '# Written by storagelifetime.py',
                  f'# Last updated: {str(datetime.now())}']
        with open(outfile, 'w') as fid:
            fid.write('\n'.join(header))
            fid.write('\n')
        df.to_csv(outfile, index=False, mode='a')

    return df

def get_lifetime(run, lifefile, fitfn=None, p0=None):
    """Draw and fit counts for a run or set of runs

    Args:
        run (int): run number to fit and draw.
        lifefile (str): path to file with the counts (output of get_storage_cnts)
        fitfn (fn handle|None): if none, don't do fit. else fit this function
        p0 (iterable): initial fit paramters
    """

    run = str(run)

    # get data
    df = pd.read_csv(lifefile, comment='#', index_col=0)
    df = df.loc[run]

    # get data
    df.sort_values('storage duration (s)', inplace=True)
    storage_duration = df['storage duration (s)'].values
    counts = df['counts (1/uA)'].values
    dcounts = df['dcounts (1/uA)'].values

    # draw data
    plt.figure()
    plt.errorbar(storage_duration, counts, dcounts, fmt='.')
    plt.yscale('log')
    plt.xlabel('Storage Duration (s)')
    plt.ylabel('Normalized Number of Counts (uA$^{-1}$)')
    plt.title(f'Run {run}: background-subtracted and normalized by beam current',
              fontsize='xx-small')

    # do the fit
    if fitfn is not None:

        # default p0
        if p0 is None:
            p0 = np.ones(fitfn.__code__.co_argcount-1)

        # fit
        m = Minuit(LeastSquares(x = storage_duration,
                                y = counts,
                                yerror = dcounts,
                                model = fitfn), *p0)
        m.migrad()
        par = m.values
        std = m.errors

        # draw
        plt.plot(storage_duration, fitfn(storage_duration, **par.to_dict()))

        if hasattr(fitfn, 'print'):
            plt.text(0.95, 0.95, fitfn.print(par, std),
                    ha='right',
                    va='top',
                    transform=plt.gca().transAxes,
                    fontsize='x-small',
                    backgroundcolor='w',
                    multialignment='left')

    plt.tight_layout()

    # get save location
    dirname = os.path.dirname(lifefile)
    dirname = dirname if dirname else '.'

    # save results - figure
    plt.savefig(os.path.join(dirname, f'{df.iloc[0]["experiment"]}_run{run}_lifetime.pdf'))

    # load old fit results
    lifefile = os.path.join(dirname, 'lifetimes.csv')
    try:
        df_old = pd.read_csv(lifefile, comment='#', index_col=0)
    except FileNotFoundError:
        df_old = pd.DataFrame()

    # remove data from this run
    else:
       df_old = df_old.drop(index=run, errors='ignore')

    # make dataframe for new data
    values = m.values.to_dict()
    errors = m.errors.to_dict()
    errors = {f'd{key}':val for key, val in errors.items()}
    df = pd.DataFrame({**values, **errors}, index=[run])
    df.index.name = 'run'

    # save result
    df = pd.concat((df, df_old), axis='index')

    header = ['# Storage Lifetimes',
              f'# Fit function: {fitfn.name if hasattr(fitfn, "name") else ""}',
              '# Written by storagelifetime.py',
              f'# Last updated: {str(datetime.now())}',
              ]

    with open(lifefile, 'w') as fid:
        fid.write('\n'.join(header))
        fid.write('\n')
    df.to_csv(lifefile, mode='a')

def get_global_lifetime(lifefile, fitfn, p0=None):
    """Fit all runs with a shared lifetime

    Args:
        lifefile (str): path to file with the counts (output of get_storage_cnts)
        fitfn (fn handle|None): if none, don't do fit. else fit this function
        p0 (iterable): initial fit paramters

    Returns:
        tuple: (par, std) output of global_fitter

    Notes:
        too much copy/paste from get_lifetime... but too lazy to properly combine these two
    """

    # get data
    df = pd.read_csv(lifefile, comment='#', index_col=0)

    # get data
    df.sort_values('storage duration (s)', inplace=True)
    df.reset_index(inplace=True)

    run = []
    storage_duration = []
    counts = []
    dcounts = []

    for r, g in df.groupby('run'):
        run.append(r)
        storage_duration.append(g['storage duration (s)'].values)
        counts.append(g['counts (1/uA)'].values)
        dcounts.append(g['dcounts (1/uA)'].values)

    # get lifetime index
    life_idx = None
    for i, arg in enumerate(fitfn.__code__.co_varnames[1:]):
        if arg.lower() == 'tau':
            life_idx = i
            break

    # do the fit
    shared = [i == life_idx for i in range(fitfn.__code__.co_argcount-1)]
    g = global_fitter(fitfn, storage_duration, counts, dcounts,
                      shared = shared)

    if p0 is not None:
        g.fit(p0=p0)
    else:
        g.fit()

    par, std, _, _ = g.get_par()

    # draw data and fits
    plt.figure()

    for i in range(len(run)):
        line = plt.errorbar(storage_duration[i], counts[i], dcounts[i], fmt='.',
                            label=f'Run {run[i]}')
        plt.plot(storage_duration[i], fitfn(storage_duration[i], *par[i]),
                 color=line[0].get_color())

    plt.yscale('log')
    plt.xlabel('Storage Duration (s)')
    plt.ylabel('Normalized Number of Counts (uA$^{-1}$)')
    plt.title(f'Global Fit: background-subtracted and normalized by beam current',
              fontsize='xx-small')

    plt.text(0.95, 0.95, f'Global lifetime: {par[0][life_idx]:.5g} $\\pm$ {std[0][life_idx]:.5g} s',
        ha='right',
        va='top',
        transform=plt.gca().transAxes,
        fontsize='x-small',
        backgroundcolor='w',
        multialignment='left')

    plt.legend(fontsize='xx-small', loc='lower left')

    plt.tight_layout()

    # get save location
    dirname = os.path.dirname(lifefile)
    dirname = dirname if dirname else '.'

    # save results - figure
    plt.savefig(os.path.join(dirname, 'global_fit.pdf'))

    return (par, std)

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

# RUN ============================================

if __name__ == '__main__':

    # settings
    # settings.datadir = 'root_files'     # path to root data
    settings.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer]
    settings.DET_NAMES.pop('He3')       # don't check He3 detector data
    detector = 'Li6'                    # detector to use when getting counts [Li6|He3]
    outfile = 'storagelifetime/storagecounts.csv'      # save counts output
    run_numbers = [1846]   # example: [1846, '1847+1848']

    # periods settings
    periods = {'production':  0,
            'storage':     1,
            'count':       2,
            'background':  1}

    # setup runs
    runs = read(run_numbers)
    if isinstance(runs, ucnrun):
        runs = [runs]

    # counts and hits
    for run in runs:
        get_storage_cnts(run)
        draw_hits(run)

    # calculate lifetimes for each run
    for run in run_numbers:
        get_lifetime(run, outfile, fitfn)

    # get global lifetime
    par, std = get_global_lifetime(outfile, fitfn)
