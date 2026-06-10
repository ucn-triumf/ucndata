"""Synthetic ROOT file builder for ucndata unit tests.

Builds small, fully deterministic ROOT files that exercise all code paths
in ucnrun/__init__, _get_cycle_param, set_cycle_times_crude, etc.

Schema:
    - 3 cycles, each 100 s starting at T0 = 1717243200
    - 3 periods per cycle: durations [20, 30, 50] s
    - UCNHits_He3: 10 hits per period per cycle (timestamps known exactly)
    - UCNHits_Li-6 (dash in name — exercises rename logic in ucnrun.__init__)
    - BeamlineEpics, UCN2Epics, SequencerTree, LNDDetectorTree
"""

import ctypes
import numpy as np
import ROOT

ROOT.gROOT.SetBatch(True)
ROOT.gErrorIgnoreLevel = ROOT.kError

T0         = 1717243200   # 2024-06-01 12:00:00 UTC
N_CYCLES   = 3
CYCLE_DUR  = 100           # seconds
PERIOD_DURS = [20, 30, 50] # must sum to CYCLE_DUR


# ---------------------------------------------------------------------------
# Individual tree writers
# ---------------------------------------------------------------------------

def _write_header(f):
    """Write header TTree.

    Branch names use underscores (not spaces) so rootloader's RDataFrame can
    read them. ucnrun.py does `k.replace(' ', '_').lower()` so underscore and
    space branch names produce identical attribute names.

    Strings are stored as ROOT.std.string so rootloader returns Python str,
    not RVec<char>. Start_Time is stored as int64 nanoseconds since epoch so
    that pd.to_datetime() in ucnrun.__init__ works correctly.
    """
    tree = ROOT.TTree("header", "header")

    run_num    = ctypes.c_int(2684)
    start_ns   = ctypes.c_int64(T0 * 1_000_000_000)  # nanoseconds for pd.to_datetime
    stop_ns    = ctypes.c_int64((T0 + 300) * 1_000_000_000)

    tree.Branch("Run_Number",  run_num,  "Run_Number/I")
    tree.Branch("Start_Time",  start_ns, "Start_Time/L")
    tree.Branch("Stop_Time",   stop_ns,  "Stop_Time/L")

    # Use ROOT.std.string for text fields so rootloader returns Python str
    str_refs = {}
    for name, value in (
        ("Run_Title",         "synthetic run"),
        ("Shifters",          "tester"),
        ("Comment",           "synthetic"),
        ("Experiment_Number", "2025-01"),
    ):
        s = ROOT.std.string(value)
        tree.Branch(name, s)
        str_refs[name] = s  # keep alive until after Fill()

    tree.Fill()
    f.cd(); tree.Write()
    return (run_num, start_ns, stop_ns, str_refs)  # caller keeps refs alive


def _write_cycle_param(f):
    """Write CycleParamTree: one row per period, columns for each cycle's duration.

    set_cycle_times_crude reads nCycles from row 0.
    set_period_times filters for 'Duration' columns (one per cycle per supercycle),
    renames them by extracting the embedded digit (cycle index), and builds the
    period_durations_s DataFrame of shape (nperiods × ncycles).
    """
    tree = ROOT.TTree("CycleParamTree", "CycleParamTree")

    n_periods = ctypes.c_int(len(PERIOD_DURS))
    n_cycles  = ctypes.c_int(N_CYCLES)
    n_super   = ctypes.c_int(1)
    enable    = ctypes.c_int(1)
    inf_cyc   = ctypes.c_int(0)

    # One Duration branch per cycle in the supercycle (digit = cycle index).
    dur_vals = [ctypes.c_double(0) for _ in range(N_CYCLES)]

    tree.Branch("nPeriods",        n_periods, "nPeriods/I")
    tree.Branch("nCycles",         n_cycles,  "nCycles/I")
    tree.Branch("nSuperCyc",       n_super,   "nSuperCyc/I")
    tree.Branch("enable",          enable,    "enable/I")
    tree.Branch("infCyclesEnable", inf_cyc,   "infCyclesEnable/I")
    for ci, dv in enumerate(dur_vals):
        tree.Branch(f"period{ci}Duration_s", dv, f"period{ci}Duration_s/D")

    for period_dur in PERIOD_DURS:
        for dv in dur_vals:
            dv.value = float(period_dur)
        tree.Fill()

    f.cd(); tree.Write()


def _write_transitions(f, tree_name):
    """Write one RunTransitions_* tree with 3 rows (one per cycle)."""
    offset = 0
    tree   = ROOT.TTree(tree_name, tree_name)

    cycle_idx = ctypes.c_int(0)
    super_idx = ctypes.c_int(0)
    cyc_start = ctypes.c_double(0)
    p0_end    = ctypes.c_double(0)
    p1_end    = ctypes.c_double(0)
    p2_end    = ctypes.c_double(0)

    tree.Branch("cycleIndex",          cycle_idx, "cycleIndex/I")
    tree.Branch("superCycleIndex",     super_idx, "superCycleIndex/I")
    tree.Branch("cycleStartTime",      cyc_start, "cycleStartTime/D")
    tree.Branch("cyclePeriod0EndTime", p0_end,    "cyclePeriod0EndTime/D")
    tree.Branch("cyclePeriod1EndTime", p1_end,    "cyclePeriod1EndTime/D")
    tree.Branch("cyclePeriod2EndTime", p2_end,    "cyclePeriod2EndTime/D")

    vec0 = ROOT.std.vector("int")()
    vec1 = ROOT.std.vector("int")()
    vec2 = ROOT.std.vector("int")()
    tree.Branch("valveStatePeriod0", vec0)
    tree.Branch("valveStatePeriod1", vec1)
    tree.Branch("valveStatePeriod2", vec2)

    for i in range(N_CYCLES):
        start = T0 + i * CYCLE_DUR + offset
        cycle_idx.value = i
        super_idx.value = 0
        cyc_start.value = float(start)
        p0_end.value    = float(start + PERIOD_DURS[0])
        p1_end.value    = float(start + PERIOD_DURS[0] + PERIOD_DURS[1])
        p2_end.value    = float(start + CYCLE_DUR)

        vec0.clear(); vec0.push_back(1)
        vec1.clear(); vec1.push_back(1)
        vec2.clear(); vec2.push_back(1)

        tree.Fill()

    f.cd(); tree.Write()


def _write_sequencer(f, enabled=True):
    """Write SequencerTree at 10-s intervals.

    When enabled, emits one cycleStarted=1 row at the beginning of each cycle
    so that set_cycle_times_crude finds exactly N_CYCLES start timestamps.
    Between cycle starts the rows have cycleStarted=0, inCycle=1.  The final
    row at T0+total marks the end of the run (inCycle=0).

    When disabled: all cycleStarted values are 0, so the cycleStarted filter
    returns an empty array and set_cycle_times_crude raises DataError.
    """
    tree = ROOT.TTree("SequencerTree", "SequencerTree")

    ts      = ctypes.c_double(0)
    seq_en  = ctypes.c_int(1 if enabled else 0)
    started = ctypes.c_int(0)
    in_cyc  = ctypes.c_int(0)

    tree.Branch("timestamp",        ts,      "timestamp/D")
    tree.Branch("sequencerEnabled", seq_en,  "sequencerEnabled/I")
    tree.Branch("cycleStarted",     started, "cycleStarted/I")
    tree.Branch("inCycle",          in_cyc,  "inCycle/I")

    step  = 10
    total = N_CYCLES * CYCLE_DUR

    # One cycleStarted=1 row at the start of each cycle, then in-cycle rows.
    for ci in range(N_CYCLES):
        cycle_start = T0 + ci * CYCLE_DUR

        ts.value      = float(cycle_start)
        started.value = 1 if enabled else 0
        in_cyc.value  = 0
        tree.Fill()

        for t_rel in range(step, CYCLE_DUR, step):
            ts.value      = float(cycle_start + t_rel)
            started.value = 0
            in_cyc.value  = 1 if enabled else 0
            tree.Fill()

    # Final row: run over
    ts.value      = float(T0 + total)
    started.value = 0
    in_cyc.value  = 0
    tree.Fill()

    f.cd(); tree.Write()


def _write_beamline_epics(f):
    """Write BeamlineEpics at 5-s intervals, constant 1 uA beam."""
    tree = ROOT.TTree("BeamlineEpics", "BeamlineEpics")

    ts        = ctypes.c_double(0)
    adjcur    = ctypes.c_double(1.0)
    predcur   = ctypes.c_double(1.0)
    bonprd    = ctypes.c_double(1.0)
    rdbeamon  = ctypes.c_double(67.0)
    rdbeamoff = ctypes.c_double(1.0)

    tree.Branch("timestamp",              ts,        "timestamp/D")
    tree.Branch("B1_FOIL_ADJCUR",         adjcur,    "B1_FOIL_ADJCUR/D")
    tree.Branch("B1V_KSM_PREDCUR",        predcur,   "B1V_KSM_PREDCUR/D")
    tree.Branch("B1V_KSM_BONPRD",         bonprd,    "B1V_KSM_BONPRD/D")
    tree.Branch("B1V_KSM_RDBEAMON_VAL1",  rdbeamon,  "B1V_KSM_RDBEAMON_VAL1/D")
    tree.Branch("B1V_KSM_RDBEAMOFF_VAL1", rdbeamoff, "B1V_KSM_RDBEAMOFF_VAL1/D")

    step  = 5
    total = N_CYCLES * CYCLE_DUR
    for t_rel in range(0, total + step, step):
        ts.value = float(T0 + t_rel)
        tree.Fill()

    f.cd(); tree.Write()


def _write_ucn2_epics(f):
    """Write UCN2Epics: second EPICS tree so ttreeslow merges two sources."""
    tree = ROOT.TTree("UCN2Epics", "UCN2Epics")

    ts   = ctypes.c_double(0)
    flow = ctypes.c_double(0.5)

    tree.Branch("timestamp",          ts,   "timestamp/D")
    tree.Branch("UCN_UGD_BKGD_FLOW",  flow, "UCN_UGD_BKGD_FLOW/D")

    step  = 10
    total = N_CYCLES * CYCLE_DUR
    for t_rel in range(0, total + step, step):
        ts.value = float(T0 + t_rel)
        tree.Fill()

    f.cd(); tree.Write()


def _write_lnd(f):
    """Write LNDDetectorTree: non-empty tree required by ucnrun.check_data."""
    tree = ROOT.TTree("LNDDetectorTree", "LNDDetectorTree")

    ts    = ctypes.c_double(0)
    count = ctypes.c_double(10.0)

    tree.Branch("timestamp", ts,    "timestamp/D")
    tree.Branch("LND_count", count, "LND_count/D")

    step  = 10
    total = N_CYCLES * CYCLE_DUR
    for t_rel in range(0, total + step, step):
        ts.value = float(T0 + t_rel)
        tree.Fill()

    f.cd(); tree.Write()


def _make_he3_hits():
    """Build He3 hit arrays.

    Returns:
        tuple: (timestamps, is_ucn, channel, chargeL, psd) as numpy arrays.

    Hit layout per cycle N:
        Period 0 (T0+N*100 → T0+N*100+20):  10 hits at T0+N*100+[5..14]
        Period 1 (T0+N*100+20 → +50):        10 hits at T0+N*100+[25..34]
        Period 2 (T0+N*100+50 → +100):       10 hits at T0+N*100+[55..64]
    Plus 5 bad timestamps < 1.5e9 (filtered by ucnrun).
    """
    timestamps = []
    for ci in range(N_CYCLES):
        base = T0 + ci * CYCLE_DUR
        timestamps += [base + 5 + j  for j in range(10)]
        timestamps += [base + 25 + j for j in range(10)]
        timestamps += [base + 55 + j for j in range(10)]

    bad = [1.0, 2.0, 3.0, 4.0, 5.0]
    all_ts = np.array(bad + timestamps, dtype=np.float64)

    n = len(all_ts)
    is_ucn  = np.array([0]*5 + [i % 2 for i in range(n - 5)], dtype=np.int32)
    channel = np.zeros(n, dtype=np.int32)
    # chargeL spread across 500–2000 so hist2d in plot_psd has multiple x-bins
    rng = np.random.default_rng(42)
    chargeL = np.concatenate([[100.0]*5,
                              rng.uniform(500, 2000, n - 5)]).astype(np.float64)
    psd     = np.full(n, 0.5, dtype=np.float64)
    return all_ts, is_ucn, channel, chargeL, psd


def _make_li6_hits(chopper=False):
    """Build Li6 hit arrays.

    Timestamps offset +2 s from He3.  Channel 10 carries one hardware
    cycle-start trigger per cycle (at T0 + N*CYCLE_DUR), spaced exactly
    CYCLE_DUR apart so set_cycle_times_precise can use them.  If
    chopper=True, adds channel-15 frame markers at T0+N*100+[10, 30, 60].
    """
    timestamps = []
    for ci in range(N_CYCLES):
        base = T0 + ci * CYCLE_DUR
        timestamps += [base + 7 + j  for j in range(10)]
        timestamps += [base + 27 + j for j in range(10)]
        timestamps += [base + 57 + j for j in range(10)]

    bad = [1.0, 2.0, 3.0, 4.0, 5.0]
    all_ts = np.array(bad + timestamps, dtype=np.float64)

    n = len(all_ts)
    is_ucn  = np.array([0]*5 + [i % 2 for i in range(n - 5)], dtype=np.int32)
    channel = np.zeros(n, dtype=np.int32)
    rng = np.random.default_rng(43)
    chargeL = np.concatenate([[100.0]*5,
                              rng.uniform(200, 1500, n - 5)]).astype(np.float64)
    psd     = np.full(n, 0.3, dtype=np.float64)

    # Hardware cycle-start triggers on channel 10: one hit per cycle at T0+N*CYCLE_DUR.
    hw_ts = np.array([float(T0 + ci * CYCLE_DUR) for ci in range(N_CYCLES)])
    nc_hw = len(hw_ts)
    all_ts  = np.concatenate([all_ts,  hw_ts])
    is_ucn  = np.concatenate([is_ucn,  np.zeros(nc_hw, dtype=np.int32)])
    channel = np.concatenate([channel, np.full(nc_hw, 10, dtype=np.int32)])
    chargeL = np.concatenate([chargeL, np.zeros(nc_hw, dtype=np.float64)])
    psd     = np.concatenate([psd,     np.zeros(nc_hw, dtype=np.float64)])

    if chopper:
        chop_ts = []
        for ci in range(N_CYCLES):
            base = T0 + ci * CYCLE_DUR
            chop_ts += [base + 10, base + 30, base + 60]

        chop_arr = np.array(chop_ts, dtype=np.float64)
        nc = len(chop_arr)
        all_ts  = np.concatenate([all_ts,  chop_arr])
        is_ucn  = np.concatenate([is_ucn,  np.zeros(nc, dtype=np.int32)])
        channel = np.concatenate([channel, np.full(nc, 15, dtype=np.int32)])
        chargeL = np.concatenate([chargeL, np.zeros(nc, dtype=np.float64)])
        psd     = np.concatenate([psd,     np.zeros(nc, dtype=np.float64)])

        # sort by time so ROOT TTree is in order
        order   = np.argsort(all_ts)
        all_ts  = all_ts[order]
        is_ucn  = is_ucn[order]
        channel = channel[order]
        chargeL = chargeL[order]
        psd     = psd[order]

    return all_ts, is_ucn, channel, chargeL, psd


def _write_hits(f, tree_name, timestamps, is_ucn, channel, chargeL, psd):
    """Write a UCNHits_* event TTree."""
    tree = ROOT.TTree(tree_name, tree_name)

    t_val  = ctypes.c_double(0)
    ucn    = ctypes.c_int(0)
    ch     = ctypes.c_int(0)
    charge = ctypes.c_double(0)
    p      = ctypes.c_double(0)

    tree.Branch("tUnixTimePrecise", t_val,  "tUnixTimePrecise/D")
    tree.Branch("tIsUCN",           ucn,    "tIsUCN/I")
    tree.Branch("tChannel",         ch,     "tChannel/I")
    tree.Branch("tChargeL",         charge, "tChargeL/D")
    tree.Branch("tPSD",             p,      "tPSD/D")

    for i in range(len(timestamps)):
        t_val.value  = float(timestamps[i])
        ucn.value    = int(is_ucn[i])
        ch.value     = int(channel[i])
        charge.value = float(chargeL[i])
        p.value      = float(psd[i])
        tree.Fill()

    f.cd(); tree.Write()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_run_file(path, no_sequencer=False, no_transitions=False,
                   no_slow_trees=False, chopper=False):
    """Write a synthetic UCN run ROOT file to *path*.

    Args:
        path: destination path (str or Path)
        no_sequencer: set all sequencerEnabled=0 in SequencerTree
        no_transitions: omit RunTransitions_He3 and RunTransitions_Li6
        no_slow_trees: omit all slow control trees
        chopper: add channel-15 frame markers to UCNHits_Li-6
    """
    path = str(path)
    f    = ROOT.TFile(path, "RECREATE")

    _header_refs = _write_header(f)   # keep refs alive
    _write_cycle_param(f)

    if not no_transitions:
        _write_transitions(f, "RunTransitions_He3")
        _write_transitions(f, "RunTransitions_Li6")

    if not no_slow_trees:
        _write_sequencer(f, enabled=not no_sequencer)
        _write_beamline_epics(f)
        _write_ucn2_epics(f)
        _write_lnd(f)

    he3_ts, he3_ucn, he3_ch, he3_cl, he3_psd = _make_he3_hits()
    _write_hits(f, "UCNHits_He3", he3_ts, he3_ucn, he3_ch, he3_cl, he3_psd)

    li6_ts, li6_ucn, li6_ch, li6_cl, li6_psd = _make_li6_hits(chopper=chopper)
    _write_hits(f, "UCNHits_Li-6", li6_ts, li6_ucn, li6_ch, li6_cl, li6_psd)

    f.Write()
    f.Close()
