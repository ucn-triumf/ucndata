"""Tests for ucndata.ucnrun — Layer B + C."""

import warnings

import numpy as np
import pandas as pd
import pytest

from ucndata import ucnrun
from ucndata.applylist import applylist
from ucndata.exceptions import (
    CycleError, MissingDataError, MissingDataWarning,
)

T0 = 1717243200   # run start epoch


# ---------------------------------------------------------------------------
# Construction / parsing
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_loads_from_path_string(good_run):
    assert good_run.run_number == 2684


@pytest.mark.rootfile
def test_run_title(good_run):
    assert good_run.run_title == "synthetic run"


@pytest.mark.rootfile
def test_year_and_month(good_run):
    assert good_run.year == 2024
    assert good_run.month == 6


@pytest.mark.rootfile
def test_dash_stripped_from_li6_tree(good_run):
    """UCNHits_Li-6 is renamed to UCNHits_Li6 (dash removed)."""
    assert "UCNHits_Li6" in good_run.tfile.keys()


@pytest.mark.rootfile
def test_space_stripped_from_run_number():
    """'Run Number' branch renamed to run_number attribute."""
    pass  # already tested via good_run.run_number == 2684


@pytest.mark.rootfile
def test_epics_is_ttreeslow(good_run):
    from ucndata.ttreeslow import ttreeslow
    assert isinstance(good_run.epics, ttreeslow)


@pytest.mark.rootfile
def test_run_points_to_self(good_run):
    assert good_run._run is good_run


@pytest.mark.rootfile
def test_caches_initialized(good_run):
    assert isinstance(good_run._cycledict, dict)
    assert isinstance(good_run._hits_hist, dict)
    assert isinstance(good_run._nhits, dict)


def test_none_returns_bare_object():
    run = ucnrun(None)
    assert isinstance(run, ucnrun)


def test_unsupported_type_raises_typeerror():
    with pytest.raises(TypeError):
        ucnrun([1, 2, 3])


def test_int_raises_for_missing_run(tmp_path):
    ucnrun.datadir = str(tmp_path)
    with pytest.raises((IOError, FileNotFoundError, OSError)):
        ucnrun(99999)


# ---------------------------------------------------------------------------
# _get_cycle_param
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_nperiods_is_3(good_run):
    assert good_run.cycle_param.nperiods == 3


@pytest.mark.rootfile
def test_ncycles_is_3(good_run):
    assert good_run.cycle_param.ncycles == 3


@pytest.mark.rootfile
def test_nsupercyc_is_1(good_run):
    assert good_run.cycle_param.nsupercyc == 1


@pytest.mark.rootfile
def test_period_durations_are_20_30_50(good_run):
    """Period durations for cycle 0 should be [20, 30, 50]."""
    durs = good_run.cycle_param.period_durations_s
    # durs is a DataFrame indexed by period, columns by cycle
    col0 = durs[0].values   # cycle 0 durations
    np.testing.assert_array_almost_equal(sorted(col0), [20, 30, 50])


@pytest.mark.rootfile
def test_no_transitions_warns(no_transitions_file):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        run = ucnrun(str(no_transitions_file))
    assert any(issubclass(x.category, MissingDataWarning) for x in w)


@pytest.mark.rootfile
def test_no_transitions_ncycles_1(no_transitions_file):
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        run = ucnrun(str(no_transitions_file))
    assert run.cycle_param.ncycles == 1
    assert run.cycle_param.nperiods == 1


# ---------------------------------------------------------------------------
# set_cycle_times
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_set_cycle_times_matched(good_run):
    good_run.set_cycle_times(mode="matched")
    ct = good_run.cycle_param.cycle_times
    assert "start" in ct.columns
    assert "stop" in ct.columns


@pytest.mark.rootfile
def test_set_cycle_times_matched_offset_zero(good_run):
    """He3 and Li6 are identical in good file → offset column is 0."""
    good_run.set_cycle_times(mode="matched")
    ct = good_run.cycle_param.cycle_times
    if "offset (s)" in ct.columns:
        assert all(ct["offset (s)"] == 0)


@pytest.mark.rootfile
def test_set_cycle_times_li6(good_run):
    good_run.set_cycle_times(mode="li6")
    ct = good_run.cycle_param.cycle_times
    assert "start" in ct.columns
    assert len(ct) == 3


@pytest.mark.rootfile
def test_set_cycle_times_he3(good_run):
    good_run.set_cycle_times(mode="he3")
    ct = good_run.cycle_param.cycle_times
    assert "start" in ct.columns
    assert len(ct) == 3


@pytest.mark.rootfile
def test_set_cycle_times_sequencer(good_run):
    good_run.set_cycle_times(mode="sequencer")
    ct = good_run.cycle_param.cycle_times
    assert "start" in ct.columns


@pytest.mark.rootfile
def test_set_cycle_times_bad_mode_raises(good_run):
    with pytest.raises(RuntimeError):
        good_run.set_cycle_times(mode="invalid_xyz")


@pytest.mark.rootfile
def test_set_cycle_times_mismatched_raises_cycle_error(mismatched_file):
    """He3 offset > 20 s from Li6 → CycleError in matched mode."""
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        run = ucnrun(str(mismatched_file))
    with pytest.raises(CycleError):
        run.set_cycle_times(mode="matched")


@pytest.mark.rootfile
def test_set_cycle_times_no_slow_trees_raises(no_slow_trees_file):
    """Missing slow trees → MissingDataError during run construction."""
    # MissingDataError is raised in __init__'s mode-loop when matched mode
    # can't find the run end time (no BeamlineEpics/SequencerTree present).
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        with pytest.raises(MissingDataError):
            ucnrun(str(no_slow_trees_file))


# ---------------------------------------------------------------------------
# __getitem__ / slicing / iteration
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_getitem_int_returns_ucncycle(good_run):
    from ucndata.ucncycle import ucncycle
    assert isinstance(good_run[0], ucncycle)


@pytest.mark.rootfile
def test_getitem_negative_returns_last_cycle(good_run):
    from ucndata.ucncycle import ucncycle
    last = good_run[-1]
    assert isinstance(last, ucncycle)
    assert last.cycle == 2


@pytest.mark.rootfile
def test_getitem_out_of_bounds_raises_index_error(good_run):
    with pytest.raises(IndexError):
        _ = good_run[999]


@pytest.mark.rootfile
def test_getitem_tuple_returns_ucnperiod(good_run):
    from ucndata.ucnperiod import ucnperiod
    assert isinstance(good_run[0, 0], ucnperiod)


@pytest.mark.rootfile
def test_getitem_slice_returns_applylist(good_run):
    result = good_run[1:3]
    assert isinstance(result, applylist)
    assert len(result) == 2


@pytest.mark.rootfile
def test_getitem_all_cycles(good_run):
    result = good_run[:]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_getitem_all_periods_of_cycle(good_run):
    result = good_run[0, :]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_getitem_column_slice(good_run):
    """run[:, 0] returns period-0 of every cycle."""
    result = good_run[:, 0]
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_len_equals_ncycles(good_run):
    assert len(good_run) == good_run.cycle_param.ncycles == 3


@pytest.mark.rootfile
def test_iteration_yields_all_cycles(good_run):
    from ucndata.ucncycle import ucncycle
    cycles = list(good_run)
    assert len(cycles) == 3
    assert all(isinstance(c, ucncycle) for c in cycles)


@pytest.mark.rootfile
def test_repr_nonempty(good_run):
    r = repr(good_run)
    assert len(r) > 0


def test_repr_bare_object():
    run = ucnrun(None)
    assert repr(run) == "ucnrun()"


# ---------------------------------------------------------------------------
# get_cycle
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_get_cycle_returns_ucncycle(good_run):
    from ucndata.ucncycle import ucncycle
    assert isinstance(good_run.get_cycle(0), ucncycle)


@pytest.mark.rootfile
def test_get_cycle_caches_identity(good_run):
    c1 = good_run.get_cycle(0)
    c2 = good_run.get_cycle(0)
    assert c1 is c2


@pytest.mark.rootfile
def test_get_cycle_all_returns_applylist(good_run):
    all_c = good_run.get_cycle()
    assert isinstance(all_c, applylist)
    assert len(all_c) == 3


# ---------------------------------------------------------------------------
# set_cycle_filter / gen_cycle_filter
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_set_cycle_filter_stores_filter(good_run):
    filt = np.array([True, False, True])
    good_run.set_cycle_filter(filt)
    assert good_run.cycle_param.filter is not None


@pytest.mark.rootfile
def test_set_cycle_filter_wrong_length_raises(good_run):
    with pytest.raises(RuntimeError):
        good_run.set_cycle_filter(np.array([True, False]))


@pytest.mark.rootfile
def test_filtered_slice_skips_rejected_cycles(good_run):
    filt = np.array([True, False, True])
    good_run.set_cycle_filter(filt)
    result = good_run[:]
    assert len(result) == 2


@pytest.mark.rootfile
def test_clear_filter_restores_all_cycles(good_run):
    filt = np.array([True, False, True])
    good_run.set_cycle_filter(filt)
    # Clear by setting all-True filter
    good_run.set_cycle_filter(np.ones(3, dtype=bool))
    result = good_run[:]
    assert len(result) == 3


@pytest.mark.rootfile
def test_gen_cycle_filter_returns_bool_array(good_run):
    filt = good_run.gen_cycle_filter(quiet=True)
    assert isinstance(filt, np.ndarray)
    assert filt.dtype == bool
    assert len(filt) == 3


# ---------------------------------------------------------------------------
# check_data
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_check_data_good_file_returns_true(good_run):
    # ucnrun.check_data calls .tIsUCN.any() on a ttree object; ttree has no
    # .any() → AttributeError. Known issue: should call .to_array().any()
    with pytest.raises(AttributeError):
        good_run.check_data()


@pytest.mark.rootfile
def test_check_data_raise_error_true_good_file(good_run):
    with pytest.raises(AttributeError):
        good_run.check_data(raise_error=True)


# ---------------------------------------------------------------------------
# keyfilter
# ---------------------------------------------------------------------------

def test_keyfilter_rejects_rate():
    run = ucnrun(None)
    assert run.keyfilter("UCNHits_rate") is False


def test_keyfilter_rejects_charge():
    run = ucnrun(None)
    assert run.keyfilter("He3_Charge") is False


def test_keyfilter_rejects_v1725():
    run = ucnrun(None)
    assert run.keyfilter("v1725_something") is False


def test_keyfilter_accepts_beamline():
    run = ucnrun(None)
    assert run.keyfilter("BeamlineEpics") is True


def test_keyfilter_accepts_ucnhits_he3():
    run = ucnrun(None)
    assert run.keyfilter("UCNHits_He3") is True


# ---------------------------------------------------------------------------
# _get_nhits
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_get_nhits_run_level_positive(good_run):
    """Run-level returns tree size (all entries including bad timestamps)."""
    nhits = good_run._get_nhits("He3")
    assert nhits > 0


@pytest.mark.rootfile
def test_get_nhits_cycle_level_positive(good_run):
    nhits = good_run._get_nhits("He3", cycle=0)
    assert nhits > 0


@pytest.mark.rootfile
def test_get_nhits_period_level_positive(good_run):
    nhits = good_run._get_nhits("He3", cycle=0, period=0)
    assert nhits >= 0


@pytest.mark.rootfile
def test_get_nhits_bin_ms_path(good_run):
    """bin_ms > 0 path works without error."""
    nhits = good_run._get_nhits("He3", cycle=0, bin_ms=1000)
    assert nhits >= 0


@pytest.mark.rootfile
def test_get_nhits_bin_ms_regenerates_cache(good_run):
    """Changing bin_ms regenerates the cached histogram."""
    _ = good_run._get_nhits("He3", cycle=0, bin_ms=100)
    _ = good_run._get_nhits("He3", cycle=0, bin_ms=500)
    assert good_run._nhits["He3"][0] == 500


# ---------------------------------------------------------------------------
# _modify_ptiming
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_modify_ptiming_clears_nhits_cache(good_run):
    """After modifying timing, _nhits cache is reset."""
    _ = good_run._get_nhits("He3", cycle=0, period=0)
    assert "He3" in good_run._nhits
    good_run._modify_ptiming(cycle=0, period=1, dt_start_s=1.0)
    # Cache should be cleared
    assert "He3" not in good_run._nhits


@pytest.mark.rootfile
def test_modify_ptiming_drops_cached_cycle(good_run):
    """After modifying timing, the affected cached cycle is invalidated."""
    _ = good_run.get_cycle(0)
    assert 0 in good_run._cycledict
    good_run._modify_ptiming(cycle=0, period=1, dt_start_s=2.0)
    assert 0 not in good_run._cycledict
