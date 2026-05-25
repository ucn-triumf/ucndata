"""Tests for ucndata.chopper (crun, ccycle, cperiod, cframe) — Layer B."""

import numpy as np
import pytest

from ucndata.applylist import applylist
from ucndata.chopper import crun, ccycle, cperiod, cframe

T0 = 1717243200


# ---------------------------------------------------------------------------
# crun construction
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_crun_builds(chopper_run):
    assert isinstance(chopper_run, crun)


@pytest.mark.rootfile
def test_crun_has_frame_start_times(chopper_run):
    assert hasattr(chopper_run.cycle_param, "frame_start_times")
    assert len(chopper_run.cycle_param.frame_start_times) > 0


@pytest.mark.rootfile
def test_crun_nframes_positive(chopper_run):
    assert chopper_run.cycle_param.nframes > 0


@pytest.mark.rootfile
def test_crun_frames_within_run_duration(chopper_run):
    """All frame start times are before the run's last cycle stop."""
    stop_max = chopper_run.cycle_param.cycle_times.stop.max()
    times    = chopper_run.cycle_param.frame_start_times
    assert np.all(times < stop_max)


@pytest.mark.rootfile
def test_crun_chop_time_ch_default(chopper_run):
    assert chopper_run.chop_time_ch == 15


# ---------------------------------------------------------------------------
# crun __getitem__
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_crun_getitem_int_returns_ccycle(chopper_run):
    assert isinstance(chopper_run[0], ccycle)


@pytest.mark.rootfile
def test_crun_getitem_period_returns_cperiod(chopper_run):
    assert isinstance(chopper_run[0, 0], cperiod)


@pytest.mark.rootfile
def test_crun_getitem_frame_returns_cframe(chopper_run):
    assert isinstance(chopper_run[0, 0, 0], cframe)


@pytest.mark.rootfile
def test_crun_slice_returns_applylist(chopper_run):
    result = chopper_run[:]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_crun_period_slice(chopper_run):
    """crun[:, 0] returns period-0 from each cycle."""
    result = chopper_run[:, 0]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_crun_cycle_period_slice(chopper_run):
    """crun[0, :] returns all periods of cycle 0."""
    result = chopper_run[0, :]
    assert isinstance(result, applylist)


@pytest.mark.rootfile
def test_crun_out_of_bounds_raises(chopper_run):
    with pytest.raises(IndexError):
        _ = chopper_run[999]


@pytest.mark.rootfile
def test_crun_bad_index_type_raises(chopper_run):
    with pytest.raises((IndexError, TypeError)):
        _ = chopper_run["not_an_int"]


# ---------------------------------------------------------------------------
# crun get_cycle
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_crun_get_cycle_returns_ccycle(chopper_run):
    cycle = chopper_run.get_cycle(0)
    assert isinstance(cycle, ccycle)


# ---------------------------------------------------------------------------
# crun get_tof
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_crun_get_tof_returns_tuple(chopper_run):
    result = chopper_run.get_tof()
    assert result is not None
    assert isinstance(result, tuple)
    assert len(result) == 2


@pytest.mark.rootfile
def test_crun_get_tof_bins_and_hist_lengths_match(chopper_run):
    bins, hist = chopper_run.get_tof()
    assert len(bins) == len(hist) + 1  # standard numpy histogram convention


@pytest.mark.rootfile
def test_crun_get_tof_filter_excludes_bad_cycles(chopper_run):
    """get_tof excludes filtered cycles."""
    bins_all, hist_all = chopper_run.get_tof()
    # Reject one cycle
    chopper_run.set_cycle_filter(np.array([True, False, True]))
    bins_filt, hist_filt = chopper_run.get_tof()
    # Histogram sum should be <= unfiltered sum
    assert hist_filt.sum() <= hist_all.sum()
    chopper_run.set_cycle_filter(np.ones(3, dtype=bool))


# ---------------------------------------------------------------------------
# ccycle
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_ccycle_trimmed_frame_times(chopper_run):
    """ccycle.frame_start_times are within the cycle window."""
    cycle = chopper_run[0]
    times = cycle.cycle_param.frame_start_times
    assert np.all(times >= cycle.cycle_start)
    assert np.all(times < cycle.cycle_stop)


@pytest.mark.rootfile
def test_ccycle_getitem_returns_cperiod(chopper_run):
    assert isinstance(chopper_run[0][0], cperiod)


@pytest.mark.rootfile
def test_ccycle_getitem_out_of_bounds_raises(chopper_run):
    with pytest.raises(IndexError):
        _ = chopper_run[0][999]


@pytest.mark.rootfile
def test_ccycle_bad_index_type_raises(chopper_run):
    with pytest.raises((IndexError, TypeError)):
        _ = chopper_run[0]["bad"]


@pytest.mark.rootfile
def test_ccycle_get_period_returns_cperiod(chopper_run):
    p = chopper_run[0].get_period(0)
    assert isinstance(p, cperiod)


# ---------------------------------------------------------------------------
# cperiod
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_cperiod_has_nframes(chopper_run):
    period = chopper_run[0, 0]
    assert hasattr(period.cycle_param, "nframes")


@pytest.mark.rootfile
def test_cperiod_frame_times_within_period(chopper_run):
    period = chopper_run[0, 0]
    times  = period.cycle_param.frame_start_times
    if len(times) > 0:
        assert np.all(times >= period.period_start)
        assert np.all(times < period.period_stop)


@pytest.mark.rootfile
def test_cperiod_len_equals_nframes(chopper_run):
    period = chopper_run[0, 0]
    assert len(period) == period.cycle_param.nframes


@pytest.mark.rootfile
def test_cperiod_iteration_yields_cframes(chopper_run):
    period = chopper_run[0, 0]
    for frame in period:
        assert isinstance(frame, cframe)
        break  # only check the first one


@pytest.mark.rootfile
def test_cperiod_getitem_returns_cframe(chopper_run):
    frame = chopper_run[0, 0, 0]
    assert isinstance(frame, cframe)


@pytest.mark.rootfile
def test_cperiod_getitem_out_of_bounds_raises(chopper_run):
    with pytest.raises(IndexError):
        _ = chopper_run[0, 0][999]


@pytest.mark.rootfile
def test_cperiod_bad_index_type_raises(chopper_run):
    with pytest.raises((IndexError, TypeError)):
        _ = chopper_run[0, 0]["bad"]


# ---------------------------------------------------------------------------
# cframe
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_cframe_has_attributes(chopper_run):
    frame = chopper_run[0, 0, 0]
    assert hasattr(frame, "frame")
    assert hasattr(frame, "frame_start")
    assert hasattr(frame, "frame_stop")
    assert hasattr(frame, "frame_dur")


@pytest.mark.rootfile
def test_cframe_index(chopper_run):
    frame = chopper_run[0, 0, 0]
    assert frame.frame == 0


@pytest.mark.rootfile
def test_cframe_start_lt_stop(chopper_run):
    frame = chopper_run[0, 0, 0]
    assert frame.frame_start < frame.frame_stop


@pytest.mark.rootfile
def test_cframe_dur_positive(chopper_run):
    frame = chopper_run[0, 0, 0]
    assert frame.frame_dur > 0


@pytest.mark.rootfile
def test_cframe_get_nhits_nonnegative(chopper_run):
    frame = chopper_run[0, 0, 0]
    nhits = frame.get_nhits("Li6")
    assert nhits >= 0


@pytest.mark.rootfile
def test_cframe_repr_contains_frame(chopper_run):
    frame = chopper_run[0, 0, 0]
    r     = repr(frame)
    assert "frame" in r.lower()


# ---------------------------------------------------------------------------
# offset_frames
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_offset_frames_tiny_shift_does_not_raise(chopper_run):
    """A tiny positive shift is within run bounds."""
    chopper_run.offset_frames(dt=0.1)


@pytest.mark.rootfile
def test_offset_frames_negative_large_raises(chopper_run):
    """Shift that pushes frames to negative times raises ValueError."""
    # Frame times are absolute epoch timestamps ~T0+10. Shift by -(T0+100) makes
    # them negative (T0+10 - T0 - 100 = -90 < 0).
    with pytest.raises(ValueError):
        chopper_run.offset_frames(dt=-(T0 + 100))


@pytest.mark.rootfile
def test_offset_frames_past_end_raises(chopper_run):
    """Shift that pushes frames past run end raises ValueError."""
    with pytest.raises(ValueError):
        chopper_run.offset_frames(dt=1e9)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

@pytest.mark.plotting
@pytest.mark.rootfile
def test_crun_inspect_runs(chopper_run):
    import matplotlib.pyplot as plt
    # crun.inspect() calls super().inspect() internally but returns None itself
    chopper_run.inspect(bin_ms=1000)
    plt.close("all")
