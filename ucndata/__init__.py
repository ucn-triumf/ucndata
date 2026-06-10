# init
# Derek Fujimoto
# June 2024

from .ucnrun import ucnrun
from .ucncycle import ucncycle
from .ucnperiod import ucnperiod
from .ucnbase import ucnbase
from .ttreeslow import ttreeslow
from .applylist import applylist
from .exceptions import *
from .datetime import to_datetime, from_datetime

# path to the directory which contains the root files
DATADIR = "/data3/ucn/root_files"

# detector tree names
DET_NAMES = {'He3':{'hits':         'UCNHits_He3',
                    'hits_orig':    'UCNHits_He3', # as saved in the root file
                    'charge':       'He3_Charge',
                    'rate':         'He3_Rate',
                    'transitions':  'RunTransitions_He3',
                    'hitsseq':      'hitsinsequence_he3',
                    'hitsseqcumul': 'hitsinsequencecumul_he3',
                    },
                'Li6':{'hits':         'UCNHits_Li6',
                    'hits_orig':    'UCNHits_Li-6', # as saved in the root file
                    'charge':       'Li6_Charge',
                    'rate':         'Li6_Rate',
                    'transitions':  'RunTransitions_Li6',
                    'hitsseq':      'hitsinsequence_li6',
                    'hitsseqcumul': 'hitsinsequencecumul_li6',
                    },
            }

# needed slow control trees: for checking data quality
SLOW_TREES = ('BeamlineEpics', 'SequencerTree')

# EPICS trees to group into a single slow control tree
EPICS_TREES = [ 'BeamlineEpics',        'UCN2EpPha5Last',   'UCN2EpicsPhase2B',
                'UCN2EpPha5Oth',        'UCN2EpicsPhase3',  'UCN2EpPha5Pre',
                'UCN2EpicsPressures',   'UCN2EpPha5Tmp',    'UCN2EpicsTemperature',
                'UCN2Epics',            'UCN2Pur',          'UCN2EpicsOthers',
                'UCN2EpLD2'
                ]

# data thresholds for checking data
DATA_CHECK_THRESH = {'beam_min_current': 0.1, # uA
                        'pileup_cnt_per_ms': 10, # if larger than this, then pileup and delete
                        'pileup_within_first_s': 1, # time frame for pileup in each period
                    }
