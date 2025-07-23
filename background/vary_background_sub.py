# Vary background subtraction to see if there is any large effect on taking background data distant in time from the data run
# use the counts vs current data
# Derek Fujimoto
# Jul 2025

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# settings
filename = '../counts_vs_current/nofoil_0s.csv'

# get data
df = pd.read_csv(filename, comment='#')

df['current_rounded'] = df.current.round().astype(int)

# draw with best background subtraction
def background_sub(df, label):

    x = df.current
    y = df.counts.copy()
    by = df.background.copy()
    dy = y**0.5
    dby = by**0.5

    # rescale the background
    by_last = df.bkgd_last_20s
    y_last = df.cycle_last_20s

    dby_last = by_last**0.5
    dy_last = y_last**0.5

    factor = y_last / by_last
    dfactor = factor * ((dby_last/by_last)**2 + (dy_last/y_last)**2)**0.5

    dby = factor*by * ((dby/by)**2 + (dfactor/factor)**2)**0.5
    by *= factor

    # background subtraction
    dy = (dy**2+dby**2)**0.5
    y -= by

    # linear fit
    fn = lambda x, a: a*x
    par, _ = curve_fit(fn, x, y, sigma=dy, absolute_sigma=True)
    fitx = np.linspace(0,40,10)

    # draw residuals
    # plt.errorbar(df.cycle_bkgd-df.cycle_count, y-fn(x,*par), dy, fmt='o', label=label, fillstyle='none')
    # plt.errorbar(x, y-fn(x,*par), dy, fmt='o', label=label, fillstyle='none')

    line = plt.errorbar(x, y, dy, fmt='o', label=label, fillstyle='none')
    plt.plot(fitx, fn(fitx, *par), color=line[0].get_color())


# set the backgrounds
df2 = df.copy()
for _, g in df2.groupby('current_rounded'):
    df2.loc[g.index, 'background'] = g.background.iloc[-1]
    df2.loc[g.index, 'bkgd_last_20s'] = g.bkgd_last_20s.iloc[-1]
    df2.loc[g.index, 'cycle_bkgd'] = g.cycle_bkgd.iloc[-1]

# draw
background_sub(df, 'Best')
background_sub(df2, 'Last')

# plot elements
plt.ylabel('UCN Counts')
# plt.ylabel('UCN Counts - Linear Fit')
# plt.xlabel('Bkgd Cycle Number - Count Cycle Number')
plt.xlabel('Current (uA)')
plt.legend(fontsize='x-small')
plt.tight_layout()