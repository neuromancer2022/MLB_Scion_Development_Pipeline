# pylint: disable=W,C,R
import warnings
warnings.filterwarnings("ignore")  # suppress SettingWithCopyWarning and deprecation warnings
import pandas as pd
pd.options.mode.chained_assignment = None  # suppress SettingWithCopyWarning at pandas level
from pathlib import Path
import sys, traceback
import os
import subprocess
import numpy as np
import decimal #for floating point to string conversion and maintaining precision
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import deque #for list processing
from collections import OrderedDict
import argparse
import math
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import xgboost as xgb
from xgboost import plot_importance
from lightgbm import LGBMClassifier
from lightgbm import LGBMRegressor
from lightgbm import plot_importance
import statsmodels.formula.api as smf
import statsmodels.api as sm
import statsmodels.stats.api as sms
from statsmodels.iolib.table import SimpleTable, default_txt_fmt
import joblib
import MLB_dbvar as MLB_dbvar
import MLB_Scion_Cfg as MLB_cfg
import MLB_Scion_Globals as MLB_global
import MLB_Scion_Preds as MLB_preds
import MLB_Scion_MasterDB as MLB_masterdb
import MLB_Scion_Mups as MLB_matchup
import MLB_Scion_dGEN as MLB_dgen
import MLB_Scion_dTrans as MLB_dtrans
# pylint: disable=c0301

#Print opening banner to console
print("\n"+ MLB_global.APP_BANNER + "\n" + MLB_global.APP_OWNER + "\n")        
# Set environment vars and define key global vars
cwd = os.getcwd()
# Resolve output directories from env vars set by run_scion.py / run_experiment.py.
# Fall back to cwd so MLB_Scion.py still works when called directly.
preds_out_dir = os.environ.get("MLB_SCION_PREDS_DIR", cwd)
logs_out_dir  = os.environ.get("MLB_SCION_LOGS_DIR",  cwd)
# Resolve SYSTEM_PATH and CONFIG_FNAME from env vars (set by wrappers)
_env_system_path  = os.environ.get("MLB_SCION_SYSTEM_PATH",  None)
_env_config_fname = os.environ.get("MLB_SCION_CONFIG_FNAME", None)
if _env_system_path:
    MLB_global.SYSTEM_PATH = _env_system_path
if _env_config_fname:
    MLB_global.CONFIG_FNAME = _env_config_fname
#create new context for use of ctx (to do with floating point/string conversion and maintaining precision)
ctx = decimal.Context()
ctx.prec = MLB_global.NN_DP_PRECISION #set precision based on setup parameter

def _errorReport():
    print("Review the error report below and resolve any issues.\n")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print ("*** print_tb:")
    traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    print ("*** print_exception:")
    traceback.print_exception(exc_type, exc_value, exc_traceback,
                            limit=2, file=sys.stdout)
    print ("*** print_exc:")
    traceback.print_exc()
    print ("*** format_exc, first and last line:")
    formatted_lines = traceback.format_exc().splitlines()
    print (formatted_lines[0])
    print (formatted_lines[-1])
    print ("*** format_exception:")
    print (traceback.format_exception(exc_type, exc_value,
                                        exc_traceback))
    print ("*** extract_tb:")
    print (traceback.extract_tb(exc_traceback))
    print ("*** format_tb:")
    print (traceback.format_tb(exc_traceback))
    print ("*** tb_lineno:", exc_traceback.tb_lineno)
    sys.exit(1)

def float_to_str(f):
    """
    see https://stackoverflow.com/questions/38847690/convert-float-to-string-in-positional-format-without-scientific-notation-and-fa/38847691#38847691
    Convert the given float to a string,
    without resorting to scientific notation
    """
    d1 = ctx.create_decimal(repr(f))
    return format(d1, 'f')

def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("\nPress key to exit.\n")
    sys.exit(-1)

def adjustModelSpread(bookieLine, playPosition, adjValue):
    adjLine = bookieLine
    if playPosition != MLB_global.ACTION_NOPLAY:
        if playPosition == MLB_global.ACTION_LINE_HF or playPosition == MLB_global.ACTION_LINE_HD:
            adjLine += adjValue
        else:
            adjLine -= adjValue
    return adjLine
    
def getB1Position(probThresh, bookieHMLine, bookieVMLine, bookieHProb, modelProb):
    #B1 = Prb of Home Team Win
    #Assume voter and initialise vars
    playPosition = MLB_global.ACTION_NOPLAY
    if modelProb >= probThresh: #play HOME
        if bookieHMLine < bookieVMLine: #HF
            playPosition = MLB_global.ACTION_LINE_HF
        else: #HD
            playPosition = MLB_global.ACTION_LINE_HD
    else: #play V
        if bookieHMLine < bookieVMLine: #VD
            playPosition = MLB_global.ACTION_LINE_VD
        else: #play VF
            playPosition = MLB_global.ACTION_LINE_VF
    
    return playPosition

def getG2Position(probThresh, bookieHMLine, bookieVMLine, modelProb):
    #G2 = Prb of Fave Team Win (fave as determined by bookieML)
    #Assume voter and initialise vars
    playPosition = MLB_global.ACTION_NOPLAY
    if bookieHMLine < bookieVMLine: #play HFVD
        if modelProb >= probThresh:
            playPosition = MLB_global.ACTION_LINE_HF
        else:
            playPosition = MLB_global.ACTION_LINE_VD
    else: #play VFHD
        if modelProb >= probThresh:
            playPosition = MLB_global.ACTION_LINE_VF
        else:
            playPosition = MLB_global.ACTION_LINE_HD
            
    return playPosition

def getEnsBPFeatureDP(modelCfg):
    bpvardp = 10 #default
    ens = modelCfg.getCurrentTaskModelEnsemble()
    if ens == MLB_global.MODEL_PROBENS1: 
        bpvardp = int(modelCfg.getSysProbBPVarDP())
    else:
        if ens == MLB_global.MODEL_PROBENS2: 
            bpvardp = int(modelCfg.getSysProbSTATSONLYBPVarDP())
    
    return bpvardp

def getPriceVoteMatchStatus(hBookiePrice, vBookiePrice, modelHPrice, modelVote):
    pricevoteMatch = False
    if hBookiePrice < vBookiePrice:
        if modelVote == MLB_global.ACTION_LINE_HF  and modelHPrice < 0:
            pricevoteMatch = True
        else:
            if modelVote == MLB_global.ACTION_LINE_VD  and modelHPrice > 0:
                pricevoteMatch = True
    else:
        if modelVote == MLB_global.ACTION_LINE_VF  and modelHPrice > 0:
            pricevoteMatch = True
        else:
            if modelVote == MLB_global.ACTION_LINE_HD  and modelHPrice < 0:
                pricevoteMatch = True
    return pricevoteMatch

def getDefaultDogPlay(hBookiePrice, vBookiePrice, sysCfgObj=None, predsObj=None):
    # V26.06b (PDF §9.4): when NEITHER ensemble flags the favourite, the default
    # play is the DOG (the side opposite the favourite). Under the new strategy
    # every in-scope game is played, so the old win-loss-price threshold gate
    # (which could suppress the dog to NoPlay) is REMOVED. sysCfgObj/predsObj are
    # retained as optional args for call-site compatibility but are unused.
    #
    # Favourite side is taken from the bookie prices (shorter/more-negative price
    # = favourite). Ties (equal prices) => home dog, matching §9.1's tie rule
    # (book_close(home)==0.5 => visitor fave / home dog).
    if hBookiePrice < vBookiePrice:      # home favourite -> dog is the visitor
        defaultDogPlay = MLB_global.ACTION_LINE_VD
    else:                                # visitor favourite (or tie) -> home dog
        defaultDogPlay = MLB_global.ACTION_LINE_HD

    return defaultDogPlay

def deriveBookProbabilities(predsObj):
    # V26.06b (PDF §9.1). Returns the two de-vigged home probabilities the
    # strategy needs:
    #   book_close(home) = devig of the CLOSING implied probabilities.
    #                      Determines the FAVE side (home iff > 0.5; ties -> vis fave).
    #   book_mid(home)   = devig of the MEAN of opening and closing implied
    #                      probabilities (per side, then normalised). Used for the
    #                      probability-points gap.
    # If opening prices are missing/invalid, book_mid falls back to book_close.
    _hClose = float(predsObj.getPreds_H_Bookie_Bet_Prob())
    _vClose = float(predsObj.getPreds_V_Bookie_Bet_Prob())
    _bookCloseHome = MLB_global.calcDeVigProb(_hClose, _vClose, h_or_v=MLB_global.HOME)

    _hOpen = float(predsObj.getPreds_H_Bookie_Opening_Prob())
    _vOpen = float(predsObj.getPreds_V_Bookie_Opening_Prob())
    _openValid = (0.0 < _hOpen < 1.0) and (0.0 < _vOpen < 1.0)
    _closeValid = (0.0 < _hClose < 1.0) and (0.0 < _vClose < 1.0)
    if _openValid and _closeValid:
        _meanH = (_hOpen + _hClose) / 2.0
        _meanV = (_vOpen + _vClose) / 2.0
        _bookMidHome = MLB_global.calcDeVigProb(_meanH, _meanV, h_or_v=MLB_global.HOME)
    else:
        # No usable opening line -> mid == close (best available)
        _bookMidHome = _bookCloseHome

    return _bookCloseHome, _bookMidHome


def validateEnsemblePosition(ens, faveIsHome, ensSideIsHome, ensVote, ensGap, flagVoteThreshold, strongVoteThreshold, gapThreshold, predsObj):
    # V26.06b play strategy (PDF §9.2). Determine the ENSEMBLE STATE for one model.
    #
    # An ensemble is only ever FLAGGED when it BACKS THE FAVOURITE side (side(M)
    # equals the book_close fave side). Given that, its probability-points gap
    # over book_mid must clear the edge threshold, and its side-vote share sets
    # the tier:
    #   STRONG-FLAG : vote >= strongVoteThreshold (0.93)
    #   FLAG        : vote >= flagVoteThreshold   (0.83)   [STRONG is a subset]
    #   SILENT      : everything else (backs the dog, or on the fave but under-gated)
    #
    # Returns (ensState, predsObj). ensState is one of MLB_global.ENS_STATE_*.
    ensState = MLB_global.ENS_STATE_SILENT
    _backsFave = (ensSideIsHome == faveIsHome)   # side(M) == FAVE side
    if _backsFave and ensGap >= gapThreshold:
        if ensVote >= strongVoteThreshold:
            ensState = MLB_global.ENS_STATE_STRONG
        elif ensVote >= flagVoteThreshold:
            ensState = MLB_global.ENS_STATE_FLAG
        else:
            ensState = MLB_global.ENS_STATE_SILENT

    # Annotate the game with this ensemble's state / reason for silence
    _addEnsStateComment(ens, ensState, _backsFave, predsObj)

    return ensState, predsObj


def _addEnsStateComment(ens, ensState, backsFave, predsObj):
    # Adds the per-ensemble state comment (PDF §9.2). For SILENT, distinguishes
    # 'backs the dog' from 'on the favourite but under-gated'.
    if ens == MLB_global.MODEL_PROBENS1:
        if ensState == MLB_global.ENS_STATE_STRONG:
            predsObj.addComment(MLB_global.messageScionEns1StrongFlag)
        elif ensState == MLB_global.ENS_STATE_FLAG:
            predsObj.addComment(MLB_global.messageScionEns1Flag)
        elif backsFave:
            predsObj.addComment(MLB_global.messageScionEns1SilentGate)
        else:
            predsObj.addComment(MLB_global.messageScionEns1SilentDog)
    else:
        if ensState == MLB_global.ENS_STATE_STRONG:
            predsObj.addComment(MLB_global.messageScionEns2StrongFlag)
        elif ensState == MLB_global.ENS_STATE_FLAG:
            predsObj.addComment(MLB_global.messageScionEns2Flag)
        elif backsFave:
            predsObj.addComment(MLB_global.messageScionEns2SilentGate)
        else:
            predsObj.addComment(MLB_global.messageScionEns2SilentDog)

    return predsObj

def determineScionSidePosition(sysCfgObj, predsObj, mupComments):
    # V26.06b (Standard Edition) play strategy - PDF section 9 (implementation-ready).
    #
    #   Ensembles: ENS1 = StatsOnly (V127), ENS2 = LeanStatsOnly (V129).
    #
    #   1) For each ensemble M, compute its STATE per section 9.2:
    #        side(M)   = home iff med(M) >= 0.5      (med = ensemble home-win prob)
    #        gap(M)    = signed edge of med over book_mid on M's OWN side
    #        vote(M)   = side-vote share (VoteAgreement)
    #        FAVE side = home iff book_close(home) > 0.5   (ties -> visitor fave)
    #        STRONG-FLAG : side==FAVE and gap>=gapThr and vote>=0.93
    #        FLAG        : side==FAVE and gap>=gapThr and vote>=0.83
    #        SILENT      : otherwise (backs the dog, or on the fave but under-gated)
    #   2) Apply the section 9.4 decision table (exactly one row fires; every game
    #      is played - NoPlay only when the bookie prices are invalid):
    #        both flagged        -> play FAVE; 7* if both STRONG else 5*
    #        exactly one flagged -> if FAVE==HOME: play HF 3*
    #                               else (FAVE==VIS): play HOME DOG 1* (no override)
    #        none flagged        -> play DOG; if DOG==VIS: 1*
    #                               else (HOME dog): closing-price tiered 5*/3*/5*
    #   3) VF (visitor-favourite) plays are now ALLOWED (both-flagged, vis fave).
    #   4) NULL starting-pitcher games are ALLOWED (noted in comments only).
    #
    # ASSUMPTION 1: sysCfgObj and predsObj have the required component data stored.
    # ASSUMPTION 2: bookie prices are rounded to the nearest integer for decisions.
    try:
        # 1. Key bookie inputs
        _hBookiePrice = predsObj.getPreds_H_Bookie_Bet_Price()    # hom_clml (closing)
        _vBookiePrice = predsObj.getPreds_V_Bookie_Bet_Price()    # vis_clml (closing)
        _hSP_Null = predsObj.getPreds_H_SP_Null()
        _vSP_Null = predsObj.getPreds_V_SP_Null()
        _stakeMode = int(sysCfgObj.getSysStakeMode())
        _kellyFrac = float(sysCfgObj.getSysKellyFract())
        # Strategy gates
        _strongVoteThresh   = float(MLB_global.PROB_STRONG_VOTE_THRESHOLD)         # 0.93
        _ens1FlagVoteThresh = float(sysCfgObj.getSysProbAgreeThresh())             # 0.83
        _ens1GapThresh      = float(sysCfgObj.getSysProbPointsGap())               # 0.02
        _ens2FlagVoteThresh = float(sysCfgObj.getSysProbSTATSONLYAgreeThresh())    # 0.83
        _ens2GapThresh      = float(sysCfgObj.getSysProbSTATSONLYPointsGap())      # 0.02
        # Ensemble outputs
        _ens1Med  = float(predsObj.getPreds_Ens1_HWinProb())      # med(V127)
        _ens1Vote = float(predsObj.getPreds_Ens1_VoteAgreement()) # vote(V127)
        _ens2Med  = float(predsObj.getPreds_Ens2_HWinProb())      # med(V129)
        _ens2Vote = float(predsObj.getPreds_Ens2_VoteAgreement()) # vote(V129)
        # Defaults
        _scionPOS = MLB_global.ACTION_NOPLAY
        _scionCONF = _scionMultiplier = _scionStake = _scionEdge = 0.0
        _starPlay = MLB_global.ModelConfidenceTypes.ZEROSTAR
        _ens1State = _ens2State = MLB_global.ENS_STATE_SILENT
        _favePOS = MLB_global.ACTION_NOPLAY

        # 2. Only decide if valid H and V bookie prices were calculated
        if MLB_global.validTeamPrice(_hBookiePrice) and MLB_global.validTeamPrice(_vBookiePrice):
            # 2a. Note (do NOT suppress) null-pitcher games - V26.06b allows them
            if _hSP_Null and _vSP_Null:
                predsObj.addComment(MLB_global.messageScionNullBothSPAllowed)
            elif _hSP_Null:
                predsObj.addComment(MLB_global.messageScionNullHSPAllowed)
            elif _vSP_Null:
                predsObj.addComment(MLB_global.messageScionNullVSPAllowed)

            # 2b. Derived book probabilities (section 9.1)
            _bookCloseHome, _bookMidHome = deriveBookProbabilities(predsObj)
            _faveIsHome = (_bookCloseHome > 0.5)      # ties (==0.5) -> visitor fave

            # 2c. Per-ensemble side / gap (section 9.1)
            _ens1SideIsHome = (_ens1Med >= 0.5)
            _ens2SideIsHome = (_ens2Med >= 0.5)
            _ens1HomeEdgeMid = round(float(_ens1Med - _bookMidHome), 5)
            _ens2HomeEdgeMid = round(float(_ens2Med - _bookMidHome), 5)
            _ens1Gap = _ens1HomeEdgeMid if _ens1SideIsHome else -_ens1HomeEdgeMid
            _ens2Gap = _ens2HomeEdgeMid if _ens2SideIsHome else -_ens2HomeEdgeMid

            # 2d. Ensemble states (section 9.2)
            _ens1State, predsObj = validateEnsemblePosition(MLB_global.MODEL_PROBENS1, _faveIsHome, _ens1SideIsHome, _ens1Vote, _ens1Gap, _ens1FlagVoteThresh, _strongVoteThresh, _ens1GapThresh, predsObj)
            _ens2State, predsObj = validateEnsemblePosition(MLB_global.MODEL_PROBENS2, _faveIsHome, _ens2SideIsHome, _ens2Vote, _ens2Gap, _ens2FlagVoteThresh, _strongVoteThresh, _ens2GapThresh, predsObj)
            _ens1Flagged = _ens1State in MLB_global.ENS_FLAGGED_STATES
            _ens2Flagged = _ens2State in MLB_global.ENS_FLAGGED_STATES

            # Fave / dog positions for this game
            _favePOS = MLB_global.ACTION_LINE_HF if _faveIsHome else MLB_global.ACTION_LINE_VF
            _dogPOS  = getDefaultDogPlay(_hBookiePrice, _vBookiePrice)   # VD if home fave else HD

            # 2e. Decision table (section 9.4) - exactly one branch fires
            if _ens1Flagged and _ens2Flagged:
                # Both flag the favourite -> consensus favourite play
                _scionPOS = _favePOS
                if _ens1State == MLB_global.ENS_STATE_STRONG and _ens2State == MLB_global.ENS_STATE_STRONG:
                    _starPlay = MLB_global.ModelConfidenceTypes.SEVENSTAR
                    predsObj.addComment(MLB_global.messageScionConsensusStrong)
                else:
                    _starPlay = MLB_global.ModelConfidenceTypes.FIVESTAR
                    predsObj.addComment(MLB_global.messageScionConsensusFlag)
            elif _ens1Flagged or _ens2Flagged:
                # Exactly one ensemble flags the favourite
                if _faveIsHome:
                    # Single HOME-fave flag DOES override -> play HF 3*
                    _scionPOS = MLB_global.ACTION_LINE_HF
                    _starPlay = MLB_global.ModelConfidenceTypes.THREESTAR
                    predsObj.addComment(MLB_global.messageScionSingleHFOverride)
                else:
                    # Single VISITOR-fave flag does NOT override -> home dog, 1*
                    _scionPOS = MLB_global.ACTION_LINE_HD
                    _starPlay = MLB_global.ModelConfidenceTypes.ONESTAR
                    predsObj.addComment(MLB_global.messageScionSingleVFNoOverride)
            else:
                # Neither flags -> play the DOG
                if _dogPOS == MLB_global.ACTION_LINE_VD:
                    # Visitor dog: flat 1* (no price structure)
                    _scionPOS = MLB_global.ACTION_LINE_VD
                    _starPlay = MLB_global.ModelConfidenceTypes.ONESTAR
                    predsObj.addComment(MLB_global.messageScionDefaultVisDog)
                else:
                    # Home dog: closing-price-tiered stars (U-shaped 5*/3*/5*)
                    _scionPOS = MLB_global.ACTION_LINE_HD
                    _homCLML = round(float(_hBookiePrice))
                    if MLB_global.HOMEDOG_PRICE_TIER_LOW <= _homCLML <= MLB_global.HOMEDOG_PRICE_TIER_HIGH:
                        _starPlay = MLB_global.ModelConfidenceTypes.THREESTAR
                    else:
                        _starPlay = MLB_global.ModelConfidenceTypes.FIVESTAR
                    predsObj.addComment(MLB_global.messageScionDefaultHomeDog)

            # 2f. Confidence + reported edge (book_mid-based, on the played side)
            _scionCONF = round(max(_ens1Vote, _ens2Vote), 2)
            if _scionPOS == MLB_global.ACTION_LINE_HF or _scionPOS == MLB_global.ACTION_LINE_HD:
                _scionEdge = _ens1HomeEdgeMid
            else:
                _scionEdge = -_ens1HomeEdgeMid
        else:
            predsObj.addComment(MLB_global.messageScionInvalidTeamPrice)

        # 3. Stake + payout multiplier for the played side (stars are the stake scale)
        if _scionPOS != MLB_global.ACTION_NOPLAY:
            _scionMultiplier = MLB_global.getStakeMultiplier(_hBookiePrice, _vBookiePrice, _scionPOS)
            _scionStake = MLB_global.getStakeAmount(_stakeMode, _kellyFrac, _hBookiePrice, _ens1Med, _scionPOS, _scionMultiplier)

        # Per-ensemble reporting stake/multiplier (non-zero only when that ensemble flagged the fave)
        _ens1Multiplier = _ens1Stake = _ens2Multiplier = _ens2Stake = 0.0
        if _ens1State in MLB_global.ENS_FLAGGED_STATES and _favePOS != MLB_global.ACTION_NOPLAY:
            _ens1Multiplier = MLB_global.getStakeMultiplier(_hBookiePrice, _vBookiePrice, _favePOS)
            _ens1Stake = MLB_global.getStakeAmount(_stakeMode, _kellyFrac, _hBookiePrice, _ens1Med, _favePOS, _ens1Multiplier)
        if _ens2State in MLB_global.ENS_FLAGGED_STATES and _favePOS != MLB_global.ACTION_NOPLAY:
            _ens2Multiplier = MLB_global.getStakeMultiplier(_hBookiePrice, _vBookiePrice, _favePOS)
            _ens2Stake = MLB_global.getStakeAmount(_stakeMode, _kellyFrac, _hBookiePrice, _ens2Med, _favePOS, _ens2Multiplier)
        predsObj.setPreds_Ens1_PlayPayoutMultiplier(_ens1Multiplier)
        predsObj.setPreds_Ens1_PlayStake(_ens1Stake)
        predsObj.setPreds_Ens2_PlayPayoutMultiplier(_ens2Multiplier)
        predsObj.setPreds_Ens2_PlayStake(_ens2Stake)

        # 4. Update predsObj with the Scion side play
        predsObj.setPreds_Scion_Side_Position(_scionPOS)
        predsObj.setPreds_Scion_Side_Confidence(_scionCONF)
        predsObj.setPreds_Scion_Side_Stars(MLB_global.getNumStars(_starPlay))   # enum -> int
        if _scionPOS != MLB_global.ACTION_NOPLAY:
            predsObj.setPreds_Scion_HProbabilityEdge(_scionEdge)
            predsObj.setPreds_Scion_PlayStake(_scionStake)
            predsObj.setPreds_Scion_PlayPayoutMultiplier(_scionMultiplier)
            _numStars = MLB_global.getNumStars(_starPlay)
            if _scionPOS == MLB_global.ACTION_LINE_HF or _scionPOS == MLB_global.ACTION_LINE_HD:
                predsObj.setPreds_iPos_H_Team_Sname(MLB_global.annotateWithStars(predsObj.getPreds_iPos_H_Team_Sname(), _numStars))
            else:
                predsObj.setPreds_iPos_V_Team_Sname(MLB_global.annotateWithStars(predsObj.getPreds_iPos_V_Team_Sname(), _numStars))
        else:
            predsObj.setPreds_Scion_HProbabilityEdge(0)
            predsObj.setPreds_Scion_PlayStake(0)
            predsObj.setPreds_Scion_PlayPayoutMultiplier(0)
            predsObj.updateiPosNoPlayPrices()

    except Exception:
        print("\ndetermineScionSidePosition(): Unexpected error determining the Scion side position using one or more of the ensembles!\n")
        raise

    return predsObj

def applySideStrategy(sysCfgObj, predsObj, _mupComments=False):
    # Assumption 1: a) system is configured for model (sysCfgObj) b) data has been generated and transformed ready for ML model to process (transGameOnj) c) preds obj holds key game and prediction  infomration to apply probability-based voting strategy
    # Assumption 2: The strategy predictions are stored in relevant predsObj dict e.g. predsObj.preds_ens1_vote_dict{}
    # Assumption 3: _mupsComment has already been written to preds dict and this func will only write it to pred plays dict IF it is not empty
    try:
        #1. Get ensemble positions and store in preds
        predsObj.applyMajorityVote(MLB_global.MODEL_PROBENS1, sysCfgObj)
        predsObj.applyMajorityVote(MLB_global.MODEL_PROBENS2, sysCfgObj)
        #2. Determine and store Scion Position
        predsObj = determineScionSidePosition(sysCfgObj, predsObj, _mupComments)

    except Exception:
        print("\napplySpreadStrategy(): Unexpected error applying the Scion side strategy!\n")
        raise

    return sysCfgObj, predsObj

def _getDTProbabilities(sysCfgObj):
    try:
        #1. Open results file
        #get full path of results file
        _taskFolder = sysCfgObj.getCurrentTaskModelFolder()
        _probsFname = sysCfgObj.getSysDTProbsTXTFname()
        _probsFname = os.path.join(_taskFolder, _probsFname)
        #2. Read in probs one at a time and store in list
        _probList = []
        with open(_probsFname, "r") as _modelProbs_fh:
            for line in _modelProbs_fh:
                for prob in line.split():
                    _probList.append(float(prob))
        _modelProbs_fh.close()
            
    except Exception:
        print("\n_getDTProbabilities(): Unexpected error retrieving decision tree probabilities!\n")
        raise
    
    return _probList

def evaluateModelResponse(task, sysCfgObj, transGameObj, predsObj):
    # This function reads the predictions, re-scales them, and stores them in the preds dictionary associated with predsObj
    # 
    # Assumption 1: a) system is configured for model (sysCfgObj) b) data has been generated and transformed ready for ML model to process (transGameOnj) c) preds obj has key infomration in about the game and is ready to be updated (predsObj) 
    # Assumption 2: The model predictions are stored in sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_result_fname_attrib]
    # Assumption 3: Prices and probabilities must be with respect to the Home team as that is the case for the Bookie line we review
    #
    # Restrictions: Only the following are supported: scaling=Standardization; Model type: RFCLA and Task type: TPROB 
	
    try:
        #1. Open results file
        #get full path of results file
        _taskFolder = sysCfgObj.getCurrentTaskModelFolder()
        _resultFname = sysCfgObj.getCurrentModelOpResultFname()
        _resultFname = os.path.join(_taskFolder, _resultFname)
        _modelResults_fh = open(_resultFname, "r")
        #2. Read in data and close file
        _model_output = _modelResults_fh.readlines()
        _modelResults_fh.close()
        #3.Init key variables
        if len(_model_output) == 0:    
            print("\nError - machine learning model did not produce any response!\n")
            raise Exception
        done=False
        _modelCode = sysCfgObj.getCurrentModelCode()
        _modelType = sysCfgObj.getCurrentModelTaskType()
        _modelTarget = sysCfgObj.getCurrentModelTarget()
        _modelEns = sysCfgObj.getCurrentTaskModelEnsemble()
        _taskRndPred = int(sysCfgObj.getCurrentModelRoundPreds())
        _modelScaleType = sysCfgObj.getCurrentModelIpScaleType()
        _h_bookie_price = predsObj.getPreds_H_Bookie_Bet_Price()
        _h_bookie_prob = predsObj.getPreds_H_Bookie_Bet_Prob()
        _v_bookie_price = predsObj.getPreds_V_Bookie_Bet_Price()
        playPos = MLB_global.ACTION_NOPLAY
        p = 0.0
        _modelProbs=[]
        #4. Process model output
        for index, line in enumerate(_model_output):
            #4.1 convert line string into a list and then iterate across list
            #should be one line with min of one item and max of 4
            tmpList = line.split(MLB_global.MODEL_PRED_SEPARATOR) #first line will be game id, second line will be a profile of activations
            tokenList = [i for i in tmpList if i] #remove any empty strings
            ctr=1
            #4.2 Process each token
            for token in tokenList: #refers to either a game_id or a specific output activation
                if done:
                    break
                token = token.strip('\n')
                if token:
                    if _modelType == MLB_global.ModelTypes.RFCLA.name or _modelType == MLB_global.ModelTypes.XGBCLA.name or MLB_global.ModelTypes.LGBMCLA.name: #RF considered!
                        #4.2.1 Based on the task_type and specific target, convert value to float and then destandardise
                        if task==MLB_global.TaskTypes.TPROB: 
                            _pTargets = sysCfgObj.modelcfg.getSysProbTargets()
                            if _modelTarget not in  _pTargets:
                                print("\nError - only B1 (Home Win Prob) is the only target recognised for probability tasks!")
                                raise Exception
                            else:
                                #get DT model probabilities (intepretation of probabilities will depend on target)
                                _modelProbs = _getDTProbabilities(sysCfgObj) 
                                #descale and round if required
                                sysMinP = float(sysCfgObj.getSysProbMin())
                                sysMaxP = float(sysCfgObj.getSysProbMax())
                                ens = sysCfgObj.getCurrentTaskModelEnsemble() #No need to check this, as only one ensemble is supported.
                                _probThresh = float(sysCfgObj.getSysProbThresh())
                                p = float(token) #prediction (08May24: this is too blunt a value, so we use _modelProbs value)
                                p = transGameObj.limitFeature(p, sysMinP, sysMaxP)
                                if _modelTarget == "B1": #  Only "B1 Home Win" is supported
                                    #prob list struct is [V_Win, H_Win] thus get last item of list for H Win prob
                                    _modelHProbs = round(_modelProbs[-1],2)
                                    playPos = getB1Position(_probThresh, _h_bookie_price, _v_bookie_price, _h_bookie_prob, _modelHProbs)
                                    predsObj.updateVoterDict(_modelEns, _modelCode, _modelHProbs, playPos)
                                    done = True
                                else:#must be G2 Fave_WIN
                                    #prob list struct is [D_Win, F_Win]
                                    _modelProbs = round(_modelProbs[-1],2)
                                    playPos = getG2Position(_probThresh, _h_bookie_price, _v_bookie_price, _modelProbs)
                                    predsObj.updateVoterDict(_modelEns, _modelCode, _modelProbs, playPos)
                                    done = True
                        else:
                            print("\nError - task target unrecognised - cannot postprocess machine learning response!")
                            raise Exception
                    else:
                        ctr+=1
                # are we done?
                if done:                  
                    break
            # We should be done if here
            if done:
                break
            else:
              raise Exception               
            
    except Exception:
        print("\nevaluateModelResponse(): Unexpected error evaluating the response from the machine learning subsystems!\n")
        raise
    
    return done, predsObj

def  _getNNResponse(sysCfgObj):
    # Assumption: we are in the task model folder and all configuration settings are correct and data has been generated, scaled and prepared for the model
    success = False
    try:
        x = sysCfgObj.getSysNNExec()
        y = sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_cfg_fname_attrib]
        commandLine = x + " " + y
        errCode = subprocess.call(commandLine,shell=True)
        if errCode == 0: success = True
        else: raise Exception
        #The NN response will be stored in the filename indicated in sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_result_fname_attrib]
    except Exception:
        print("\n_getNNResponse(): unexpected error initialising or testing neural network subsystem using config file " + str(sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_cfg_fname_attrib]) + " and test file " + str(sysCfgObj.getSysNNIpPatternTxt()) + ".\n")
        raise
    
    return success

def _loadDecisionTree(dtFname):
    return joblib.load(dtFname)

def  _getDTResponse(sysCfgObj, transGameObj):
    # Assumption 1: we are in the task model folder and all configuration settings are correct and data has been generated, scaled and prepared for the model
    # Assumption 2: scikit-learn version 1.2.1 is being used
    success = False
    try:
        #1. Determine tree type
        _isClassification = False
        _modelType = sysCfgObj.getCurrentModelTaskType()
        if _modelType ==  MLB_global.ModelTypes.RFREG.name:
            dt_model = RandomForestRegressor() #default is regressor
        elif _modelType ==  MLB_global.ModelTypes.RFCLA.name:
            dt_model = RandomForestClassifier() #default is classifier
            _isClassification = True
        elif _modelType ==  MLB_global.ModelTypes.XGBREG.name:
            dt_model = xgb.XGBRegressor() #default is regressor
        elif _modelType ==  MLB_global.ModelTypes.XGBCLA.name:
            dt_model = xgb.XGBClassifier() #default is classifier
            _isClassification = True
        elif _modelType ==  MLB_global.ModelTypes.LGBMREG.name:
            dt_model = LGBMRegressor() #default is regressor
        else: #must be lgbm classifier
            dt_model = LGBMClassifier()
            _isClassification = True
        #2. Load model
        _modelFname = sysCfgObj.getCurrentModelTaskCfgFname()
        dt_model = _loadDecisionTree(_modelFname)
        #3. Test model and store predictions
        dt_testdata_df = pd.read_csv(transGameObj.scaled_categvartrans_game_fname_decisiontree_csv, header=0)
        dt_testpreds = dt_model.predict(dt_testdata_df)
        dt_response = np.asarray(dt_testpreds)
        _resFname = sysCfgObj.getCurrentModelOpResultFname()
        np.savetxt(_resFname, dt_response, delimiter=MLB_global.MODEL_PRED_SEPARATOR)
        #4, If classification, also get and storee probabilities
        if _isClassification:
            dt_testprobs = dt_model.predict_proba(dt_testdata_df)
            dt_probs = np.asarray(dt_testprobs)
            _resFname = sysCfgObj.getSysDTProbsTXTFname()
            np.savetxt(_resFname, dt_probs, delimiter=MLB_global.MODEL_PRED_SEPARATOR)
        #signal all ok
        success = True
    except:
        print("\n_getDTResponse(): unexpected error initialising or testing the decision tree subsystem.\n")
        success = False
    
    return success

def getModelResponse(sysCfgObj, transGameObj):
    # This function applies the transformed data to the machine learning model and stores the outcome in the predsObj
    # 
    # Assumption 1: i) system is configured for model (sysCfgObj) ii) data has been generated and transformed ready for ML model to process (transGameOnj) iii) preds obj has key infomration in about the game and is ready to be updated (predsObj) 
    # Assumption 2: After testing, the results will be stored in sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_result_fname_attrib]  
    try:
        #1. Lets change to system task subfolder (whch is where the transformed data is and the model files)
        #backup current wd
        owd = os.getcwd()
        #get task folder and make it current working directory
        taskFolder = sysCfgObj.getCurrentTaskModelFolder()
        os.chdir(taskFolder)
        new_cwd = os.getcwd()
        #2. Remove any previous version of sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_result_fname_attrib] 
        resFname = sysCfgObj.getCurrentModelOpResultFname()
        if os.path.isfile(resFname):
            os.remove(resFname)    
        resFname = sysCfgObj.getSysDTProbsTXTFname()
        if os.path.isfile(resFname):
            os.remove(resFname)    
        #3. Call relevant machine learning model based sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_type_attrib]
        success = True
        _modelType = sysCfgObj.getCurrentModelTaskType()
        if _modelType ==  MLB_global.ModelTypes.NN.name:
            success = _getNNResponse(sysCfgObj)
        else: #must be decision tree response
            success = _getDTResponse(sysCfgObj, transGameObj)
            
        #4. Restore original working directory
        try:
            os.chdir(owd)
            new_cwd = os.getcwd()

        except OSError:
            print("\nError: can no longer access the original working directory!")
            success = False
            raise Exception
        #5. Raise issue if not success
        if not success: raise Exception
            
    except Exception:
        print("\ngetModelResponse(): Unexpected error getting the response from the machine learning subsystems!\n")
        raise
    
    return success

def _getStrengthValueAndCategory(dgenObj, fieldName, stats_df, avgIndex, stdevIndex, flipCategory=False):
    # Note Higher value doesnt necessarily mean good hence the flip option (although I dont like this old sloppy programming and it needs to go)
    _strValue = _avgVal = _stdeVal = 0.0
    _strCateg = ""
    #a. get strength value
    _strValue = float(dgenObj._currentgame_df[fieldName].values[0])
    #b. get stats
    _avgVal = float(stats_df[fieldName].values[avgIndex])
    _stdeVal = float(stats_df[fieldName].values[stdevIndex])
    #c. get strength categ
    _strCateg = MLB_global.calcStrengthCategory(_strValue, _avgVal, _stdeVal, flipCategory)

    return _strValue, _strCateg 

def _annotatePrice(_price, _strCat):
    _strPrice = "{:.1f}".format(float(_price))
    _isElite = MLB_global.isElite(_strCat)
    if _isElite:
        _strPrice  += (" " + MLB_global.TEXT_HIGHLIGHT_DELIMITER2)
    return _strPrice

def updatePredsWithStrPriceCateg(dgenObj, predsObj, sysCfgObj):
    #Assumption 1: Called by updatePredsWithdGEN()
    #Assumption 2: Primitive strength prices have already been populated in predsObj by updatePredsWithdGEN()
     #a. read in stats data
    strCategFname = sysCfgObj.getStrengthStatsPathFname()
    _feature_insample_stats_df = pd.read_csv(strCategFname, header=0)
    _feature_insample_stats_df = _feature_insample_stats_df.fillna(MLB_dbvar.NO_DATA)
    #b. set indices for avg and stdev
    _avgIndex = 1
    _stdevIndex = 4
    _strValue = _strPrice = 0.0
    _strCateg = ""
    #c. Update team-based Offense strength values and categories
    _fieldName = MLB_dbvar.dbvar_V_MenOnBase_Strength_YTD
    _strValue, _strCateg = _getStrengthValueAndCategory(dgenObj, _fieldName, _feature_insample_stats_df, _avgIndex, _stdevIndex)
    predsObj.setPreds_V_Offense_StrengthCategory(_strCateg)
    _strPrice = predsObj.getPreds_V_OffensePrice()
    predsObj.setPreds_V_OffenseStrPrice(_annotatePrice(_strPrice, _strCateg))
    _fieldName = MLB_dbvar.dbvar_H_MenOnBase_Strength_YTD
    _strValue, _strCateg = _getStrengthValueAndCategory(dgenObj, _fieldName, _feature_insample_stats_df, _avgIndex, _stdevIndex)
    predsObj.setPreds_H_Offense_StrengthCategory(_strCateg)
    _strPrice = predsObj.getPreds_H_OffensePrice()
    predsObj.setPreds_H_OffenseStrPrice(_annotatePrice(_strPrice, _strCateg))
    #d. Update team-based Defense/Pitcher strength values and categories
    _fieldName = MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD
    _strValue, _strCateg = _getStrengthValueAndCategory(dgenObj, _fieldName, _feature_insample_stats_df, _avgIndex, _stdevIndex)
    predsObj.setPreds_V_DefenseStrengthCategory(_strCateg)
    _strPrice = predsObj.getPreds_V_DefensePrice()
    predsObj.setPreds_V_DefenseStrPrice(_annotatePrice(_strPrice, _strCateg))
    _fieldName = MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD
    _strValue, _strCateg = _getStrengthValueAndCategory(dgenObj, _fieldName, _feature_insample_stats_df, _avgIndex, _stdevIndex, True)
    predsObj.setPreds_H_DefenseStrengthCategory(_strCateg)
    _strPrice = predsObj.getPreds_H_DefensePrice()
    predsObj.setPreds_H_DefenseStrPrice(_annotatePrice(_strPrice, _strCateg))
    
    return predsObj
    
def updatePredsWithdGEN(dgenObj, predsObj, sysCfgObj):
    # This function updates the predsObj with key dGEN values (we are DIRECTLY accessing dGEN..not good!)
    # Assumption 1: predsObj.initPredsWithMUPS() has already been called and thus info re game lines, ids, team names has already been added to predsObj
    # Assumption 2: dGEN obj contains all of the required data
    #a. Compound Date-based attributes
    predsObj.setPreds_monthweek(dgenObj._currentgame_df[MLB_dbvar.dbvar_G_MonthWeek].values[0])
    #b. Team-based Offense and Defense prices 
    predsObj.setPreds_H_OffensePrice(MLB_global.convertProbtoMoneyLine(dgenObj._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Strength_YTD].values[0]))
    predsObj.setPreds_H_DefensePrice(MLB_global.convertProbtoMoneyLine(1 - dgenObj._currentgame_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD].values[0]))
    predsObj.setPreds_V_OffensePrice(MLB_global.convertProbtoMoneyLine(dgenObj._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Strength_YTD].values[0]))
    predsObj.setPreds_V_DefensePrice(MLB_global.convertProbtoMoneyLine(dgenObj._currentgame_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD].values[0]))
    predsObj = updatePredsWithStrPriceCateg(dgenObj, predsObj, sysCfgObj)
    #c. Initialise prediction vars
    predsObj.setPreds_Ens1_PlayPosition(MLB_global.ACTION_NOPLAY)
    predsObj.setPreds_Ens2_PlayPosition(MLB_global.ACTION_NOPLAY)
    predsObj.setPreds_Scion_Side_Position(MLB_global.ACTION_NOPLAY)    
    
    return predsObj

def processBookieHomeLineSpan(game_positive_span_processed, spanCtr, spanGradations, predsObj, mupsDB, gameData):
    # THIS WILL NEED REDESIGNING TO TAKE ACCOUNT OF HOM_ML AND PROB DIFF FROM ORIGINAL OPENING PROB (SO WE EXTEND THE CLOSE)
    #Assumption 1: gameData stores the original HOM Lines (so we can roll back to it if we span in other direction)
    #Assumption 2: MUPs object stores the revised HOM and VIS Lines
    #Assumption 3: Vis Lines are NOT altered in any way and there it is assumed there is no requirement to do so.
    #0. Init vars
    game_span_processed = False
    bookieHMiddleLine = mupsDB.getCurrentMUPBOOKIEML()
    #1. Check if we dont need to span
    if spanGradations == 0 or spanGradations == MLB_dbvar.NO_DATA or (spanCtr == (math.fabs(spanGradations)) and game_positive_span_processed) :
        game_span_processed = True
        predsObj.resetOPLAdjustedFlag()
    else: #we have span to process
        #2. Check if we've processed positive span
        if spanCtr == (math.fabs(spanGradations)) and not game_positive_span_processed:
            #2a. setup to process positive span
            game_positive_span_processed = True
            spanCtr = 1 #reset ctr
            spanGradations = -1 * spanGradations
            #restore original lines from gameData
            bookieHMiddleLine = gameData.getInitialMiddleLine()
        else:
            #2b. Update counter
            spanCtr += 1
        #3. modify middleline
        if spanGradations < 0:
            _x = bookieHMiddleLine - MLB_global.DEFAULT_SPAN_CENTS
            _xabs = math.fabs(_x)
            if _xabs < 100: #did we go from a +100 to -100 territory
                bookieHMiddleLine = -100 - (100-_xabs)
            else:
                bookieHMiddleLine = _x
        else:
            _x = bookieHMiddleLine + MLB_global.DEFAULT_SPAN_CENTS
            _xabs = math.fabs(_x)
            if _xabs < 100: #did we go from a -100 to +100 territory
                bookieHMiddleLine = 100 + (100-_xabs)
            else:
                bookieHMiddleLine = _x
        #4. update MUPS
        mupsDB.setCurrentMUPBookieML(bookieHMiddleLine)
        #5. update Preds
        predsObj.setOPLAdjustedFlag()
        predsObj.initPredsALL(mupsDB)
        predsObj.addComment(MLB_global.messageOPLAdjusted)
        #6. reset GenerateGameStatus as we need to regen data with new line
        gameData.resetGenerateGameStatus()

    return game_span_processed, game_positive_span_processed, spanCtr, spanGradations, predsObj, mupsDB, gameData

def checkEnoughGames(masterDBObj, mupsDB, sysCfgObj):
    #Assumptions: i) MasterdB populate, ii) MUPs object populated amd current mup details stored in current_mup_dict
    #            iii) system configuration file parsed and cfg for current task/model stored in task_model_settings   
    #Ensure there is sufficient number of games in masterDB for at least one window of data)
    #Check for H team:
    success = masterDBObj.checkEnoughGames(sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_windowsize_attrib], mupsDB.current_mup_dict[mupsDB.mup_hid_attrib])
    if success:
        success = masterDBObj.checkEnoughGames(sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_windowsize_attrib], mupsDB.current_mup_dict[mupsDB.mup_vid_attrib])
    if not success:
        print("MLB_Scion:checkEnoughGames(): Fatal error - insufficent number of available games in the master database to process one or more matchup games using a base window size of "+str(sysCfgObj.task_model_settings[sysCfgObj.cfg_task_model_windowsize_attrib]))
        
    return success


if __name__ == "__main__":
    parser = argparse.ArgumentParser("\nPredicts MLB games given a csv of updated MLB data and a csv containing the team matchups to be predicted.\n")
    parser.add_argument("usrMasterDB_Fname", help="CSV file containing updated MLB database")
    parser.add_argument("usrMatchup_Fname", help="CSV file containing a list of games to be predicted")
    args = parser.parse_args()  # if incorrect operation entered, program will bomb here
    
    try:
        #2. Initialise system
        #2.1 Load and validate master MLB database
        masterDB = MLB_masterdb.scionMASTERDB(cwd, args.usrMasterDB_Fname)
        #2.2 Load and validate the mups file
        mupsDB = MLB_matchup.scionMUP(cwd, args.usrMatchup_Fname)
        #2.3 Load and parse config file
        sysCfg = MLB_cfg.scionCFG(MLB_global.SYSTEM_PATH, MLB_global.CONFIG_FNAME)
        #2.4 Define new preds object
        predsObj = MLB_preds.scionPREDS(preds_out_dir, MLB_global.APP_VER_SHORT)
        #3. Now process each match up in the mups file
        numMups = mupsDB.getNumMUP()
        for mupIndex in range(0, numMups):
            #3.1 Get current mup and store in the mup dict
            mupsDB.getMUPDict(mupIndex)
            #3.2 init gameData. Note:for each mup, we only want to generate the full set of features for the game of interest ONCE and let transformedGameData select what it needs
            # gameData will create a subfolder that will be the new working directory for the dTrans module
            gameData = MLB_dgen.scionDGEN(logs_out_dir, masterDB, mupsDB, sysCfg)
            gameDataWd = gameData.getWorkingDir()
            #3.3 Init preds with current game information from mupsDB
            predsObj.initPredsALL(mupsDB)
            #3.4 Report progress to the user
            per_complete = 0.00
            if numMups > 0:
                per_complete = (mupIndex+1)/numMups*100
            original_hml = predsObj.getPreds_H_Bookie_Bet_Price()
            original_total = float(mupsDB.getCurrentMUPOverClose())
            print("\rGenerating predictions --> game {0} of {1} ({2:.1f}%)".format(mupIndex+1, numMups, per_complete) + " [ {0} {1} @ {2} | HML {3} | TOTAL {4} ]".format(str(mupsDB.current_mup_dict[mupsDB.mup_date_attrib]), 
                                                                                                                                                                    str(mupsDB.current_mup_dict[mupsDB.mup_vis_sname_attrib]), 
                                                                                                                                                                    str(mupsDB.current_mup_dict[mupsDB.mup_hom_sname_attrib]), 
                                                                                                                                                                    original_hml, original_total), end="                   ")
            sys.stdout.flush()
            #3.5 Validate inputs related to opl and opt and also MUP game date and comments
            skip_game = False #assume all is okay with the game until we have evidence to the contrary
            _mupComments = mupsDB.getCurrentMUPComments()
            if _mupComments and str(MLB_dbvar.NO_DATA) not in _mupComments:
                _mupComments = MLB_global.punctuateComment(_mupComments)
                predsObj.addComment(_mupComments) #Add to comments field in preds file
            if int(original_hml) == MLB_dbvar.NO_DATA or int(original_total) == MLB_dbvar.NO_DATA:
                skip_game = True #skip game
                #issue message in preds comments field
                predsObj.addComment(MLB_global.messageGameSkipMissingOPLOPTOVIG)
            #3.6 validate mup date with respect to the Master DB
            if not skip_game:
                if (mupsDB.current_mup_dict[mupsDB.mup_date_attrib] < masterDB.masterdb_oldest_game):
                    skip_game = True #skip game
                    #issue message in preds comments field
                    predsObj.addComment(MLB_global.messageGameSkipDateOutOfRange)    
            #3.7 Validate opl span value and initialise associated variables
            mupsDB.validateCurrentBOOKIESPAN(mupIndex)
            spanGradations = math.ceil(mupsDB.getCurrentMUPBOOKIESPAN()/MLB_global.DEFAULT_SPAN_CENTS) #as SPAN indicates max value in cents eg 100
            game_span_processed = False
            game_positive_span_processed = False #This is first iteration of span
            spanCtr = 0 # 0 refers to game without any mods
            #3.8 Process the current game (including spanning either side of the opl)
            while not game_span_processed:  #only opl is active for span
                if not skip_game:
                    #3.8.1 For each active task type, process each model and get responses 
                    success = True
                    _predId = predsObj._createPredId() #in case line has changed
                    predsObj.setPreds_Id(_predId)
                    predsObj.initVoterDicts()
                    for task in sysCfg.modelcfg._model_task_types_active: 
                        #get sys folder for task
                        task_sys_folder = sysCfg.getTaskFolder(task)
                        #get number of models for current task
                        num_task_models = sysCfg.getNumTaskModels(task)
                        if not num_task_models:
                            print("\nPossible configuration error - the number of task models specified for " + str(task) + " appears to be zero!! Please review the system configuration file " + MLB_global.CONFIG_FNAME + "\n")
                            raise Exception
                        else:
                            #3.8.1.1 For each model, get dictionary of settings and run the model, and store preds
                            model_count = 1
                            while model_count <= num_task_models:
                                #a. get model settings dict (which will be accessed via the dict: sysCfg.task_model_settings and the relevant sysCfg._cfg_task_var eg sysCfg.task_model_settings[sysCfg._cfg_task_round_preds_attrib])
                                sysCfg.getTaskModelSettings(task, model_count)
                                #b. validate model settings and raise exception if it fails
                                sysCfg.validateModelSettings(task, model_count)
                                #c. generate data if has not already been generated
                                if gameData.data_generated == False:    
                                    #1. check if enough games
                                    success = checkEnoughGames(masterDB, mupsDB, sysCfg)
                                    if not success: break
                                    #2. generate game data
                                    sysCfg, predsObj = gameData.generateGameData(mupsDB, sysCfg, predsObj, task, model_count) #data will only be fully generated ONCE per matchup
                                    #3. exit loop and report reason in preds file if skip_game == True otherwise check which we need to round the BPVars from the mups
                                    skip_game = gameData.getSkipGameStatus()
                                    if skip_game:
                                        skip_game_reason = gameData.getSkipGameReason()
                                        predsObj.addComment(MLB_global.messageGameSkipdGEN)
                                        predsObj.addComment(skip_game_reason)
                                        break
                                if not skip_game:
                                    #d. round BP features based on ensemble
                                    bpdp = getEnsBPFeatureDP(sysCfg)
                                    gameData.roundBPFeatures(mupsDB, bpdp)
                                    #e. transform the data (selected features, scaling, categ var processing will be different per model so this func will be called many times per matchup)
                                    transformedGameData = MLB_dtrans.scionDTRANS(gameDataWd, gameData.getGameData(), masterDB, mupsDB, sysCfg)
                                    transformedGameData.transformGameData(task, model_count, sysCfg.getCurrentModelTarget())
                                    #f. get model response and store in sysCfg.task_model_settings[sysCfgObj.cfg_task_model_result_fname_attrib]
                                    success = getModelResponse(sysCfg, transformedGameData)
                                    #g. if all ok, evaluate response and store in predsObj
                                    if not success: break
                                    success, predsObj = evaluateModelResponse(task, sysCfg, transformedGameData, predsObj)
                                #g. if all ok, increment model_count
                                if success:
                                    model_count += 1
                                else:
                                    break
                            if skip_game:
                                break
                    #3.9 Check if processing completed successfully
                    if not success:
                        print("\nError - there appears to be an irregularity with either scaling the data or the Scion machine learning subsystem. Please review the configuration files, including mask files, within the various system subfolders and ensure ALL required files are present and correct.")
                        raise Exception
                    if skip_game:
                        print(" ---> game skipped!")
                        #we still want to store information about skipped games so create id and update verbose dataframe
                        _predId = predsObj._createPredId()
                        predsObj.setPreds_Id(_predId)
                        predsObj.updateVerboseDataFrame() #update verbose dataframe as we still want to keep a record of the skipped game
                        predsObj.updateiPosDataFrame()
                    else:
                        #3.10 Update preds obj with base game data
                        predsObj = updatePredsWithdGEN(gameData, predsObj, sysCfg)
                        #3.11 Apply side strategy 
                        sysCfg, predsObj = applySideStrategy(sysCfg, predsObj, _mupComments)
                        #3.12 Do we have a Totals strategy? If so, run it
                        #if MLB_global.TaskTypes.TTOTAL in sysCfg.modelcfg._model_task_types_active:
                        #    succes, sysCfg, predsObj = applyTotalStrategy(sysCfg, predsObj)
                        #3.13 Update play dict
                        predsObj.updatePredPlayDict(sysCfg, _mupComments)
                        #3.14 Update preds dataframes AND store interim results in case there is a powercut etc
                        predsObj.updateVerboseDataFrame()
                        predsObj.updateiPosDataFrame()
                        predsObj.storeVerbosePreds()
                        predsObj.storeSummaryPreds()
                        predsObj.storePredsAsMarkdown()
                        #3.15 Process span
                        game_span_processed, game_positive_span_processed, spanCtr, spanGradations, predsObj, mupsDB, gameData = processBookieHomeLineSpan(game_positive_span_processed, spanCtr, spanGradations, predsObj, mupsDB, gameData)
                else:
                    #we still want to store information about skipped games so create id and update verbose dataframe
                    _predId = predsObj._createPredId()
                    predsObj.setPreds_Id(_predId)
                    predsObj.updateVerboseDataFrame() #update verbose dataframe as we still want to keep a record of the skipped game
                    predsObj.updateiPosDataFrame()
                    game_span_processed = True #so we can break out of loop as no point continuing
                                  
        #4. finally write results to csv
        predsObj.storeVerbosePreds()
        predsObj.storeSummaryPreds()
        predsObj.setPlayPredsIndices()
        predsObj.storePredsAsMarkdown()
        predsObj.displayPreds()
        predsObj.displayExitMessage()
    
    except Exception:
        print("\n\n"+ MLB_global.APP_NAME + " encountered a fatal error and terminated!")        
        _errorReport()