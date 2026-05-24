# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import time
import pandas as pd
import math
from pathlib import Path
import enum
import shlex #for splitting strings by white space but preserving words within quotes
import MLB_dbvar as MLB_dbvar

# Define key global vars
APP_VER = "V25.08b2 (Standard Edition)"
APP_VER_SHORT = "V25_08b2SE"
APP_NAME = "MLB Scion" 
APP_NAME_SHORT = "Scion" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2025"

MASK_ON = 1
EPSILON = 0.00001 #this is to avoid divide by zero errors with iqr and log calculations; see https://blogs.sas.com/content/iml/2011/04/27/log-transformations-how-to-handle-negative-data-values.html
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
MODEL_PROBENS1 = "V113PM210_2023"
MODEL_PROBENS2 = "V113PM150_2023"
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

#System Messages (NOTE: OPP variables discontinued)
messageGameSkipMissingOPLOPTOVIG = "Game skipped - one or more of the following missing: BOOKIE H MIDDLE LINE, VIG, BOOKIE TOTAL. "
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
messageScionNoVFPlay = "VF plays are NOT supported. "
messageScionEnsNoFavePlay = "Fave plays are disallowed. "
messageScionEns1Play = "Play determined by Ens1 only. "
messageScionEns2Play = "Play determined by Ens2 only. "
messageScionEns1n2Play = "Play determined by Ens1 and Ens2 agreement. "
messageScionEns1n2Disagree = "No play as Ens1 and Ens2 have conflicting positions. "
#Ensemble majority vote and price DISAGREE messages
messageScionEns1PricePlayMismatch = "Ens1 price diagrees with Ens1 majority vote! "
messageScionEns2PricePlayMismatch = "Ens2 price diagrees with Ens2 majority vote! "
#Ensemble price not exceed gap
messageScionEns1GapNotExceeded = "Ens1 price does not exceed cent_gap constraint! "
messageScionEns2GapNotExceeded = "Ens2 price does not exceed cent_gap constraint! "
#Ensemble price outside allowable range
messageScionEns1OutsideRange = "Ens1 price is outside allowable range! "
messageScionEns2OutsideRange = "Ens2 price is outside allowable range! "
#Ensemble ignored due to either outside bookieline constraints 
messageScionEns1BookieOutsideRange = "Ens1 is NoPlay as bookie-line outside range. "
messageScionEns2BookieOutsideRange = "Ens2 is NoPlay as bookie-line outside range. "
messageScionEns2NoFavePlay = "Ens2 is NoPlay as bookie-line outside range for Fave play. "
#Ensemble ignored due to voter agreement threshold not satisfied
messageScionEns1InsufficientVoters = "Ens1 is NoPlay due to insufficient voter agreement. "
messageScionEns2InsufficientVoters = "Ens2 is NoPlay due to insufficient voter agreement. "
#No play due to Null Pitcher
messageScionNoPlayNullPitcher = "NoPlay due to a NULL Starting Pitcher. "
#No play due to H or V price evaluating to an abs value within 0 to 99
messageScionInvalidTeamPrice = "Ens2 is NoPlay due to an invalid bookie team price being calculated. Game skipped! "
#unknown
messageScionEnsUnknownEnsemble = "Unknown ensemble. "
#default DOG play   
messageScionDefaultDogPlay = "Default dog play! "
messageScionNoDefaultDogPlay = "No default dog play as win-loss threshold not met! "
messageScionEns2MajorityVoteDogPlay = "Ens2 Majority Vote Dog play! "

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

def validTeamPrice(teamPrice):
    _teamPrice = abs(teamPrice)
    if _teamPrice >=100:
        return True
    else:
        return False

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
    if y == 0:
        if zeroToMidPoint:
            return 1.0
        return 0.00
    else:
        return float(x / y)

def calcProbRatio(x, y, zeroToMidPoint=False):
    sum = float(x + y)
    if not sum or not x:
        if zeroToMidPoint:
            return 0.5
        return 0.00
    else:
        return float(x / sum)
        
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
    else:
        return 0
        
def annotateWithStars(textStr, numStars):
    _starStr = genStarStr(numStars)
    _starString = _starStr + " " + textStr + " " + _starStr
    return _starString