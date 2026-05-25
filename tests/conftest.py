"""Shared pytest fixtures for ucndata test suite.

Sets up matplotlib Agg backend and patches os.get_terminal_size before
any ucndata import so __repr__ works under pytest capture.
"""

import os
import unittest.mock as mock

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

from _root_builder import build_run_file


# ---------------------------------------------------------------------------
# Support fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True, scope="session")
def patch_terminal_size():
    """Monkeypatch os.get_terminal_size so every __repr__ works in CI."""
    fake = os.terminal_size((120, 40))
    with mock.patch("os.get_terminal_size", return_value=fake):
        yield


@pytest.fixture(autouse=True)
def close_plots():
    """Close all matplotlib figures after every test."""
    yield
    plt.close("all")


# ---------------------------------------------------------------------------
# Synthetic ROOT file fixtures (session-scoped — built once)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def good_run_file(tmp_path_factory):
    """Path to the 'good' synthetic ROOT file (3 cycles, 3 periods)."""
    path = tmp_path_factory.mktemp("root") / "good_run.root"
    build_run_file(path)
    return path


@pytest.fixture(scope="session")
def no_sequencer_file(tmp_path_factory):
    """sequencerEnabled=0 throughout — whole run is one cycle."""
    path = tmp_path_factory.mktemp("root") / "no_seq.root"
    build_run_file(path, no_sequencer=True)
    return path


@pytest.fixture(scope="session")
def no_transitions_file(tmp_path_factory):
    """RunTransitions trees absent — emits MissingDataWarning."""
    path = tmp_path_factory.mktemp("root") / "no_trans.root"
    build_run_file(path, no_transitions=True)
    return path


@pytest.fixture(scope="session")
def mismatched_file(tmp_path_factory):
    """He3 cycleStartTime +25 s from Li6 — matched mode raises CycleError."""
    path = tmp_path_factory.mktemp("root") / "mismatched.root"
    build_run_file(path, mismatched=True)
    return path


@pytest.fixture(scope="session")
def no_slow_trees_file(tmp_path_factory):
    """Slow control trees absent — set_cycle_times raises MissingDataError."""
    path = tmp_path_factory.mktemp("root") / "no_slow.root"
    build_run_file(path, no_slow_trees=True)
    return path


@pytest.fixture(scope="session")
def chopper_file(tmp_path_factory):
    """UCNHits_Li-6 has channel-15 frame markers — drives crun tests."""
    path = tmp_path_factory.mktemp("root") / "chopper.root"
    build_run_file(path, chopper=True)
    return path


# ---------------------------------------------------------------------------
# ucnrun / crun fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def good_run(good_run_file):
    """Fresh ucnrun for every test (tests may mutate cycle_param)."""
    from ucndata import ucnrun
    return ucnrun(str(good_run_file))


@pytest.fixture(scope="session")
def good_run_cached(good_run_file):
    """Read-only ucnrun shared across all tests in the session."""
    from ucndata import ucnrun
    return ucnrun(str(good_run_file))


@pytest.fixture(scope="function")
def empty_run():
    """Bare ucnrun(None) for Layer C (hand-populate attributes)."""
    from ucndata import ucnrun
    return ucnrun(None)


@pytest.fixture(scope="function")
def chopper_run(chopper_file):
    """Fresh crun for chopper tests."""
    from ucndata.chopper import crun
    return crun(str(chopper_file))
