# Run analysis for TCN6A-010: first tests at 1 uA
# Derek Fujimoto
# June 2025
from ucndata import read, ucnrun
import os
import tools

# settings
ucnrun.cycle_times_mode = 'li6'   # what frontend to use for determining cycle times [li6|he3|matched|sequencer|beamon]
# ucnrun.keyfilter = lambda self, x: True
channel_cuts = False
       
outfile = 'TCN6A_010/summary.csv'   # save counts output
#run_numbers = [2489,2488]   # example: [1846, '1847+1848']

# setup save dir
os.makedirs(os.path.dirname(outfile), exist_ok=True)

# setup runs
#runs = read(run_numbers)
#if isinstance(runs, ucnrun):
#    runs = [runs]

# test analysis 
#run = runs[0]

#run = read(['old_files/ucn_run_00001877.root', 2489])
run = read(2529)

def get_counts(run):

    # recalculate PSD
    df = run.tfile.UCNHits_Li6
    df = df.loc[df.tChargeL>0]
    psd = (df.tChargeL-df.tChargeS)/df.tChargeL
    print(len(psd), len(run.tfile.UCNHits_Li6))
    df.loc[:, 'tPSD'] = psd.astype(float)
    run.tfile.UCNHits_Li6 = df
    
    
    counts = []

    for cyc in run:

        i = 2 - (cyc.cycle % 2)
        
        # get counts from new cuts
        try:
            df = cyc[i].get_hits('Li6')
        except KeyError:
            continue

        # channel-wise cuts    
        if channel_cuts:
            df_list = []    
            for ch in range(9):
                
                df_ch = df.loc[df.tChannel == ch]
                
                # cuts
                if ch == 0:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.3)   
                elif ch == 1:
                    idx =   (df_ch.tChargeL > 300) & \
                            (df_ch.tPSD > 0.3)
                elif ch == 2:
                    idx =   (df_ch.tChargeL > 400) & \
                            (df_ch.tPSD > 0.3)
                elif ch == 3:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.2)
                elif ch == 4:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.2)
                elif ch == 5:
                    idx =   (df_ch.tChargeL > 400) & \
                            (df_ch.tPSD > 0.2)
                elif ch == 6:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.2)
                elif ch == 7:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.2)
                elif ch == 8:
                    idx =   (df_ch.tChargeL > 350) & \
                            (df_ch.tPSD > 0.2)
                            
                df_ch = df_ch.loc[idx]
                df_list.append(df_ch)
            
                print(f'Cycle {cyc.cycle} CH: {ch} N = {len(df_ch)}')
                
            df = pd.concat(df_list)
        
        # all-cycle cuts
        else:
            idx = (df.tChargeL > 2000) & (df.tPSD > 0.3)
            df = df.loc[idx]
        
        print(f'Cycle {cyc.cycle} total: {len(df)}')
        counts.append(len(df))
        if len(df) == 0: continue

        # histogram
        bins = np.arange(int(np.floor(min(df.index))), int(np.ceil(max(df.index)))+2)
        hist, _ = np.histogram(df.index, bins=bins)
        plt.plot(bins[:-1], hist)

    print(f'background-subtracted counts: {np.diff(counts)}')
    cnts = np.abs(np.diff(counts))
    print(f'Total average: {np.mean(cnts)} +/- {np.std(cnts)}')
    
    
    
    
    
        




