# Run analysis for TCN6A-050: source lifetime measurement at varying beam energies
# Derek Fujimoto
# June 2025
from ucndata import read, ucnrun
import os
import tools
from scipy.optimize import curve_fit
import pandas as pd
import numpy as np

# settings
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
outfile = 'TCN6A_050/summary.csv'    # save counts output

# include cycles to drop - manual cycle filter
run_numbers = { 2575:[1],
                2576:[2],
                2577:[2],
                2578:[19], # 15 maybe
                2579:[1,2,3,4,5,8], # 0, 7 maybe
                2580:[], # all good
                2581:[], # all good
                2582:[], # all good
                2584:[], # all good 
                2585:[], # all good 
                2587:[], # all good 
                2588:[1], # 0 maybe
                2590:[0], 
                2592:[], # all good
               }

os.makedirs('TCN6A_050', exist_ok=True)

# look for bad data in the run
def inspect_run(run):
    fig, ax = plt.subplots(nrows=2, ncols=1, sharex=True,
                        layout='constrained', figsize=(8,10))

    run.beam1a_current_uA.plot(ax=ax[0])
    run.beam_current_uA.plot(ax=ax[0])
    plt.sca(ax[0])
    run.draw_cycle_times()
    
    plt.sca(ax[1])
    plt.plot(*run.get_hits_histogram('Li6'))
    plt.yscale('log')
    ax[0].set_title(run.run_number,fontsize='x-small')
    run.draw_cycle_times()
    
# extract counts from runs
df_list = []
for n, filt in run_numbers.items():

    # read
    run = ucnrun(n)
    
    # manual cycle filter
    if filt:
        cycflit = np.ones(run.cycle_param.ncycles)
        cycflit[filt] = 0    
        run.set_cycle_filter(cycflit)
    
    # get counts from cycles
    counts = run[:,2].get_counts('Li6')
    
    
    
    
    
    break

