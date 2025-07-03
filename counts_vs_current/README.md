# Draw counts vs current from Li6 detectors

Simulation data can be found [here](https://docs.google.com/spreadsheets/d/1cguGTJseRPwugzmHmRnlhKoFZU4LIulD1Jv2bFTXel0/edit?gid=15994532#gid=15994532).

* Used data from Li6 runs with the following timing scheme:
    * 100 s irradiation
    * 10 s storage
    * 120 s counting
* Background subtraction used nearest background measurement, integrating counts over the same timeframe
* Errors are clearly underestimated from Poissonian statistics only


## Results

* [Runscript](counts_vs_current.py)
* Data saved here: [no foil](nofoil_0s.csv), and [with foil](withfoil.csv)
* [Main figure of counts vs current](6A_counts.pdf)
* [Figures of UCN counts with backgrounds](figures)



# Draw single pulse

* [Runscript](draw_pulse.py)
* Specifically one with zero storage time (Run 2573, cycle 0)
* Output [figure here](run2573_cycle0.pdf)

# Draw counts vs current during irradiation

Using the same runs as in the counts vs current, now get the counts from the irradiation cycles to look for the effects of detector deadtime.

* [Runscript](irrcounts_vs_current.py)
* [Data saved here](irradiation_nofoil.csv)
* [Figure](6A_counts_irradiation.pdf)

Clearly the trend is no longer linear, but the data rate is nowhere near the 2~MHz promised in the Li6 detector paper. Variation may be due to the incoming count rate interacting with the buffer fill and clear times.