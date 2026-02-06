# The Chopper Module

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)

For chopper experiments, we expect that a timing signal is sent to the same digitizer receiving the signal from the detectors. In Jan 2026 this signal was sent into channel 15. This signal determines the start time of a frame: a short window, typically on the order of 1 s, within a period related to a chopper blocking the UCN guide or not. 

The module does the following: 

* Add a new cframe object, similar to a period object
  * This object has the `frame_start`, `frame_stop`, and `frame_dur` properties
* Redefine new crun, ccycle, and cperiod classes for use with the chopper. These are extended with additional indexing to include the frames. 
* The `cycle_param` dictionary is augmented with the `nframes` and `frame_start_times` parameters. 
  * `nframes` is the number of frames in that run/cycle/period
  * `frame_start_times` is a numpy array of all the frame start times in that run/cycle/period
* Modify the `inspect` function to include frames in the drawn output: draws alternating grey bands to indicate frames
* Add a `offset_frames` function which shifts the start times of all frames

Other than the above the functionality of the base `ucndata` package is preserved.

## Examples and How-To

Basic load a run:
```python
# import run class from the module
from ucndata.chopper import crun

# load run - same functionlity as ucnrun
run = crun(3310)
```

Indexing and broadcasting:
```python
# select cycle 0, period 1, all frames
run[0,1,:]

# broadcasting works as before: get number of hits in each frame for the above selection of frames
run[0,1,:].get_nhits('Li6')

# get all frames for all cycles, period 0
run[:,0,:]

# get frames 10 - 49 for all cycles, period 0
run[:,0,10:50]
```

[**Back to Index**](index.md)\
[**Next page: Tips and FAQ**](tips.md)