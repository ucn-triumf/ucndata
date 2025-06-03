# Draw rate vs current for beam_on times
# Derek Fujimoto
# Nov 2024

from ucndata import read, settings

# settings
run = 2393
TNIM2_thresh = 1

# get data
u = read(run)

# get periods when beam is on
beam = u.tfile.BeamlineEpics.B1U_TNIM2_10SECAVG
beam = beam[~beam.index.duplicated(keep='first')]

beam_on = beam[beam > TNIM2_thresh]
