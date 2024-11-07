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
def path(r):        return r.path
def duration_hours(r):
    times = r.tfile.BeamlineEpics.index.values
    return (numpy.max(times)-numpy.min(times))/3600

# BEAMLINE ---------------------------------------------------------------
def beam_current_mean(r):

    # beam currents for each cycle/period
    means = r[:,:].beam_current_uA.apply(numpy.mean)

    # get mean currents for all periods
    df = pandas.DataFrame(means).mean(axis='index')

    # get period with largest current
    return df.max()

def beam_current_std(r):

    period = production_period(r)

    # beam currents for each cycle/period
    stdev = r[:,period].beam_current_uA.apply(numpy.std)

    # get stdev of period with largest current
    return numpy.mean(stdev)

def beam_duration_on(r):    return numpy.mean(r.beam_on_s)
def beam_duration_off(r):   return numpy.mean(r.beam_off_s)

# RUN PARAMETERS ---------------------------------------------------------
def production_period(r):
    # beam currents for each cycle/period
    means = r[:,:].beam_current_uA.apply(numpy.mean)

    # get period with largest current
    return pandas.DataFrame(means).mean(axis='index').argmax()

def count_period_li6(r):
    # period with highest counts
    counts, _ = r[:,:].get_counts('Li6').transpose()
    mean_counts = numpy.mean(counts, axis=1)
    return numpy.argmax(mean_counts)

def count_period_he3(r):
    # period with highest counts
    counts, _ = r[:,:].get_counts('He3').transpose()
    mean_counts = numpy.mean(counts, axis=1)
    return numpy.argmax(mean_counts)

# STATISTICS -------------------------------------------------------------
def counts_li6(r):  return r.get_hits('Li6')['tIsUCN'].sum()
def counts_he3(r):  return r.get_hits('He3')['tIsUCN'].sum()

def background_li6(r):
    counts, _ = r[:, production_period(r)].get_counts('Li6').transpose()
    return numpy.mean(counts)

def background_he3(r):
    counts, _ = r[:, production_period(r)].get_counts('He3').transpose()
    return numpy.mean(counts)

# SOURCE PARAMETERS ------------------------------------------------------

# MISC -------------------------------------------------------------------

