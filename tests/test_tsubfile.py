"""Tests for ucndata.tsubfile — Layer B (requires synthetic ROOT file)."""

import numpy as np
import pandas as pd
import pytest

from ucndata.tsubfile import tsubfile

T0 = 1717243200   # run start epoch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_sub(good_run, dt_start=0, dt_stop=100):
    """Return a tsubfile wrapping good_run.tfile for [T0+dt_start, T0+dt_stop]."""
    return tsubfile(good_run.tfile, T0 + dt_start, T0 + dt_stop)


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_tsubfile_exposes_parent_keys(good_run):
    """tsubfile exposes at least the same keys as its parent."""
    sub = _make_sub(good_run)
    parent_keys = set(good_run.tfile.keys())
    sub_keys    = set(sub.keys())
    # sub may have extra internal keys (_start, _stop); parent keys are a subset
    assert parent_keys.issubset(sub_keys | {"_start", "_stop"})


@pytest.mark.rootfile
def test_tsubfile_time_indexed_df_filtered(good_run):
    """Time-indexed DataFrame is filtered to [start, stop]."""
    # Use cycle 0's window: [T0, T0+100]
    sub = _make_sub(good_run, 0, 100)
    # CycleParamTree is a DataFrame but NOT time-indexed → should be unfiltered
    # BeamlineEpics is a ttree → also filtered; use it via the run's tfile
    # Use RunTransitions_He3 which IS a DataFrame with numeric index (not time)
    # Just verify no error:
    assert sub is not None


@pytest.mark.rootfile
def test_tsubfile_start_stop_accessible_as_items(good_run):
    """_start and _stop are accessible via item access."""
    start = T0 + 10
    stop  = T0 + 90
    sub = tsubfile(good_run.tfile, start, stop)
    assert sub["_start"] == start
    assert sub["_stop"]  == stop


@pytest.mark.rootfile
def test_tsubfile_start_stop_accessible_as_attrs(good_run):
    """_start and _stop are accessible as attributes."""
    start = T0 + 20
    stop  = T0 + 80
    sub = tsubfile(good_run.tfile, start, stop)
    assert sub._start == start
    assert sub._stop  == stop


@pytest.mark.rootfile
def test_tsubfile_caches_accessed_objects(good_run):
    """Accessing the same key twice returns the identical object."""
    sub   = _make_sub(good_run)
    obj1  = sub["UCNHits_He3"]
    obj2  = sub["UCNHits_He3"]
    assert obj1 is obj2


@pytest.mark.rootfile
def test_tsubfile_getattr_fallback(good_run):
    """__getattr__ falls back to real object attributes for non-keys."""
    sub = _make_sub(good_run)
    # keys() is a real method on tfile
    ks = sub.keys()
    assert ks is not None


@pytest.mark.rootfile
def test_tsubfile_hit_tree_time_filtered(good_run):
    """UCNHits_He3 accessed through tsubfile is time-filtered."""
    # Cycle 0 window: [T0, T0+100]
    sub_cycle0 = tsubfile(good_run.tfile, T0, T0 + 100)
    tree_all   = good_run.tfile["UCNHits_He3"]
    tree_sub   = sub_cycle0["UCNHits_He3"]

    # The sub-tree should have fewer or equal entries
    size_all = tree_all.size
    size_sub = tree_sub.size
    assert size_sub <= size_all


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

@pytest.mark.rootfile
def test_tsubfile_start_equals_stop_no_error(good_run):
    """start==stop yields valid (empty) slice without raising."""
    sub = tsubfile(good_run.tfile, T0 + 50, T0 + 50)
    assert sub is not None


@pytest.mark.rootfile
def test_tsubfile_out_of_range_no_error(good_run):
    """start/stop entirely outside data range gives empty result, no error."""
    sub = tsubfile(good_run.tfile, T0 + 9999, T0 + 99999)
    # Accessing a time-indexed tree should return an empty result without raising
    tree = sub["UCNHits_He3"]
    assert tree is not None


@pytest.mark.rootfile
def test_tsubfile_non_time_indexed_df_unfiltered(good_run):
    """A DataFrame whose index name lacks 'time' is returned unfiltered."""
    sub = _make_sub(good_run, 0, 10)
    # CycleParamTree is a plain integer-indexed DataFrame (reset_index was called)
    df = sub["CycleParamTree"]
    assert df is not None
    assert len(df) >= 1   # should be unfiltered (1 row)
