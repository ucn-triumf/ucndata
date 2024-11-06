# read UCN data or a set of UCN data
# Derek Fujimoto
# Aug 2024

import glob
from multiprocessing import cpu_count, Pool
from .ucnrun import ucnrun
from .applylist import applylist
from .merge import merge_inlist
from collections.abc import Iterable
from tqdm import tqdm
import numpy as np
from functools import partial
import os

def read(path, as_dataframe=True, nproc=-1, header_only=False):
    """Read out single or multiple UCN run files from ROOT

    Args:
        path (str|list): path to file, may include wildcards
            may be a list of paths which may include wildcards
            OR list of ints to specify run numbers
            OR list of mixed ints and strings either of run numbers or of the format 'x+y' to denote merged runs, where x and y are ints
        as_dataframe (bool): if true, convert to dataframes
        nproc (int): number of processors used in read. If <= 0, use total - nproc. If > 0 use nproc.
        header_only (bool): if true, read only the header

    Example:
        ```python
        # example with run numbers
        runs = read([1846, 1847, 1848])

        # example with wildcards
        runs = read('/path/datadir/ucn_run_000018*')

        # example with merged runs and mixed types
        runs = read([1846, '1847+1848', '1849', '/path/datadir/ucn_run_0000185*'])
        ```

    Returns:
        applylist: sorted by run number, contains ucnrun objects
    """

    # normalize input
    if not isinstance(path, Iterable) or isinstance(path, str):
        path = [path]

    # expand wildcards
    pathlist = []
    for p in path:
        if isinstance(p, str):
            pathlist.extend(glob.glob(p))
    else:
        pathlist.append(path)

    # check for merged runs
    read_in_paths = []
    items_to_merge = []
    for p in path:

        # if a path then cannot be a merged run so just add to the list
        if os.path.isfile(p):
            read_in_paths.append(p)

        # if it's an int or float, then also cannot be merged
        elif isinstance(p, (int, float, np.number)):
            read_in_paths.append(p)

        # if it's a string that's really an int then not merged
        elif isinstance(p, str) and p.isdigit():
            read_in_paths.append(int(p))

        # if it's a string with a '+' in it then it's a merged run
        elif isinstance(p, str) and '+' in p:
            p = [i.strip() for i in p.split('+')]
            p = [int(i) if i.isdigit() else i for i in p]
            items_to_merge.append(p)
            read_in_paths.extend(p)

        # unknown input type
        else:
            raise RuntimeError(f'Bad read input "{p}"')

    # read out the data
    if nproc <= 0:
        nproc = max((cpu_count()+nproc, 1))

    with Pool(nproc) as pool:
        fn = partial(ucnrun, header_only=header_only)
        iterable = tqdm(pool.imap_unordered(fn, read_in_paths),
                        leave=False,
                        total=len(read_in_paths),
                        desc='Reading run data',
                        position=1)
        data = np.fromiter(iterable, dtype=object)
    print()

    # sort result
    run_numbers = [d.run_number for d in data]
    idx = np.argsort(run_numbers)

    output = applylist(data[idx])

    # do the merging
    for to_merge in items_to_merge:
        output = merge_inlist(output, to_merge)

    # to dataframe
    if as_dataframe:
        output.to_dataframe()

    # return single run
    if len(output) == 1:
        return output[0]

    # return run list
    else:
        return output

