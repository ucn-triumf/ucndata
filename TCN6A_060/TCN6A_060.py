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
outfile = 'TCN6A_060/summary.csv'    # save counts output
run_numbers = [2560,2561,2562,2563,2569]   # example: [1846, '1847+1848']
speeds = [90,80,60,40,23] # Hz

os.makedirs('TCN6A_060', exist_ok=True)

def PT013_to_T(P):
    return  1.23007765 + \
            3.37038378e-1*P + \
            7.37237263e-2*P*P + \
            1.87289546e-2*P**3 + \
            6.56933877e-3*P**4 + \
            1.09332641e-3*P**5

# fit function to counts vs lifetimes
def fitfn(t, p0, tau, off):
    return p0*np.exp(-t/tau) + off

def read_data():

    # setup runs
    runs = read(run_numbers)
    if isinstance(runs, ucnrun):
        runs = [runs]

    # default filters for bad cycles
    for run in runs:
        run.set_cycle_filter(run.gen_cycle_filter(period_production=0, period_count=2))


    # get counts and storage times 
    df_list = []
    for run, sp in zip(runs, speeds):

        counts = run[:,2].get_counts('Li6')
        counts, dcounts = np.array(counts).transpose()

        # get storage times
        storage = run.cycle_param.period_durations_s.loc[1, np.array(run[:].cycle)]

        # get pt013
        x = run[:,:2].tfile.UCN2EpPha5Pre.UCN2_ISO_PT013_RDPRESS.sum()
        n = run[:,:2].tfile.UCN2EpPha5Pre.UCN2_ISO_PT013_RDPRESS.size
        
        pt013 = x/n
        pt013_all = np.sum(x, axis=1)/np.sum(n, axis=1)
           
        df_list.append(pd.DataFrame({'counts':counts, 
                                     'dcounts':dcounts, 
                                     'storage':storage, 
                                     'Pumping Speed (Hz)':sp, 
                                     'PT013 Irradiation':pt013[:,0], 
                                     'PT013 Storage':pt013[:,1], 
                                     'PT013':pt013_all}))
        
    df = pd.concat(df_list)
    df.to_csv('TCN6A_060/counts_times.csv')

def analyze_data():

    df = pd.read_csv('TCN6A_060/counts_times.csv')
    pars = []
    dpars = []
    meta = []
       
    # fitting each speed
    plt.figure()
    for sp, g in df.groupby('Pumping Speed (Hz)'):  

        # skip fitting bad data
        if len(g) <= 1:
            continue
      
        par, cov = curve_fit(fitfn, g.storage, g.counts, sigma=g.dcounts, absolute_sigma=True,
                            p0=(max(g.counts), 1, min(g.counts)))
        std = np.diag(cov)**0.5
        
        pars.append(par)
        dpars.append(std)
        meta.append(g.dropna().mean())

        line = plt.errorbar(g.storage, g.counts, g.dcounts, fmt='o', fillstyle='none', label=f'{sp:d} Hz ($\\tau = {par[1]:.1f}\pm{std[1]:.1f}$)')
        fitx = np.linspace(min(g.storage), max(g.storage), 100)
        plt.plot(fitx, fitfn(fitx, *par), color=line[0].get_color())
        
    plt.xlabel('Storage Duration (s)')
    plt.ylabel('Raw UCN Counts')
    plt.legend(fontsize='x-small')
    plt.title('TCN6A-060', fontsize='x-small')
    plt.tight_layout()
    plt.savefig('TCN6A_060/pump_speed_lifetimes.pdf')
    
    # draw results vs speeds
    meta = pd.concat(meta, axis=1).transpose()
    pars = np.array(pars).transpose()
    dpars = np.array(dpars).transpose()
    
    # save fit results
    df = pd.DataFrame({'amp':pars[0], 'damp':std[0],
                       'tau':pars[1], 'dtau':std[1],
                       'offset':pars[2], 'doffset':std[2]})
    meta.drop(columns=['cycle'], inplace=True)
    
    meta['PT013 Temperature (K)'] = PT013_to_T(meta['PT013'])
    meta['PT013 Storage Temperature (K)'] = PT013_to_T(meta['PT013 Storage'])
    meta['PT013 Irradiation Temperature (K)'] = PT013_to_T(meta['PT013 Irradiation'])
    
    df = pd.concat((meta, df), axis='columns')
    
    df.to_csv('TCN6A_060/fit_results.csv')
    
        

    
def draw_data(xaxis):

    df = pd.read_csv('TCN6A_060/fit_results.csv')

    fig, ax = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=False, 
                           layout='constrained',
                           figsize=(5,8))
                           
    parnames = ['Amplitude', r'$\tau$ (s)', 'Offset']
    colnames = ['amp', 'tau', 'offset']
    for i in range(3):
        
        ax[i].errorbar(df[xaxis], df[colnames[i]], df[f'd{colnames[i]}'], fmt='o', fillstyle='none')
        ax[i].set_ylabel(parnames[i])
    ax[2].set_xlabel(xaxis)
    
        
    

## RUN ==========================

#read_data()
analyze_data()
draw_data('Pumping Speed (Hz)')
draw_data('PT013 Temperature (K)')
