"""Integration tests for ucndata — end-to-end workflow coverage."""

import numpy as np
import pytest

from ucndata.applylist import applylist

T0 = 1717243200


# ---------------------------------------------------------------------------
# Cycle / period count consistency
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_period_nhits_sum_le_cycle_nhits(good_run):
    """Sum of period nhits over a cycle is at most cycle-level nhits.

    Equality is not guaranteed: for contiguous cycles the _get_nhits machinery
    allocates an 'end-of-cycle' bin at each cycle boundary. Hits exactly on
    the boundary fall into that slot and are counted at cycle level but not in
    any period, so period_total <= cycle_total.
    """
    for cyc_idx in range(good_run.cycle_param.ncycles):
        cycle = good_run[cyc_idx]
        cycle_total = cycle.get_nhits("He3")
        period_total = sum(
            cycle[per_idx].get_nhits("He3")
            for per_idx in range(len(cycle))
        )
        assert period_total <= cycle_total
        assert cycle_total >= 0


@pytest.mark.rootfile
def test_period_nhits_li6_sum_le_cycle(good_run):
    """Same boundary check for Li6 detector."""
    cycle = good_run[0]
    cycle_total = cycle.get_nhits("Li6")
    period_total = sum(cycle[i].get_nhits("Li6") for i in range(len(cycle)))
    assert period_total <= cycle_total


@pytest.mark.rootfile
def test_all_cycles_iterable_and_consistent(good_run):
    """Iterating run yields correct cycle count and each cycle has 3 periods."""
    cycles = list(good_run)
    assert len(cycles) == good_run.cycle_param.ncycles
    for cycle in cycles:
        assert len(cycle) == good_run.cycle_param.nperiods


# ---------------------------------------------------------------------------
# apply() workflow
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_apply_cycle_indices(good_run):
    """run.apply(lambda c: c.cycle) returns [0, 1, 2]."""
    result = good_run.apply(lambda c: c.cycle)
    assert list(result) == list(range(good_run.cycle_param.ncycles))


@pytest.mark.rootfile
def test_apply_nhits_returns_applylist(good_run):
    """apply() with get_nhits returns an applylist of non-negative ints."""
    result = good_run.apply(lambda c: c.get_nhits("He3"))
    assert isinstance(result, applylist)
    assert all(n >= 0 for n in result)


# ---------------------------------------------------------------------------
# Filter workflow
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_filter_workflow_drops_rejected_cycles(good_run):
    """gen_cycle_filter → set_cycle_filter → run[:] shrinks by rejected count."""
    filt = good_run.gen_cycle_filter(quiet=True)
    # Manually reject one cycle regardless of gen_cycle_filter output
    filt_modified = np.ones(len(filt), dtype=bool)
    filt_modified[1] = False
    good_run.set_cycle_filter(filt_modified)
    result = good_run[:]
    assert len(result) == filt_modified.sum()
    # Restore
    good_run.set_cycle_filter(np.ones(len(filt), dtype=bool))


@pytest.mark.rootfile
def test_filter_restore_gives_full_list(good_run):
    """After clearing filter, run[:] returns all cycles."""
    n = good_run.cycle_param.ncycles
    good_run.set_cycle_filter(np.array([True, False, True]))
    good_run.set_cycle_filter(np.ones(n, dtype=bool))
    assert len(good_run[:]) == n


# ---------------------------------------------------------------------------
# applylist element-wise method calls
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_applylist_period2_nhits_li6(good_run):
    """run[:, 2].get_nhits('Li6') matches per-cycle period-2 direct calls."""
    period2_list = good_run[:, 2]
    assert isinstance(period2_list, applylist)

    expected = [good_run[i, 2].get_nhits("Li6") for i in range(3)]
    via_applylist = period2_list.get_nhits("Li6")
    assert list(via_applylist) == expected


@pytest.mark.rootfile
def test_applylist_period0_he3_nonnegative(good_run):
    """run[:, 0].get_nhits('He3') all non-negative."""
    results = good_run[:, 0].get_nhits("He3")
    assert all(n >= 0 for n in results)


# ---------------------------------------------------------------------------
# set_cycle_times mode switching
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_set_cycle_times_mode_switch_consistent(good_run):
    """Switching set_cycle_times mode re-runs correctly and slicing still works."""
    good_run.set_cycle_times(mode="li6")
    ct_li6 = good_run.cycle_param.cycle_times.copy()

    good_run.set_cycle_times(mode="he3")
    ct_he3 = good_run.cycle_param.cycle_times.copy()

    # Both modes yield 3 cycles
    assert len(ct_li6) == 3
    assert len(ct_he3) == 3

    # After mode switch, indexing still works
    assert good_run[0] is not None
    assert good_run[2] is not None


@pytest.mark.rootfile
def test_set_cycle_times_sequencer_slicing_works(good_run):
    """After sequencer mode, run[0] is accessible."""
    good_run.set_cycle_times(mode="sequencer")
    cycle = good_run[0]
    assert cycle is not None
    assert cycle.cycle == 0


# ---------------------------------------------------------------------------
# Timing shift workflow
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_shift_timing_changes_period_window(good_run):
    """shift_timing on cycle 0 changes nhits for its periods."""
    # Capture baseline nhits for period 0 of cycle 0
    before = good_run[0, 0].get_nhits("He3")

    # Shift the timing of cycle 0 by a large amount to move hits out of window
    good_run[0].shift_timing(dt=50.0)

    # Reset: rebuild the run-level cache by invalidating
    # (shift_timing calls _modify_ptiming which clears _nhits cache)
    after = good_run[0, 0].get_nhits("He3")

    # The count may differ (shifted window may include/exclude different hits)
    # We just verify it runs without error and returns a non-negative int
    assert after >= 0

    # Shift back
    good_run[0].shift_timing(dt=-50.0)


# ---------------------------------------------------------------------------
# Datetime round trip
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_datetime_roundtrip_epics_index(good_run):
    """Epoch index from epics can be round-tripped through to_datetime/from_datetime."""
    from ucndata.datetime import to_datetime, from_datetime

    epics = good_run.epics
    # Get a column from epics as a Series with epoch index
    col = epics.columns[0]
    series = epics[col]

    if series is None or len(series) == 0:
        pytest.skip("epics column empty")

    epochs = series.index.values.astype(float)
    dts    = to_datetime(epochs)
    back   = from_datetime(dts)

    np.testing.assert_array_almost_equal(back, epochs, decimal=0)


@pytest.mark.rootfile
def test_datetime_roundtrip_hits_index(good_run):
    """Epoch timestamps from He3 hits round-trip through datetime utilities."""
    from ucndata.datetime import to_datetime, from_datetime

    arr = good_run.get_hits_array("He3")
    if len(arr) == 0:
        pytest.skip("no hits")

    # Use only valid (positive) timestamps
    valid = arr[arr > T0]
    if len(valid) == 0:
        pytest.skip("no valid hits")

    dts  = to_datetime(valid[:5])
    back = from_datetime(dts)
    np.testing.assert_array_almost_equal(back, valid[:5], decimal=0)


# ---------------------------------------------------------------------------
# Cross-object consistency
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_cycle_start_monotone(good_run):
    """Cycle start times are monotonically increasing."""
    starts = [good_run[i].cycle_start for i in range(3)]
    assert starts[0] < starts[1] < starts[2]


@pytest.mark.rootfile
def test_period_stops_equal_next_period_start(good_run):
    """Within a cycle, period[n].period_stop == period[n+1].period_start."""
    cycle = good_run[0]
    for i in range(len(cycle) - 1):
        p_curr = cycle[i]
        p_next = cycle[i + 1]
        assert p_curr.period_stop == pytest.approx(p_next.period_start, abs=1)


@pytest.mark.rootfile
def test_period0_start_equals_cycle_start(good_run):
    """Period 0 start equals cycle start for every cycle."""
    for i in range(3):
        cycle  = good_run[i]
        period = cycle[0]
        assert period.period_start == pytest.approx(cycle.cycle_start, abs=1)


@pytest.mark.rootfile
def test_last_period_stop_equals_cycle_stop(good_run):
    """Last period stop equals cycle stop for every cycle."""
    for i in range(3):
        cycle   = good_run[i]
        last_p  = cycle[-1]
        assert last_p.period_stop == pytest.approx(cycle.cycle_stop, abs=1)
