# Generate a searchable database of runs and relevant parameters using parquet
# Derek Fujimoto
# Nov 2024

import fastparquet as fp
import settings as datasettings
import searchables
import pandas as pd
import numpy as np
import shutil, os, glob

from ucndata import ucnrun
from tqdm import tqdm
from multiprocessing import cpu_count, Pool

def add_runs_to_database(run_number_list):
    """Get the searchable data from a set of runs and add it to the database

    Args:
        run_number_list (iterable|int|str): a single run number int
            or path to file or a list of these

    Returns:
        None: updates database parquet file
    """

    # check input
    if isinstance(run_number_list, (int, np.integer, str)):
        run_number_list = [run_number_list]

    # make dataframe for the new runs
    nproc = max((cpu_count()-1, 1))
    with Pool(nproc) as pool:
        iterable = tqdm(pool.imap_unordered(get_run_searchables, run_number_list),
                        leave=True,
                        total=len(run_number_list),
                        desc='Generating searchable columns',
                        position=1)
        df = np.fromiter(iterable, dtype=object)

    df = pd.concat(df, axis='columns').transpose()
    df.set_index('run', inplace=True)

    # read the database
    try:
        db = fp.ParquetFile(datasettings.filename).to_pandas()
    except FileNotFoundError:
        db = pd.DataFrame()

    # replace values in database
    db.drop(index=df.index, errors='ignore', inplace=True)

    # concat
    db = pd.concat((db, df), axis='index')

    # get good datatypes
    db = db.convert_dtypes()

    # save
    fp.write(datasettings.filename, db)

def get_columns():
    """Get the columns in the database

    Returns:
        list: column names
    """
    return fp.ParquetFile(datasettings.filename).columns

def get_database(columns=None):
    """Get the database as a pandas dataframe.

    Args:
        columns (iterable|None): list of column names. If none then get all columns
            Speed is increased for fewer columns fetched

    Returns:
        pd.DataFrame: the database
    """
    return fp.ParquetFile(datasettings.filename).to_pandas(columns)

def get_run_searchables(run_number):
    """Get searchable run parameters as dictionary

    Args:
        run_number (int|str): run to generate searchable objects from

    Returns:
        pd.Series: of searchable items
    """

    # get list of functions
    function_list = dir(searchables)
    function_list = [f for f in function_list if '_' != f[0] ]
    del function_list[function_list.index('pandas')]
    del function_list[function_list.index('numpy')]
    del function_list[function_list.index('ucndata')]
    del function_list[function_list.index('os')]

    # read the run
    run = ucnrun(run_number)

    # make searchable dict
    searchdir = {fn: getattr(searchables, fn)(run) for fn in function_list}

    return pd.Series(searchdir)

def regen_database(path=None):
    """Regenerate the whole database. Useful if adding columns.

    Args:
        path (str|None): path to root file directory. If none, get paths from existing database

    Returns:
        None: delete and re-write database file
    """

    # get filepaths in the database
    if path is None:
        paths = get_database(['path']).values
        paths = paths[:, 0]
    else:
        paths = glob.glob(os.path.join(path, 'ucn_run_*.root'))

    # backup the database
    bkup = datasettings.filename + '.bkup'
    try:
        shutil.copy(datasettings.filename, bkup)
    except FileNotFoundError:
        pass

    # delete the database if exists
    else:
        os.remove(datasettings.filename)

    # get those files
    add_runs_to_database(paths)

def search_database(filters):
    """Get the database by column filters. See [fastparquet documentation](https://fastparquet.readthedocs.io/en/latest/api.html#fastparquet.ParquetFile.to_pandas)

    Args:
        filters (list of list of tuples or list of tuples): [[(column, op, val), …],…] where op is [==, =, >, >=, <, <=, !=, in, not in] The innermost tuples are transposed into a set of filters applied through an AND operation. The outer list combines these sets of filters through an OR operation. A single list of tuples can also be used, meaning that no OR operation between set of filters is to be conducted.

    Returns:
        np.ndarray: list of run numbers satisfying the search results

    Example:
        ```python
        # lets use this shorthand
        [C] = [condition] = [column, op, value]

        # this means [C1] AND [C2]
        [ [[C1], [C2]] ]

        # this means [C1] OR [C2]
        [ [C1], [C2] ]

        # this also means [C1] OR [C2]
        [ [[C1]], [[C2]] ]

        # this means ([C1] AND [C2]) OR ([C3] AND [C4])
        [ [[C1], [C2]], [[C3], [C4]] ]
        ```
    """
    return fp.ParquetFile(datasettings.filename).to_pandas(datasettings.output_columns,
                                                       filters=filters,
                                                       row_filter=True)

