# read UCN data or a set of UCN data
# Derek Fujimoto
# Aug 2024

import glob
from multiprocessing import cpu_count, Pool, RLock
from .ucnrun import ucnrun
from .applylist import applylist
from collections.abc import Iterable
from tqdm import tqdm
import numpy as np
from functools import partial

def read(path, nproc=-1, header_only=False):
    """Read out single or multiple UCN run files from ROOT

    Args:
        path (str|list): path to file, may include wildcards, may be a list of paths which may include wildcards or list of ints to specify run numbers
        nproc (int): number of processors used in read. If <= 0, use total - nproc. If > 0 use nproc.
        header_only (bool): if true, read only the header

    Example:
        >>> # example with run numbers
        >>> runs = read([1846, 1847, 1848])

        >>> # example with wildcards
        >>> runs = read('/path/datadir/ucn_run_000018*')

    Returns:
        applylist: sorted by run number, contains ucnrun objects
    """

    # normalize input
    if not isinstance(path, Iterable):
        path = [path]

    # expand wildcards
    if isinstance(path[0], str):
        pathlist = []
        for p in path:
            pathlist.extend(glob.glob(p))

    else:
        pathlist = path

    # read out the data
    if nproc <= 0:
        nproc = max(cpu_count()-nproc, 1)

    with Pool(nproc) as pool:
        fn = partial(ucnrun, header_only=header_only)
        iterable = tqdm(pool.imap_unordered(fn, pathlist),
                        leave=False,
                        total=len(pathlist),
                        desc='Reading',
                        position=1)
        data = np.fromiter(iterable, dtype=object)

    # sort result
    run_numbers = [d.run_number for d in data]
    idx = np.argsort(run_numbers)

    output = applylist(data[idx])

    # return single run
    if len(output) == 1:
        return output[0]

    # return run list
    else:
        return output

