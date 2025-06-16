# Run analysis for TCN6A-020: source saturation measurement with lifetime measurement at 1 uA
# Derek Fujimoto
# June 2025
from ucndata import read, ucnrun
import os
import tools

# settings
ucnrun.cycle_times_mode = 'li6'   # li6|he3|matched|sequencer|beamon
outfile = 'TCN6A_020/summary.csv'   # save counts output
counts_col = 'counts_bkgd' # counts_raw|counts_bkgd|counts_bdgd_norm (1/uA)
run_numbers = [2543,2546,2547,2548] # 2544,2545,  # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# check existing runs to skip re-analysis of counts
#try:
#    old = pd.read_csv(outfile, comment='#')
#except FileNotFoundError:
#    pass
#else:
#   run_numbers = [r for r in run_numbers if r not in old['run']]

# setup runs
runs = read(run_numbers)
if isinstance(runs, ucnrun):
    runs = [runs]

# setup analyzer
ana = tools.Analyzer('lifetime', outfile)

# counts and hits
for run in runs:
    ana.get_counts(run)
    ana.draw_hits(run)

# get results from counts
df = pd.read_csv(outfile, comment='#')
df.sort_values('production duration (s)', inplace=True)


## LIFETIME MEASUREMENTS =====================================================
 
# fit function to counts vs lifetimes
@tools.prettyprint(r'$p_0 \exp(-t/\tau)$', '$p_0$', r'$\tau$')
def fitfn_life(t, p0, tau):
    return p0*np.exp(-t/tau)
    
# do the fits for each production time
plt.figure()
for t_prod, g in df.groupby('production duration (s)'):
    tools.fit(fitfn_life,
            df['storage duration (s)'],
            df[counts_col],
            df[f'd{counts_col}'],
            p0 = (1,1),
            err_kwargs = {
                'marker':'o',
                'ls':'none',
                'fillstyle':'none',
                'label':'Irradiation {int(t_prod):d} s'},
            xlabel = 'Storage Duration (s)',
            ylabel = 'UCN Raw Counts',
            index = t_prod,
            index_name = 'Production Time (s)',
            outfile = f'TCN6A_020/life_{counts_col.split(" ")[0]}.csv')

## SATURATION MEASUREMENTS ===================================================

# fit function to counts vs production times
@tools.prettyprint(r'$p_0 (1-\exp(-t/\tau))$', '$p_0$', r'$\tau$')
def fitfn_sat(t, p0, tau):
    return p0*(1-np.exp(-t/tau))
    
# do the fits for each storage time
plt.figure()
for t_store, g in df.groupby('storage duration (s)'):
    tools.fit(fitfn_sat,
        df['production duration (s)'],
        df[counts_col],
        df[f'd{counts_col}'],
        p0 = (1,1),
        err_kwargs = {
            'marker':'o',
            'ls':'none',
            'fillstyle':'none',
            'label':'Storage {int(t_store):d} s'},
        xlabel = 'Production Duration (s)',
        ylabel = 'UCN Counts',
        index = t_store,
        index_name = 'Storage Time (s)',
        outfile = f'TCN6A_020/satur_{counts_col.split(" ")[0]}.csv')
        
## SUMMARY PLOTS =============================================================

# get data
df_sat = pd.read_csv(f'TCN6A_020/satur_{counts_col.split(" ")[0]}.csv', comment='#')
df_life = pd.read_csv(f'TCN6A_020/life_{counts_col.split(" ")[0]}.csv', comment='#')

plt.figure()

plt.errorbar(df_sat['Sqtorage Time (s)'], df_sat['tau'], df_sat['dtau'], 
             marker='o',
             ls='none',
             fillstyle='none',
             label='Saturation Time vs Storage Time')
             
plt.errorbar(df_life['Irradiation Time (s)'], df_life['tau'], df_life['dtau'], 
             marker='o',
             ls='none',
             fillstyle='none',
             label='Lifetime vs Irradiation Time')
             
plt.xlabel('Irradiation Time [Storage Time] (s)', fontsize='x-small')
plt.ylabel('Lifetime [Saturation Time] (s)', fontsize='x-small')
plt.legend(fontsize='x-small')
plt.tight_layout()



        
        
