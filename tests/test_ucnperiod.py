"""Tests for ucndata.ucnperiod — Layer B + C."""

import numpy as np
import pytest

from ucndata.ucnperiod import ucnperiod
from ucndata.tsubfile import tsubfile
from ucndata.ttreeslow import ttreeslow

T0 = 1717243200


# ---------------------------------------------------------------------------
# Core attributes
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_is_ucnperiod(good_run):
    assert isinstance(good_run[0, 0], ucnperiod)


@pytest.mark.rootfile
def test_period_index(good_run):
    assert good_run[0, 0].period == 0
    assert good_run[0, 1].period == 1
    assert good_run[0, 2].period == 2


@pytest.mark.rootfile
def test_period0_start_equals_cycle_start(good_run):
    """Period 0 of cycle 0 starts at T0."""
    p = good_run[0, 0]
    assert p.period_start == pytest.approx(T0, abs=1)


@pytest.mark.rootfile
def test_period1_start_equals_period0_end(good_run):
    """Period 1 of cycle 0 starts at T0 + 20."""
    p = good_run[0, 1]
    assert p.period_start == pytest.approx(T0 + 20, abs=1)


@pytest.mark.rootfile
def test_period2_start_equals_period1_end(good_run):
    """Period 2 of cycle 0 starts at T0 + 50."""
    p = good_run[0, 2]
    assert p.period_start == pytest.approx(T0 + 50, abs=1)


@pytest.mark.rootfile
def test_period0_stop(good_run):
    """Period 0 stops at T0 + 20."""
    p = good_run[0, 0]
    assert p.period_stop == pytest.approx(T0 + 20, abs=1)


@pytest.mark.rootfile
def test_period2_stop_equals_cycle_stop(good_run):
    """Period 2 stops at T0 + 100 (cycle end)."""
    p = good_run[0, 2]
    assert p.period_stop == pytest.approx(T0 + 100, abs=1)


@pytest.mark.rootfile
def test_period0_dur(good_run):
    assert good_run[0, 0].period_dur == pytest.approx(20, abs=1)


@pytest.mark.rootfile
def test_period1_dur(good_run):
    assert good_run[0, 1].period_dur == pytest.approx(30, abs=1)


@pytest.mark.rootfile
def test_period2_dur(good_run):
    assert good_run[0, 2].period_dur == pytest.approx(50, abs=1)


@pytest.mark.rootfile
def test_tfile_is_tsubfile(good_run):
    assert isinstance(good_run[0, 0].tfile, tsubfile)


@pytest.mark.rootfile
def test_epics_is_ttreeslow(good_run):
    assert isinstance(good_run[0, 0].epics, ttreeslow)


@pytest.mark.rootfile
def test_repr_nonempty(good_run):
    r = repr(good_run[0, 0])
    assert len(r) > 0


@pytest.mark.rootfile
def test_repr_contains_cycle_and_period(good_run):
    r = repr(good_run[0, 0])
    assert "cycle" in r.lower() or "0" in r


# ---------------------------------------------------------------------------
# get_nhits
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_get_nhits_period_nonnegative(good_run):
    """get_nhits returns a non-negative integer."""
    nhits = good_run[0, 0].get_nhits("He3")
    assert nhits >= 0


@pytest.mark.rootfile
def test_get_nhits_period1_nonnegative(good_run):
    nhits = good_run[0, 1].get_nhits("Li6")
    assert nhits >= 0


@pytest.mark.rootfile
def test_get_nhits_bin_ms_path(good_run):
    """bin_ms > 0 path works."""
    nhits = good_run[0, 0].get_nhits("He3", bin_ms=1000)
    assert nhits >= 0


@pytest.mark.rootfile
def test_get_nhits_matches_run_level(good_run):
    """period.get_nhits matches run._get_nhits(cycle, period)."""
    period = good_run[0, 1]
    nhits_period = period.get_nhits("He3")
    nhits_run    = good_run._get_nhits("He3", cycle=0, period=1)
    assert nhits_period == nhits_run


# ---------------------------------------------------------------------------
# modify_timing
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_modify_timing_does_not_raise(good_run):
    """modify_timing(dt_start_s, dt_stop_s) delegates without error."""
    period = good_run[0, 1]
    period.modify_timing(dt_start_s=1.0, dt_stop_s=0.0)


@pytest.mark.rootfile
def test_modify_timing_updates_period_start(good_run):
    """modify_timing(dt_start_s) updates period_start on the period object."""
    period = good_run[0, 1]
    before = period.period_start
    period.modify_timing(dt_start_s=5.0)
    # Compare the shift, not the absolute value — epoch timestamps are ~1.7e9 s,
    # so pytest.approx's default relative tolerance (1e-6) would mask a 5 s error.
    assert period.period_start - before == pytest.approx(5.0)


@pytest.mark.rootfile
def test_modify_timing_updates_period_stop(good_run):
    """modify_timing(dt_stop_s) updates period_stop on the period object."""
    period = good_run[0, 1]
    before = period.period_stop
    period.modify_timing(dt_stop_s=5.0)
    assert period.period_stop - before == pytest.approx(5.0)


@pytest.mark.rootfile
def test_modify_timing_updates_period_dur(good_run):
    """modify_timing updates period_dur to reflect the new start/stop."""
    period = good_run[0, 1]
    before = period.period_dur
    # Shift start by +3 and stop by +2 → duration shrinks by 1
    period.modify_timing(dt_start_s=3.0, dt_stop_s=2.0)
    assert period.period_dur - before == pytest.approx(-1.0)

# ---------------------------------------------------------------------------
# is_pileup (BUG-1 regression)
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_is_pileup_false_on_clean_data(good_run):
    """is_pileup returns False for clean synthetic data (no pileup)."""
    period = good_run[0, 0]
    # This exercises the BUG-1 fix: uses self.get_hits_array() not super().get_hits()
    result = period.is_pileup("Li6")
    assert result is False


@pytest.mark.rootfile
def test_is_pileup_returns_bool(good_run):
    result = good_run[1, 0].is_pileup("He3")
    assert isinstance(result, (bool, np.bool_))
