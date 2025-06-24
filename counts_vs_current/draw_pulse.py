# draw a single counting pulse for the paper
# Derek Fujimoto
# June 2025

from ucndata import ucnrun
import matplotlib.pyplot as plt
import numpy as np

run = ucnrun(2573)
cyc = run[0]

# get histogram
hist = cyc.get_hits_histogram('Li6', bin_ms=10)
hist = hist.to_dataframe()
hist.set_index('tUnixTimePrecise', inplace=True)

hist = hist.loc[hist.Count>10]

# time of valve open
t_valve = cyc[2].period_start

# draw
plt.figure()
for periodn in (0,2):
    start = cyc[periodn].period_start
    stop = cyc[periodn].period_stop

    df = hist.loc[start:stop]

    df.index -= t_valve  # time since start
    plt.semilogy(df.index, df.Count)

# draw remaining
df = hist.loc[stop:]
df.index -= t_valve  # time since start
plt.semilogy(df.index, df.Count, color='k')

# plot elements
plt.xlim(-20, 200)
plt.ylim(20, 13000)
plt.text(3.5, 10000, 'Irradiation\n(gate closed)', va='top', ha='left', color='C0', fontsize='small')
plt.text(15, 480, 'Counting\n(gate open)', va='bottom', ha='left', color='C1', fontsize='small')
plt.text(127, 80, 'Background\n(gate closed)', va='bottom', ha='left', color='k', fontsize='small')
plt.ylabel("UCN Counts/10 ms")
plt.xlabel("Time Since Gate Open (s)")
plt.tight_layout()
plt.savefig('run2573_cycle0.pdf')