# useful tools
# Derek Fujimoto
# June 2025
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
from iminuit import Minuit
from iminuit.cost import LeastSquares

def prettyprint(fn_equation, *parnames):
    """Function decorator which allows it to have a print function. This takes as
    argument the list of parameters and their errors and prints nicely the fit result
    for use in matplotlib (latex is rendered)

    Args:
        fn_equation (str): latex-rendered string of the equation used in the function
        parnames (str): parameter names
    """
    def wrapper(fn):
        def print(par, std):
            text = [f'Function: {fn_equation}']
            for i, name in enumerate(parnames):
                text.append(f'{name}: {par[i]:.5g} $\pm$ {std[i]:.5g}')
            return '\n'.join(text)
        fn.print = print
        fn.name = fn_equation
        return fn
    return wrapper

class Analyzer(object):

    def __init__(self, mode, outfile):
        """
        Args:
            r (ucnrun): run data to calculate lifetime for
            mode (str): lifetime|saturation
            outfile (str): file to write at the end
        """
        self.mode = mode
        self.outfile = outfile
        self.detector = 'Li6'

        # epics equipment to average values over: equip_name:period to average over
        if mode in 'lifetime':
            self.equipment = {'BeamlineEpics':           'production',
                              'UCN2Epics':               'storage',
                              'UCN2EpicsTemperature':    'storage',
                              'UCN2EpicsPressures':      'storage',
                              'UCN2EpicsOthers':         'storage',
                              'UCN2EpicsPhase2B':        'storage',
                              'UCN2EpicsPhase3':         'storage',
                              'UCN2EpPha5Pre':           'storage',
                              'UCN2EpPha5Oth':           'storage',
                              'UCN2EpPha5Tmp':           'storage',
                              'UCN2EpPha5Last':          'storage',
                              'UCN2Pur':                 'storage',
                        }
            self.periods = {'production':  0,
                            'storage':     1,
                            'count':       2,
                            'background':  1,}


        elif mode in 'saturation':
            self.equipment = {'BeamlineEpics':           'production',
                              'UCN2Epics':               'production',
                              'UCN2EpicsTemperature':    'production',
                              'UCN2EpicsPressures':      'production',
                              'UCN2EpicsOthers':         'production',
                              'UCN2EpicsPhase2B':        'production',
                              'UCN2EpicsPhase3':         'production',
                              'UCN2EpPha5Pre':           'production',
                              'UCN2EpPha5Oth':           'production',
                              'UCN2EpPha5Tmp':           'production',
                              'UCN2EpPha5Last':          'production',
                              'UCN2Pur':                 'production',
                        }
            self.periods = {'production':  0,
                            'count':       1,
                            'background':  0}

    def get_counts(self, run):
        """Get counts needed for a storage lifetime or source saturation calculation for a single run.
        Save this to file.

        Args:
            run (ucnrun): run data to calculate lifetime for


        Returns:
            pd.DataFrame: with counts needed for lifetime calculation
        """

        # print status
        print(f'Run {run.run_number} ' + '='*40 )

        # filter cycles
        run.set_cycle_filter(run.gen_cycle_filter(period_production=self.periods['production'],
                                            period_count=self.periods['count'],
                                            period_background=self.periods['background']))

        # get beam current and means
        beam_currents = run[:, self.periods['production']].beam_current_uA

        dbeam_currents = beam_currents.std()
        beam_currents = beam_currents.mean()

        # get storage durations and associated counts
        if self.mode in 'lifetime':
            duration = run[:, self.periods['storage']].cycle_param.period_durations_s
            duration_label = 'storage duration (s)'
        elif self.mode in 'saturation':
            duration = run[:, self.periods['production']].cycle_param.period_durations_s
            duration_label = 'production duration (s)'

        counts_bkgd = run[:, self.periods['background']].get_counts(self.detector)
        counts_bkgd = counts_bkgd.transpose()

        counts_norm = run[:, self.periods['count']].get_counts(self.detector,
                                            bkgd=counts_bkgd[0],
                                            dbkgd=counts_bkgd[1],
                                            norm=beam_currents,
                                            dnorm=dbeam_currents)

        counts = run[:, self.periods['count']].get_counts(self.detector,
                                            bkgd=counts_bkgd[0],
                                            dbkgd=counts_bkgd[1])
                                            
        counts_raw = run[:, self.periods['count']].get_counts(self.detector)

        # get durations
        durations = {f'{k} duration (s)': run.cycle_param.period_durations.loc[p, 0] for k, p in self.periods.items()}

        # make into a dataframe
        df = pd.DataFrame({'run': run.run_number,
                        'experiment': run.experiment_number,
                        'counts_bkgd_norm (1/uA)': counts_norm[:, 0],
                        'dcounts_bkgd_norm (1/uA)': counts_norm[:, 1],
                        'counts_bkgd': counts[:, 0],
                        'dcounts_bkgd': counts[:, 1],
                        'counts_raw': counts_raw[:, 0],
                        'dcounts_raw': counts_raw[:, 1],
                        'bkgd (counts)': counts_bkgd[0],
                        'dbkgd (counts)': counts_bkgd[1],
                        'beam_current (uA)': beam_currents,
                        'dbeam_current (uA)': dbeam_currents,
                        **durations,
                        })

        # add epics summary variables
        df_list = [df]
        for equip, period in self.equipment.items():
            df_list.append(pd.DataFrame(getattr(run[:, self.periods[period]].tfile, equip).mean()))
        df = pd.concat(df_list, axis='columns')

        # save file
        if self.outfile:
            dirname = os.path.dirname(self.outfile)
            if dirname:
                os.makedirs(dirname, exist_ok=True)

            # read file if exists
            try:
                df_old = pd.read_csv(self.outfile, comment='#')
            except FileNotFoundError:
                df_old = pd.DataFrame()

            # remove data from this run
            else:
                idx = df_old['run'] != run.run_number
                df_old = df_old.loc[idx]

            # add this to the old data
            df = pd.concat((df, df_old), axis='index')

            # write to file
            header = [f'# UCN counts, durations, and average metadata for {self.mode} measurement',
                      f'# Last updated: {str(datetime.now())}']
            with open(self.outfile, 'w') as fid:
                fid.write('\n'.join(header))
                fid.write('\n')
            df.to_csv(self.outfile, index=False, mode='a')

        return df

    def draw_hits(self, run):
        """Draw hits histogram for each run

        Args:
            run (ucnrun): run data
            outdir (str): directory in which to save figure
        """

        outdir = os.path.dirname(self.outfile)

        plt.figure(figsize=(6,6))

        # force iteration over all cycles
        for i in range(run.cycle_param.ncycles):

            # get cycle and check if it passed filter
            cycle = run[i]
            if run.cycle_param.filter is None:
                is_good = True
            else:
                is_good = run.cycle_param.filter[i]

            # plot histogram
            bins, hist = cycle.get_hits_histogram(self.detector, as_datetime=True)
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

        # plot elements for viewing
        plt.title(f'Run {run.run_number}')
        plt.tight_layout()

def fit(fitfn, x, y, dy, p0, err_kwargs, 
        index=None, index_name=None, outfile=None, xlabel=None, ylabel=None):
    """Draw and fit counts for a run or set of runs

    Args:
        x, y, dy (iterable): data to fit
        p0 (iterable): initial fit paramters
        err_kwargs (dict): keyword arguments to pass to plt.errorbar
        xlabel, ylabel (str): axis titles
        index: use this as the index of the file
        index_name (str): use this as index name
    """

    # setup index
    if index is None:
        index = 0
    if index_name is None:
        index_name = ''

    # draw data
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
        df = pd.DataFrame({**values, **errors}, index=[index])
        df.index.name = index_name

        header = [f'# Fit function: {fitfn.name if hasattr(fitfn, "name") else ""}',
                  f'# Last updated: {str(datetime.now())}']

        # get old data and concat
        try:
            df_old = pd.read_csv(outfile, comment='#')
        except FileNotFoundError:
            pass
        else:
            df = pd.concat(df_old, df)

        with open(outfile, 'w') as fid:
            fid.write('\n'.join(header))
            fid.write('\n')
        df.to_csv(outfile, mode='a', index=False)

    return
