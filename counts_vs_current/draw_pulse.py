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
ax = plt.gca()
axin = ax.inset_axes((0.5,0.5,0.45,0.45))

for periodn in (0,2):
    start = cyc[periodn].period_start
    stop = cyc[periodn].period_stop

    df = hist.loc[start:stop]

    df.index -= t_valve  # time since start
    ax.plot(df.index, df.Count)
    axin.plot(df.index, df.Count)

# draw remaining
df = hist.loc[stop:]
df.index -= t_valve  # time since start
ax.plot(df.index, df.Count, color='k')
axin.plot(df.index, df.Count, color='k')

# plot elements
axin.set_xlim(-20, 150)
axin.set_ylim(20, 13000)
ax.set_ylim(0, 800)
ax.set_xlim(-10, 200)
axin.set_yscale('log')

axin.set_xticks([0,50,100,150])
ax.set_xticks([0,50,100,150,200])
axin.tick_params(axis='both', which='both', labelsize='xx-small')

axin.text(3.5, 10000, 'Irradiation\n(gate closed)', va='top', ha='left', color='C0', fontsize='xx-small')
ax.text(15, 480, 'Counting\n(gate open)', va='bottom', ha='left', color='C1', fontsize='small')
axin.text(15, 480, 'Counting\n(gate open)', va='bottom', ha='left', color='C1', fontsize='xx-small')
ax.text(127, 80, 'Background\n(gate closed)', va='bottom', ha='left', color='k', fontsize='small')
ax.set_ylabel("UCN Counts/10 ms")
ax.set_xlabel("Time Since Gate Open (s)")
axin.set_ylabel("UCN Counts/10 ms", fontsize='xx-small')
axin.set_xlabel("Time Since Gate Open (s)", fontsize='xx-small')

plt.tight_layout()
plt.savefig('run2573_cycle0.pdf')