# Get storage lifetime - simplified example
# Derek Fujimoto
# Nov 2024
from ucndata import settings, read
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# settings
settings.datadir = 'test_files'
production_period = 0
storageperiod =     1
countperiod =       2
backgroundperiod =  1
detector = 'Li6'
run_numbers = [1846, 1873]

# get all runs
runs = read(run_numbers)
for r in runs:

    # filter bad cycles
    r.set_cycle_filter(r.gen_cycle_filter(period_production=production_period,
                                          period_count=countperiod))

    # get beam current and means
    beam_currents = r[:, production_period].beam_current_uA
    dbeam_currents = beam_currents.std()
    beam_currents = beam_currents.mean()

    # get storage durations and associated counts
    storage_duration = r[:, storageperiod].cycle_param.period_durations_s
    counts_bkgd = r[:, backgroundperiod].get_counts(detector)
    counts_bkgd = counts_bkgd.transpose()

    counts = r[:, countperiod].get_counts(detector,
                                        bkgd=counts_bkgd[0], dbkgd=counts_bkgd[1],
                                        norm=beam_currents, dnorm=dbeam_currents)

    # sort
    idx = np.argsort(storage_duration)
    storage_duration = storage_duration[idx]
    counts = counts[idx]

    # fit
    fn = lambda x, p0, tau: p0*np.exp(-x/tau)
    par, cov = curve_fit(fn, storage_duration, counts[:,0], sigma=counts[:,1], absolute_sigma=True)
    std = np.diag(cov)**0.5

    # draw
    plt.figure()
    plt.errorbar(storage_duration, counts[:, 0], counts[:, 1], fmt='.')
    plt.semilogy(storage_duration, fn(storage_duration, *par))
    plt.xlabel('Storage Duration (s)')
    plt.ylabel('Normalized Number of Counts (uA$^{-1}$)')
    plt.title(f'Run {r.run_number}')
    plt.tight_layout()

    print(f'lifetime: {par[1]:.5g} +\- {std[1]:.5g} (s)')
    
    
    
