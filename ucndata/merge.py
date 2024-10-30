# Merge a list of ucnrun objects into a single object
# Derek Fujimoto
# Oct 2024

from .ucnrun import ucnrun
from .applylist import applylist
from .exceptions import *
from rootloader import tfile, ttree, th1, th2, attrdict
import numpy as np
import pandas as pd
import warnings

def merge(ucnlist):
    """Merge a list of ucndata objects into a single object

    Args:
        ucnlist (list): iterable of ucndata objects

    Returns:
        ucnrun: single object with all data inside of it
    """

    # sort by run number, assume run numbers are in chronological order
    ucnlist = np.array(ucnlist)
    run_num = [d.run_number for d in ucnlist]
    idx = np.argsort(run_num)
    ucnlist = ucnlist[idx]

    # initialize output object
    ucnmerged = ucnrun(None)

    # set header items as arrays
    for key in ucnlist[0].__dict__.keys():

        # skip some things
        if key in ('tfile', 'cycle_param'):
            continue

        # make and set arrays
        values = np.array([getattr(data, key) for data in ucnlist])
        setattr(ucnmerged, key, values)

    # merge cycle_param
    ucnmerged.cycle_param = attrdict()
    names = tuple(ucnlist[0].cycle_param.keys())
    for name in names:
        param = [r.cycle_param[name] for r in ucnlist]

        # booleans
        if isinstance(param[0], bool):
            ucnmerged.cycle_param[name] = any(param)

        # sum ints
        elif isinstance(param[0], (int, np.integer)):
            ucnmerged.cycle_param[name] = np.sum(param)

        # dataframes
        elif isinstance(param[0], pd.DataFrame):
            if name == 'cycle_times':
                df = pd.concat(param, axis='index')
                df.reset_index(drop=True, inplace=True)
                ucnmerged.cycle_param[name] = df

            elif name == 'valve_states':
                v0 = param[0]
                if not all([all(v0 == v) for v in param]):
                    raise MergeError('Not all valve states the same')
                ucnmerged.cycle_param[name] = v0

            elif name in ('period_end_times', 'period_durations_s'):
                df = pd.concat(param, axis='columns')
                df = df.transpose()
                df.reset_index(drop=True, inplace=True)
                df = df.transpose()
                ucnmerged.cycle_param[name] = df

            else:
                warnings.warn(f'Unknown cycle_param dataframe named "{name}" in run {ucnlist[0].run_number}', MergeWarning)
                ucnmerged.cycle_param[name] = pd.concat(param)

        # series
        elif isinstance(param[0], pd.Series):
            ucnmerged.cycle_param[name] = pd.concat(param)

        # none
        elif param[0] is None:
            ucnmerged.cycle_param[name] = None

        # else
        else:
            warnings.warn(f'Unknown cycle_param type "{type(param[0])}" in run {ucnlist[0].run_number}', MergeWarning)
            ucnmerged.cycle_param[name] = param[0]

    # setup merge tfiles
    obj_names = [] # list of all contained objects
    for dat in ucnlist:

        # convert tfiles to dataframes
        dat.tfile.to_dataframe()

        # get names of objects
        obj_names.extend(list(dat.tfile.keys()))

    # get unique object names
    obj_names = np.unique(obj_names)

    # set tfile
    ucnmerged.tfile = tfile(None)

    # merge tfile
    for name in obj_names:

        name = str(name)
        lst = [dat.tfile[name] for dat in ucnlist if name in dat.tfile.keys()]
        df = pd.concat(lst, axis='index')

        first_attrs = lst[0].attrs # first item for its metadata

        # merge tree
        if first_attrs['type'] is ttree:
            ucnmerged.tfile[name] = df.copy()
            ucnmerged.tfile[name].attrs['type'] = ttree

        # merge th1
        elif first_attrs['type'] is th1:

            # error pre-treatment
            df[first_attrs['ylabel'] + " error"] **= 2

            # sum
            values = df.groupby(first_attrs['xlabel']).sum()

            # errors post treatment
            values[first_attrs['ylabel'] + " error"] **= 0.5

            # reset index
            values.reset_index(inplace=True)

            # set
            ucnmerged.tfile[name] = values.copy()

            # common attrs
            ucnmerged.tfile[name].attrs['type'] = th1
            for key in ('name', 'title', 'xlabel', 'ylabel', 'base_class', 'nbins'):
                ucnmerged.tfile[name].attrs[key] = first_attrs[key]

            # summed attrs
            ucnmerged.tfile[name].attrs['sum'] = sum([i.attrs['sum'] for i in lst])
            ucnmerged.tfile[name].attrs['entries'] = int(sum([i.attrs['entries'] for i in lst]))

        # merge th2
        elif first_attrs['type'] is th2:

            # error pre-treatment
            df[first_attrs['zlabel'] + " error"] **= 2

            # sum
            values = df.groupby([first_attrs['xlabel'], first_attrs['ylabel']]).sum()

            # errors post treatment
            values[first_attrs['zlabel'] + " error"] **= 0.5

            # set
            ucnmerged.tfile[name] = values.copy()

            # common attrs
            ucnmerged.tfile[name].attrs['type'] = th2
            for key in ('name', 'title', 'xlabel', 'ylabel', 'zlabel',
                        'base_class', 'nbinsx', 'nbinsy'):
                ucnmerged.tfile[name].attrs[key] = first_attrs[key]

            # summed attrs
            ucnmerged.tfile[name].attrs['sum'] = sum([i.attrs['sum'] for i in lst])
            ucnmerged.tfile[name].attrs['entries'] = int(sum([i.attrs['entries'] for i in lst]))

    return ucnmerged

def merge_inlist(ucnlist, mergeruns):
    """Merge runs within a list and return a new list with the merged objects

    Args:
        ucnlist (list): iterable of ucndata objects
        mergeruns (list): iterable of run numbers to merge

    Example:
        x = [ucnrun(r) for r in (1846, 1847, 1848)]
        y = merge_inlist(x, (1846, 1847))

        # y now contains two entries: merged 1846+1847 and 1848

    Returns:
        applylist: of ucnruns, some are merged, as indicated
    """

    # convert input to applylist
    ucnlist = applylist(ucnlist)

    # get run numbers
    run_number = ucnlist.run_number

    # get index of those we want to merge
    idx = np.array([r in mergeruns for r in run_number])

    # do merge and drop
    merged = merge(ucnlist[idx])
    ucnlist = ucnlist[~idx]

    # append merged runs
    first = np.where(idx)[0][0]
    ucnlist.insert(first, merged)

    return ucnlist
