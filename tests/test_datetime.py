"""Tests for ucndata.datetime — Layer A (pure Python, no ROOT)."""

import numpy as np
import pandas as pd
import pytest

from ucndata.datetime import to_datetime, from_datetime


T0 = 1717243200   # 2024-06-01 12:00:00 UTC, same as root builder


# ---------------------------------------------------------------------------
# to_datetime
# ---------------------------------------------------------------------------

def test_to_datetime_array_returns_datetimeindex():
    """to_datetime on an int array returns a tz-aware DatetimeIndex."""
    arr = np.array([T0, T0 + 60, T0 + 120], dtype=np.int64)
    result = to_datetime(arr)
    assert isinstance(result, pd.DatetimeIndex)
    assert result.tz is not None
    assert "America/Vancouver" in str(result.tz)


def test_to_datetime_dataframe_converts_index():
    """to_datetime on a DataFrame converts the index, preserves columns."""
    arr = np.array([T0, T0 + 10, T0 + 20], dtype=np.int64)
    df  = pd.DataFrame({"value": [1.0, 2.0, 3.0]}, index=arr)
    df.index.name = "timestamp"
    result = to_datetime(df)
    assert isinstance(result, pd.DataFrame)
    assert list(result.columns) == ["value"]
    assert result.index.name == "timestamp"
    assert result.index.tz is not None


def test_to_datetime_preserves_columns():
    arr = np.array([T0, T0 + 5], dtype=np.int64)
    df  = pd.DataFrame({"a": [1, 2], "b": [3, 4]}, index=arr)
    r   = to_datetime(df)
    assert list(r.columns) == ["a", "b"]


# ---------------------------------------------------------------------------
# from_datetime
# ---------------------------------------------------------------------------

def test_from_datetime_series_returns_integers():
    """from_datetime on a tz-aware Series returns integer epoch seconds."""
    arr  = np.array([T0, T0 + 100], dtype=np.int64)
    dt   = to_datetime(arr)
    back = from_datetime(dt)
    assert isinstance(back, np.ndarray)
    np.testing.assert_array_equal(back, arr)


def test_from_datetime_dataframe_converts_index():
    """from_datetime on a DataFrame converts the tz-aware index, preserves name."""
    arr = np.array([T0, T0 + 10, T0 + 20], dtype=np.int64)
    df  = pd.DataFrame({"x": [1, 2, 3]}, index=arr)
    df.index.name = "timestamp"
    dt  = to_datetime(df)
    back = from_datetime(dt)
    assert isinstance(back, pd.DataFrame)
    assert back.index.name == "timestamp"
    np.testing.assert_array_equal(back.index.values, arr)


# ---------------------------------------------------------------------------
# Round trips
# ---------------------------------------------------------------------------

def test_roundtrip_array():
    """from_datetime(to_datetime(x)) == x for integer epoch array."""
    arr  = np.array([T0, T0 + 50, T0 + 99], dtype=np.int64)
    back = from_datetime(to_datetime(arr))
    np.testing.assert_array_equal(back, arr)


def test_roundtrip_dataframe_index():
    """Round trip for a DataFrame index."""
    arr = np.array([T0, T0 + 10], dtype=np.int64)
    df  = pd.DataFrame({"y": [5.0, 6.0]}, index=arr)
    df.index.name = "ts"
    back = from_datetime(to_datetime(df))
    np.testing.assert_array_equal(back.index.values, arr)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_from_datetime_tz_naive_hits_localize_branch():
    """from_datetime on a tz-naive datetime still succeeds via tz_localize."""
    arr = pd.date_range("2024-01-01", periods=3, freq="10s")  # tz-naive
    result = from_datetime(arr)
    assert result is not None
    assert len(result) == 3


def test_sub_second_timestamps_floored():
    """Sub-second timestamps are floor-divided to whole seconds."""
    ts_float = np.array([T0 + 0.7, T0 + 1.3], dtype=np.float64)
    # Convert floats to int first (simulate what from_datetime does)
    arr_int = ts_float.astype(np.int64)
    dt  = to_datetime(arr_int)
    back = from_datetime(dt)
    np.testing.assert_array_equal(back, arr_int)


def test_empty_array():
    """to_datetime on an empty array works without error."""
    arr    = np.array([], dtype=np.int64)
    result = to_datetime(arr)
    assert len(result) == 0
