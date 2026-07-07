# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import time
import pandas as pd
import math
import numpy as np
from pathlib import Path
import enum
import shlex #for splitting strings by white space but preserving words within quotes
import MLB_dbvar as MLB_dbvar

# Define key global vars
APP_VER = "V26.06b (Standard Edition)"
APP_VER_SHORT = "V26_06bSE"
APP_NAME = "MLB Scion" 
APP_NAME_SHORT = "Scion" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2026"

MASK_ON = 1
EPSILON = 0.00001 #this is to avoid divide by zero errors with iqr and log calculations; see https://blogs.sas.com/content/iml/2011/04/27/log-transformations-how-to-handle-negative-data-values.html
FIP_FALLBACK = 4.0          # recent MLB league-average FIP
BULLPEN_ERA_FALLBACK = 4.2  # recent MLB league-average bullpen ERA

# Using enum class create enumerations
class ScaleTypes(enum.Enum):
    NoScale = 0
    MinMax = 1
    Robust = 2 
    Standardize = 3
    Centre = 4
    Log = 5
    LogStandardize = 6
    PowerYeoJohnson = 7

class VariableTypes(enum.Enum): # eg self._vartype = VariableTypes.Continuous_Feature
    Continuous_Feature = 0 #this will also cover N/A or ""
    Categorical_Feature = 1
    Continuous_Target = 2
    Categorical_Target = 3 
    Drop = 4
    Features = 5
    Targets = 6

class MiddleLineTypes(enum.Enum):
    Unknown = 0
    Prob = 1
    Money = 2

class StakeTypes(enum.Enum):
    Unknown = 0
    Flat = 1
    Kelly = 2

class ModelTypes(enum.Enum):
    NN = 0
    OLS = 1
    RFREG = 2 
    RFCLA = 3
    CATBREG = 4
    CATBCLA = 5
    LGBMREG = 6
    LGBMCLA = 7
    XGBREG = 8
    XGBCLA = 9

class TaskTypes(enum.Enum):
    TRUN = 0
    TTOTAL = 1
    TPROB = 2

class ModelConfidenceTypes(enum.Enum):
    ZEROSTAR = 0
    ONESTAR = 1
    TWOSTAR = 2 
    THREESTAR = 3
    FOURSTAR = 4
    FIVESTAR = 5
    SIXSTAR = 6
    SEVENSTAR = 7

class EnsembleProbabilityTypes(enum.Enum):
    Default = 0
    MedianAllVoters = 1
    AvgMajorityVotersOnly = 2

GAME_ID_INDEX = 0  # relates to index of value in main dictionary
GAME_THRESHOLD = 5 # different to NBA (which is 3)
H_OR_V_INDEX = 1  # relates to index of value in main dictionary
HOME = 0
VISITOR = 1
HOME_VISITOR = 2 # this is for Preds comments field when both home and visitor have new starting pitchers (with no historical stats)
YES = 1
MAYBE = 0
NO = -1
TEAM_UNKNOWN = -1
MASK_ACTIVE_VAR = 1
SLEEPLEN = 3
VIS_VIG_PRICE_PERC = 5
OPT_MEDIAN = 8.5
DEFAULT_SPAN_CENTS = 5
DEFAULT_FLAT_STAKE_UNITS = 1.0
DEFAULT_FRACT_KELLY = 0.25
BOOKIEPROBADJVAL = 0.15
BOOKIETOTADJVAL = 3.0
AVG_H = "H"
AVG_V = "V"
G_ATTRIB = "G_" #for dGEN closing prob avgs
DATE_F = '%Y%m%d'
WINDOW_START_DATE_OFFSET = 360 #in days
DEFAULT_WINDOW_SIZE = 10
# Output folder roots — read from environment variables set by run_scion.py /
# run_experiment.py. If not set (e.g. running MLB_Scion.py directly), fall
# back to the original hidden-folder names relative to cwd.
LOG_FOLDER_ROOTNAME   = os.environ.get("MLB_SCION_LOGS_DIR",  ".MLB_scion_logs")
LOG_SUBFOLDER_ROOTNAME = ".logs"
PREDS_FOLDER_ROOTNAME  = os.environ.get("MLB_SCION_PREDS_DIR", ".MLB_scion_preds")
PREDS_SUBFOLDER_ROOTNAME = ".preds"
SYSTEM_PATH = ""  #replaced by env var value from the YAML
DESKTOP_PATH = "~/Desktop/"
CONFIG_FNAME = "MLB_Scion_CFG.txt"
LOG_FNAME_STEM = "MLB_Scion_log_"
_FNAME_CSV_EXT = ".csv"
_FNAME_TXT_EXT = ".txt"
ACTION_PLAY = "Play"
ACTION_NOPLAY = "No Play"
ACTION_NOPLAYPUSH = "No Play (PUSH)"
ACTION_NOPLAYGAP = "No Play (FAILED GAP CRITERION)"
ACTION_PLAYGAP = "PLAY SCION (PASSED GAP CRITERION)"
ACTION_GAPSUPPRESS_YES_SYSGAP = "Yes - system gap applied"
ACTION_YES = "Yes"
ACTION_NO = "No"
ACTION_NA = "N/A"
ACTION_TOTAL_U = "Under"
ACTION_TOTAL_O = "Over"
ACTION_LINE_HF = "HomFave"
ACTION_LINE_HD = "HomDog"
ACTION_LINE_VF = "VisFave"
ACTION_LINE_VD = "VisDog"
ACTION_LINE_POS = "+"
ACTION_LINE_NEG = "-"
ACTION_LINE_ZERO = "0"
MODEL_PRED_SEPARATOR = " "
MODEL_PROBENS1 = "STATSONLY_PM150"
MODEL_PROBENS2 = "LEANSTATSONLY_PM150"
MODEL_TOTALENS = "TOTALENS"
MODEL_PROBENS = [MODEL_PROBENS1, MODEL_PROBENS2]
HISTORY_LENGTHS = [5,10, 20, 365]
MIDDLEINE_PROB = "MLprob"
MIDDLEINE_PRICE = "MLprice"
ELITE_LIST = ["Strong", "Very Strong", "Extremely Strong", "Invincible!"]
DF_COL_TYPE_INT = "int"
DF_COL_TYPE_FLOAT = "float"
DF_COL_TYPE_STR = "str"
DF_COL_TYPES = [DF_COL_TYPE_INT,DF_COL_TYPE_FLOAT,DF_COL_TYPE_STR]
MLB_MASTER_OLDESTGAME_DATE = datetime.today()-timedelta(1) #default is yesterday
MLB_MASTER_RECENTGAME_DATE = datetime.now() #default is now
HELP_FNAME = "HELP_"+ str(MLB_MASTER_RECENTGAME_DATE.date()) + APP_NAME + ".txt"
MIN_BIT_VAL = "-1"
MAX_BIT_VAL = "1"
TEXT_HIGHLIGHT_DELIMITER1 = "*"
TEXT_HIGHLIGHT_DELIMITER2 = "#"
TEXT_HIGHLIGHT_DELIMITER3 = "^"
DEFAULT_CONF_PROB = 0.50
NN_DP_PRECISION = 9
DROP_ATTRIB = 2

# ─────────────────────────────────────────────────────────────────────────────
# V26.06b (Standard Edition) play-strategy specification constants
# ─────────────────────────────────────────────────────────────────────────────
# A model (ensemble) is FLAGGED only when it backs the FAVE side (as defined by
# the de-vigged CLOSING line), its probability-points gap over book_mid clears
# the edge threshold, AND its side-vote share clears a vote gate:
#   FLAG        : vote >= PROB_FLAG_VOTE_THRESHOLD  (0.83, from config agree thr)
#   STRONG-FLAG : vote >= PROB_STRONG_VOTE_THRESHOLD (0.93)
# The FLAG (0.83) gate is read from the config (getSysProb[STATSONLY]AgreeThresh);
# the STRONG (0.93) gate is a fixed strategy constant defined here.
PROB_STRONG_VOTE_THRESHOLD = 0.93

# Ensemble states (PDF §9.2)
ENS_STATE_SILENT = "SILENT"
ENS_STATE_FLAG   = "FLAG"
ENS_STATE_STRONG = "STRONG-FLAG"
ENS_FLAGGED_STATES = [ENS_STATE_FLAG, ENS_STATE_STRONG]

# Home-dog closing-line price tiers (PDF §9.3 / §9.5 note 3). U-shaped, NOT
# monotone: the middle band is the weak one. hom_clml is the home CLOSING money
# line (positive for a home dog).
#   hom_clml <  +100                        -> 5 star
#   HOMEDOG_PRICE_TIER_LOW <= hom_clml <= HOMEDOG_PRICE_TIER_HIGH -> 3 star
#   hom_clml >= +120                        -> 5 star
HOMEDOG_PRICE_TIER_LOW  = 100
HOMEDOG_PRICE_TIER_HIGH = 119

#System Messages (NOTE: OPP variables discontinued)
messageGameSkipMissingOPLOPTOVIG = "Game skipped - Bookie line information missing. "
messageGameDataSuccess = "Game data generated. "
messageGameSkipDateOutOfRange = "Game skipped - The date range for the matchup is outside of the limits of the master database. "
messageGameSkipMissingGame = "Game skipped - cannot find the game data for this game. "
messageGameSkipNotEnoughDataHOME = "Game skipped - insufficient data for the home team in the database to generate statistics for the game. "
messageGameSkipNotEnoughDataVIS = "Game skipped - insufficient data for the visitor team in the database to generate statistics for the game. "
messageGameSkipNotEnoughHVDataHOME = "Game skipped - insufficient HV data within date range for home team in the database to generate statistics for the game. "
messageGameSkipNotEnoughHVDataVIS = "Game skipped - insufficient HV data  within date range for visitor team in the database to generate statistics for the game. "
messageGameSkipUnrecogGId = "Game skipped - game id cannot be located in the master database. "
messageGameSkipUnrecogGId = "Game skipped - game id cannot be located in the master database. "
messageGameSkipdGEN = "Game skipped - scionDGEN() did not have the required data to fully process the game. "
messageOPLAdjusted = "Moneyline is a SPAN value. "
messageGameHomePitcherNoData = "H_SP is Null, team-based avg used. "
messageGameVisPitcherNoData = "V_SP is Null, team-based avg used. "
#Ensemble play determination messages
messageScionNoVFPlay = "VF plays are disallowed. "
messageScionNoStrategyPlay = "No play due to strategy constraints. "
messageScionEnsNoFavePlay = "Fave plays are disallowed. "
messageScionEns1NoDogPlay = "StatOnlyEns only dog plays disallowed. "
messageScionEns1Play = "Play determined by StatOnlyEns only. "
messageScionEns2Play = "Play determined by LeanStatOnlyEns only. "
messageScionEns2PlayEns1Disagree = "Play determined by LeanStatOnlyEns when it disagrees with StatOnlyEns. "
messageScionEns1n2Play = "Play determined by StatOnlyEns and LeanStatOnlyEns agreement. "
messageScionEns1n2Disagree = "No play as StatOnlyEns and LeanStatOnlyEns disagree. "
#Ensemble majority vote and price DISAGREE messages
messageScionEns1PricePlayMismatch = "StatOnlyEns price diagrees with StatOnlyEns majority vote! "
messageScionEns2PricePlayMismatch = "LeanStatOnlyEns price diagrees with LeanStatOnlyEns majority vote! "
#Ensemble probability-based restrictions
messageScionEns1GapNotExceeded = "StatOnlyEns probability points gap does not exceed threshold (no edge found)! "
messageScionEns1GapAgainstVote = "StatOnlyEns probability points gap exceeded but against its vote! "
messageScionEns2GapNotExceeded = "LeanStatOnlyEns probability points gap does not exceed threshold (no edge found)! "
messageScionEns2GapAgainstVote = "LeanStatOnlyEns probability points gap exceeded but against its vote! "
#Ensemble price outside allowable range
messageScionEns1OutsideRange = "StatOnlyEns price is outside allowable range! "
messageScionEns2OutsideRange = "LeanStatOnlyEns price is outside allowable range! "
#Ensemble ignored due to either outside bookieline constraints 
messageScionEns1BookieOutsideRange = "StatOnlyEns is NoPlay as bookie-line outside range. "
messageScionEns2BookieOutsideRange = "LeanStatOnlyEns is NoPlay as bookie-line outside range. "
messageScionEns2NoFavePlay = "LeanStatOnlyEns is NoPlay as bookie-line outside range for Fave play. "
#Ensemble ignored due to voter agreement threshold not satisfied
messageScionEns1InsufficientVoters = "StatOnlyEns is NoPlay due to insufficient voter agreement. "
messageScionEns2InsufficientVoters = "LeanStatOnlyEns is NoPlay due to insufficient voter agreement. "
#No play due to Null Pitcher
messageScionNullHSP = "NoPlay as H_SP is Null. "
messageScionNullVSP = "NoPlay as V_SP is Null. "
messageScionNullBothSP = "NoPlay as BOTH H_SP and V_SP are Null. "
#No play due to H or V price evaluating to an abs value within 0 to 99
messageScionInvalidTeamPrice = "LeanStatOnlyEns is NoPlay due to an invalid bookie team price being calculated. Game skipped! "
#unknown
messageScionEnsUnknownEnsemble = "Unknown ensemble. "
#default DOG play   
messageScionDefaultDogPlay = "Default dog play! "
messageScionNoDefaultDogPlay = "No default dog play as win-loss threshold not met! "
messageScionEns2MajorityVoteDogPlay = "LeanStatOnlyEns Majority Vote Dog play! "
messageScionRiskMinNoPlay = "No play due to risk minimisation constraints. "
messageScionRiskMinVisDogNoPlay = "No play - split-silent VisDog skipped to reduce risk. "
messageScionEns1DogChoice = "Dog play determined by StatOnlyEns. "
messageScionEns2DogChoice = "Dog play determined by LeanStatOnlyEns. "

# ─────────────────────────────────────────────────────────────────────────────
# V26.06b (Standard Edition) play-strategy messages
# ENS1 = StatsOnly (V127); ENS2 = LeanStatsOnly (V129)
# ─────────────────────────────────────────────────────────────────────────────
# Per-ensemble state comments
messageScionEns1StrongFlag  = "StatOnlyEns STRONG-FLAGs the fave (gap>=thr, vote>=0.93). "
messageScionEns1Flag        = "StatOnlyEns FLAGs the fave (gap>=thr, vote>=0.83). "
messageScionEns1SilentDog   = "StatOnlyEns SILENT - backs the dog."
messageScionEns1SilentGate  = "StatOnlyEns SILENT - on the fave but below the gap/vote gates. "
messageScionEns2StrongFlag  = "LeanStatOnlyEns STRONG-FLAGs the fave (gap>=thr, vote>=0.93). "
messageScionEns2Flag        = "LeanStatOnlyEns FLAGs the fave (gap>=thr, vote>=0.83). "
messageScionEns2SilentDog   = "LeanStatOnlyEns SILENT as it backs the dog. "
messageScionEns2SilentGate  = "LeanStatOnlyEns SILENT as backs fave but below gap/vote gates. "
# Decision-row comments (PDF §9.3 / §9.4). Exactly one fires per game.
messageScionConsensusStrong = "Both ensembles STRONG-FLAG the fave (7-star consensus) play. "
messageScionConsensusFlag   = "Both ensembles FLAG the fave (not BOTH strong so 5-star consensus play). "
messageScionSingleHFOverride = "Single ensemble FLAGs the HomFave (3-star play. "
messageScionSingleVFNoOverride = "Single ensemble FLAGs the VisFave BUT not enough to override default HomDog (1-star) "
messageScionDefaultVisDog   = "No ensemble flag: default 1-star VisDog play. "
messageScionDefaultHomeDog  = "No ensemble flag: default HomDog play based on bookie price tier. "
# Registry mapping (ensemble id, state/reason) -> comment, so per-ensemble comment
# selection is a single lookup rather than an if/else branch (PDF section 9.2).
# ENS1 = StatsOnly (V127); ENS2 = LeanStatsOnly (V129).
messageScionEnsStateComment = {
    MODEL_PROBENS1: {
        ENS_STATE_STRONG: messageScionEns1StrongFlag,
        ENS_STATE_FLAG:   messageScionEns1Flag,
        "silent_gate":    messageScionEns1SilentGate,
        "silent_dog":     messageScionEns1SilentDog,
    },
    MODEL_PROBENS2: {
        ENS_STATE_STRONG: messageScionEns2StrongFlag,
        ENS_STATE_FLAG:   messageScionEns2Flag,
        "silent_gate":    messageScionEns2SilentGate,
        "silent_dog":     messageScionEns2SilentDog,
    },
}

def setColType(df, col_list, col_type):
    try:
        if col_type not in DF_COL_TYPES:
            print("\nMLB_global.setColType: unrecognised column data type given!")
            raise Exception
        else:
            for col in col_list:
                if col in df.columns: #might not be the case if col_list is a superset of df.columns
                    df[col] = df[col].astype(col_type)
    except Exception:
        raise
    return df

def getModelTypeName(typeNo):
    return ModelTypes(typeNo).name

def hasModelTypeValue(usrValue):
    validValues = set(item.value for item in ModelTypes)
    return usrValue in validValues

def hasModelTypeName(usrName):
    validNames = set(item.name for item in ModelTypes)
    return usrName in validNames

def getTaskTypeName(taskNo):
    return TaskTypes(taskNo).name

def hasTaskTypeValue(usrValue):
    validValues = set(item.value for item in TaskTypes)
    return usrValue in validValues

def hasTaskTypeName(usrName):
    validNames = set(item.name for item in TaskTypes)
    return usrName in validNames

def getStakeTypeName(stakeNo):
    return StakeTypes(stakeNo).name

def hasStakeTypeValue(usrValue):
    validValues = set(item.value for item in StakeTypes)
    return usrValue in validValues

def hasStakeTypeName(usrName):
    validNames = set(item.name for item in StakeTypes)
    return usrName in validNames

def isOppSide(price1, price2):
    if (price1 < 0 and price2 > 0) or (price1 > 0 and price2 < 0):
        return True
    else:
        return False

def convertProbtoMoneyLine(probValue):
    probValue = float(probValue)
    if probValue == 0: probValue = 0.5
    elif probValue == 1: probValue = 0.9
    if probValue >= 0.5:
        return round((probValue / (1-probValue))*-100,1)
    else:
        return round(((1-probValue) / probValue)*100,1)

def convertMoneyLinetoProb(moneylineValue):
    if int(moneylineValue) == MLB_dbvar.NO_DATA:
        return MLB_dbvar.NO_DATA
    moneylineValue = float(moneylineValue)
    absOdds = math.fabs(moneylineValue)
    if moneylineValue < 0:
        return round((absOdds / (100+absOdds)),6)
    else:
        return round(( 100 / (100+absOdds)),6)

#This logic is as per the MLB strategy spreadsheet
# IF(OR(AND(modelPrice<0,bookiePrice>0),AND(modelPrice>0,bookiePrice<0)),ABS(modelPrice-bookiePrice)-100,ABS(modelPrice-bookiePrice)))
def calcPriceDiff(bookiePrice, modelPrice):
    priceDiff = 0.0
    if (modelPrice < 0 and bookiePrice > 0) or (modelPrice > 0 and bookiePrice < 0):
        priceDiff = math.fabs(modelPrice-bookiePrice)-100
    else:
        priceDiff = math.fabs(modelPrice-bookiePrice)
    return round(priceDiff,2)

#This formula is as per the MLB strategy spreadsheet
# =IF(HOMPRICE<=0,IF(HOMPRICE=-100,100,IF(ABS(HOMPRICE+(VIG/100*ABS(HOMPRICE)))<100,100,ABS(HOMPRICE+(VIG/100*ABS(HOMPRICE))))),-1*HOMPRICE-(VIG/100*ABS(HOMPRICE)))
def CalcVisPrice(homePrice, percVig):
    _visPrice = 0.0
    _absVisPrice = math.fabs(homePrice+(percVig/100*math.fabs(homePrice)))
    if homePrice <= 0:
        if homePrice == -100:
            _visPrice = 100
        elif _absVisPrice < 100:
            _visPrice = 100
        else:
            _visPrice = _absVisPrice
    else:
        _visPrice = -1 * homePrice - (percVig/100*math.fabs(homePrice))
    return _visPrice

def calcTeamPrice(midPrice, vig, h_or_v):
    price = 100.0
    if h_or_v == HOME:
        if midPrice < 0: #HomeFave
            price = midPrice - vig
        else: #HomeDog
            _priceIdx = midPrice - 100
            if vig > _priceIdx:
                _diff = vig - _priceIdx
                price = -100 - _diff
            else:
                price = midPrice - vig
    else:
        if midPrice < 0 or midPrice == price: #VisDog
            _priceIdx = math.fabs(midPrice) - 100
            if vig > _priceIdx:
                _diff = vig - _priceIdx
                price = -100 - _diff
            else:
                price = math.fabs(midPrice) - vig    
        else: #VisFave
            price = -1 * (midPrice + vig)

    return price

#28th Jul 2021: homopline and homclosline are middle lines and require ovig and cvig for us to be able to translate into a price/prob for home and vis accordingly. 
# The following two func therefore do this conversion with a middle line prob and middle line price respectively
# Eg If middleline = +205 and vig = 5 then home price = +200 and vis price = -210
#    If middleline is -205 and vig is 5 then home price = -210 and vis price = +200
#    If middleLine is - and vig > priceIndex then Vis price is also negative based on vig - index
#    If middleLine is +/-100 then both H and V have same -ve price based on vig i.e 100/04 = -104 for H and V
def ConvertMiddleLineToPrices(mLine, centVig, mLineType=None):
    if int(mLine) == MLB_dbvar.NO_DATA or int(centVig) == MLB_dbvar.NO_DATA:
        _visPrice = MLB_dbvar.NO_DATA
        _homePrice = MLB_dbvar.NO_DATA
    else:    
        _middleLinePrice = mLine
        if mLineType == MiddleLineTypes.Prob.value:
            _middleLinePrice = convertProbtoMoneyLine(float(mLine))
        _visPrice = 0.0
        _homePrice = 0.0
        _homePrice = calcTeamPrice(_middleLinePrice, centVig, HOME)
        _visPrice = calcTeamPrice(_middleLinePrice, centVig, VISITOR)
        if _homePrice == 100 and _visPrice == 100:
            _visPrice = -100

    return _homePrice, _visPrice

def validTeamPrice(teamPrice):
    _teamPrice = abs(teamPrice)
    if _teamPrice >=100:
        return True
    else:
        return False

def calcDeVigProb(bookieHProb, bookieVProb, h_or_v):
    _totalProb = bookieHProb + bookieVProb
    deVigProb = 0.5
    if _totalProb != 0:
        if h_or_v == HOME:
            deVigProb = bookieHProb / _totalProb
        else:
            deVigProb = bookieVProb / _totalProb

    return deVigProb

def punctuateComment(strComment):
    _punct = ". "
    if strComment:
        strComment = str(strComment) + _punct
    return strComment

def convertNumpytoNative(numpy_var):
    native_var = getattr(numpy_var, "tolist", lambda x=numpy_var: x)()

    return native_var

#function for subtract one list from another
def filterList(full_list, excludes):
    s = set(excludes)
    return (x for x in full_list if x not in s)

def roundModelPred(number):
    return float(round(number * 2.0) / 2.0)

def checkMatch(teamA_ld, teamB_ld):
    if teamA_ld == teamB_ld:
        return  MLB_dbvar.G_WIN
    else:
        return  MLB_dbvar.G_LOSE

def calcRunEfficiency(runsgained, hits, runs2b, homeruns):
    denominator = float(hits + runs2b +(homeruns*3))
    if denominator>0:
        return float(runsgained / denominator)
    else:
        return 0.0

def calcMOB(hits, walks, runs2b, homeruns, hitsbypitch, errors, doubleplays):
    return float(hits + walks + runs2b + homeruns + hitsbypitch - (errors + doubleplays))

def calcTotalBases(hits, runs2b, runs3b, homeruns):
    return float(hits+runs2b+(2*runs3b)+(3*homeruns))



def calcRatio(x, y, zeroToMidPoint=False):
    """x / y, with fallback for near-zero denominators.

    Returns:
      - x / y  when |y| >= 1e-6
      - 1.0    when |y| < 1e-6 and zeroToMidPoint=True
      - 0.00   when |y| < 1e-6 and zeroToMidPoint=False

    The |y| < 1e-6 zero-tolerance (tightened from the original `if y == 0`)
    catches floating-point residue that the exact-equality check missed.

    SEMANTIC LIMITATION - read before adding new call sites:

    When |y| < 1e-6 and |x| > 0, the true value of x/y is mathematically
    +/- infinity, but this function returns 0.00 (or 1.0). That fallback
    is INFORMATION-LOSING and silently wrong for some call sites:

      - Run_Pythag (FIXED at call site, not here): using this function for
        R = calcRatio(Runs_Gained, Runs_Allowed) returns 0 when RA=0,
        which mislabels a perfectly-dominant team (no runs allowed) as
        worst-Pythag (Pythag=0). Cascades into Pythag_Luck_Factor as a
        false 'maximally lucky' signal. FIX: use closed-form
            Pythag = RG^2 / (RG^2 + RA^2)
        directly, bypassing calcRatio entirely. Well-defined as 1.0
        when RA=0 and RG>0. See pythag.py in the data-quality pipeline
        for the drop-in pattern.

      - Other MEDIUM-risk call sites (rare edge cases, no semantic
        inversion like Pythag had - left to call-site fixes when
        convenient):
            EarnedRunAvg          = ER / IP  (IP=0 with ER>0 -> 0)
            MenOnBase_Efficiency  = Runs / MOB  (MOB=0 with Runs>0 -> 0)
            MenOnBaseTBRatio      = TotalBases / MOB
            WalkStrikeoutRatio    = Walks / Strikeouts  (K=0 with BB>0 -> 0)

    For LOW-risk call sites (NP, OutsPitched, AtBats, accumulated career
    totals etc.) the denominator is never plausibly zero in real data,
    so the fallback semantics are immaterial.
    """
    # If either input is NaN, the share is undefined, so return the neutral
    if pd.isna(x) or pd.isna(y):
        if zeroToMidPoint:
            return 1.0
        return 0
    if abs(y) < 1e-6:
        if zeroToMidPoint:
            return 1.0
        return 0.00
    return float(x / y)

def calcProbRatio(x, y, zeroToMidPoint=False):
    """X/(X+Y) share with three-layer fallback when undefined.

    Fallback layers (any one triggers the neutral 0.5 / 0.0 return):
      1. Either input is NaN.
      2. |X+Y| < 1e-6 (exact cancellation or FP residue from signed inputs).
      3. Result < 0 or > 1 (signed inputs partially cancelled but |X+Y| > 1e-6,
         producing a mathematically-valid but non-share value). Required for
         signed centred-at-zero variables like Pythag_Luck_Factor and any other
         feature whose H and V values can have opposite sign with similar
         magnitude. Without this guard, X/(X+Y) can land anywhere in (-inf, inf)
         when sum nearly cancels - previously seen at -1000 and +1551 in
         G_VHRatio_Pythag_Luck_Factor data.

    For non-negative inputs (counts, totals, magnitudes), layer 3 never fires:
    X/(X+Y) is mathematically guaranteed to be in [0,1]. So this guard is a
    no-op for the common case and a safety net for the signed case.
    """
    # Layer 1: NaN input -> neutral share
    if pd.isna(x) or pd.isna(y):
        return 0.5
    # Layer 2: near-zero denominator (catches cancellation residue too)
    denom = float(x + y)
    if abs(denom) < 1e-6:
        if zeroToMidPoint:
            return 0.5          # neutral share - H and V indistinguishable
        return 0.00
    ratio = float(x / denom)
    # Layer 3: out-of-[0,1] result -> sign-conflict between H and V
    if ratio < 0.0 or ratio > 1.0:
        if zeroToMidPoint:
            return 0.5
        return 0.00
    return ratio

def divByZeroCatch(numerator, denominator, min_denominator=1e-6):
    """Safe division. Returns NaN if denominator is too close to
    zero or if inputs/result are not finite."""
    if pd.isna(numerator) or pd.isna(denominator):
        return np.nan
    if abs(denominator) < min_denominator:
        return np.nan
    result = numerator / denominator
    if not np.isfinite(result):
        return np.nan
    return result


def computeFIP(hr_allowed, walks_allowed, hbp_allowed, k_gained,
               outs_pitched, min_ip=5.0):
    """Compute Fielding-Independent Pitching with defensive guards.

    Returns the formula result when inputs are valid and IP >= min_ip.
    Otherwise returns FIP_FALLBACK (module-level constant, default 4.0)
    rather than NaN, since dGEN runs standalone without the imputer
    pipeline and every output cell must be a usable numeric value.

    min_ip default 5.0 suits 10G windows; lower it (e.g. 3.0) for the
    smaller YTD_HV home-only sample. To tune the fallback value globally,
    edit FIP_FALLBACK at the top of this module.
    """
    inputs = [hr_allowed, walks_allowed, hbp_allowed, k_gained, outs_pitched]
    if any(pd.isna(v) for v in inputs):
        return FIP_FALLBACK
    ip = outs_pitched / 3.0
    if ip < min_ip:
        return FIP_FALLBACK
    fip = (13 * hr_allowed + 3 * (walks_allowed + hbp_allowed)
           - 2 * k_gained) / ip + 3.12
    if not np.isfinite(fip):
        return FIP_FALLBACK
    return fip

def computeBullpenERA(team_er, sp_er, bullpen_outs, min_outs=3,
                     era_cap=27.0):
    """Compute approximate bullpen ERA with defensive guards.

    Returns a value in [0, era_cap] in all cases. When inputs are invalid
    (NaN, low IP, non-finite result), returns BULLPEN_ERA_FALLBACK (module-
    level constant, default 4.2) rather than NaN. dGEN runs standalone here
    without the imputer pipeline, so every output cell must be a usable
    numeric value.

    Why the floor + cap (added v5.7):

    The arithmetic bullpen_er = team_er - sp_er pairs a TEAM-window stat
    with an SP-window stat over different game sets, so sp_er > team_er
    is entirely possible and produces negative bullpen_er. Floor at 0
    (physical: bullpen cannot allow negative earned runs). The x27
    multiplier inflates small-window noise into wild outliers; cap at
    27.0 (per-inning physical ceiling) suppresses small-sample noise.

    To tune the fallback value globally, edit BULLPEN_ERA_FALLBACK at
    the top of this module.
    """
    if any(pd.isna(v) for v in [team_er, sp_er, bullpen_outs]):
        return BULLPEN_ERA_FALLBACK
    if bullpen_outs < min_outs:
        return BULLPEN_ERA_FALLBACK
    # Floor: bullpen cannot allow negative earned runs.
    bullpen_er = max(0.0, team_er - sp_er)
    era = 27.0 * bullpen_er / bullpen_outs
    if not np.isfinite(era):
        return BULLPEN_ERA_FALLBACK
    # Cap: per-inning physical ceiling.
    if era > era_cap:
        era = era_cap
    return era

def calcMedian(probList):
    sortedList = sorted(probList)
    listLen = len(sortedList)
    if listLen % 2 == 0:
        median = (sortedList[listLen//2 - 1] + sortedList[listLen//2]) / 2
    else:
        median = sortedList[listLen//2]
    return median   

def calcAddFeatures(x, y):
    if x == MLB_dbvar.NO_DATA or y == MLB_dbvar.NO_DATA:
        return 0.00
    else:
        return float(x + y)

def calcSubFeatures(x, y):
    if x == MLB_dbvar.NO_DATA or y == MLB_dbvar.NO_DATA:
        return 0.00
    else:
        return float(x - y)

def floorNumtoZero(num):
    if num == MLB_dbvar.NO_DATA:
        return 0.00
    elif num < 0:
        return 0.0
    else:
        return num

def limitProb0109(prob):
    if prob < 0.1:
        return 0.1
    elif prob > 0.9:
        return 0.9
    else:
        return prob

def isElite(strCategory):
    return strCategory in ELITE_LIST

def genStarStr(numStars):
    _starStr = ""
    if numStars > 0:
        for x in range(numStars):
            _starStr += "*"
    return _starStr

def annotateWithStars(textStr, numStars):
    _starStr = genStarStr(numStars)
    _starString = _starStr + " " + textStr + " " + _starStr
    return _starString

def calcStrengthCategory(strVal, insampleAVG, insampleSTDEV, flipCATEGORIES=False):
    #This function returns the strength category of strength value given the insample average and stdev.
    #06 May 2024: flipCATEGORIES allows categories to be flipped such that high +ve values can be bad and high -ve values good
    #             eg H_MenOnBase_Allowed_20G versus H_MenOnBase_20G
    strCateg = "Unknown"
    _absStrVal = math.fabs(strVal)
    insampleAVG = float(insampleAVG)
    insampleSTDEV = float(insampleSTDEV)
    if (_absStrVal <= insampleAVG): 
        if not flipCATEGORIES: #Avg to Trash
            if(_absStrVal >= insampleAVG-(1*insampleSTDEV)):
                strCateg = "Average"
            elif(_absStrVal > insampleAVG-(2*insampleSTDEV) and _absStrVal < insampleAVG-(1*insampleSTDEV)):
                strCateg = "Weak"
            elif(_absStrVal > insampleAVG-(2.5*insampleSTDEV) and _absStrVal <= insampleAVG-(2*insampleSTDEV)):
                strCateg = "Very Weak"
            elif(_absStrVal > insampleAVG-(3*insampleSTDEV) and _absStrVal <= insampleAVG-(2.5*insampleSTDEV)):
                strCateg = "Extremely Weak"
            else:
                strCateg = "Trash"
        else:
            # avg to invincible
            if(_absStrVal >= insampleAVG-(1*insampleSTDEV)):
                strCateg = "Average"
            elif(_absStrVal > insampleAVG-(2*insampleSTDEV) and _absStrVal < insampleAVG-(1*insampleSTDEV)):
                strCateg = "Strong"
            elif(_absStrVal > insampleAVG-(2.5*insampleSTDEV) and _absStrVal <= insampleAVG-(2*insampleSTDEV)):
                strCateg = "Very Strong"
            elif(_absStrVal > insampleAVG-(3*insampleSTDEV) and _absStrVal <= insampleAVG-(2.5*insampleSTDEV)):
                strCateg = "Extremely Strong"
            else:
                strCateg = "Invincible"
    else:
        if not flipCATEGORIES: # average to invincible
            if(_absStrVal <= insampleAVG+(1*insampleSTDEV)):
                strCateg = "Average"
            elif(_absStrVal > insampleAVG+(1*insampleSTDEV) and _absStrVal < insampleAVG+(2*insampleSTDEV)):
                strCateg = "Strong"
            elif(_absStrVal >= insampleAVG+(2*insampleSTDEV) and _absStrVal < insampleAVG+(2.5*insampleSTDEV)):
                strCateg = "Very Strong"            
            elif(_absStrVal >= insampleAVG+(2.5*insampleSTDEV) and _absStrVal < insampleAVG+(3*insampleSTDEV)):
                strCateg = "Extremely Strong"
            else:
                strCateg = "Invincible!"
        else:  #Avg to Trash
            if(_absStrVal <= insampleAVG+(1*insampleSTDEV)):
                strCateg = "Average"
            elif(_absStrVal > insampleAVG+(1*insampleSTDEV) and _absStrVal < insampleAVG+(2*insampleSTDEV)):
                strCateg = "Weak"
            elif(_absStrVal >= insampleAVG+(2*insampleSTDEV) and _absStrVal < insampleAVG+(2.5*insampleSTDEV)):
                strCateg = "Very Weak"            
            elif(_absStrVal >= insampleAVG+(2.5*insampleSTDEV) and _absStrVal < insampleAVG+(3*insampleSTDEV)):
                strCateg = "Extremely Weak"
            else:
                strCateg = "Trash"

    return strCateg

def getNumStars(numStars):
    # V26.06b: the ModelConfidenceTypes enum value IS the star count, so 6 and 7
    # are now covered (the 1/3/5/7 stake scale needs SEVENSTAR).
    if numStars == ModelConfidenceTypes.ONESTAR:
        return 1
    elif numStars == ModelConfidenceTypes.TWOSTAR:
        return 2
    elif numStars == ModelConfidenceTypes.THREESTAR:
        return 3
    elif numStars == ModelConfidenceTypes.FOURSTAR:
        return 4
    elif numStars == ModelConfidenceTypes.FIVESTAR:
        return 5
    elif numStars == ModelConfidenceTypes.SIXSTAR:
        return 6
    elif numStars == ModelConfidenceTypes.SEVENSTAR:
        return 7
    else:
        return 0

def calcPercBookieHold(bookieHProb, bookieVProb):
    _probSum = bookieHProb + bookieVProb
    if _probSum == 0:
        return 0
    else:
        return (1 - (1/(_probSum)))

def calcKellyStake(bookiePrice, ensPrice):
    _kellyStake = 0.0
    if bookiePrice != MLB_dbvar.NODATA and ensPrice != MLB_dbvar.NO_DATA:
        _bookieProb = convertMoneyLinetoProb(bookiePrice)
        _ensProb = convertMoneyLinetoProb(ensPrice)
        if _bookieProb != 0:
            _kellyStake = (_ensProb - _bookieProb) / _bookieProb
    return round(_kellyStake, 3)

def getStakeMultiplier(hBookiePrice, vBookiePrice, ensMajorityVote):
    _stakeMultiplier = 1.0
    if hBookiePrice != MLB_dbvar.NO_DATA and vBookiePrice != MLB_dbvar.NO_DATA:
        if ensMajorityVote ==  ACTION_LINE_HF or ensMajorityVote ==  ACTION_LINE_HD:
            if hBookiePrice < 0:
                _stakeMultiplier = 100/abs(hBookiePrice)
            else:
                _stakeMultiplier = hBookiePrice/100
        else:
            if vBookiePrice < 0:
                _stakeMultiplier = 100/abs(vBookiePrice)
            else:
                _stakeMultiplier = vBookiePrice/100
    return round(_stakeMultiplier, 3)

def getStakeAmount(stakeMode, kellyFrac, hBookiePrice, ensHProb, ensPos, stakeMultiplier):
    _stakeAmount = 0.0
    if stakeMode == StakeTypes.Flat.value:
        _stakeAmount = DEFAULT_FLAT_STAKE_UNITS
    elif stakeMode == StakeTypes.Kelly.value:
        _kellyStake = 0.0
        if ensPos == ACTION_LINE_HF or ensPos == ACTION_LINE_HD:
            _kellyStake = kellyFrac * max(0, ensHProb - (1-ensHProb)/stakeMultiplier)
            _kellyStake = round(_kellyStake, 5)
        else:
            _kellyStake = kellyFrac * max(0, (1-ensHProb) - ensHProb/stakeMultiplier)
            _kellyStake = round(_kellyStake, 5)
    else:
        print("\nMLB_Scion_Globals.getStakeAmount: Unrecognised stake model!")
        raise Exception

    return _stakeAmount 