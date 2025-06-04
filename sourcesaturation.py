# Get source saturation
# Derek Fujimoto
# Nov 2024

from ucndata import settings, read, ucnrun
from tools import *
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from iminuit import Minuit
from iminuit.cost import LeastSquares
from datetime import datetime

def fitfn(t, p0, tau):
    return p0*(1-np.exp(-t/tau))

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

    counts_norm = run[:, periods['count']].get_counts(detector,
                                        bkgd=counts_bkgd[0],
                                        dbkgd=counts_bkgd[1],
                                        norm=beam_currents,
                                        dnorm=dbeam_currents,
                                        )

    counts = run[:, periods['count']].get_counts(detector,
                                        bkgd=counts_bkgd[0],
                                        dbkgd=counts_bkgd[1],
                                        )


    # make into a dataframe
    df = pd.DataFrame({'run': run.run_number,
                       'experiment': run.experiment_number,
                       'production duration (s)': production_duration,
                       'counts_norm (1/uA)': counts_norm[:, 0],
                       'dcounts_norm (1/uA)': counts_norm[:, 1],
                       'counts': counts[:, 0],
                       'dcounts': counts[:, 1],
                       'bkgd (counts)': counts_bkgd[0],
                       'beam_current (uA)': beam_currents,
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

def get_saturation_time(x, y, dy, p0=None):
    """Draw and fit counts for a run or set of runs

    Args:
        run (int): run number to fit and draw.
        p0 (iterable): initial fit paramters
    """
    # fit
    m = Minuit(LeastSquares(x = x,
                            y = y,
                            yerror = dy,
                            model = fitfn), *p0)
    m.migrad()
    par = m.values
    std = m.errors

    return (par, std)

def fit(x, y, dy, p0, err_kwargs, outfile=None, xlabel=None, ylabel=None):
    """Draw and fit counts for a run or set of runs

    Args:
        x, y, dy (iterable): data to fit
        p0 (iterable): initial fit paramters
        err_kwargs (dict): keyword arguments to pass to plt.errorbar
        xlabel, ylabel (str): axis titles
    """

    plt.errorbar(x, y, dy, **err_kwargs)
    plt.yscale('log')
    if xlabel is not None: plt.xlabel(xlabel)
    if ylabel is not None: plt.ylabel(ylabel)

    # fit
    m = Minuit(LeastSquares(x = x,
                            y = y,
                            yerror = dy,
                            model = fitfn), *p0)
    m.migrad()
    par = m.values
    std = m.errors

    # draw
    plt.plot(x, fitfn(x, **par.to_dict()))
    plt.text(0.95, 0.95, fitfn.print(par, std),
            ha='right',
            va='top',
            transform=plt.gca().transAxes,
            fontsize='x-small',
            backgroundcolor='w',
            multialignment='left')

    plt.grid(which='both', axis='both', visible=True)
    plt.tight_layout()

    # load old fit results
    if outfile is not None:

        # get save location
        dirname = os.path.dirname(outfile)
        dirname = dirname if dirname else '.'

        # save results - figure
        plt.savefig(os.path.join(dirname, f'{os.path.splitext(os.path.basename(outfile))[0]}.pdf'))

        # make dataframe for new data
        values = m.values.to_dict()
        errors = m.errors.to_dict()
        errors = {f'd{key}':val for key, val in errors.items()}
        df = pd.DataFrame({**values, **errors})

        # save result
        df = pd.concat((df, df_old), axis='index')

        header = ['# Source Saturation',
                 f'# Fit function: {fitfn.name if hasattr(fitfn, "name") else ""}',
                  '# Written by sourcesaturation.py',
                 f'# Last updated: {str(datetime.now())}',
                 ]

        with open(outfile, 'w') as fid:
            fid.write('\n'.join(header))
            fid.write('\n')
        df.to_csv(outfile, mode='a')

    return

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
    plt.ylabel('UCN Hits')
    plt.ylim(-30, None)
    plt.xticks(rotation=90)
    plt.gca().tick_params(axis='x', which='major', labelsize='x-small')
    plt.tight_layout()

    # save file
    savefile = os.path.join(outdir, f'{run.experiment_number}_run{run.run_number}_hits.pdf')
    plt.savefig(savefile)