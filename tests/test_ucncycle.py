"""Tests for ucndata.ucncycle — Layer B + C."""

import numpy as np
import pytest

from ucndata.applylist import applylist
from ucndata.ucncycle import ucncycle
from ucndata.ucnperiod import ucnperiod
from ucndata.tsubfile import tsubfile
from ucndata.ttreeslow import ttreeslow

T0 = 1717243200


# ---------------------------------------------------------------------------
# Core attributes
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_is_ucncycle(good_run):
    assert isinstance(good_run[0], ucncycle)


@pytest.mark.rootfile
def test_cycle_index_attribute(good_run):
    assert good_run[0].cycle == 0
    assert good_run[1].cycle == 1
    assert good_run[2].cycle == 2


@pytest.mark.rootfile
def test_supercycle_is_zero(good_run):
    assert good_run[0].supercycle == 0


@pytest.mark.rootfile
def test_cycle_start(good_run):
    assert good_run[0].cycle_start == T0
    assert good_run[1].cycle_start == T0 + 100
    assert good_run[2].cycle_start == T0 + 200


@pytest.mark.rootfile
def test_cycle_stop(good_run):
    assert good_run[0].cycle_stop == pytest.approx(T0 + 100, abs=1)
    assert good_run[1].cycle_stop == pytest.approx(T0 + 200, abs=1)


@pytest.mark.rootfile
def test_cycle_dur(good_run):
    assert good_run[0].cycle_dur == pytest.approx(100, abs=1)


@pytest.mark.rootfile
def test_period_durations_trimmed_to_cycle(good_run):
    """cycle_param.period_durations_s for a cycle has 3 elements."""
    cycle = good_run[0]
    durs  = cycle.cycle_param.period_durations_s
    assert len(durs) == 3


@pytest.mark.rootfile
def test_tfile_is_tsubfile(good_run):
    assert isinstance(good_run[0].tfile, tsubfile)


@pytest.mark.rootfile
def test_epics_is_ttreeslow(good_run):
    assert isinstance(good_run[0].epics, ttreeslow)


@pytest.mark.rootfile
def test_len_equals_nperiods(good_run):
    assert len(good_run[0]) == 3


@pytest.mark.rootfile
def test_iteration_yields_ucnperiods(good_run):
    cycle = good_run[0]
    for per in cycle:
        assert isinstance(per, ucnperiod)


@pytest.mark.rootfile
def test_getitem_int_returns_ucnperiod(good_run):
    assert isinstance(good_run[0][0], ucnperiod)


@pytest.mark.rootfile
def test_getitem_negative_wraps(good_run):
    cycle = good_run[0]
    last  = cycle[-1]
    assert last.period == 2


@pytest.mark.rootfile
def test_getitem_slice_returns_applylist(good_run):
    result = good_run[0][:]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_getitem_out_of_bounds_raises(good_run):
    with pytest.raises(IndexError):
        _ = good_run[0][999]


@pytest.mark.rootfile
def test_get_period_caches(good_run):
    cycle = good_run[0]
    p1    = cycle.get_period(0)
    p2    = cycle.get_period(0)
    assert p1 is p2


@pytest.mark.rootfile
def test_get_period_all_returns_applylist(good_run):
    all_p = good_run[0].get_period()
    assert isinstance(all_p, applylist)
    assert len(all_p) == 3


@pytest.mark.rootfile
def test_repr_nonempty(good_run):
    r = repr(good_run[0])
    assert len(r) > 0


@pytest.mark.rootfile
def test_get_nhits_delegates_to_run(good_run):
    cycle       = good_run[0]
    nhits_cycle = cycle.get_nhits("He3")
    nhits_run   = good_run._get_nhits("He3", cycle=0)
    assert nhits_cycle == nhits_run


# ---------------------------------------------------------------------------
# check_data
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_check_data_good_cycle_true(good_run):
    assert good_run[0].check_data() is True


@pytest.mark.rootfile
def test_check_data_quiet_does_not_raise(good_run):
    result = good_run[0].check_data(quiet=True)
    assert result in (True, False)


@pytest.mark.rootfile
def test_check_data_raise_error_good_cycle(good_run):
    assert good_run[0].check_data(raise_error=True) is True


# ---------------------------------------------------------------------------
# shift_timing
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_shift_timing_does_not_raise(good_run):
    cycle = good_run[0]
    # Just check it doesn't raise
    cycle.shift_timing(dt=2.0)


# ---------------------------------------------------------------------------
# draw_cycle_times (plotting)
# ---------------------------------------------------------------------------

@pytest.mark.plotting
@pytest.mark.rootfile
def test_draw_cycle_times_returns_periods(good_run):
    import matplotlib.pyplot as plt
    cycle  = good_run[0]
    result = cycle.draw_cycle_times()
    assert result is not None
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_draw_cycle_times_xmode_epoch(good_run):
    import matplotlib.pyplot as plt
    good_run[0].draw_cycle_times(xmode="epoch")
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_draw_cycle_times_xmode_duration_run(good_run):
    import matplotlib.pyplot as plt
    good_run[0].draw_cycle_times(xmode="duration_run")
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_draw_cycle_times_xmode_duration_cycle(good_run):
    import matplotlib.pyplot as plt
    good_run[0].draw_cycle_times(xmode="duration_cycle")
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_draw_cycle_times_bad_xmode_raises(good_run):
    with pytest.raises(RuntimeError):
        good_run[0].draw_cycle_times(xmode="invalid_xyz")
