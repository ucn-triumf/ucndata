"""Tests for ucndata.applylist — Layer A (pure Python, no ROOT)."""

import math
import builtins

import numpy as np
import pytest

from ucndata.applylist import applylist


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_construction_from_range():
    x = applylist(range(5))
    assert isinstance(x, list)
    assert list(x) == [0, 1, 2, 3, 4]


def test_construction_from_list():
    x = applylist([10, 20, 30])
    assert isinstance(x, list)
    assert len(x) == 3


def test_construction_from_ndarray():
    x = applylist(np.arange(4))
    assert isinstance(x, list)
    assert len(x) == 4


def test_is_list_subclass():
    assert isinstance(applylist([1, 2]), list)


# ---------------------------------------------------------------------------
# Attribute access on contained objects
# ---------------------------------------------------------------------------

class _Obj:
    def __init__(self, val):
        self.val = val
    def double(self):
        return self.val * 2


def test_attribute_access_returns_applylist():
    objs = applylist([_Obj(1), _Obj(2), _Obj(3)])
    vals = objs.val
    assert isinstance(vals, applylist)
    assert list(vals) == [1, 2, 3]


def test_attribute_access_recursive_nested():
    inner = applylist([_Obj(10), _Obj(20)])
    outer = applylist([inner])
    result = outer.val
    assert isinstance(result, applylist)
    assert isinstance(result[0], applylist)
    assert list(result[0]) == [10, 20]


def test_real_list_attribute_resolves():
    """Native list attributes like .copy and .append still work."""
    x = applylist([1, 2, 3])
    c = x.copy()
    assert isinstance(c, applylist)
    assert list(c) == [1, 2, 3]


# ---------------------------------------------------------------------------
# __call__ — element-wise method invocation
# ---------------------------------------------------------------------------

def test_call_invokes_element_methods():
    words = applylist(["hello", "world"])
    result = words.upper()
    assert isinstance(result, applylist)
    assert list(result) == ["HELLO", "WORLD"]

# ---------------------------------------------------------------------------
# apply()
# ---------------------------------------------------------------------------

def test_apply_returns_new_list():
    x = applylist([1, 2, 3])
    y = x.apply(lambda a: a ** 2)
    assert isinstance(y, applylist)
    assert list(y) == [1, 4, 9]
    assert list(x) == [1, 2, 3]   # original unchanged


def test_apply_inplace_returns_none_and_mutates():
    x = applylist([1, 2, 3])
    result = x.apply(lambda a: a * 10, inplace=True)
    assert result is None
    assert isinstance(x, applylist)
    assert list(x) == [10, 20, 30]


def test_apply_recurses_into_nested_applylist():
    inner = applylist([1, 2])
    outer = applylist([inner, applylist([3, 4])])
    result = outer.apply(lambda a: a * 2)
    assert isinstance(result, applylist)
    assert isinstance(result[0], applylist)
    assert list(result[0]) == [2, 4]
    assert list(result[1]) == [6, 8]


# ---------------------------------------------------------------------------
# Arithmetic operators
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("op,scalar,expected", [
    ("add",      5, [6, 7, 8]),
    ("sub",      1, [0, 1, 2]),
    ("mul",      3, [3, 6, 9]),
    ("floordiv", 2, [0, 1, 1]),
    ("truediv",  2, [0.5, 1.0, 1.5]),
    ("mod",      2, [1, 0, 1]),
    ("pow",      2, [1, 4, 9]),
])
def test_arithmetic_scalar(op, scalar, expected):
    x = applylist([1, 2, 3])
    result = getattr(x, f"__{op}__")(scalar)
    assert isinstance(result, applylist)
    for r, e in zip(result, expected):
        assert r == pytest.approx(e)


# ---------------------------------------------------------------------------
# Comparison operators
# ---------------------------------------------------------------------------

def test_eq_returns_applylist_of_bools():
    x = applylist([1, 2, 3])
    r = (x == 2)
    assert isinstance(r, applylist)
    assert list(r) == [False, True, False]


def test_ne():
    x = applylist([1, 2, 3])
    assert list(x != 2) == [True, False, True]


def test_lt():
    x = applylist([1, 2, 3])
    assert list(x < 2) == [True, False, False]


def test_gt():
    x = applylist([1, 2, 3])
    assert list(x > 2) == [False, False, True]


def test_le():
    x = applylist([1, 2, 3])
    assert list(x <= 2) == [True, True, False]


def test_ge():
    x = applylist([1, 2, 3])
    assert list(x >= 2) == [False, True, True]


# ---------------------------------------------------------------------------
# Unary operators
# ---------------------------------------------------------------------------

def test_neg():
    x = applylist([1, -2, 3])
    assert list(-x) == [-1, 2, -3]


def test_pos():
    x = applylist([1, -2, 3])
    assert list(+x) == [1, -2, 3]


def test_abs():
    x = applylist([-1, 2, -3])
    assert list(abs(x)) == [1, 2, 3]


def test_round():
    x = applylist([1.4, 2.6, 3.5])
    # round() element-wise via numpy
    assert list(np.round(x)) == [1, 3, 4]


def test_floor():
    x = applylist([1.7, 2.3])
    assert list(np.floor(x)) == [1, 2]


def test_ceil():
    x = applylist([1.2, 2.8])
    assert list(np.ceil(x)) == [2, 3]

# ---------------------------------------------------------------------------
# Bitwise operators
# ---------------------------------------------------------------------------

def test_and():
    x = applylist([0b101, 0b110])
    r = x & 0b100
    assert list(r) == [0b100, 0b100]


def test_or():
    x = applylist([0b001, 0b010])
    r = x | 0b100
    assert list(r) == [0b101, 0b110]


def test_xor():
    x = applylist([0b111, 0b000])
    r = x ^ 0b101
    assert list(r) == [0b010, 0b101]


# ---------------------------------------------------------------------------
# __getitem__
# ---------------------------------------------------------------------------

def test_getitem_int():
    x = applylist([10, 20, 30])
    assert x[1] == 20


def test_getitem_slice_returns_applylist():
    x = applylist([10, 20, 30, 40])
    s = x[1:3]
    assert isinstance(s, applylist)
    assert list(s) == [20, 30]


def test_getitem_bool_ndarray():
    x = applylist([10, 20, 30])
    mask = np.array([True, False, True])
    r = x[mask]
    assert isinstance(r, applylist)
    assert list(r) == [10, 30]


def test_getitem_int_ndarray():
    x = applylist([10, 20, 30])
    idx = np.array([2, 0])
    r = x[idx]
    assert isinstance(r, applylist)
    assert list(r) == [30, 10]


def test_getitem_list_of_indices():
    x = applylist([10, 20, 30])
    r = x[[2, 0]]
    assert isinstance(r, applylist)
    assert list(r) == [30, 10]


def test_getitem_tuple_of_indices():
    x = applylist([10, 20, 30])
    r = x[(2, 1)]
    assert isinstance(r, applylist)
    assert list(r) == [30, 20]


# ---------------------------------------------------------------------------
# astype
# ---------------------------------------------------------------------------

def test_astype_converts_in_place():
    x = applylist(np.arange(3))   # np.int64 elements
    x.astype(int)
    assert all(type(v) is int for v in x)


# ---------------------------------------------------------------------------
# transpose
# ---------------------------------------------------------------------------

def test_transpose_2d():
    x = applylist([[1, 2, 3], [4, 5, 6]])
    t = x.transpose()
    assert isinstance(t, applylist)
    assert len(t) == 3   # 3 columns → 3 rows after transpose
    assert list(t[0]) == [1, 4]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_attribute_on_scalar_elements_raises():
    """Accessing attribute on applylist of scalars raises AttributeError."""
    x = applylist([1.0, 2.0, 3.0])
    with pytest.raises(AttributeError):
        _ = x.nonexistent_attr


def test_array_protocol_name_raises():
    """Names with __array_ raise AttributeError (numpy protocol guard)."""
    x = applylist([_Obj(1)])
    with pytest.raises(AttributeError):
        _ = x.__array_something__


def test_empty_applylist_attribute_raises():
    """Attribute access on empty applylist raises IndexError (self[0] fails)."""
    x = applylist([])
    with pytest.raises(IndexError):
        _ = x.val
