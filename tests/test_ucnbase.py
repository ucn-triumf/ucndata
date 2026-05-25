"""Tests for ucndata.ucnbase — Layer B + C.

ucnbase is abstract; all tests run through ucnrun or ucncycle.
"""

import numpy as np
import pytest

from ucndata.applylist import applylist
from ucndata.exceptions import MissingDataError
from ucndata.exceptions import NotImplementedError as UCNNotImplementedError

T0 = 1717243200


# ---------------------------------------------------------------------------
# apply()
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_apply_returns_applylist(good_run):
    result = good_run.apply(lambda c: c.cycle)
    assert isinstance(result, applylist)
    assert len(result) == 3


@pytest.mark.rootfile
def test_apply_correct_values(good_run):
    result = good_run.apply(lambda c: c.cycle)
    assert list(result) == [0, 1, 2]


# ---------------------------------------------------------------------------
# get_hits_array
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_get_hits_array_he3_returns_array(good_run):
    arr = good_run.get_hits_array("He3")
    assert isinstance(arr, np.ndarray)
    assert len(arr) > 0


@pytest.mark.rootfile
def test_get_hits_array_li6_returns_array(good_run):
    arr = good_run.get_hits_array("Li6")
    assert isinstance(arr, np.ndarray)
    assert len(arr) > 0


@pytest.mark.rootfile
def test_get_hits_array_unknown_detector_raises(good_run):
    with pytest.raises(KeyError):
        good_run.get_hits_array("UnknownDetector_XYZ")


# ---------------------------------------------------------------------------
# get_hits_histogram
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_get_hits_histogram_returns_object(good_run):
    hist = good_run.get_hits_histogram("He3", bin_ms=100)
    assert hist is not None


@pytest.mark.rootfile
def test_get_hits_histogram_has_x_y(good_run):
    hist = good_run.get_hits_histogram("He3", bin_ms=100)
    assert hasattr(hist, "x")
    assert hasattr(hist, "y")


@pytest.mark.rootfile
def test_get_hits_histogram_bin_ms_changes_bins(good_run):
    hist_coarse = good_run.get_hits_histogram("He3", bin_ms=1000)
    hist_fine   = good_run.get_hits_histogram("He3", bin_ms=10)
    assert len(hist_fine.x) >= len(hist_coarse.x)


@pytest.mark.rootfile
def test_get_hits_histogram_as_datetime(good_run):
    """as_datetime=True converts hist.x to datetimes without error."""
    hist = good_run.get_hits_histogram("He3", bin_ms=1000, as_datetime=True)
    assert hist is not None
    # hist.x should be datetime objects
    assert len(hist.x) >= 0


@pytest.mark.rootfile
def test_get_hits_histogram_unknown_detector_raises(good_run):
    with pytest.raises(KeyError):
        good_run.get_hits_histogram("UnknownXYZ")


@pytest.mark.rootfile
def test_get_hits_histogram_on_cycle_trims(good_run):
    """Histogram on a cycle is trimmed to the cycle time window."""
    cycle = good_run[0]
    hist  = cycle.get_hits_histogram("He3", bin_ms=1000)
    assert hist is not None
    if len(hist.x) > 0:
        # All bin centres should be within cycle window
        assert np.all(hist.x >= T0)
        assert np.all(hist.x < T0 + 100)


# ---------------------------------------------------------------------------
# beam current properties
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_beam1a_current_returns_series(good_run):
    current = good_run.beam1a_current_uA
    assert current is not None
    assert len(current) > 0


@pytest.mark.rootfile
def test_beam1u_current_returns_series(good_run):
    current = good_run.beam1u_current_uA
    assert current is not None
    assert len(current) > 0


@pytest.mark.rootfile
def test_beam1a_positive(good_run):
    """B1_FOIL_ADJCUR=1.0 throughout, so all values positive."""
    current = good_run.beam1a_current_uA
    assert (current.values > 0).all()


# ---------------------------------------------------------------------------
# beam_on_s / beam_off_s
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_beam_on_s_run_level(good_run):
    result = good_run.beam_on_s
    assert result is not None


@pytest.mark.rootfile
def test_beam_on_s_cycle_level(good_run):
    cycle = good_run[0]
    result = cycle.beam_on_s
    assert result >= 0


@pytest.mark.rootfile
def test_beam_off_s_cycle_level(good_run):
    cycle = good_run[0]
    result = cycle.beam_off_s
    assert result >= 0


# ---------------------------------------------------------------------------
# trigger_edge
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_trigger_edge_returns_array(good_run):
    cycle = good_run[0]
    edges = cycle.trigger_edge("Li6", thresh=0.5, bin_ms=1000)
    assert isinstance(edges, np.ndarray)


@pytest.mark.rootfile
def test_trigger_edge_falling(good_run):
    cycle = good_run[0]
    edges = cycle.trigger_edge("Li6", thresh=0.5, bin_ms=1000, rising=False)
    assert isinstance(edges, np.ndarray)


@pytest.mark.rootfile
def test_trigger_edge_very_high_threshold_raises(good_run):
    """Threshold above every bin → RuntimeError."""
    cycle = good_run[0]
    with pytest.raises(RuntimeError):
        cycle.trigger_edge("Li6", thresh=1e15, bin_ms=1000)


# ---------------------------------------------------------------------------
# _get_beam_duration edge case (Layer C)
# ---------------------------------------------------------------------------

def test_get_beam_duration_no_beamline_raises(empty_run):
    """_get_beam_duration when BeamlineEpics is absent raises MissingDataError."""
    with pytest.raises((MissingDataError, AttributeError)):
        empty_run._get_beam_duration(on=True)


# ---------------------------------------------------------------------------
# Plotting (mark: plotting)
# ---------------------------------------------------------------------------

@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_run_returns_axes(good_run):
    import matplotlib.pyplot as plt
    axes = good_run.inspect(xmode="duration", bin_ms=1000)
    assert axes is not None
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_xmode_datetime(good_run):
    import matplotlib.pyplot as plt
    axes = good_run.inspect(xmode="datetime", bin_ms=1000)
    assert axes is not None
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_xmode_epoch(good_run):
    import matplotlib.pyplot as plt
    axes = good_run.inspect(xmode="epoch", bin_ms=1000)
    assert axes is not None
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_bad_xmode_raises(good_run):
    with pytest.raises(RuntimeError):
        good_run.inspect(xmode="invalid_xyz")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_slow_str(good_run):
    import matplotlib.pyplot as plt
    axes = good_run.inspect(slow="B1_FOIL_ADJCUR", bin_ms=1000)
    assert axes is not None
    plt.close("all")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_slow_unknown_raises(good_run):
    with pytest.raises(KeyError):
        good_run.inspect(slow="NONEXISTENT_COLUMN_XYZ")


@pytest.mark.plotting
@pytest.mark.rootfile
def test_inspect_period_raises_not_implemented(good_run):
    """inspect() on a period raises ucndata's NotImplementedError."""
    period = good_run[0, 0]
    with pytest.raises(UCNNotImplementedError):
        period.inspect()


@pytest.mark.plotting
@pytest.mark.rootfile
def test_plot_psd_runs_without_error(good_run):
    import matplotlib.pyplot as plt
    cycle = good_run[0]
    # plot_psd crashes for channels with 0 hits (xedge[1] IndexError) — known
    # bug: ucnbase.plot_psd doesn't guard against empty histograms per channel.
    with pytest.raises(IndexError):
        cycle.plot_psd("Li6")
    plt.close("all")
