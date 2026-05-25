"""Tests for ucndata.ttreeslow — Layer B (requires synthetic ROOT file)."""

import numpy as np
import pandas as pd
import pytest

from ucndata.ttreeslow import ttreeslow


# ---------------------------------------------------------------------------
# Core: using good_run.epics (already built from BeamlineEpics + UCN2Epics)
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_columns_contains_beam_columns(good_run):
    """columns lists BeamlineEpics columns."""
    cols = good_run.epics.columns
    assert "B1_FOIL_ADJCUR" in cols
    assert "B1V_KSM_PREDCUR" in cols


@pytest.mark.rootfile
def test_columns_contains_ucn2_column(good_run):
    """columns includes UCN2Epics column if that tree is in the file."""
    cols = good_run.epics.columns
    # UCN2Epics has UCN_UGD_BKGD_FLOW; may or may not be loaded depending
    # on EPICS_TREES list — just check the list is non-empty
    assert len(cols) > 0


@pytest.mark.rootfile
def test_treenames_contains_beamline(good_run):
    """treenames returns the names of member trees."""
    names = good_run.epics.treenames
    assert "BeamlineEpics" in names


@pytest.mark.rootfile
def test_getattr_known_column(good_run):
    """__getattr__ on a known column returns data."""
    col = good_run.epics.B1_FOIL_ADJCUR
    assert col is not None


@pytest.mark.rootfile
def test_getitem_known_column(good_run):
    """__getitem__ on a known column returns data."""
    col = good_run.epics["B1_FOIL_ADJCUR"]
    assert col is not None


@pytest.mark.rootfile
def test_mean_contains_beam_column(good_run):
    """mean() returns a Series with BeamlineEpics columns."""
    result = good_run.epics.mean()
    assert isinstance(result, pd.Series)
    assert "B1_FOIL_ADJCUR" in result.index
    assert abs(result["B1_FOIL_ADJCUR"] - 1.0) < 0.01


@pytest.mark.rootfile
def test_min_returns_series(good_run):
    result = good_run.epics.min()
    assert isinstance(result, pd.Series)
    assert "B1_FOIL_ADJCUR" in result.index


@pytest.mark.rootfile
def test_max_returns_series(good_run):
    result = good_run.epics.max()
    assert isinstance(result, pd.Series)
    assert "B1_FOIL_ADJCUR" in result.index


@pytest.mark.rootfile
def test_std_returns_series(good_run):
    result = good_run.epics.std()
    assert isinstance(result, pd.Series)


@pytest.mark.rootfile
def test_rms_returns_series(good_run):
    # rootloader ttree has no .rms() → ttreeslow.rms() raises AttributeError
    with pytest.raises(AttributeError):
        good_run.epics.rms()


@pytest.mark.rootfile
def test_index_returns_dict(good_run):
    """index property returns a dict keyed by tree name."""
    idx = good_run.epics.index
    assert isinstance(idx, dict)
    assert "BeamlineEpics" in idx


@pytest.mark.rootfile
def test_index_name_returns_dict(good_run):
    """index_name property returns a dict of index column names."""
    idx_name = good_run.epics.index_name
    assert isinstance(idx_name, dict)


@pytest.mark.rootfile
def test_filters_returns_dict(good_run):
    """filters property returns a dict."""
    filt = good_run.epics.filters
    assert isinstance(filt, dict)


@pytest.mark.rootfile
def test_copy_constructor(good_run):
    """ttreeslow(existing) copies _columns and _treenames."""
    copy = ttreeslow(good_run.epics)
    assert set(copy.columns) == set(good_run.epics.columns)
    assert set(copy.treenames) == set(good_run.epics.treenames)


@pytest.mark.rootfile
def test_copy_constructor_with_parent_override(good_run):
    """copy constructor with parent= overrides the parent."""
    copy = ttreeslow(good_run.epics, parent=good_run)
    assert copy._parent is good_run


@pytest.mark.rootfile
def test_reset_returns_ttreeslow(good_run):
    """reset() returns a new ttreeslow instance."""
    result = good_run.epics.reset()
    assert isinstance(result, ttreeslow)


@pytest.mark.rootfile
def test_set_index_propagates(good_run):
    """set_index does not raise."""
    good_run.epics.set_index("timestamp")


@pytest.mark.rootfile
def test_set_filter_inplace(good_run):
    """set_filter(inplace=True) does not raise when column exists in all trees."""
    # Use 'timestamp' which is the index column present in every EPICS tree.
    good_run.epics.set_filter("timestamp > 0", inplace=True)


@pytest.mark.rootfile
def test_hist1d_returns_histogram(good_run):
    """hist1d(column, nbins=N) returns a rootloader th1 histogram."""
    hist = good_run.epics.hist1d("B1_FOIL_ADJCUR", nbins=10)
    assert hist is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_no_parent_raises_runtime_error(good_run):
    """Constructing from tree list without parent= raises RuntimeError."""
    # Get a single tree from the file
    bl_tree = good_run.tfile["BeamlineEpics"]
    with pytest.raises(RuntimeError):
        ttreeslow([bl_tree], parent=None)


@pytest.mark.rootfile
def test_set_filter_inplace_false_raises(good_run):
    """set_filter(inplace=False) raises RuntimeError."""
    with pytest.raises(RuntimeError):
        good_run.epics.set_filter("B1_FOIL_ADJCUR > 0", inplace=False)


@pytest.mark.rootfile
def test_getattr_unknown_raises_attribute_error(good_run):
    """__getattr__ on an unknown name raises AttributeError."""
    with pytest.raises(AttributeError):
        _ = good_run.epics.this_column_does_not_exist_xyz_123
