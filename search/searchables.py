# functions to generate searchable parameters
# Derek Fujimoto
# Nov 2024

"""
    RULES

    * Each function takes as input a ucnrun and returns a single value (not an array or list)
    * The function name will be the column name in the database
    * If you import more than numpy or pandas you will need to update gen_database.get_run_searchables

"""

import pandas, numpy, ucndata, os

# HEADER ITEMS ----------------------------------------------------------
def day(r):     return pandas.to_datetime(r.start_time).day
def month(r):   return r.month
def year(r):    return r.year

def run(r):         return r.run_number
def comment(r):     return r.comment
def title(r):       return r.run_title
def shifters(r):    return r.shifters
def experiment(r):  return r.experiment_number

# BEAMLINE ---------------------------------------------------------------
def beam_current_mean(r):

    # beam currents for each cycle/period
    means = r[:,:].beam_current_uA.apply(numpy.mean)

    # get mean currents for all periods
    df = pandas.DataFrame(means).mean(axis='index')

    # get period with largest current
    return df.max()

def beam_current_std(r):

    # beam currents for each cycle/period
    means = r[:,:].beam_current_uA.apply(numpy.mean)
    stdev = r[:,:].beam_current_uA.apply(numpy.std)

    # get period for most largest current
    period = pandas.DataFrame(means).mean(axis='index').argmax()

    # get stdev of period with largest current
    return pandas.DataFrame(stdev)[period].mean(axis='index')

def beam_duration_on(r):    return numpy.mean(r.beam_on_s)
def beam_duration_off(r):   return numpy.mean(r.beam_off_s)

# STATISTICS -------------------------------------------------------------
def counts_li6(r):  return r.get_hits('Li6')['tIsUCN'].sum()
def counts_he3(r):  return r.get_hits('He3')['tIsUCN'].sum()

# SOURCE PARAMETERS ------------------------------------------------------

# MISC -------------------------------------------------------------------
def path(r):
    filename = f'ucn_run_{r.run_number:0>8}.root'
    rel_path = os.path.join(ucndata.settings.datadir, filename)
    return os.path.abspath(rel_path)