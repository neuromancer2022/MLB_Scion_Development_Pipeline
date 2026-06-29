# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import copy #for copying dicts
import time
import math
import numpy as np
import pandas as pd
from pathlib import Path

import MLB_dbvar as MLB_dbvar
import MLB_globals as MLB_global
import MLB_dGEN_Log as MLB_log
import MLB_dGEN_MasterDB as MLB_masterdb
import MLB_dGEN_GTP as MLB_gtp

####### Although the matchup file may contain more than the above subset of columns, only the matchup_CSV_Attribs subset will be read in
# args.usrWindowSize, args.usrHistoryWithinSeason, args.usrHistoryDecay
class scionDGEN:
    def __init__(self, root_wd, masterDBobj, gtpObj, windowSize, historyWithinSeason, historyDecay):
        #path and static filenames
        self.dgen_root_wd = root_wd
        self._dgen_timestamp = datetime.today()
        self._foldername = MLB_global.DATA_FOLDER_NAME + self._dgen_timestamp.strftime('%Y%m%d') #includes subfolder
        self.dgen_wd = os.path.join(root_wd, self._foldername) #working directory where files or subfolders will be created and stored
        #control flags
        self._skip_game = False
        self._skip_game_reason = ""
        self._use_base_attrib = True
        self._is_G_base_attrib = False
        self._is_Avg = True
        self._is_HV = False
        self._data_generated = False
        self._history_within_season = int(historyWithinSeason)
        self._history_decay = int(historyDecay)
        #dataframes
        self._gameprimitives_df = pd.DataFrame #stores a single game retrieved from the master DB based on G_Id, this is used for obtaining key base-level game data seeded by dBASE
        self._currentgame_df = pd.DataFrame #stores a single game whose key game/team info and statistics are determined by the primitives in self._gameprimitives_df
        self._processedgames_df = pd.DataFrame() #storeds each processed ._currentgame_df (as we will be using pd.append(), see https://stackoverflow.com/questions/54112105/typeerror-append-missing-1-required-positional-argument-other)
        #log, data and gtp objs
        self.masterDB = masterDBobj
        self.gtpDB = gtpObj
        self.dgenLOG = MLB_log.dGENLOG(self.dgen_root_wd, self.dgen_wd, self.gtpDB.getGTPFnameNOExt()) # log file in root
        #dynamic fnames (change for each game)
        self._game_fname_csv = ""
        self._home_log_fname_txt = ""
        self._vis_log_fname_txt = ""
        self._results_fname_stem = MLB_global.RESULTS_FNAME_STEM + str(self.gtpDB.getGTPFnameNOExt()) + "_" + self._dgen_timestamp.strftime('%Y%m%d%H%M%S') + ".csv"
        self._processed_games_fname_csv = ""
        self._processed_games_subfolder_fname_csv = ""
        self._dgen_log_fname_csv = ""
        self._dgen_log_subfolder_fname_csv = ""
        #file handles
        self._home_logfile_fh = ""
        self._vis_logfile_fh = ""
        #game dicts
        self._all_historical_games = {}
        self._historical_games = {}
        self._ordered_historical_games = {}
        self._lookahead_games = {}
        #game info from gtpDB
        self._game_id = 0
        self._home_id = 0
        self._vis_id = 0
        self._game_date = self._dgen_timestamp
        #historical strength values for H and V (according to average across window_size num of games)
        self._homeAvgStrength = MLB_dbvar.STRENGTH_WINDOW_AVG
        self._visAvgStrength = MLB_dbvar.STRENGTH_WINDOW_AVG
        #input window and dates
        self._window_HVstatus = "" #For a window-size of historical games, this stores the pattern of H or V status flags from most recent to last eg if at home for 5 games immediately before current game then HHHHHVVVVV
        self._window_size = int(windowSize)
        self._g5_window_size = 5 #last 5 games
        self._g20_window_size = 20 #we want at most 20
        self._ytd_window_size = MLB_global.DEFAULT_WINDOW_SIZE #as we dont know how many games will be in the window
        self._pitcher_window_size = MLB_global.DEFAULT_WINDOW_SIZE
        self._pitcher_games_ytd = 0
        self._pitcher_games_all = 0
        self._game_date_minusone = self._game_date - timedelta(days=1) #capture previous day date so we can search for past team games in DB
        self._game_date_plusone = self._game_date + timedelta(days=1) #capture next day date so we can search for future team games in DB
        self._window_start_date = datetime.now()
        self._window_start_date = self._window_start_date.date()
        self._window_end_date = pd.Timestamp(self.masterDB.masterdb_oldest_game) #refers to the earliest game in the database
        self._window_end_date = self._window_end_date.date()
        self._season_start_date = self._window_end_date
        self._season_end_date = self._game_date + relativedelta(day=1,months=(self._monthsToAdd(self._game_date)))
        self._season_end_date = self._season_end_date.date()
        self._ytd_window_end_date = self._game_date_minusone 
        self._ytd_window_start_date = self._game_date + relativedelta(years=-1) #1 year back
        self._g5_window_end_date = self._game_date_minusone 
        self._g5_window_start_date = self._game_date + relativedelta(years=-15) #15 year back
        self._g20_window_end_date = self._game_date_minusone 
        self._g20_window_start_date = self._game_date + relativedelta(years=-15) #15 years back
        #create DGEN subfolder
        self._createDGENFolder()
        self._initProcessedGameDF()
        
    def _createDGENFolder(self):
        #Attempts to create a log folder so that files can be stored there
        #An exception will be raised if the folder cannot be created
        try:
            if not self._data_generated:
                os.makedirs(self.dgen_wd, exist_ok=True)    
        except:
            print("\nscionDGEN._createDGENFolder(): unexpected error creating the system folder " + str(self.dgen_wd))
            raise
    
    def _initProcessedGameDF(self):
        #processedgames_df needs to have same structure as master_df BUT no data
        self._processedgames_df = self.masterDB.copyMasterStructure(False)
        
    def getWorkingDir(self):
        return self.dgen_wd
    
    def _openTeamLogFiles(self):
        try:
            #create filenames    
            self._home_log_fname_txt = MLB_global.DATA_FNAME_STEM + "H_" + str(self._home_id) + "_" + self._game_date.strftime('%Y%m%d') + ".txt"
            self._home_log_fname_txt = os.path.join(self.dgen_wd, self._home_log_fname_txt)
            self._vis_log_fname_txt =  MLB_global.DATA_FNAME_STEM + "V_" + str(self._vis_id) + "_" + self._game_date.strftime('%Y%m%d') + ".txt"
            self._vis_log_fname_txt = os.path.join(self.dgen_wd, self._vis_log_fname_txt)
            #file handles
            self._home_logfile_fh = open(self._home_log_fname_txt, "wt")
            self._vis_logfile_fh = open(self._vis_log_fname_txt, "wt")
            
        except Exception:
            print("\nscionDGEN.openTeamLogFiles(): unexpected error when creating and opening system log files for the Home or Visitor team.\n")
            raise
        
    def _closeTeamLogFiles(self):
        #Assumption:  files were open successfully and have not been closed
        try:
            self._home_logfile_fh.close()
            self._vis_logfile_fh.close()
            
        except Exception:
            print("\nscionDGEN.closeTeamLogFiles(): unexpected error when attempting to close the system log files for the Home or Visitor team.\n")
            raise
    
    def getGameData(self):
        return self._currentgame_df.copy()
    
    def getCurrentGTPData(self):
        #Assumption:  the current GTP has been loaded into the dict
        self._game_id = self.gtpDB.getCurrentGTPGameId() #we will retrieve the game from the masterDB based on the game_id
        self._game_date = self.gtpDB.getCurrentGTPDate()
        self._home_id = self.gtpDB.getCurrentGTPHomeId()
        self._vis_id = self.gtpDB.getCurrentGTPVisId()
        #store in log
        self.dgenLOG.setCurrentGameId(self._game_id)
        self.dgenLOG.setCurrentGameDate(self._game_date)
        self.dgenLOG.setCurrentGameVisId(self._vis_id)
        self.dgenLOG.setCurrentGameHomeId(self._home_id)  
        self.updateGameInstances(0)

    def getGamePrimitiveData(self, gameId):
        #Assumption: game exists!!!
        self._gameprimitives_df = self.masterDB.getGame(gameId)

    def getSkipGameStatus(self):
        return self.skip_game
    
    def getSkipGameReason(self):
        return self._skip_game_reason

    def setSkipGameReason(self, reason):
        self._skip_game_reason = str(reason)
        
    def setGameStatusUpdate(self, updateComment):
        self.dgenLOG.addStatusUpdate(updateComment)
        
    def updateGameLogDataFrame(self):
        self.dgenLOG.updateLogDataFrame()
        self.dgenLOG.initLogDict()
        
    def storeGameLogData(self):
        self.dgenLOG.storeLogData()

    def _getCurrent_GameDate(self):
        return self._game_date
    def _getCurrent_H_OML(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0]    
    def _getCurrent_H_CML(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0]    
    def _getCurrent_V_OML(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0]    
    def _getCurrent_V_CML(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0]    
    def _getCurrentMoneyLineDelta(self,h_or_v):
        if h_or_v == MLB_global.HOME:
            return self._currentgame_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0] - self._currentgame_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0]
        else:
            return self._currentgame_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0] - self._currentgame_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0]
    def _getCurrentCLT(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOver].values[0]
    def _getCurrentCLTML(self):
        return self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOverLine].values[0]  

    def _setCurrentPrimitives(self, gameId):
        #initialises key primitives in _currentgame_df based on that stored in _gameprimitives_df
        self.getGamePrimitiveData(gameId)
        self._currentgame_df = self.masterDB.copyMasterStructure()
        self._currentgame_df[MLB_dbvar.dbvar_G_Id].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Id].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Date].values[0] = self._game_date = self._gameprimitives_df[MLB_dbvar.dbvar_G_Date].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Day].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Day].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Month].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Month].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Year].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Year].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_MonthWeek].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_MonthWeek].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0] = self._home_id = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_Id].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0] = self._vis_id = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_Id].values[0]
        self._updateVisDistanceTravelledAttrib() #to ensure we have values for V_Nextx_DistanceTravelled when echoing opponent
        self._currentgame_df[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Total].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_Runs].values[0] + self._gameprimitives_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_NightGame].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_NightGame].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Opening_TotalOver].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Opening_TotalOver].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Opening_TotalOverLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Opening_TotalOverLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOver].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Closing_TotalOver].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOverLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Closing_TotalOverLine].values[0]
        #get and set home and vis opening prices
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_OpeningProbabilityLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_OpeningProbabilityLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_H_CLL_OPL_Prob_Diff].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_H_CLL_OPL_Prob_Diff].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_OpeningProbabilityLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_OpeningProbabilityLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_V_CLL_OPL_Prob_Diff].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_V_CLL_OPL_Prob_Diff].values[0]
        #set ivan vars
        self._currentgame_df[MLB_dbvar.dbvar_G_Ivan_BP_DefenseProbability].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Ivan_BP_DefenseProbability].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Ivan_BP_OffenseProbability].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Ivan_BP_OffenseProbability].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Ivan_BP_NullProbability].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Ivan_BP_NullProbability].values[0]
        self._currentgame_df[MLB_dbvar.dbvar_G_Ivan_BP_NoLineProbability].values[0] = self._gameprimitives_df[MLB_dbvar.dbvar_G_Ivan_BP_NoLineProbability].values[0]
    
    def _setCurrentBookieMoneyLine(self, h_or_v, moneyLine):
        if h_or_v == MLB_global.HOME:
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0] = float(moneyLine)
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_Probability].values[0] = float(MLB_global.convertMoneyLinetoProb(moneyLine))
        else:
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0] = float(moneyLine)
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_Probability].values[0] = float(MLB_global.convertMoneyLinetoProb(moneyLine))

    def _setCurrentBookieTotal(self, totalValue):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0] = float(totalValue)

    def _setCurrentBookieTotalLine(self, totalMoneyLine):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOverLine].values[0] = float(totalMoneyLine)

    def _storeCurrentGameData(self):
        #Assumption: Data has been geenrated and categorical variables dealt with BEFORE this function is called
        # Task information must be provided
        try:
            #create filenames
            now = datetime.today()
            self._game_fname_csv = MLB_global.DATA_FNAME_STEM + "_H_" + str(self._home_id) + "_V_" + str(self._vis_id) + "_" + self._game_date.strftime('%Y%m%d') + "_RAWDATA_" + now.strftime('%Y%m%d%H%M%S') + ".csv"
            self._game_fname_csv = os.path.join(self.dgen_wd, self._game_fname_csv)
            #store data
            self._currentgame_df.to_csv(self._game_fname_csv, index=False)
            
        except Exception:
            print("\nscionDGEN.storeCurrentGameData(): unexpected error storing generated game data to csv files.\n")
            raise
    
    def _orderTeamGameDict(self, game_dict, in_reverse=False):
        #Assumption:  games have been stored in relevant team dict self._ordered_historical_games, self._ordered_historical_games and self._ordered_opp_games
        #Returns sorted dict
        try:
            tmp_dict = copy.deepcopy(game_dict) #so we dont change the original
            tmp_dict = OrderedDict(sorted(tmp_dict.items(), reverse=in_reverse))

        except Exception:
            print("\nscionDGEN.orderTeamGameDict(): unexpected error when sorting a game dictionary.\n")
            raise
        
        return tmp_dict
    
    def _initGenDicts(self):
        try:
            # Assumption: Data has been read in and appropriate vars initialised    
            self._all_historical_games = {}
            self._historical_games = {}
            self._ordered_historical_games = {}
            self._lookahead_games = {}
            self._ytd_window_size = 0
            self._pitcher_window_size = 0
            self._window_HVstatus = "" #For a window-size of historical games, this stores the pattern of H or V status flags from most recent to last eg if at home for 5 games immediately before current game then HHHHHVVVVV
        except:
            print("\nscionDGEN._initGenDicts(): unexpected error initialising dGEN dictionaries\n")
            raise

    def _initGenDates(self):
        try:
            # Assumption: Data has been read in and appropriate vars initialised
            self._game_date_minusone = self._game_date - timedelta(days=1) #capture previous day date so we can search for past team games in DB
            self._game_date_plusone = self._game_date + timedelta(days=1) #capture next day date so we can search for future team games in DB
            self._window_start_date = datetime.now()
            self._window_start_date = self._window_start_date.date()
            self._window_end_date = pd.Timestamp(self.masterDB.masterdb_oldest_game) #refers to the earliest game in the database
            self._window_end_date = self._window_end_date.date()
            self._season_start_date = self._window_end_date
            self._season_end_date = self._game_date + relativedelta(day=1,months=(self._monthsToAdd(self._game_date)))
            self._ytd_window_end_date = self._g20_window_end_date = self._game_date_minusone #do not want to include date of actual game 
            self._ytd_window_start_date = self._game_date + relativedelta(years=-1) #1 year back
            self._g20_window_start_date = self._game_date + relativedelta(years=-15) #15 years back
            self._g5_window_end_date = self._game_date_minusone 
            self._g5_window_start_date = self._game_date + relativedelta(years=-15) #15 year back
            if self._ytd_window_start_date < self._window_end_date:
                self._ytd_window_start_date = self._window_end_date
            if self._g20_window_start_date < self._window_end_date:
                self._g20_window_start_date = self._window_end_date    
            if self._g5_window_start_date < self._window_end_date:
                self._g5_window_start_date = self._window_end_date 
        except:
            print("\nscionDGEN._initGenDates(): unexpected error initialising different window dates for the data generation process\n")
            raise

    def _initGameData(self):
        #Assumption 1: 
        try:
            # If game exists, get a new Master dataframe with a single row initialised to game primitives and NO_DATA
            _gameExists = self.masterDB.gameExists(self._game_id)
            if _gameExists:
                self._skip_game = False
                self._setCurrentPrimitives(self._game_id)
                self._setBookieProbMLToOPL()
                self._setBookieTotalToOPT()
            else:
                self._skip_game = True
                self.updateLogStatus(MLB_global.messageGameSkipMissingGame)    
        except Exception:
            print("\nscionDGEN._initGameData(): unexpected error when initialising the dataframe for the current game.\n")
            raise
        
    def _monthsToSubtract(self, game_date):
        """ returns an integer representing the number of months to substract from the given game date to arrive at the starting month of the season

        game_date = date of game (as type timestamp.date() )

        """
        game_month = game_date.month
        months_to_subtract = 0
        if game_month <  MLB_dbvar.MONTH_START:
            months_to_subtract = (12 - MLB_dbvar.MONTH_START)+game_month+1
        else:
            months_to_subtract = game_month-MLB_dbvar.MONTH_START
        
        return months_to_subtract 

    def _monthsToAdd(self, game_date):
        """ returns an integer representing the number of months to add from the given game date to arrive at the ENDing month of the season

        game_date = date of game (as type timestamp.date() )

        """
        game_month = game_date.month
        months_to_add = 0
        if game_month >  MLB_dbvar.MONTH_END:
            months_to_add = 12 - game_month+MLB_dbvar.MONTH_END+1 #we want to go one extra month beyond end date
        else:
            months_to_add = MLB_dbvar.MONTH_END-game_month+1
        
        return months_to_add
    
    def _setSeasonStartDate(self):
        #a. Calc season start date for current matchup
        _month_delta = self._monthsToSubtract(self._game_date)
        self._season_start_date = self._game_date+relativedelta(day=1,months=(-1*_month_delta))
            
    def _applyHistoryWithinSeason(self):
        try:
            self._setSeasonStartDate()
            # Assumption: Data has been read in and appropriate vars initialised
            if self._ytd_window_start_date < self._season_start_date:
                self._ytd_window_start_date = self._season_start_date
            #b. update dictionaries
            self._historical_games = self.masterDB.getTeamGames(self._game_date, self._home_id, None, self._season_start_date, self._game_date_minusone)
            self._all_historical_games = self.masterDB.getTeamGames(self._game_date, self._home_id) #for lookback
            self._historical_games = self.masterDB.getTeamGames(self._game_date, self._vis_id, None, self._season_start_date, self._game_date_minusone)
            self._all_historical_games = self.masterDB.getTeamGames(self._game_date, self._vis_id) #for lookback
        except:
            print("\nscionDGEN._applyHistoryWithinSeason(): unexpected error initialising date variables and dictionaries with games starting from the beginning of the season w.r.t current matchup game.\n")
            raise
             
    def _getWindowData(self, fileHandle, windowSize, ordered_game_dict, full_ordered_game_dict):
        try:
            # Assumption 1: Data has been read in, appropriate vars initialised and file handle opened
            # Assumption 2: self._currentgame_df has been initialised via a call to initGameData
            # Assumption 3: windowSize will either be self._window_size, self._g5_window_size or self._g20_window_size
            # Assumption 4: ALL team games (for team of interest) appear in ordered_game_dict
            # This function will: a) remove game_date from ordered_dict b) remove any items beyond self._window_size c) changes self._window_start and self_.end_date vars c) updates the original dicts provided as input d) populate self._window_HVstatus
            
            # Dicts are automatically pass by REFERENCE so originals will change (without making deep copies)
            # See: (see https://stackoverflow.com/questions/2465921/how-to-copy-a-dictionary-and-only-edit-the-copy) and https://stackoverflow.com/questions/15078519/python-dictionary-passed-as-an-input-to-a-function-acts-like-a-global-in-that-fu
            # and https://stackoverflow.com/questions/33791285/is-it-possible-to-create-a-dictionary-inside-a-function-using-python  
            #1. Initialise variables
            game_ctr = 1
            keys_to_delete = []
            self._window_HVstatus = ""
            gameDatePresent = False
            if self._history_within_season == MLB_global.YES:
                self._setSeasonStartDate()
            #2. Traverse ordered dict and store details of only those games within the input window or current season
            #We need to capture the actual start_date for the beginning of the window
            for k, v in ordered_game_dict.items():
                if k==self._game_date or game_ctr > windowSize or (self._history_within_season == MLB_global.YES and k < self._season_start_date): 
                    keys_to_delete.append(k)
                    if k==self._game_date:
                        gameDatePresent = True
                else: #we have a valid game within the window
                    if game_ctr == 1: #this is the most recent date in the historical game window (as dict is in desc order)
                        self._window_end_date = k #store most recent game in the window 
                        fileHandle.write("\nFor an historical input window of " + str(windowSize) + " games, the following available games have been retrieved from the master database: ")
                    else:
                        if self._history_within_season == MLB_global.YES:
                            if k >= self._season_start_date: #We need to capture the start date
                                self._window_start_date = k
                        else:
                            self._window_start_date = k #this will eventually store the last/oldest game in the window
                    #Display valid list of games                        
                    fileHandle.write("\nGame " + str(k) + " : [" + str(int(v[MLB_global.GAME_ID_INDEX])) + ", " + str(int(v[MLB_global.H_OR_V_INDEX])) + "]")
                    game_ctr+=1
                    #Update self._window_HVstatus
                    status =  int(v[MLB_global.H_OR_V_INDEX])
                    if status == MLB_global.HOME:
                        self._window_HVstatus += "H"
                    else:
                        self._window_HVstatus += "V"
            #3. Store results to log file
            gamesFound = game_ctr-1
            if self._history_within_season == MLB_global.YES:
                fileHandle.write("\nNOTE: the beginning of the input window is hard limited to the beginning of the season relating to the game being predicted")
            fileHandle.write("\n\nNumber of historical games found : " + str(gamesFound))
            fileHandle.write("\nWindow Start Date : " + self._window_start_date.strftime('%Y-%m-%d'))
            fileHandle.write("\nWindow End Date : " + self._window_end_date.strftime('%Y-%m-%d'))
            fileHandle.write("\n\nVERIFICATION NOTE: The date of the game to be predicted is " + self._game_date.strftime('%Y-%m-%d') + " and should NOT appear in the input window above and thus not included in any team-level statistical calculations.")
            #4. del game date AND dates of games outside the window
            for key in keys_to_delete:
                del ordered_game_dict[key]
            #5. if gameDatePresent, del JUST the game date from full_ordered_game_dict
            if gameDatePresent:
                del full_ordered_game_dict[self._game_date]
            #6. if insufficient games found then set skip_game to True
            if gamesFound < MLB_global.GAME_THRESHOLD:
                self._skip_game = True
        except:
            print("\nscionDGEN._getWindowData(): unexpected error reading an input window of data from the team game dicts.\n")
            raise
    
    def _enoughGames(self):
        #Assumption 1: Scion game threshold is set in MLB_global
        #Assumption 2: relevant H or V game dict has been populated prior to calling this func
        #a, get len of dict
        _numGames = len(self._historical_games)
        #b. check whether H or V and then check relevant dict against threshold and return True if ok, otherwise False
        if (_numGames < MLB_global.GAME_THRESHOLD):
            return False
        else:
            return True 

    def _checkIsOverBookieTotal(self, game_df):
        is_over = MLB_dbvar.G_TIE
        actual_total = float(game_df[MLB_dbvar.dbvar_G_V_Runs].values[0] + game_df[MLB_dbvar.dbvar_G_H_Runs].values[0])
        bt = float(game_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0])
        if actual_total > bt:
            is_over = MLB_dbvar.G_WIN
        else:
            if actual_total < bt:
                is_over = MLB_dbvar.G_LOSE
        return is_over
    
    def _checkIsOverBookieCLT(self, game_df):
        #This is for prev games hence CLL rather than Bookie_Total (which can be OPT, intermediate, CLT)
        is_over = MLB_dbvar.G_TIE
        actual_total = float(game_df[MLB_dbvar.dbvar_G_V_Runs].values[0] + game_df[MLB_dbvar.dbvar_G_H_Runs].values[0])
        clt = float(game_df[MLB_dbvar.dbvar_G_Closing_TotalOver].values[0])
        if actual_total > clt:
            is_over = MLB_dbvar.G_WIN
        else:
            if actual_total < clt:
                is_over = MLB_dbvar.G_LOSE
        return is_over

    def _populateContiguousGameFields(self, h_or_v):
        """
        #This function counts the number of contiguous H or Vs in self._window_HVstatus from left to right.
        # Assumption 1: The left most symbols refer to most recent games
        # Assumption 2: Once status changes then the count stops eg HHHVHVHVVH results in hContigCount=3, vContigCount=0....and vice versa if states were inverted
        # Assumption 3: self._currentgame_df is the game to be updated
        
        """
        #initialise count variables
        hContigCount = 0
        vContigCount = 0

        if len(self._window_HVstatus) > 0: 
            #we have data to store, so iterate over it
            ctr = 1
            prevSym = ""
            for currSym in self._window_HVstatus:
                if currSym == "H" and not vContigCount:
                    hContigCount += 1
                else:
                    if currSym == "V" and not hContigCount:
                        vContigCount += 1
                if ctr == 1:
                    prevSym = currSym
                    ctr+=1
                else:
                    if currSym != prevSym:
                        break
                    else:
                        ctr+=1

        if (h_or_v == MLB_global.HOME): 
            self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesH].values[0] = hContigCount
            self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesV].values[0] = vContigCount
        else:
            self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesH].values[0] = hContigCount
            self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesV].values[0] = vContigCount
            
    def _populateLookbackFields(self, home_or_vis, fileHandle):
        """
        #This is a huge inefficient function that needs significant redesign BUT not now
        # Assumption 1: The historical games will be taken from copies of self._all_historical_home/vis_games dicts which consist of ALL available historical game data (not limited by window) and list MUST be populated BEFORE this func is called 
        # Assumption 2: self._currentgame_df is the game to be updated
        # NOTE 1:Uniqueness is based on Opp_Team_Id AND whether team of interest was at Home or a Visitor.#Format: <Team_Id>_<Home_VIS>
        # NOTE 2:Lookbacks are taken from self._all_ordered_historical_home/vis_game_dict and thus are NOT constrained by the window size. 
        # NOTE 3:Strength values of team and opponent are SHALLOW i.e. based on spot values and not averages of say X games before the historical game in question
        
        """
        fileHandle.write("\n\n*--- GETTING LOOKBACK GAME DATA...")
        fileHandle.write("\n*--- Searching for three 'unique' look back opponents...where uniqueness is based on opponent Team_ID AND whether current team was at Home or a Visitor...")
        
        #init vars
        lookback1_found = False
        lookback2_found = False
        lookback3_found = False
        opponent1_team_ID = MLB_dbvar.NO_DATA
        opponent1_game_ID = 0
        opponent2_team_ID = MLB_dbvar.NO_DATA
        opponent2_game_ID = 0
        opponent3_team_ID = MLB_dbvar.NO_DATA
        opponent3_game_ID = 0
        strength_game_ID = 0
        team_id = MLB_dbvar.NO_DATA
        opponent1_game_date = self._game_date
        lookback_summary = ""
        lookback_weighted_strength = 0.0
        sum_opponent_strength = 0.0
        productsum_team_strength = 0.0
        historical_games = {} #we will make deep copys of H or V dict so we do not inadvertantly alter them (which we wont but good to be safe)
              
        #Get Team ID and conf div of main team
        if (home_or_vis == MLB_global.HOME): 
            team_id = int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0]) #distance travelled, confdiv, sameconfdiv
            historical_games = copy.deepcopy(self._all_historical_games)     
        else:
            team_id = int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0]) #distance travelled, confdiv, sameconfdiv
            historical_games = copy.deepcopy(self._all_historical_games)

        team_LeagueDiv = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(team_id)
        team_Div = MLB_dbvar.TEAM_DIVISION.get(team_id)
        #1. Add details for the most recent previous opponent (use this also as default for opponents 2 and 3 just in case we have no unique opponents within window
        #get details of first (most recent previous opponent)
        for k_lb, v_lb in historical_games.items(): 
            #retrieve game by G_Id so there will only be ONE game
            lookback_game = self.masterDB.retrieveGames(MLB_dbvar.dbvar_G_Id, v_lb[MLB_global.GAME_ID_INDEX])
            #process it
            if not lookback1_found:
                lookback_summary = ""
                opponent1_game_ID = int(v_lb[MLB_global.GAME_ID_INDEX])
                fileHandle.write("\nfound the FIRST previous opponent from game " +str(opponent1_game_ID))
                lookback1_found = True
                opponent1_game_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #ONLY for opponent_1 for calc Days_Rest
                is_over = self._checkIsOverBookieCLT(lookback_game)
                if (home_or_vis == MLB_global.HOME): #process first lookback game
                    if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME: 
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Home].values[0] = MLB_dbvar.YES_HOME
                        lookback_summary += "H_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_DistanceTravelled].values[0] = 0.0
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] 
                        #did team win?
                        if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_WIN
                            lookback_summary += "W_"
                        else:
                            lookback_summary += "L_"
                            if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_LOSE
                            else:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_TIE
                    else:
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Home].values[0] = MLB_dbvar.NOT_HOME
                        lookback_summary += "V_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0])
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] 
                        #did team win?
                        if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                            lookback_summary += "W_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_WIN
                        else:
                            lookback_summary += "L_"
                            if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_LOSE
                            else:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0] = MLB_dbvar.G_TIE
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get( self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0])
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                    prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0])
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                    threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                    runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                    strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0]), threshold_date) #
                    productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0]
                    sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0]
                    if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0]:
                        lookback_summary += "S_"
                    else:
                        lookback_summary += "W_"
    
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0]))
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                    if self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                        lookback_summary += "Y"
                    else:
                        lookback_summary += "N"
                    
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Summary].values[0] = lookback_summary
                    
                    #set default value for historical opponents 2 and 3 of H team for current game
                    opponent1_team_ID = str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0])) + "_" + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Home].values[0]))  
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_LeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_SameLeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_DistanceTravelled].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Home].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Win].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1StrengthRatio].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1CLL].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Summary].values[0]
                    fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1Strength].values[0])))
                    fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                    fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1StrengthRatio].values[0]))
                else:
                    if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME: 
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Home].values[0] = MLB_dbvar.YES_HOME
                        lookback_summary += "H_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_DistanceTravelled].values[0] = 0.0
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] 
                        #did team win?
                        if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_WIN
                            lookback_summary += "W_"
                        else:
                            lookback_summary += "L_"
                            if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_LOSE
                            else:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_TIE
                    else:
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Home].values[0] = MLB_dbvar.NOT_HOME
                        lookback_summary += "V_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0])
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] 
                        #did team win?
                        if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                            lookback_summary += "W_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_WIN
                        else:
                            lookback_summary += "L_"
                            if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_LOSE
                            else:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0] = MLB_dbvar.G_TIE
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0])
                    prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0])
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                    threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                    runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                    strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0]), threshold_date) #
                    productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0]
                    sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0]
                    if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0]:
                        lookback_summary += "S_"
                    else:
                        lookback_summary += "W_"
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0]))
                    if self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                        lookback_summary += "Y"
                    else:
                        lookback_summary += "N"
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Summary].values[0] = lookback_summary

                    #set default value for historical opponents 2 and 3 of V team for current game
                    opponent1_team_ID = str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0])) + "_" + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Home].values[0]))  
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_LeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_SameLeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_SameDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_DistanceTravelled].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Home].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Win].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1StrengthRatio].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1CLL].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Summary].values[0]
                    fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1Strength].values[0])))
                    fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                    fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1StrengthRatio].values[0]))
            else: #okay, we have most recent opponent so let's get the next previous two unique opponents (unique is based on opponent team ID and whether current team was at home or not)
                if not lookback2_found:
                    lookback_summary = ""
                    is_over = self._checkIsOverBookieCLT(lookback_game)
                    opponent2_game_ID = int(v_lb[MLB_global.GAME_ID_INDEX])    
                    if (home_or_vis == MLB_global.HOME): 
                        if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME:
                            opponent2_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0])) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent1_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback2_found = True
                                fileHandle.write("\nfound the SECOND previous opponent from game " +str(opponent2_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Home].values[0] = MLB_dbvar.YES_HOME
                                lookback_summary += "H_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_DistanceTravelled].values[0] = 0.0
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_TIE
                        else:
                            opponent2_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0])) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent1_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback2_found = True
                                fileHandle.write("\nfound the SECOND previous opponent from game " +str(opponent2_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Home].values[0] = MLB_dbvar.NOT_HOME
                                lookback_summary += "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0])
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                    lookback_summary += "W_"
                                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_WIN
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0] = MLB_dbvar.G_TIE
                        if lookback2_found == True:
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get( self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                            prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                            threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                            runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                            strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0]), threshold_date) #
                            productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0]
                            sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0]
                            if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0]:
                                lookback_summary += "S_"
                            else:
                                lookback_summary += "W_"

                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0]))

                            if self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookback_summary += "Y"
                            else:
                                lookback_summary += "N"
                            
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Summary].values[0] = lookback_summary

                            #set default value for historical opponents 2 and 3 of V team for current game
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_LeagueDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameLeagueDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_SameDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_DistanceTravelled].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Home].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Win].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2StrengthRatio].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2CLL].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Summary].values[0]
                            fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2Strength].values[0])))
                            fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2StrengthRatio].values[0]))
                    else:
                        is_over = self._checkIsOverBookieCLT(lookback_game) #should be higher up as not based on Home or Vis
                        if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME: #Is the Visitor at home for this lookback game?
                            opponent2_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0])) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent1_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback2_found = True
                                fileHandle.write("\nfound the SECOND previous opponent from game " +str(opponent2_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]                        
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Home].values[0] = MLB_dbvar.YES_HOME
                                lookback_summary += "H_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_DistanceTravelled].values[0] = 0.0
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_TIE
                        else:
                            opponent2_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0])) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent1_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback2_found = True
                                fileHandle.write("\nfound the SECOND previous opponent from game " +str(opponent2_game_ID))
                                is_over = self._checkIsOverBookieCLT(lookback_game)
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Home].values[0] = MLB_dbvar.NOT_HOME
                                lookback_summary += "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0])
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0] = MLB_dbvar.G_TIE
                        if lookback2_found == True:
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get( self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                            prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                            threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                            runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                            strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0]), threshold_date) #
                            productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0]
                            sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0]
                            if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0]:
                                lookback_summary += "S_"
                            else:
                                lookback_summary += "W_"

                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0]))
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                            
                            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookback_summary += "Y"
                            else:
                                lookback_summary += "N"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Summary].values[0] = lookback_summary
                            #set default value for historical opponents 2 and 3 of V team for current game
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_LeagueDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameLeagueDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_SameDiv].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_DistanceTravelled].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Home].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Win].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2StrengthRatio].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3CLL].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2CLL].values[0]
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Summary].values[0]
                            fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2Strength].values[0])))
                            fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2StrengthRatio].values[0]))
                elif lookback2_found and not lookback3_found:
                    lookback_summary = ""
                    is_over = self._checkIsOverBookieCLT(lookback_game) #should be higher up as not based on Home or Vis
                    opponent3_game_ID = int(v_lb[MLB_global.GAME_ID_INDEX])
                    if (home_or_vis == MLB_global.HOME): 
                        if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME:
                            opponent3_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0])) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent3_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback3_found = True
                                fileHandle.write("\nfound the THIRD previous opponent from game " +str(opponent3_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Home].values[0] = MLB_dbvar.YES_HOME
                                lookback_summary += "H_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_DistanceTravelled].values[0] = 0.0
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_TIE
                        else:
                            opponent3_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0])) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent3_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback3_found = True
                                fileHandle.write("\nfound the THIRD previous opponent from game " +str(opponent3_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Home].values[0] = MLB_dbvar.NOT_HOME
                                lookback_summary += "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0])
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                    lookback_summary += "W_"
                                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_WIN
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Win].values[0] = MLB_dbvar.G_TIE
                        if lookback3_found == True:
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get( self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                            prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                            threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                            runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                            strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0]), threshold_date) #
                            productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0]
                            sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0]
                            if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0]:
                                lookback_summary += "S_"
                            else:
                                lookback_summary += "W_"
                        
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0]))
                            if self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookback_summary += "Y"
                            else:
                                lookback_summary += "N"
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Summary].values[0] = lookback_summary
                            fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3Strength].values[0])))
                            fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3StrengthRatio].values[0]))
                            break
                    else:
                        if v_lb[MLB_global.H_OR_V_INDEX] == MLB_global.HOME:
                            opponent3_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0])) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent3_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback3_found = True
                                fileHandle.write("\nfound the THIRD previous opponent from game " +str(opponent3_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Home].values[0] = MLB_dbvar.YES_HOME
                                lookback_summary += "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_DistanceTravelled].values[0] = 0.0
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                #did team win?
                                if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_TIE
                        else:
                            opponent3_team_ID = str(int(lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0])) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent3_team_ID != opponent2_team_ID:
                                #we have a unique opponent
                                lookback3_found = True
                                fileHandle.write("\nfound the THIRD previous opponent from game " +str(opponent3_game_ID))
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0] = lookback_game[MLB_dbvar.dbvar_G_H_Id].values[0]
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Home].values[0] = MLB_dbvar.NOT_HOME
                                lookback_summary += "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0])
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3CLL].values[0] = lookback_game[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] #OPL for team NOT their opponent
                                if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] > lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_WIN
                                    lookback_summary += "W_"
                                else:
                                    lookback_summary += "L_"
                                    if lookback_game[MLB_dbvar.dbvar_G_V_Runs].values[0] < lookback_game[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_LOSE
                                    else:
                                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Win].values[0] = MLB_dbvar.G_TIE         
                        if lookback3_found ==  True:
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_LeagueDiv].values[0] = prevld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get( self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,prevld)
                            prevdiv = MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0])
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameDiv].values[0] = MLB_global.checkMatch(team_Div,prevdiv)
                            threshold_date = lookback_game[MLB_dbvar.dbvar_G_Date].values[0] #type will by Numpy datetime64
                            runStrength_game_ID, team_strength = self.masterDB.getHistoricalRunStrength(team_id, threshold_date)
                            strength_game_ID, self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0] = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0]), threshold_date) #
                            productsum_team_strength += team_strength * self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0]
                            sum_opponent_strength += self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0]
                            if team_strength >= self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0]:
                                lookback_summary += "S_"
                            else:
                                lookback_summary += "W_"

                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(team_strength,self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0]))

                            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookback_summary += "Y"
                            else:
                                lookback_summary += "N"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Summary].values[0] = lookback_summary
                            fileHandle.write(" and their team ID is " + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_Id].values[0])) + ". For game " + str(strength_game_ID) + " their game strength was " + str(float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3Strength].values[0])))
                            fileHandle.write("\nNOTE: Team " + str(team_id) + "'s game strength value going into this game was " + str(team_strength) + " and derived from historical game " + str(runStrength_game_ID))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3StrengthRatio].values[0]))
                            break
                        
        if lookback2_found == False:
            fileHandle.write("\nNOTE: Unique second and third previous opponents were NOT found in the available data so details of the first opponent are used for both. ---*\n\n")
        else:
            if lookback3_found == False:
                fileHandle.write("\nNOTE: A unique third previous opponent was NOT found in the available data so details of the second opponent is used. ---*\n\n")
        
        #calculate days rest
        days_rest = MLB_dbvar.Calc_DaysRest(self._game_date, opponent1_game_date)
                           
        #update Days Rest and Lookback Strength vars
        lookback_weighted_strength = MLB_global.calcRatio(productsum_team_strength, sum_opponent_strength)
        if (home_or_vis == MLB_global.HOME): 
            self._currentgame_df[MLB_dbvar.dbvar_G_H_DaysRest].values[0] = days_rest
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Lookback_Strength].values[0] = lookback_weighted_strength
        else:
            self._currentgame_df[MLB_dbvar.dbvar_G_V_DaysRest].values[0] = days_rest
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Lookback_Strength].values[0] = lookback_weighted_strength
                
    def _echoOpponentOnLookaheadFields(self, home_or_vis, fileHandle):
        # This function simply copies information about the current opponent on the H or V look ahead fields
        # Assumption 1: self._currentgame_df is the game to be updated
        fileHandle.write("\n*--- Look ahead information is not available and therefore the current opponent data will be echoed on the look ahead fields")
        #threshold date for lookaheads (which is date of game to be updated...so we will use this to find game immediately before this one)
        thresholdDate = self._game_date
        #init key id and strength vars
        teamId = runStrength_game_ID = 0
        runStrength = 0.0
        opponentTeamId = opponentStrengthGameId = 0
        opponentrunStrength = 0.0
        lookahead_summary = ""
        lookahead_weighted_strength = 0.0
        sum_opponent_strength = 0.0
        productsum_team_strength = 0.0

        #If Home team then copy Visitor opponent data into Home look ahead fields
        if (home_or_vis == MLB_global.HOME):
            #HOME TEAM: get id, confdiv and strength going into current game
            teamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0])
            teamDiv = MLB_dbvar.TEAM_DIVISION.get(teamId)
            teamConfDiv = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(teamId)
            runStrength_game_ID, runStrength = self.masterDB.getHistoricalRunStrength(teamId, thresholdDate)
            fileHandle.write("\nThe game strength for team " + str(teamId) + " going into these lookahead games is " + str(runStrength) + " and was derived from historical game " + str(runStrength_game_ID))   
            #OPPONENT (VIS TEAM): get id and strength
            opponentTeamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0])
            opponentStrengthGameId, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponentTeamId, thresholdDate)
            fileHandle.write("\nThe current opponent is team " + str(opponentTeamId) + " and their strength going into the current game is " + str(opponentrunStrength) + " and was derived from game "  +str(opponentStrengthGameId))
            #POPULATE LOOKAHEAD FIELDS
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0] = opponentTeamId
            oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponentTeamId)
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0] = MLB_global.checkMatch(teamDiv,oppdiv)
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponentTeamId)
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameLeagueDiv].values[0] = MLB_global.checkMatch(teamConfDiv,oppld)
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0] = MLB_dbvar.YES_HOME
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_DistanceTravelled].values[0] = 0.0
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Strength].values[0] = opponentrunStrength
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Strength].values[0]))
            productsum_team_strength = runStrength * opponentrunStrength
            sum_opponent_strength = opponentrunStrength
            lookahead_weighted_strength = MLB_global.calcRatio(productsum_team_strength, sum_opponent_strength) 
            #Build lookahead summary H/V_S/W_Y/N
            if self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0] == MLB_dbvar.YES_HOME:
                lookahead_summary = "H_"
            else:
                lookahead_summary = "V_"
            if runStrength >= opponentrunStrength:
                lookahead_summary += "S_"
            else:
                lookahead_summary += "W_"
            if self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                lookahead_summary += "Y"
            else:
                lookahead_summary += "N"
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Summary].values[0] = lookahead_summary

            #set default for lookahead 2 and 3
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_LeagueDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameLeagueDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_DistanceTravelled].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Strength].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1StrengthRatio].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Summary].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Lookahead_Strength].values[0] = lookahead_weighted_strength  
        else:
            #VIS TEAM: get id, confdiv and strength going into current game
            teamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0])
            teamDiv = MLB_dbvar.TEAM_DIVISION.get(teamId)
            teamConfDiv = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(teamId)
            runStrength_game_ID, runStrength = self.masterDB.getHistoricalRunStrength(teamId, thresholdDate)
            #OPPONENT (HOME TEAM): get id and strength
            opponentTeamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0])
            opponentStrengthGameId, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponentTeamId, thresholdDate)
            #populate Home lookahead fields
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0] = opponentTeamId
            oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponentTeamId)
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0] = MLB_global.checkMatch(teamDiv,oppdiv)
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponentTeamId)
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameLeagueDiv].values[0] = MLB_global.checkMatch(teamConfDiv,oppld)
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0] = MLB_dbvar.NOT_HOME
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_DistanceTravelled].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Strength].values[0] = opponentrunStrength
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Strength].values[0]))
            productsum_team_strength = runStrength * opponentrunStrength
            sum_opponent_strength = opponentrunStrength
            lookahead_weighted_strength = MLB_global.calcRatio(productsum_team_strength, sum_opponent_strength) 
            #Build lookahead summary H/V_S/W_Y/N
            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0] == MLB_dbvar.YES_HOME:
                lookahead_summary = "H_"
            else:
                lookahead_summary = "V_"
            if runStrength >= opponentrunStrength:
                lookahead_summary += "S_"
            else:
                lookahead_summary += "W_"
            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                lookahead_summary += "Y"
            else:
                lookahead_summary += "N"
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Summary].values[0] = lookahead_summary

            #set default for lookahead 2 and 3
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_LeagueDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameLeagueDiv].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_DistanceTravelled].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Strength].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1StrengthRatio].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Summary].values[0]
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Lookahead_Strength].values[0] = lookahead_weighted_strength  
            
    # When a team is on their last game of the season then we need to echo their current opponent on the lookahead fields
    # To determine this, we simply check to if the relevant dict (self._lookahead_games or self._lookahead_games) is empty
    def _getEchoOpponentLookaheadStatus(self, home_or_vis):
        #This function returns True if we need to echo lookahead, else returns false
        #Assumption: self._lookahead_games and self._lookahead_games have already been populated before this func is called
        echoLookaheadStatus = False 
        if (home_or_vis == MLB_global.HOME):
            if not self._lookahead_games:
                echoLookaheadStatus = True
        else:
            if not self._lookahead_games:
                echoLookaheadStatus = True
        return echoLookaheadStatus
        
    def _populateLookAheadFields(self, h_or_v, fileHandle):
        #This is a huge inefficient function that needs significant redesign BUT not now!!!
        # Assumption 1: self._currentgame_df is the game to be updated
        # Assumption 2: The list of lookahead games is stored in self._lookahead_games and self._lookahead_games AND are games from the current season of game of interest
        # Assumption 3: self._game_date_plusone has been assigned a valid value prior to this func being called
        
        # NOTE 1:Uniqueness is based on Opp_Team_Id AND whether team of interest was at Home or a Visitor.#Format: <Team_Id>_<Home_VIS>
        # NOTE 2:Strength values of team and opponent are SHALLOW i.e. based on spot values and not averages of say X games before the current game to be predicted (and thus also before the look ahead games)

        #1. Initialise vars
        lookahead1_found = False
        lookahead2_found = False
        lookahead3_found = False
        echoLookahead = False
        opponent1_team_ID = MLB_dbvar.NO_DATA
        opponent1_game_ID = 0
        opponent2_team_ID = MLB_dbvar.NO_DATA
        opponent2_game_ID = 0
        opponent3_team_ID = MLB_dbvar.NO_DATA
        opponent3_game_ID = 0
        teamId = runStrength_game_ID = 0
        runStrength = 0.0
        opponentTeamId = opponentStrengthGameId = 0
        opponentrunStrength = 0.0
        sum_opponent_strength = 0.0
        productsum_team_strength = 0.0
        lookahead_weighted_strength = 0.0
        game_date = self._game_date
        lookahead_summary = ""
        lookahead_games_dict = {} #we will make deep copys of H or V look ahead dict so we do not inadvertantly alter them (which we wont but good to be safe)
        lookahead_game_df = pd.DataFrame

        fileHandle.write("\n\n*--- GETTING LOOKAHEAD GAME DATA...")
        
        #2. Get lookahead games
        fileHandle.write("\n*--- Processing available look ahead information...")
        _end_date = self._season_end_date #MUST be end date for current season (for game under consideration)
        if h_or_v == MLB_global.HOME:
            team_id = int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0])
        else: #Visitor
            team_id = int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0])
        #get all lookahead games
        self._lookahead_games = self.masterDB.getTeamGames(self._game_date, team_id, None, self._game_date_plusone, _end_date)
        #get copy of ALL look ahead games
        lookahead_games_dict = copy.deepcopy(self._lookahead_games)
        
        #3. Check if we need to echo current opponent on lookahead fields
        echoLookahead = self._getEchoOpponentLookaheadStatus(h_or_v)
        if echoLookahead:
            self._echoOpponentOnLookaheadFields(h_or_v, fileHandle)
            return
        
        #4. get H or V team's conf div and team strength
        team_Div = MLB_dbvar.TEAM_DIVISION.get(team_id)
        team_LeagueDiv = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(team_id)
        runStrength_game_ID, runStrength = self.masterDB.getHistoricalRunStrength(team_id, game_date) #get strength for team

        fileHandle.write("\nThe game strength for team " + str(team_id) + " going into these lookahead games is " + str(runStrength) + " and was derived from historical game " + str(runStrength_game_ID))    
        
        #5. For available look ahead games, get strength for opponents (NB opponentX_division is NOT used)
        for k_la, v_la in lookahead_games_dict.items():
            #retrieve game
            lookahead_game_df = self.masterDB.retrieveGames(MLB_dbvar.dbvar_G_Id, v_la[MLB_global.GAME_ID_INDEX]).copy()
            lookahead_summary = ""
            opponentrunStrength = 0.0
            #process it
            if not lookahead1_found:
                opponent1_game_ID = int(v_la[MLB_global.GAME_ID_INDEX])
                fileHandle.write("\nfound the FIRST upcoming opponent from game " +str(opponent1_game_ID))
                if (h_or_v == MLB_global.HOME):
                    if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0] = MLB_dbvar.YES_HOME
                        lookahead_summary = "H_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_DistanceTravelled].values[0] = 0.0
                    else:
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0] = MLB_dbvar.NOT_HOME
                        lookahead_summary = "V_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0])
                    opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0]), game_date) # _dGEN_MasterDB library assigns an insample avg strg for non-existent games
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Strength].values[0] = opponentrunStrength
                    if runStrength >= opponentrunStrength:
                        lookahead_summary += "S_"
                    else:
                        lookahead_summary += "W_"
                    productsum_team_strength += runStrength * opponentrunStrength
                    sum_opponent_strength += opponentrunStrength
                    #store opponent id as we want to avoid this for the next lookahead if possible
                    opponentTeamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0])
                    opponentUniqueTeamId = str(opponentTeamId) + "_" + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0]))
                    oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponentTeamId)
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                    if self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                        lookahead_summary += "Y"
                    else:
                        lookahead_summary += "N"
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponentTeamId)
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,opponentrunStrength))
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Summary].values[0] = lookahead_summary
                    fileHandle.write(" and their team ID is " + str(opponentTeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                    fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1StrengthRatio].values[0]))        
                    #set default for lookahead 2 and 3
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Id].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Home].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_LeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_SameLeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1Strength].values[0] 
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1StrengthRatio].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_DistanceTravelled].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next1_Summary].values[0]
                else:
                    if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0] = MLB_dbvar.YES_HOME
                        lookahead_summary = "H_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_DistanceTravelled].values[0] = 0.0
                    else:
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0] = MLB_dbvar.NOT_HOME
                        lookahead_summary = "V_"
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0])
                    opponentTeamId = int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0])
                    opponentUniqueTeamId = str(opponentTeamId) + "_" + str(int(self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0]))
                    opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponentTeamId, game_date)
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Strength].values[0] = opponentrunStrength
                    if runStrength >= opponentrunStrength:
                        lookahead_summary += "S_"
                    else:
                        lookahead_summary += "W_"
                    productsum_team_strength += runStrength * opponentrunStrength
                    sum_opponent_strength += opponentrunStrength
                    #store opponent id as we want to avoid this for the next lookahead if possible
                    oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponentTeamId)
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                    if self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0] == MLB_dbvar.G_WIN:
                        lookahead_summary += "Y"
                    else:
                        lookahead_summary += "N"
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponentTeamId)
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,opponentrunStrength))
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Summary].values[0] = lookahead_summary
                    fileHandle.write(" and their team ID is " + str(opponentTeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                    fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1StrengthRatio].values[0]))        
                    #set default for lookahead 2 and 3                    
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Id].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Home].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_LeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_SameLeagueDiv].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1Strength].values[0] 
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1StrengthRatio].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_DistanceTravelled].values[0]
                    self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next1_Summary].values[0]
                #update flag
                lookahead1_found = True
                opponent1_team_ID = opponentUniqueTeamId
            elif not lookahead2_found: #search for unique second opponent
                opponent2_game_ID = int(v_la[MLB_global.GAME_ID_INDEX])
                if (h_or_v == MLB_global.HOME):
                    if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                        opponent2TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                        opponent2UniqueTeamId = str(opponent2TeamId) + "_" + str(MLB_dbvar.YES_HOME)
                        if opponent2UniqueTeamId != opponent1_team_ID:
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Home].values[0] = MLB_dbvar.YES_HOME
                            lookahead_summary = "H_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_DistanceTravelled].values[0] = 0.0
                            lookahead2_found = True
                    else:
                        opponent2TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                        opponent2UniqueTeamId = str(opponent2TeamId) + "_" + str(MLB_dbvar.NOT_HOME)
                        if opponent2UniqueTeamId != opponent1_team_ID:
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Home].values[0] = MLB_dbvar.NOT_HOME
                            lookahead_summary = "V_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,opponent2TeamId)
                            lookahead2_found = True
                    if lookahead2_found == True:
                        opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponent2TeamId, game_date) 
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Strength].values[0] = opponentrunStrength
                        if runStrength >= opponentrunStrength:
                            lookahead_summary += "S_"
                        else:
                            lookahead_summary += "W_"
                        productsum_team_strength += runStrength * opponentrunStrength
                        sum_opponent_strength += opponentrunStrength
                        #store opponent id as we want to avoid this for the next lookahead if possible
                        oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponent2TeamId)
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                        if self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameDiv].values[0] == MLB_dbvar.G_WIN:
                            lookahead_summary += "Y"
                        else:
                            lookahead_summary += "N"
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponent2TeamId)
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,opponentrunStrength))
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Summary].values[0] = lookahead_summary
                        fileHandle.write("\nfound the SECOND upcoming opponent from game " +str(opponent2_game_ID))
                        fileHandle.write(" and their team ID is " + str(opponent2TeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                        fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2StrengthRatio].values[0]))        
                        #set default for lookahead 3
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_LeagueDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_SameLeagueDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Home].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2Strength].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2StrengthRatio].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_DistanceTravelled].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next2_Summary].values[0]
                else:
                    if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                        opponent2TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                        opponent2UniqueTeamId = str(opponent2TeamId) + "_" + str(MLB_dbvar.YES_HOME)
                        if opponent2UniqueTeamId != opponent1_team_ID:
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Home].values[0] = MLB_dbvar.YES_HOME
                            lookahead_summary = "H_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_DistanceTravelled].values[0] = 0.0
                            lookahead2_found = True
                    else:
                        opponent2TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                        opponent2UniqueTeamId = str(opponent2TeamId) + "_" + str(MLB_dbvar.NOT_HOME)
                        if opponent2_team_ID != opponent1_team_ID:
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Home].values[0] = MLB_dbvar.NOT_HOME
                            lookahead_summary = "V_"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0])
                            lookahead2_found = True
                    if lookahead2_found == True:
                        opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponent2TeamId, game_date)
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Strength].values[0] = opponentrunStrength
                        if runStrength >= opponentrunStrength:
                            lookahead_summary += "S_"
                        else:
                            lookahead_summary += "W_"
                        productsum_team_strength += runStrength * opponentrunStrength
                        sum_opponent_strength += opponentrunStrength
                        #store opponent id as we want to avoid this for the next lookahead if possible
                        oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponent2TeamId)
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                        if self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameDiv].values[0] == MLB_dbvar.G_WIN:
                            lookahead_summary += "Y"
                        else:
                            lookahead_summary += "N"
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponent2TeamId)
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength, opponentrunStrength))
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Summary].values[0] = lookahead_summary
                        fileHandle.write("\nfound the SECOND upcoming opponent from game " +str(opponent2_game_ID))
                        fileHandle.write(" and their team ID is " + str(opponent2TeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                        fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2StrengthRatio].values[0]))        
                        #set default for lookahead 3
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Id].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Id].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_LeagueDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameLeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_SameLeagueDiv].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Home].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Home].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Strength].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2Strength].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3StrengthRatio].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2StrengthRatio].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_DistanceTravelled].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_DistanceTravelled].values[0]
                        self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Summary].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next2_Summary].values[0]
            else: 
                if not lookahead3_found: #search for unique third opponent
                    opponent3_game_ID = int(v_la[MLB_global.GAME_ID_INDEX])
                    if (h_or_v == MLB_global.HOME):
                        if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                            opponent3TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                            opponent3UniqueTeamId = str(opponent3TeamId) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent3UniqueTeamId != opponent2UniqueTeamId:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Home].values[0] = MLB_dbvar.YES_HOME
                                lookahead_summary = "H_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_DistanceTravelled].values[0] = 0.0
                                lookahead3_found = True
                        else:
                            opponent3TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                            opponent3UniqueTeamId = str(opponent3TeamId) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent3UniqueTeamId != opponent2UniqueTeamId:
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Home].values[0] = MLB_dbvar.NOT_HOME
                                lookahead_summary = "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,opponent3TeamId)
                                lookahead3_found = True
                        if lookahead3_found == True:
                            opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponent3TeamId, game_date)
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3Strength].values[0] = opponentrunStrength
                            if runStrength >= opponentrunStrength:
                                lookahead_summary += "S_"
                            else:
                                lookahead_summary += "W_"
                            productsum_team_strength += runStrength * opponentrunStrength
                            sum_opponent_strength += opponentrunStrength
                            #store opponent id as we want to avoid this for the next lookahead if possible
                            oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponent3TeamId)
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                            if self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookahead_summary += "Y"
                            else:
                                lookahead_summary += "N"
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponent3TeamId)
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength,opponentrunStrength))
                            self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3_Summary].values[0] = lookahead_summary
                            fileHandle.write("\nfound the THIRD upcoming opponent from game " +str(opponent3_game_ID))
                            fileHandle.write(" and their team ID is " + str(opponent3TeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_H_Next3StrengthRatio].values[0]))        
                            break
                    else:
                        if (v_la[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                            opponent3TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_V_Id].values[0]
                            opponent3UniqueTeamId = str(opponent3TeamId) + "_" + str(MLB_dbvar.YES_HOME)
                            if opponent3UniqueTeamId != opponent2UniqueTeamId:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Home].values[0] = MLB_dbvar.YES_HOME
                                lookahead_summary = "H_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_DistanceTravelled].values[0] = 0.0
                                lookahead3_found = True
                        else:
                            opponent3TeamId = self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Id].values[0] = lookahead_game_df[MLB_dbvar.dbvar_G_H_Id].values[0]
                            opponent3UniqueTeamId = str(opponent3TeamId) + "_" + str(MLB_dbvar.NOT_HOME)
                            if opponent3UniqueTeamId != opponent2UniqueTeamId:
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Home].values[0] = MLB_dbvar.NOT_HOME
                                lookahead_summary = "V_"
                                self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_DistanceTravelled].values[0] = MLB_dbvar.Get_DistanceTravelled_KM(team_id,opponent3TeamId)
                                lookahead3_found = True
                        if lookahead3_found == True:
                            opp_strength_game_ID, opponentrunStrength = self.masterDB.getHistoricalRunStrength(opponent3TeamId,game_date)
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3Strength].values[0] = opponentrunStrength
                            if runStrength >= opponentrunStrength:
                                lookahead_summary += "S_"
                            else:
                                lookahead_summary += "W_"
                            productsum_team_strength += runStrength * opponentrunStrength
                            sum_opponent_strength += opponentrunStrength
                            #store opponent id as we want to avoid this for the next lookahead if possible
                            oppdiv = MLB_dbvar.TEAM_DIVISION.get(opponent3TeamId)
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameDiv].values[0] = MLB_global.checkMatch(team_Div,oppdiv)
                            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameDiv].values[0] == MLB_dbvar.G_WIN:
                                lookahead_summary += "Y"
                            else:
                                lookahead_summary += "N"
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_LeagueDiv].values[0] = oppld = MLB_dbvar.TEAM_LEAGUE_DIVISION.get(opponent3TeamId)
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_SameLeagueDiv].values[0] = MLB_global.checkMatch(team_LeagueDiv,oppld)
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3StrengthRatio].values[0] = math.fabs(MLB_global.calcProbRatio(runStrength, opponentrunStrength))
                            self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3_Summary].values[0] = lookahead_summary
                            fileHandle.write("\nfound the THIRD upcoming opponent from game " +str(opponent3_game_ID))
                            fileHandle.write(" and their team ID is " + str(opponent3TeamId) + ". For Game " + str(opp_strength_game_ID) + " their strength was " + str(float(opponentrunStrength)))
                            fileHandle.write("\nThe resulting strength ratio for team " + str(team_id) + " is " + str(self._currentgame_df[MLB_dbvar.dbvar_G_V_Next3StrengthRatio].values[0]))        
                            break
        #Report whether or not we were able to find unique lookaheads
        if lookahead2_found == False:
            fileHandle.write("\nNOTE: Unique second and third future opponents were NOT found in the available data so details of the next opponent are used for both. ---*\n\n")
        else:
            if lookahead3_found == False:
                fileHandle.write("\nNOTE: A unique third opponent was NOT found in the available data so details of the second opponent was used! ---*\n\n")

        #update Lookahead Strength
        lookahead_weighted_strength = MLB_global.calcRatio(productsum_team_strength, sum_opponent_strength)
        if (h_or_v == MLB_global.HOME): 
            self._currentgame_df[MLB_dbvar.dbvar_G_H_Lookahead_Strength].values[0] = lookahead_weighted_strength
        else:
            self._currentgame_df[MLB_dbvar.dbvar_G_V_Lookahead_Strength].values[0] = lookahead_weighted_strength

    def _updatePitcherDaysRest(self, home_or_vis, ordered_games_to_process):
        #Assumption 1: self._game_data_df is the game to be updated
        #Assumption 2: the dict ordered_games_to_process contains historical games for SP's team (H or V)...it is NOT a list of games for just that SP (who mightve played for other teams previously)
        #              Included in this assumption is that either ALL games or YTD games for team  of interest will be contained in ordered_games_to_process
        #Assumption 3: ordered_games_to_process is organised in reverse chronological order so most recent games are encountered first

        #1. Get SP Id for team of interest (either H or V)
        if (home_or_vis == MLB_global.HOME):
            pitcher_id = self._currentgame_df[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]
        else:
            pitcher_id = self._currentgame_df[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]
        #2. Get date of SPs last game (if it exists)
        num_games = len(ordered_games_to_process)
        spFound = False
        if num_games > 0:
            #get first populate historical opponent attributes and calculate the averages for the relevant features
            #NB the default values for historical opponents 2 and 3 will be that for opponent 1
            #Traverse games list until we find SP
            for k, v in ordered_games_to_process.items(): #we have a window of games, process each game in window
                # get game from window
                historical_game = self.masterDB.retrieveGames(MLB_dbvar.dbvar_G_Id, v[MLB_global.GAME_ID_INDEX])
                if (v[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                    #check if SP pitcher of interest
                    if pitcher_id == historical_game[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]:
                        spFound = True
                else:
                    #check if SP pitcher of interest
                    if pitcher_id == historical_game[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]:
                        spFound = True
                #break if we've found it!
                if spFound:
                    break
        #3. Calc Days rest (if prior game exists)
        daysRest = MLB_dbvar.MAX_DAYS_REST
        gameDate = self._getCurrent_GameDate()
        if spFound:
            previousGameDate = historical_game[MLB_dbvar.dbvar_G_Date].values[0]
            daysRest = MLB_dbvar.Calc_DaysRest(gameDate, previousGameDate)
        #4. Update relevant SP field    
        if (home_or_vis == MLB_global.HOME):
            self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_DaysRest].values[0] = daysRest
        else:
            self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_DaysRest].values[0] = daysRest
    
    def _calcPitcherFeatureStats(self, home_or_vis, ordered_games_to_process, attribute_list, baseAttrib_list=None, fileHandle=None, windowLimit=None):
        #Assumption 1: the following settings have been set before calling this function: self._use_base_attrib, self._is_Avg, self._is_HV
        #Assumption 2: self._game_data_df is the game to be updated
        #Assumption 3: the dict ordered_games_to_process contains historical games for SP's team (H or V)...it is NOT a list of games for just that SP (who mightve played for other teams previously)
        #              Included in this assumption is that either ALL games or YTD games for team  of interest will be contained in ordered_games_to_process
        # Returns processed_game_ctr 
        
        #1. Get SP Id for team of interest (either H or V)
        if (home_or_vis == MLB_global.HOME):
            pitcher_id = self._currentgame_df[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]
        else:
            pitcher_id = self._currentgame_df[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]
        
        #2. Get number of games to process and check whether it meets the threshold (it should do!)
        # If there isnt sufficient data then the values will remain at -1000000 and a separate process
        # will be required to replace them with insample averages
        num_games = len(ordered_games_to_process)
        processed_game_ctr = 0
        if num_games > 0:
            avg_attrib = ""
            sum_total = float(0.0)
            
            for i, x in enumerate(attribute_list):
                # update to refer to either home or visitor attrib of game to be updated
                if (home_or_vis == MLB_global.HOME):
                    avg_attrib = MLB_global.AVG_H + x
                else:
                    avg_attrib = MLB_global.AVG_V + x
            
                #populate historical opponent attributes and calculate the averages for the relevant features
                #NB the default values for historical opponents 2 and 3 will be that for opponent 1
                processed_game_ctr = 0
                sum_total = float(0.0)
                y_attrib = ""
                for k, v in ordered_games_to_process.items(): #we have a window of games, process each game in window
                    # get game from window
                    historical_game = self.masterDB.retrieveGames(MLB_dbvar.dbvar_G_Id, v[MLB_global.GAME_ID_INDEX])
                    skip_historical_game = False

                    ########
                    # Only avg or sum IF sp_id is present (as they will not be the SP for all of the team's historical games
                    # eg Tepper might be playing for Atlanta Braves for self._current_game and so only when Tepper is playing for this team in historical games is the value stored/acted upon
                    # If Tepper is not the SP for a particular historical game (for Atlanta Braves) then the game is skipped
                    #######
                                    
                    # sum appropriate attribute value based on whether H or V in ordered_games_to_process
                    # current team could be home or away for any of the games in the window
                    if self._use_base_attrib and baseAttrib_list != None:
                        x = baseAttrib_list[i] #get base attrib and can use same index i for 'attribute_list' as lists MUST be union friendly and ordered

                    if self._is_HV:
                        #update sum only if their H/V status for historical game is same as current game (home_or_vis) on whether team is H or V for current game in window
                        if avg_attrib.find(MLB_dbvar.HOME_attrib_str) != -1: 
                            if (v[MLB_global.H_OR_V_INDEX] == MLB_global.HOME): #sum only if home games
                                #check if SP pitcher of interest
                                if pitcher_id == historical_game[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]:
                                    y_attrib = MLB_global.AVG_H + x
                                else:
                                    skip_historical_game = True
                            else:
                                skip_historical_game = True
                                
                        else:
                            if (v[MLB_global.H_OR_V_INDEX] == MLB_global.VISITOR): #must be
                                #check if SP pitcher of interest
                                if pitcher_id == historical_game[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]:
                                    y_attrib = MLB_global.AVG_V + x
                                else:
                                    skip_historical_game = True
                            else:#shouldnt reach this
                                skip_historical_game = True
                    else: #we will sum whether team is H or V
                        if (v[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                            #check if SP pitcher of interest
                            if pitcher_id == historical_game[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0]:
                                y_attrib = MLB_global.AVG_H + x
                            else:
                                skip_historical_game = True
                        else:
                            #check if SP pitcher of interest
                            if pitcher_id == historical_game[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0]:
                                y_attrib = MLB_global.AVG_V + x
                            else:
                                skip_historical_game = True

                    #update accummulative total and counts
                    if not skip_historical_game:
                            sum_total += float(historical_game[y_attrib].values[0])
                            processed_game_ctr += 1

                    #check if there is a windowlimit, and if so, break if we've reached it
                    if windowLimit != None:
                        if processed_game_ctr == windowLimit:
                            break

                    # after finished processing, check if we're at end of window and if so, break
                    if (processed_game_ctr == num_games):
                        break
                
                #Calc average or rounded sum as appropriate
                self._currentgame_df[avg_attrib].values[0] = float(0.00)
                if processed_game_ctr > 0: #it will be at this stage but..
                    if self._is_Avg:
                        self._currentgame_df[avg_attrib].values[0] = float(round(sum_total / processed_game_ctr,2))
                    else:
                        self._currentgame_df[avg_attrib].values[0] = float(round(sum_total,2))

        #return number of games processed so SP features can be further processed if required (eg assigned insample averages)
        return processed_game_ctr
        
    def _calcFeatureStats(self, home_or_vis, ordered_games_to_process, attribute_list, baseAttrib_list=None, fileHandle=None):
        #Assumption 1: the following settings have been set before calling this function: self._use_base_attrib, self._is_Avg, self._is_HV
        #Assumption 2: self._game_data_df is the game to be updated
        #ASsumption 3: the dict ordered_games_to_process contains ONLY those games to be included in the stats calculations. If there is not enough then skip_game will bet set to True
        
        #1. Get number of games to process and check whether it meets the threshold (it should do!)
        num_games = len(ordered_games_to_process)
        if num_games < MLB_global.GAME_THRESHOLD:
            self._skip_game = True
        else:
            avg_attrib = ""
            sum_total = float(0.0)

            for i, x in enumerate(attribute_list):
                # update to refer to either home or visitor attrib of game to be updated
                if (home_or_vis == MLB_global.HOME):
                    avg_attrib = MLB_global.AVG_H + x
                else:
                    avg_attrib = MLB_global.AVG_V + x
            
                #calc sum based on historical data 
                processed_game_ctr = 0
                sum_total = float(0.0)
                y_attrib = ""
                for k, v in ordered_games_to_process.items(): #we have a window of games, process each game in window
                    # get game from window
                    historical_game = self.masterDB.retrieveGames(MLB_dbvar.dbvar_G_Id, v[MLB_global.GAME_ID_INDEX])
                    skip_historical_game = False
                
                    # sum appropriate attribute value based on whether H or V in ordered_games_to_process
                    # current team could be home or away for any of the games in the window
                    if self._use_base_attrib and baseAttrib_list != None:
                        x = baseAttrib_list[i] #get base attrib and can use same index i for 'attribute_list' as lists MUST be union friendly and ordered
                        #now check if base attrib is a G attrib and if so initialise y_attrib accordingly
                        if self._is_G_base_attrib:
                            y_attrib = MLB_global.G_ATTRIB

                    if self._is_HV:
                        #update sum only if their H/V status for historical game is same as current game (home_or_vis) on whether team is H or V for current game in window
                        if avg_attrib.find(MLB_dbvar.HOME_attrib_str) != -1: 
                            if (v[MLB_global.H_OR_V_INDEX] == MLB_global.HOME): #sum only if home games
                                y_attrib += MLB_global.AVG_H + x
                            else:
                                skip_historical_game = True
                        else:
                            if (v[MLB_global.H_OR_V_INDEX] == MLB_global.VISITOR): #must be visitor
                                y_attrib += MLB_global.AVG_V + x
                            else: 
                                skip_historical_game = True
                    else: #we will sum whether team is H or V
                        if (v[MLB_global.H_OR_V_INDEX] == MLB_global.HOME):
                            y_attrib += MLB_global.AVG_H + x
                        else:
                            y_attrib += MLB_global.AVG_V + x

                    #update accummulative total and counts
                    if not skip_historical_game:
                            sum_total += float(historical_game[y_attrib].values[0])
                            processed_game_ctr += 1
                            y_attrib = ""

                    # after finished processing, check if we're at end of window and if so, break
                    if (processed_game_ctr == num_games):
                        break
                
                #Calc average or rounded sum as appropriate
                self._currentgame_df[avg_attrib].values[0] = float(0.00)
                if processed_game_ctr > 0: #it will be at this stage but..
                    if self._is_Avg:
                        self._currentgame_df[avg_attrib].values[0] = float(round(sum_total / processed_game_ctr,2))
                    else:
                        self._currentgame_df[avg_attrib].values[0] = float(round(sum_total,2))
        
    def _updateLeagueDivAttribs(self):
        self._currentgame_df[MLB_dbvar.dbvar_G_H_League].values[0] = str(MLB_dbvar.TEAM_LEAGUE.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_V_League].values[0] = str(MLB_dbvar.TEAM_LEAGUE.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Division].values[0] = x = str(MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_V_Division].values[0] = y = str(MLB_dbvar.TEAM_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Same_Div].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Same_Div].values[0] = MLB_global.checkMatch(x, y)
        self._currentgame_df[MLB_dbvar.dbvar_G_H_LeagueDiv].values[0] = x = str(MLB_dbvar.TEAM_LEAGUE_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_V_LeagueDiv].values[0] = y = str(MLB_dbvar.TEAM_LEAGUE_DIVISION.get(self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0]))
        self._currentgame_df[MLB_dbvar.dbvar_G_H_Same_LeagueDiv].values[0] = self._currentgame_df[MLB_dbvar.dbvar_G_V_Same_LeagueDiv].values[0] = MLB_global.checkMatch(x, y)

    def _updateOvertimeAttribs(self):
        if(self._currentgame_df[MLB_dbvar.dbvar_H_Duration].values[0] > MLB_dbvar.MLB_NORMALGAME_DURATION):
            self._currentgame_df[MLB_dbvar.dbvar_H_OverTime].values[0] = MLB_global.YES
        else:
            self._currentgame_df[MLB_dbvar.dbvar_H_OverTime].values[0] = MLB_global.NO
        
        if(self._currentgame_df[MLB_dbvar.dbvar_V_Duration].values[0] > MLB_dbvar.MLB_NORMALGAME_DURATION):
            self._currentgame_df[MLB_dbvar.dbvar_V_OverTime].values[0] = MLB_global.YES
        else:
            self._currentgame_df[MLB_dbvar.dbvar_V_OverTime].values[0] = MLB_global.NO
    
    def _updateVisDistanceTravelledAttrib(self):
        # Assumption: H and V Id fields have been populated
        # This func MUST be called during initiPrimitives as G_V_DistanceTravelled is used to initialise V_NextX_Distance_Travelled when echoing current opponent
        fieldName=MLB_dbvar.dbvar_G_V_DistanceTravelled
        fieldValue = MLB_dbvar.Get_DistanceTravelled_KM(self._currentgame_df[MLB_dbvar.dbvar_G_H_Id].values[0],self._currentgame_df[MLB_dbvar.dbvar_G_V_Id].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)
               
    def _updateDistanceTravelledAttribs(self):
        # HOM Team
        # Sum dist trav over last 3 games
        fieldName=MLB_dbvar.dbvar_G_H_TotalDistanceTravelled_3G
        fieldValue = float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev1_DistanceTravelled].values[0] + self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev2_DistanceTravelled].values[0] + self._currentgame_df[MLB_dbvar.dbvar_G_H_Prev3_DistanceTravelled].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)     
        #VIS team
        #First determine dist trav for current game
        self._updateVisDistanceTravelledAttrib()
        # Sum dist trav over last 3 games
        fieldName=MLB_dbvar.dbvar_G_V_TotalDistanceTravelled_3G
        fieldValue = float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev1_DistanceTravelled].values[0] + self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev2_DistanceTravelled].values[0] + self._currentgame_df[MLB_dbvar.dbvar_G_V_Prev3_DistanceTravelled].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)     
        
    def _updateStrengthAttribs(self):
        #ASSUMPTION: all avg/sum component attribs (eg _Runs_Gained, _Runs_Allowed, _Wins, _Losses) MUST have already been assigned values
        #Strength value calculations are now consisten i.e. gained / (gained+allowed)
        # 1. Calculate strength values for the home team
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_YTD_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Allowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_YTD_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Wins_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_YTD_HV].values[0])
        # 2. Calculate strength values for the visitor team
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_YTD_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Allowed].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Allowed_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Allowed_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Allowed_YTD].values[0]) 
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_5G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses_5G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_20G].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses_20G].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses_HV].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_YTD].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses_YTD].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_YTD_HV].values[0] = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Losses_YTD_HV].values[0])
        
    def _updateEfficiencyAttribs(self):
        #1. Calculate H efficiency values
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency_Sum
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency_Sum_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Efficiency_Sum_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. Calculate V efficiency values
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency_Sum
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency_Sum_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Efficiency_Sum_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum_5G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum_20G
        fieldValue = MLB_global.calcRunEfficiency(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
      
    def _updateMenOnBaseAttribs(self):
        #1. Calculate H Men On Base Attribs
        fieldName=MLB_dbvar.dbvar_H_MenOnBase
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Efficiency
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorMade].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_5G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Efficiency_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_5G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorMade_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_20G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Efficiency_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_20G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorMade_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_YTD
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Efficiency_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_YTD
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ErrorMade_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBase_Strength_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. Calculate H Total Bases Attribs
        fieldName=MLB_dbvar.dbvar_H_TotalBases
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_TotalBases_Sum
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_TotalBases_5G
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_TotalBases_20G
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_TotalBases_YTD
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBaseTBRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_MenOnBaseTBRatio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #3. Calculate V Men On Base Attribs
        fieldName=MLB_dbvar.dbvar_V_MenOnBase
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Efficiency
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorMade].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_5G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Efficiency_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_5G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorMade_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_20G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Efficiency_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_20G
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorMade_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_YTD
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Efficiency_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_YTD
        fieldValue = MLB_global.calcMOB(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_ErrorMade_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBase_Strength_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #4. Calculate V Total Bases Attribs
        fieldName=MLB_dbvar.dbvar_V_TotalBases
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_TotalBases_Sum
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_TotalBases_5G
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_TotalBases_20G
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_TotalBases_YTD
        fieldValue = MLB_global.calcTotalBases(self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBaseTBRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_MenOnBaseTBRatio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
   
    def _updatePythagAttribs(self):
        """
        Pythagorean expectation: the fraction of games a team would be
        expected to win given their average runs scored and allowed.

        Formula in closed form: RG^2 / (RG^2 + RA^2)
            where RG = avg Runs_Gained per game, RA = avg Runs_Allowed.

        Mathematically identical to R^2 / (R^2 + 1) where R = RG / RA, for RA > 0. 
        The closed form is preferred because it sidesteps
        MLB_global.calcRatio()'s zero-denominator behaviour:

            R = calcRatio(RG, RA)   when RA = 0 returns 0.0 (not +inf)
            -> R^2 = 0
            -> R^2 / (R^2 + 1) = 0     # WRONG: a team that gave up zero
                                       # runs gets the WORST possible
                                       # Pythag instead of the BEST (1.0).
                                       # Cascades into Pythag_Luck_Factor
                                       # as a false 'maximally lucky' signal.

        The closed form below is well-defined for all non-negative RG, RA:
            RA = 0, RG > 0  ->  RG^2 / (RG^2 + 0) = 1.0   (perfect dominance)
            RA = 0, RG = 0  ->  0 / 0 -> caught by 1e-12 guard -> 0.5 (no data)
            RA > 0          ->  identical value to the buggy 2-step calcRatio path

        See pythag.py in the MLB data-quality pipeline for the same logic
        applied to historical CSVs (recomputes H/V_Run_Pythag_* in place
        without requiring a 4-day dGEN rerun).
        """
        #1. HOME pythag
        fieldName=MLB_dbvar.dbvar_H_Run_Pythag
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Pythag_Sum
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Pythag_5G
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Pythag_20G
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Pythag_YTD
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

        fieldName=MLB_dbvar.dbvar_H_Pythag_Luck_Factor
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Pythag_Luck_Factor_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Pythag_Luck_Factor_20G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Pythag_Luck_Factor_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

        #2. VIS pythag
        fieldName=MLB_dbvar.dbvar_V_Run_Pythag
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Pythag_Sum
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Pythag_5G
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Pythag_20G
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Pythag_YTD
        # Closed-form Pythag: RG^2 / (RG^2 + RA^2).
        _rg = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD].values[0]
        _ra = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0]
        _den = _rg * _rg + _ra * _ra
        fieldValue = 0.5 if _den < 1e-12 else (_rg * _rg) / _den
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        
        fieldName=MLB_dbvar.dbvar_V_Pythag_Luck_Factor
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Pythag_Luck_Factor_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Pythag_Luck_Factor_20G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Pythag_Luck_Factor_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _updateRunDiffPerGame(self):
        #1. HOME
        fieldName=MLB_dbvar.dbvar_H_Run_Differential_Per_Game
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Differential_Per_Game_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Differential_Per_Game_20G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Run_Differential_Per_Game_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. VIS        
        fieldName=MLB_dbvar.dbvar_V_Run_Differential_Per_Game
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Differential_Per_Game_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Differential_Per_Game_20G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Run_Differential_Per_Game_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _updateWeightedOffenseIndex(self):
        #1. HOME
        fieldName=MLB_dbvar.dbvar_H_Weighted_Offense_Index
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Weighted_Offense_Index_5G
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Weighted_Offense_Index_20G
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_Weighted_Offense_Index_YTD
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. VIS        
        fieldName=MLB_dbvar.dbvar_V_Weighted_Offense_Index
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Weighted_Offense_Index_5G
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Weighted_Offense_Index_20G
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_Weighted_Offense_Index_YTD
        fieldValue =    0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0]) + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _updateAtBatDependents(self):
        #1. HOME
        fieldName=MLB_dbvar.dbvar_H_OBP
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OBP_5G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OBP_20G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OBP_YTD
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_SLG
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_SLG_5G
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_SLG_20G
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_SLG_YTD
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_wOBA
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_wOBA_5G
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_wOBA_20G
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_wOBA_YTD
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_YTD].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OPS
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_H_OBP].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SLG].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OPS_5G
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_H_OBP_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SLG_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OPS_20G
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_H_OBP_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SLG_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_OPS_YTD
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_H_OBP_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SLG_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #    
        #2. VIS       
        fieldName=MLB_dbvar.dbvar_V_OBP
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OBP_5G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OBP_20G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OBP_YTD
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_SLG
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_SLG_5G
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_5G].values[0])     
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_SLG_20G
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_SLG_YTD
        fieldValue =  MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_wOBA
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_wOBA_5G
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_wOBA_20G
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_wOBA_YTD
        fieldValue =  (0.691 * self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0] + 0.722 * self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0] + 0.882 * (self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0] + 1.252 * self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0] + 1.580 * self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0] + 2.037 * self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_YTD].values[0])) / (self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksGained_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OPS
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_V_OBP].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SLG].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OPS_5G
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_V_OBP_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SLG_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OPS_20G
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_V_OBP_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SLG_20G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_OPS_YTD
        fieldValue =  self._currentgame_df[MLB_dbvar.dbvar_V_OBP_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SLG_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _updatePitchDependents(self):
        #1. HOME.
        # ── H_FIP (10-game window) ─────────────────────────────────────
        fieldName = MLB_dbvar.dbvar_H_FIP
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0],
            min_ip = 3.0   # 10-game window: 5 IP minimum is plenty
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── H_FIP_5G (5-game window) ───────────────────────────────────
        fieldName = MLB_dbvar.dbvar_H_FIP_5G
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_5G].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_5G].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0],
            min_ip = 3.0   # 5-game window: 3 IP minimum
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── H_FIP_YTD (12-month window) ────────────────────────────────
        fieldName = MLB_dbvar.dbvar_H_FIP_YTD
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_YTD].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_YTD].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0],
            min_ip = 3.0  # 12-month window: 20 IP minimum
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── H_FIP_YTD_HV (12-month home-only window) ───────────────────
        fieldName = MLB_dbvar.dbvar_H_FIP_YTD_HV
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_YTD_HV].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD_HV].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_YTD_HV].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD_HV].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD_HV].values[0],
            min_ip = 3.0  # 12-month HV-only: stricter due to smaller sample
        )
        self._currentgame_df[fieldName].values[0] = fieldValue

        fieldName=MLB_dbvar.dbvar_H_K_Minus_BB_Pct
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0] +self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Minus_BB_Pct_5G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0] +self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_5G].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Minus_BB_Pct_20G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_20G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_20G].values[0] +self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_20G].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Minus_BB_Pct_YTD
        fieldValue = (self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0] +self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_YTD].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HR_Per_9_Allowed
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HR_Per_9_Allowed_5G
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_5G].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HR_Per_9_Allowed_20G
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_20G].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_20G].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HR_Per_9_Allowed_YTD
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Allowed_YTD].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Per_9
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained].values[0],self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Per_9_5G
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0],self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Per_9_20G
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_20G].values[0],self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_20G].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_K_Per_9_YTD
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD].values[0],self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #Correct formula is: H_BallpenOuts = H_OutsPitched - H_StartingPitcher_InningsPitched
        fieldName=MLB_dbvar.dbvar_H_BallpenOuts
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_BallpenOuts_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_BallpenOuts_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        
        # ── H_BallpenERA_Approx (10-game window team_er, YTD sp_er) ────
        # Base variant uses _YTD SP score because no 10-game SP_Score field
        # exists in the dGEN.py schema. This is by design, not a bug.
        fieldName = MLB_dbvar.dbvar_H_BallpenERA_Approx
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts].values[0],
            min_outs = 3
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── H_BallpenERA_Approx_5G (5-game window) ─────────────────────
        fieldName = MLB_dbvar.dbvar_H_BallpenERA_Approx_5G
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_5G].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts_5G].values[0],
            min_outs = 3
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── H_BallpenERA_Approx_YTD (12-month window) ──────────────────
        fieldName = MLB_dbvar.dbvar_H_BallpenERA_Approx_YTD
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_YTD].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts_YTD].values[0],
            min_outs = 5
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        #2. VIS
        # ── V_FIP (10-game window) ─────────────────────────────────────
        fieldName = MLB_dbvar.dbvar_V_FIP
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0],
            min_ip = 3.0   # 10-game window: 5 IP minimum is plenty
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── V_FIP_5G (5-game window) ───────────────────────────────────
        fieldName = MLB_dbvar.dbvar_V_FIP_5G
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_5G].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_5G].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0],
            min_ip = 3.0   # 5-game window: 3 IP minimum
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── V_FIP_YTD (12-month window) ────────────────────────────────
        fieldName = MLB_dbvar.dbvar_V_FIP_YTD
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_YTD].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_YTD].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0],
            min_ip = 3.0  # 12-month window: 20 IP minimum
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── V_FIP_YTD_HV (12-month home-only window) ───────────────────
        fieldName = MLB_dbvar.dbvar_V_FIP_YTD_HV
        fieldValue = MLB_global.computeFIP(
            hr_allowed   = self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_YTD_HV].values[0],
            walks_allowed= self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD_HV].values[0],
            hbp_allowed  = self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_YTD_HV].values[0],
            k_gained     = self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD_HV].values[0],
            outs_pitched = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD_HV].values[0],
            min_ip = 3.0  # 12-month HV-only: stricter due to smaller sample
        )
        self._currentgame_df[fieldName].values[0] = fieldValue

        fieldName=MLB_dbvar.dbvar_V_K_Minus_BB_Pct
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0] +self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Minus_BB_Pct_5G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0] +self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_5G].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Minus_BB_Pct_20G
        fieldValue =  (self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_20G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_20G].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_20G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_20G].values[0] +self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_20G].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Minus_BB_Pct_YTD
        fieldValue = (self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0]) / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0] +self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_YTD].values[0] ) + 100
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HR_Per_9_Allowed
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HR_Per_9_Allowed_5G
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_5G].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HR_Per_9_Allowed_20G
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_20G].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_20G].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HR_Per_9_Allowed_YTD
        fieldValue = 9 * (self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Allowed_YTD].values[0] / (self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0] / 3))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Per_9
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained].values[0],self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Per_9_5G
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0],self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Per_9_20G
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_20G].values[0],self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_20G].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_K_Per_9_YTD
        fieldValue = 27 * (MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD].values[0],self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0]))
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #Correct formula is: V_BallpenOuts = V_OutsPitched - V_StartingPitcher_InningsPitched
        fieldName=MLB_dbvar.dbvar_V_BallpenOuts
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_BallpenOuts_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_BallpenOuts_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        # ── V_BallpenERA_Approx (10-game window team_er, YTD sp_er) ────
        # Base variant uses _YTD SP score because no 10-game SP_Score field
        # exists in the dGEN.py schema. This is by design, not a bug.
        fieldName = MLB_dbvar.dbvar_V_BallpenERA_Approx
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts].values[0],
            min_outs = 3
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── V_BallpenERA_Approx_5G (5-game window) ─────────────────────
        fieldName = MLB_dbvar.dbvar_V_BallpenERA_Approx_5G
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_5G].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts_5G].values[0],
            min_outs = 3
        )
        self._currentgame_df[fieldName].values[0] = fieldValue
        
        # ── V_BallpenERA_Approx_YTD (12-month window) ──────────────────
        fieldName = MLB_dbvar.dbvar_V_BallpenERA_Approx_YTD
        fieldValue = MLB_global.computeBullpenERA(
            team_er      = self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_YTD].values[0],
            sp_er        = self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0],
            bullpen_outs = self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts_YTD].values[0],
            min_outs = 5
        )
        self._currentgame_df[fieldName].values[0] = fieldValue       
    
    def _updateRatioAttribs(self):
        #1. Calculate H ratios
        fieldName=MLB_dbvar.dbvar_H_StrikeoutAccuracy
        fieldValue = self._currentgame_df[fieldName].values[0] = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeoutAccuracy_Sum
        fieldValue = self._currentgame_df[fieldName].values[0] = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeoutAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeoutAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeoutAccuracy_YTD_HV
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_YTD_HV].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeAccuracy
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Strikes].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeAccuracy_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StrikeAccuracy_YTD_HV
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_YTD_HV].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Sum_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Sum_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_Sum_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_Sum_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_WalkStrikeoutRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsAllowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_WalkStrikeoutRatio_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsAllowed_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_PowerHits
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_PowerHits_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_PowerHits_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Hits_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_All
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_All
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #                  NOTE: SP WHIP and WHIP Impact has to be done seperately in the WHIP function
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Strikes_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. Calculate V ratios
        fieldName=MLB_dbvar.dbvar_V_StrikeoutAccuracy
        fieldValue = self._currentgame_df[fieldName].values[0] = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeoutAccuracy_Sum
        fieldValue = self._currentgame_df[fieldName].values[0] = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeoutAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeoutAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeoutAccuracy_YTD_HV
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_YTD_HV].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeAccuracy
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Strikes].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeAccuracy_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StrikeAccuracy_YTD_HV
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_YTD_HV].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Sum_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Sum_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_Sum_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_Sum_20G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_Sum_20G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_WalkStrikeoutRatio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsAllowed].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_WalkStrikeoutRatio_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsAllowed_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_PowerHits
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_PowerHits_Sum
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_PowerHits_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Hits_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_All
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_All
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #                  NOTE: SP WHIP and WHIP Impact has to be done seperately in the WHIP function
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_YTD
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_NP_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Strikes_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _updateEarnedRunsAttribs(self):
        # DEFENSE variable which captures the number of runs made against the pitcher MINUS any mistake made by the pitcher's team (i.e. pure effort/action by the other team's batter)
        #1. HOME earned runs
        fieldName=MLB_dbvar.dbvar_H_EarnedRuns
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRunAvg
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Innings_OutPitched].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRuns_Sum
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_Sum].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRunAvg_Sum
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Innings_OutPitched_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRuns_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_5G].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRunAvg_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Innings_OutPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRuns_Sum_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_Sum_5G].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRunAvg_Sum_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Innings_OutPitched_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRuns_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_H_ErrorForced_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_H_EarnedRunAvg_YTD
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Innings_OutPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        #2. VIS earned runs
        fieldName=MLB_dbvar.dbvar_V_EarnedRuns
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRunAvg
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Innings_OutPitched].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRuns_Sum
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_Sum].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRunAvg_Sum
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Innings_OutPitched_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRuns_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_5G].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRunAvg_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Innings_OutPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRuns_Sum_5G
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_5G].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_Sum_5G].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRunAvg_Sum_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Innings_OutPitched_Sum_5G].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRuns_YTD
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD].values[0] - self._currentgame_df[MLB_dbvar.dbvar_V_ErrorForced_YTD].values[0]
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #
        fieldName=MLB_dbvar.dbvar_V_EarnedRunAvg_YTD
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_Innings_OutPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = MLB_global.floorNumtoZero(float(fieldValue))  #

    def _updateHitsAllowedPer9InningAttribs(self):
        #1. HOME
        fieldName=MLB_dbvar.dbvar_H_HitsAllowedPer9Innings
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HitsAllowedPer9Innings_Sum
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_HitsAllowedPer9Innings_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. VIS
        fieldName=MLB_dbvar.dbvar_V_HitsAllowedPer9Innings
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HitsAllowedPer9Innings_Sum
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_Sum].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_HitsAllowedPer9Innings_5G
        fieldValue = 9 * MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
         
    def _updateWalksHitsAllowedPerInningAttribs(self):
        #1. HOME WHIP
        fieldName=MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_5G
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_YTD
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_SP_HitsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD
        # Impact = SP_WHIP / Team_WHIP.
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G
        # Impact = SP_WHIP / Team_WHIP.
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #2. VIS WHIP
        fieldName=MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_5G
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_YTD
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_SP_HitsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G
        # WHIP = (BB + Hits) / IP. Single calcRatio avoids the operator-precedence bug
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].values[0] + self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD
        # Impact = SP_WHIP / Team_WHIP. 
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G
        # Impact = SP_WHIP / Team_WHIP.
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_5G].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G
        fieldValue = MLB_global.calcRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #

    def _getVHRatioCode(self, vValue, hValue):
        #if tied then home team advantage prevails
        if vValue > hValue:
            return "V"
        else:
            return "H"

    def _buildTeamRatioCode(self):
        sepSym = "_"
        teamCode = ""
        #Build code
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_G_V_DaysRest].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_DaysRest].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_DaysRest].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_DaysRest].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_G_V_ParkImpactFactor].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ParkImpactFactor].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesV].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesV].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesH].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesH].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_HV].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_HV].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_YTD].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_YTD].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Wins].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Wins].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Losses].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Wins_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_Losses_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_20G].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeAccuracy].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeAccuracy].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRunAvg].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRunAvg].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowedPer9Innings].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowedPer9Innings].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Efficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Efficiency].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency].values[0])
        teamCode += sepSym
        teamCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_20G].values[0])
        #Update attribute value
        #fieldName=MLB_dbvar.dbvar_G_VHRatio_Team_RatioCode
        #fieldValue = teamCode
        #self._currentgame_df[fieldName].values[0] = str(fieldValue)  #

    def _buildSPRatioCode(self):
        sepSym = "_"
        spCode = ""
        #Build code
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio].values[0])
        spCode += sepSym
        spCode += self._getVHRatioCode(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio].values[0])
        #Update attribute value
        #fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_RatioCode
        #fieldValue = spCode
        #self._currentgame_df[fieldName].values[0] = str(fieldValue)  #

    def _updateVHRatioAttribs(self):
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DaysRest
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_G_V_DaysRest].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_DaysRest].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_SP_DaysRest
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_DaysRest].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_DaysRest].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_ParkImpactFactor
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_G_V_ParkImpactFactor].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ParkImpactFactor].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_ContiguousGamesV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesV].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_ContiguousGamesH
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_G_V_ContiguousGamesH].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_ContiguousGamesH].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_TotalDistanceTravelled_3G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_G_V_TotalDistanceTravelled_3G].values[0], self._currentgame_df[MLB_dbvar.dbvar_G_H_TotalDistanceTravelled_3G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_ClosingProbabilityLine_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_ClosingProbabilityLine_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ClosingProbabilityLine_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_ClosingProbabilityLine_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_ClosingProbabilityLine_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Pythag
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Pythag_Luck_Factor
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Pythag_Luck_Factor].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Pythag_Luck_Factor].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Pythag_Luck_Factor_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Pythag_Luck_Factor_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Pythag_Luck_Factor_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Pythag_Luck_Factor_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Pythag_Luck_Factor_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Pythag_Luck_Factor_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Pythag_Luck_Factor_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Pythag_Luck_Factor_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Pythag_Luck_Factor_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Differential_Per_Game
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Differential_Per_Game].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Differential_Per_Game].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Differential_Per_Game_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Differential_Per_Game_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Differential_Per_Game_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Differential_Per_Game_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Differential_Per_Game_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Differential_Per_Game_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Differential_Per_Game_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Differential_Per_Game_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Differential_Per_Game_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Weighted_Offense_Index
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Weighted_Offense_Index].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Weighted_Offense_Index].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Weighted_Offense_Index_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Weighted_Offense_Index_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Weighted_Offense_Index_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Weighted_Offense_Index_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Weighted_Offense_Index_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Weighted_Offense_Index_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Weighted_Offense_Index_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Weighted_Offense_Index_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Weighted_Offense_Index_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_At_Bat_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_At_Bat_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_At_Bat_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OBP
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OBP].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OBP].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OBP_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OBP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OBP_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OBP_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OBP_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OBP_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OBP_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OBP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OBP_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_SLG
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SLG].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_SLG].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_SLG_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SLG_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_SLG_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_SLG_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SLG_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_SLG_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_SLG_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_SLG_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_SLG_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_wOBA
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_wOBA].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_wOBA].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_wOBA_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_wOBA_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_wOBA_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_wOBA_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_wOBA_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_wOBA_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_wOBA_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_wOBA_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_wOBA_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OPS
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OPS].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OPS].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OPS_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OPS_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OPS_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OPS_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OPS_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OPS_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OPS_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OPS_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OPS_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Pythag_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Pythag_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Pythag_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Pythag_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Gained_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Gained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Gained_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_Allowed_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_Allowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_Allowed_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Strength_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_Efficiency_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_Efficiency_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_Efficiency_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsStrength_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsStrength_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Run_5InningsEfficiency_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Run_5InningsEfficiency_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsGained_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsGained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsGained_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Runs_5InningsAllowed_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Runs_5InningsAllowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Runs_5InningsAllowed_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Wins
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Wins].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Losses
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Losses].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WinLoss_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Wins_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Wins_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Losses_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Losses_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WinLoss_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Wins_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Wins_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Wins_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_Losses_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_Losses_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_Losses_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WinLoss_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WinLoss_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WinLoss_Strength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_OutsPitched_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_OutsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_OutsPitched_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeAccuracy
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeAccuracy].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeAccuracy].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeAccuracy_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeAccuracy_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeAccuracy_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsGained
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsAllowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsAllowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsAccuracy
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutAccuracy].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutAccuracy].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsGained_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsAllowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsAllowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsAccuracy_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutAccuracy_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutAccuracy_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRunAvg
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRunAvg].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRunAvg].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns_Avg_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRunAvg_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRunAvg_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRunAvg_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRunAvg_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRuns_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRuns_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_EarnedRunAvg_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_EarnedRunAvg_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_EarnedRunAvg_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio_Allowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_RunsHitsRatio_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_RunsHitsRatio_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_FIP_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_FIP_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_FIP_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Minus_BB_Pct_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Minus_BB_Pct_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Minus_BB_Pct_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HR_Per_9_Allowed_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HR_Per_9_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HR_Per_9_Allowed_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_K_Per_9_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_K_Per_9_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_K_Per_9_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed_Sum
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_Sum].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_Sum].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed_Sum_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_Sum_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_Sum_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_WalksAllowed_Sum_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_WalksAllowed_Sum_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_WalksAllowed_Sum_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_PowerHits
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_PowerHits].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_PowerHits].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_PowerHits_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_PowerHits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_PowerHits_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsAllowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsAllowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsAllowedPer9Innings
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowedPer9Innings].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowedPer9Innings].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsAllowedPer9Innings_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsAllowedPer9Innings_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsAllowedPer9Innings_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsByPitch_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsByPitch_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HitsByPitch_Allowed_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HitsByPitch_Allowed_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StrikeoutsGained_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StrikeoutsGained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StrikeoutsGained_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_2BRuns_Strength_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_2BRuns_Strength_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_2BRuns_Strength_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_3BRuns_Strength_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_3BRuns_Strength_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_3BRuns_Strength_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HomeRuns_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_HomeRuns_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_HomeRuns_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_HomeRuns_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Gained_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Gained_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Gained_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Gained_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Gained_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Allowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Allowed_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_DoublePlays_Allowed_YTD_HV].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_DoublePlays_Allowed_YTD_HV].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_TotalBases
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_TotalBases_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_TotalBases_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_TotalBases_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_TotalBases_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_TotalBases_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBaseTBRatio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBaseTBRatio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBaseTBRatio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBaseTBRatio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBaseTBRatio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBaseTBRatio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Strength
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Strength].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Strength].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Efficiency
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Efficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Efficiency].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Strength_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Strength_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Strength_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Efficiency_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Efficiency_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Efficiency_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Strength_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Strength_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Strength_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Efficiency_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Efficiency_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Efficiency_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Strength_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Strength_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Strength_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_20G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_20G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_MenOnBase_Allowed_Efficiency_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_MenOnBase_Allowed_Efficiency_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NPImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenOuts
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenOuts_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenOuts_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenOuts_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenOuts_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenERA_Approx
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenERA_Approx].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenERA_Approx].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenERA_Approx_5G
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenERA_Approx_5G].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenERA_Approx_5G].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        fieldName=MLB_dbvar.dbvar_G_VHRatio_BallpenERA_Approx_YTD
        fieldValue = MLB_global.calcProbRatio(self._currentgame_df[MLB_dbvar.dbvar_V_BallpenERA_Approx_YTD].values[0], self._currentgame_df[MLB_dbvar.dbvar_H_BallpenERA_Approx_YTD].values[0], True)
        self._currentgame_df[fieldName].values[0] = float(fieldValue)  #
        #Build team and sp ratio codes
        #self._buildTeamRatioCode()
        #self._buildSPRatioCode()
        
    def _updateBookieTargetAttribs(self):
        # Only those target attributes that are directly dependent on the currently available data will be updated
        
        # dbvar_G_H_AdjBookieProbabilityLine
        fieldName=MLB_dbvar.dbvar_G_H_AdjBookieProbabilityLine
        bookieProb = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_Probability].values[0]
        fieldValue = bookieProb
        if self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0] > self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]:
            fieldValue -= MLB_global.BOOKIEPROBADJVAL
        else:
            if self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0] <= self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]:
                fieldValue += MLB_global.BOOKIEPROBADJVAL
        #validate
        if fieldValue > MLB_global.BOOKIEPROBADJ_MAX: 
            fieldValue = MLB_global.BOOKIEPROBADJ_MAX
        else: 
            if fieldValue < MLB_global.BOOKIEPROBADJ_MIN: fieldValue = MLB_global.BOOKIEPROBADJ_MIN
        self._currentgame_df[fieldName].values[0] = float(fieldValue)

        # dbvar_G_BookieAdjustedTotal
        fieldName=MLB_dbvar.dbvar_G_BookieAdjustedTotal
        bookieTotal = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0]
        actualTotal = self._currentgame_df[MLB_dbvar.dbvar_G_Total].values[0]
        fieldValue = bookieTotal
        if actualTotal > bookieTotal:
            fieldValue += MLB_global.BOOKIETOTADJVAL
        else:
            if actualTotal < bookieTotal:
                fieldValue -= MLB_global.BOOKIETOTADJVAL
        #validate
        if fieldValue < 0: fieldValue = 0
        self._currentgame_df[fieldName].values[0] = float(fieldValue)

        # dbvar_G_Total_IsOver
        fieldName=MLB_dbvar.dbvar_G_Total_IsOver
        bookieTotal = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0]
        actualTotal = self._currentgame_df[MLB_dbvar.dbvar_G_Total].values[0]
        fieldValue = MLB_dbvar.G_TIE
        if actualTotal > bookieTotal:
            fieldValue = MLB_dbvar.G_WIN
        else:
            if actualTotal < bookieTotal:
                fieldValue = MLB_dbvar.G_LOSE
        self._currentgame_df[fieldName].values[0] = int(fieldValue)

        # G_Bookie_Prob_Bet
        fieldName=MLB_dbvar.dbvar_G_Bookie_Prob_Bet
        bookieHML = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0]
        bookieVML = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0]
        h_runs = self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        v_runs = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        fieldValue = MLB_global.ACTION_LINE_TIE
        if h_runs != v_runs:
            if bookieHML < bookieVML: #Home is fave
                if h_runs > v_runs:
                    fieldValue = MLB_global.ACTION_LINE_HF
                else:
                    fieldValue = MLB_global.ACTION_LINE_VD
            else:
                if h_runs < v_runs:
                    fieldValue = MLB_global.ACTION_LINE_VF
                else:
                    fieldValue = MLB_global.ACTION_LINE_HD
        self._currentgame_df[fieldName].values[0] = str(fieldValue)

        # G_Bookie_FaveWin 
        fieldName=MLB_dbvar.dbvar_G_Bookie_FaveWin
        bookieHML = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0]
        bookieVML = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0]
        h_runs = self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        v_runs = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        fieldValue = MLB_dbvar.G_TIE
        if h_runs != v_runs:
            if bookieHML < bookieVML: #Home is fave
                if h_runs > v_runs:
                    fieldValue = MLB_dbvar.G_WIN
                else:
                    fieldValue = MLB_dbvar.G_LOSE
            else:
                if h_runs < v_runs:
                    fieldValue = MLB_dbvar.G_WIN
                else:
                    fieldValue = MLB_dbvar.G_LOSE
        self._currentgame_df[fieldName].values[0] = int(fieldValue)

        # G_Bookie_DogWin 
        fieldName=MLB_dbvar.dbvar_G_Bookie_DogWin
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_FaveWin].values[0]
        if fieldValue == MLB_dbvar.G_WIN: #Fave won so dog lose
            fieldValue = MLB_dbvar.G_LOSE
        else:
            if fieldValue == MLB_dbvar.G_LOSE: #dog won
                fieldValue = MLB_dbvar.G_WIN
        self._currentgame_df[fieldName].values[0] = int(fieldValue)
        
    def _updateTargetAttribs(self):
        # G_level primitives must already have been populated by dBASE eg G_H_Runs, G_V_Runs, G_CLT
        # Only those target attributes that are directly dependent on the currently available data will be updated
        # Any attributes relying on the insample average or other preprocessing will not be updated
        
        # G_PH_Win
        fieldName=MLB_dbvar.dbvar_G_PH_Win
        _hRuns = self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        _vRuns = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        fieldValue = MLB_dbvar.G_TIE
        if(_vRuns < _hRuns):
            fieldValue=MLB_dbvar.G_WIN
        else:
            if(_vRuns > _hRuns):
                fieldValue=MLB_dbvar.G_LOSE
        self._currentgame_df[fieldName].values[0] = int(fieldValue)
     
        # G_PV_Win
        fieldName=MLB_dbvar.dbvar_G_PV_Win
        _hRuns = self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        _vRuns = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        fieldValue = MLB_dbvar.G_TIE
        if(_vRuns > _hRuns):
            fieldValue=MLB_dbvar.G_WIN
        else:
            if(_vRuns < _hRuns):
                fieldValue=MLB_dbvar.G_LOSE
        self._currentgame_df[fieldName].values[0] = int(fieldValue)

        # dbvar_G_H_Run_Prediction 
        fieldName=MLB_dbvar.dbvar_G_H_Run_Prediction
        runs = self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        fieldValue = MLB_dbvar.getRunCategory(runs)
        self._currentgame_df[fieldName].values[0] = str(fieldValue)

        # dbvar_G_V_Run_Prediction
        fieldName=MLB_dbvar.dbvar_G_V_Run_Prediction
        runs = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0]
        fieldValue = MLB_dbvar.getRunCategory(runs)
        self._currentgame_df[fieldName].values[0] = str(fieldValue)

        # dbvar_G_Actual_Runs_Diff
        fieldName=MLB_dbvar.dbvar_G_Actual_Runs_Diff
        fieldValue = self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0] - self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0]
        self._currentgame_df[fieldName].values[0] = float(fieldValue)

        # dbvar_G_ABSActual_Runs_Diff
        fieldName=MLB_dbvar.dbvar_G_ABSActual_Runs_Diff
        fieldValue = math.fabs(self._currentgame_df[MLB_dbvar.dbvar_G_V_Runs].values[0] - self._currentgame_df[MLB_dbvar.dbvar_G_H_Runs].values[0])
        self._currentgame_df[fieldName].values[0] = float(fieldValue)

         # dbvar_G_ABSActual_Runs_DiffCategory
        fieldName=MLB_dbvar.dbvar_G_ABSActual_Runs_DiffCategory
        runs = self._currentgame_df[MLB_dbvar.dbvar_G_ABSActual_Runs_Diff].values[0]
        fieldValue = MLB_dbvar.getRunCategory(runs)
        self._currentgame_df[fieldName].values[0] = str(fieldValue)

        #update BookieTargetAttribs
        self._updateBookieTargetAttribs()

    def _updateDependentAttribs(self):
        #ASSUMPTION: all primitive attribs MUST already have been assigned a value
        # ORDER IS IMPORTANT
        self._updateLeagueDivAttribs()
        self._updateOvertimeAttribs()
        self._updateDistanceTravelledAttribs()
        self._updateStrengthAttribs()
        self._updateEfficiencyAttribs()
        self._updateMenOnBaseAttribs()
        self._updatePythagAttribs()
        self._updateRatioAttribs()
        self._updateEarnedRunsAttribs()
        self._updateHitsAllowedPer9InningAttribs()
        self._updateWalksHitsAllowedPerInningAttribs()
        self._updateRunDiffPerGame()
        self._updateWeightedOffenseIndex()
        self._updateAtBatDependents()
        self._updatePitchDependents()
        self._updateVHRatioAttribs()
        self._updateTargetAttribs()

    def getAvgPointStrength(self, h_or_v):
        #Assumption 1: game strengths have been calculated
        #Assumption 2: It is the window-based average game strength being requested
        if h_or_v == MLB_global.HOME:
            return self._currentgame_df[MLB_dbvar.dbvar_H_Run_Strength].values[0]
        else:
            return self._currentgame_df[MLB_dbvar.dbvar_V_Run_Strength].values[0]
    
    def _setBookieProbMLToOPL(self):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_Probability].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_H_OpeningProbabilityLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_Probability].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_V_OpeningProbabilityLine].values[0])
    
    def _setBookieProbMLToCLL(self):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_Probability].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_Probability].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0])

    def _setBookieMLProb(self, moneyLine, h_or_v):
        if h_or_v == MLB_global.HOME:
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_MoneyLine].values[0] = float(moneyLine)
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_H_Probability].values[0] = MLB_global.convertMoneyLinetoProb(moneyLine)
        else:
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_MoneyLine].values[0] = float(moneyLine)
            self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_V_Probability].values[0] = MLB_global.convertMoneyLinetoProb(moneyLine)
    
    def _setBookieTotalToOPT(self):
        #Assumption 1: assumes self._currentgame_df is populated with data from raw master db which will have bookie information
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_Opening_TotalOver].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOverLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_Opening_TotalOverLine].values[0])
    
    def _setBookieTotalToCLT(self):
        #Assumption 1: assumes self._currentgame_df is populated with data from raw master db which will have bookie information
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOver].values[0])
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOverLine].values[0] = float(self._currentgame_df[MLB_dbvar.dbvar_G_Closing_TotalOverLine].values[0])
           
    def _setBookieTotal(self, totalValue):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOver].values[0] = float(totalValue)
    
    def _setBookieTotalLine(self, totalValue):
        self._currentgame_df[MLB_dbvar.dbvar_G_Bookie_TotalOverLine].values[0] = float(totalValue)

    def _setGameNoDataToZero(self):
        #Simply checks self._game_df for NFL_dbvar.NO_DATA and replaces with 0
        self._currentgame_df = self._currentgame_df.replace(int(MLB_dbvar.NO_DATA), 0)
        self._currentgame_df = self._currentgame_df.replace(float(MLB_dbvar.NO_DATA), 0.0)
                
    def _writeWindowEntryBanner(self, fileHandle):
        fileHandle.write("\n\n/**\t\t\tBEGIN: Process Non-YTD Attributes\t\t\t**/\n")
    
    def _writeWindowExitBanner(self, fileHandle):
        fileHandle.write("\n\n/**\t\t\tEND: Process Non-YTD Attributes\t\t\t**/\n")
        
    def _writeYTDEntryBanner(self, fileHandle):
        #Assumption 1: ytd dictionaries and assoc. length vars MUST have been populated BEFORE this func is called
        # for ytd
        fileHandle.write("\n\n/**\t\t\tBEGIN: Process Team-level YTD Attributes\t\t\t**/\n")
        fileHandle.write("\nSearching for historical games within the following date range:")
        fileHandle.write("\nYTD Window Start Date : " + self._ytd_window_start_date.strftime('%Y-%m-%d'))
        fileHandle.write("\nYTD Window End Date : " + self._ytd_window_end_date.strftime('%Y-%m-%d'))
        fileHandle.write("\nA total of " + str(self._ytd_window_size) + " games were discovered within this date range and will be used to calculate averages/totals for any YTD attributes.")
        
    def _writeYTDExitBanner(self, fileHandle):
        fileHandle.write("\n\n/**\t\t\tEND: Process Team-level YTD Attributes\t\t\t**/\n")
        
    def _writePlayerEntryBanner(self, fileHandle):
        fileHandle.write("\n\n/**\t\t\tBEGIN: Process Player-level Attributes\t\t\t**/\n")

    def _writePlayerExitBanner(self, fileHandle):
        fileHandle.write("\n\n/**\t\t\tEND: Process Player-level Attributes\t\t\t**/\n")
    
    def _updateGeneratedDataSet(self):
        self._processedgames_df = pd.concat([self._processedgames_df, self._currentgame_df])
        
    def storeGeneratedDataSet(self):
        #Assumption 1. Assumes self._processedgames_df has been fully populated
        #Assumption 2. Copies will be stored in cwd and dgen log directory
        #a. Create filename
        now = datetime.today()
        self._processed_games_fname_csv = os.path.join(self.dgen_root_wd, self._results_fname_stem)
        self._processed_games_subfolder_fname_csv = os.path.join(self.dgen_wd, self._results_fname_stem)
        #b. Write files to disk
        self._processedgames_df.to_csv(self._processed_games_fname_csv, index=False, header=True)
        self._processedgames_df.to_csv(self._processed_games_subfolder_fname_csv, index=False, header=True)
    
    def displayExitMessage(self):
        print("\nThe dGEN results for this run are stored in the file " + str(self._results_fname_stem) + " which is located in folders " + str(self.dgen_root_wd) + " and " + str(self.dgen_wd) + "\n")
        self.dgenLOG.displayExitMessage()
    
    def _storeCurrentGameData(self):
        #Assumption: Data has been geenrated and categorical variables dealt with BEFORE this function is called
        # Task information must be provided
        try:
            #create filenames
            now = datetime.today()
            self._game_fname_csv = MLB_global.DATA_FNAME_STEM + "_H_" + str(self._home_id) + "_V_" + str(self._vis_id) + "_" + self._game_date.strftime('%Y%m%d') + "_RAWDATA_" + now.strftime('%Y%m%d%H%M%S') + ".csv"
            self._game_fname_csv = os.path.join(self.dgen_wd, self._game_fname_csv)
            #store data
            self._currentgame_df.to_csv(self._game_fname_csv, index=False)
            
        except Exception:
            print("\nscionDGEN.storeCurrentGameData(): unexpected error storing generated game data to csv files.\n")
            raise
        
    def updateLogStatus(self, logMessage):
        #Assumption 1: this has been called due to skip game condition becoming true i.e. self._skip_game = True
        #Assumption 2: self._skip_game_reason has been assigned the relevant error message
        self._skip_game_reason = logMessage
        self.dgenLOG.addStatusUpdate(logMessage)
        
    def updateGameInstances(self, gameInstances):
        self.dgenLOG.setCurrentGameInstances(gameInstances)

    def _generateTeamData(self, h_or_v):
        #1. Get team
        if h_or_v == MLB_global.HOME:
            team_id = self._home_id
            fileHandle = self._home_logfile_fh
        else:
            team_id = self._vis_id
            fileHandle = self._vis_logfile_fh
        #2. Initialise dates and dicts
        self._initGenDates()
        self._initGenDicts()
        #3. generate team-level data
        #a. Get and sort home team game data
        if self._history_within_season == MLB_global.YES:
            self._applyHistoryWithinSeason()
        else:
            #BE CAREFUL WITH DICTS: dicts are by reference so if we do not do deep copies then we change the original (see https://stackoverflow.com/questions/2465921/how-to-copy-a-dictionary-and-only-edit-the-copy) and https://stackoverflow.com/questions/15078519/python-dictionary-passed-as-an-input-to-a-function-acts-like-a-global-in-that-fu
            self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id)
            self._all_historical_games = copy.deepcopy(self._historical_games) #this is needed for lookback; NB deepcopy doesnt copy the order of dict so no benefit in ordering then copying
        self._skip_game = not self._enoughGames()
        if self._skip_game:
            self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataHOME)
            return
        self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True) #It appears to work in that self._historical_homes remains unordered and self._ordered_historical_home_game is an ordered version!
        self._all_historical_games = self._orderTeamGameDict(self._all_historical_games, True)
        #b. get a self._window_size of historical data from self._ordered_historical_games
        self._getWindowData(fileHandle, self._window_size, self._ordered_historical_games, self._all_historical_games) #this will change the original dicts that we've passed as input
        if self._skip_game:
            if h_or_v == MLB_global.HOME:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataHOME)
            else:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataVIS)
            return
        #c. populate G var ContiguousGamesV and ContiguousGamesV given self._window_HVstatus has now been populated
        self._populateContiguousGameFields(h_or_v)
        #d. populate lookback fields
        self._populateLookbackFields(h_or_v, fileHandle)
        #e. populate lookahead fields (WE CAN ONLY USE GAMES WITHIN THE SAME SEASON)
        self._populateLookAheadFields(h_or_v, fileHandle)
        #f. calculate window-based statistics (ensure flags are correctly set before each call _calcFeatureStats)
        self._writeWindowEntryBanner(fileHandle)
        fileHandle.write("\nCalculating window-based averages...")
        self._use_base_attrib = False
        self._is_G_base_attrib = False
        self._is_Avg = True
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_ATTRIB, None, fileHandle)
        self._use_base_attrib = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_IPATTRIB, MLB_dbvar.TEAM_AVG_BASE_IPATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_HITSALLATTRIB, MLB_dbvar.TEAM_AVG_BASE_HITSALLATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating averaged values w.r.t H/V....")
        self._is_Avg = True
        self._is_HV = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_HVATTRIB, MLB_dbvar.TEAM_AVG_BASE_HVATTRIB, fileHandle)
        self._is_G_base_attrib = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_LINE_HVATTRIB, MLB_dbvar.TEAM_AVG_LINEBASE_ATTRIB, fileHandle)
        self._is_G_base_attrib = False
        fileHandle.write("done. \nCalculating cumulative total values across the window....")
        self._is_Avg = False
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_STATS_ATTRIB, MLB_dbvar.TEAM_SUM_STATSBASE_ATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_IPATTRIB, MLB_dbvar.TEAM_SUM_BASE_IPATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_HITSALLATTRIB, MLB_dbvar.TEAM_SUM_BASE_HITSALLATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_ATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating cumulative total values w.r.t H/V....")
        self._is_HV = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_STATS_HVATTRIB, MLB_dbvar.TEAM_SUM_STATSBASE_HVATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_HVATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.")
        #g. calculate g5-based statistics (ensure flags are correctly set before each call _calcFeatureStats)
        self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, self._g5_window_start_date, self._g5_window_end_date)
        self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
        self._getWindowData(fileHandle, self._g5_window_size, self._ordered_historical_games, self._all_historical_games) #this will change the original dicts that we've passed as input
        if self._skip_game:
            if h_or_v == MLB_global.HOME:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataHOME)
            else:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataVIS)
            return
        fileHandle.write("\nCalculating 5 game averages...")
        self._use_base_attrib = True
        self._is_Avg = True
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_5GATTRIB, MLB_dbvar.TEAM_AVG_BASE_5GATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_IP_5GATTRIB, MLB_dbvar.TEAM_AVG_BASE_IPATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_HITSALL_5GATTRIB, MLB_dbvar.TEAM_AVG_BASE_HITSALLATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating 5 game averages w.r.t H/V....")
        self._is_Avg = True
        self._is_HV = True
        fileHandle.write("done. There are no 5 game H/V features!")
        fileHandle.write("\nCalculating 5 game cumulative total values across the window....")
        self._is_Avg = False
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_STATS_5GATTRIB, MLB_dbvar.TEAM_SUM_STATSBASE_5GATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_IP_5GATTRIB, MLB_dbvar.TEAM_SUM_BASE_IPATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_5GATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.")
        self._writeWindowExitBanner(fileHandle)
        #h. calculate g20-based statistics (ensure flags are correctly set before each call _calcFeatureStats)
        self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, self._g20_window_start_date, self._g20_window_end_date)
        self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
        self._getWindowData(fileHandle, self._g20_window_size, self._ordered_historical_games, self._all_historical_games) #this will change the original dicts that we've passed as input
        if self._skip_game:
            if h_or_v == MLB_global.HOME:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataHOME)
            else:
                self.updateLogStatus(MLB_global.messageGameSkipNotEnoughDataVIS)
            return
        fileHandle.write("\nCalculating 20 game averages...")
        self._use_base_attrib = True
        self._is_Avg = True
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_20GATTRIB, MLB_dbvar.TEAM_AVG_BASE_20GATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating 20 game averages w.r.t H/V....")
        self._is_Avg = True
        self._is_HV = True
        fileHandle.write("done. There are no 20 game H/V features!")
        fileHandle.write("\nCalculating 20 game cumulative total values across the window....")
        self._is_Avg = False
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_STATS_20GATTRIB, MLB_dbvar.TEAM_SUM_STATSBASE_20GATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_20GATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.")
        self._writeWindowExitBanner(fileHandle)
        #i. calculate YTD-based statistics (ensure flags are correctly set before each call _calcFeatureStats)
        self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, self._ytd_window_start_date, self._ytd_window_end_date)
        self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
        self._ytd_window_size = len(self._ordered_historical_games)
        self._writeYTDEntryBanner(fileHandle)
        fileHandle.write("\nCalculating YTD-based averages...")
        self._use_base_attrib = True
        self._is_Avg = True
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_YTDATTRIB, MLB_dbvar.TEAM_AVG_BASE_YTDATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_IP_YTDATTRIB, MLB_dbvar.TEAM_AVG_BASE_IPATTRIB, fileHandle)
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_HITSALL_YTDATTRIB, MLB_dbvar.TEAM_AVG_BASE_HITSALLATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating averaged values w.r.t H/V....")
        self._is_Avg = True
        self._is_HV = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_YTDHVATTRIB, MLB_dbvar.TEAM_AVG_BASE_YTDHVATTRIB, fileHandle)
        self._is_G_base_attrib = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_AVG_LINE_YTDHVATTRIB, MLB_dbvar.TEAM_AVG_LINEBASE_ATTRIB, fileHandle)
        self._is_G_base_attrib = False
        fileHandle.write("done. \nCalculating cumulative total values across the window....")
        self._is_Avg = False
        self._is_HV = False
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_YTDATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.\nCalculating cumulative total values w.r.t H/V....")
        self._is_HV = True
        self._calcFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.TEAM_SUM_WL_YTDHVATTRIB, MLB_dbvar.TEAM_SUM_WLBASE_ATTRIB, fileHandle)
        fileHandle.write("done.\n")
        self._writeYTDExitBanner(fileHandle)
        #j. calculate Player-level statistics (YTD and All attribs)
        self._writePlayerEntryBanner(fileHandle)
        self._use_base_attrib = False
        self._is_Avg = True
        self._is_HV = False
        #1) Player YTD
        self._initGenDates()
        self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, self._ytd_window_start_date, self._ytd_window_end_date)
        self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
        self._pitcher_window_size = len(self._ordered_historical_games)
        fileHandle.write("\nCalculating YTD-based Starting Pitcher averages...")
        #Assumption: if a SP has not been active for the last 12 months they are considered a new or null pitcher
        self._pitcher_games_ytd = self._calcPitcherFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.PLAYER_AVG_YTDATTRIB, None, fileHandle, None)
        if not self._pitcher_games_ytd: #if no YTD data, then add averages to _ALL and _YTD vars
            fileHandle.write("no data found for pitcher within the last year...you will need to initialise the pitcher stats to insample averages for _5G, _YTD and _ALL features!")
        else:    
            fileHandle.write("done. " + str(self._pitcher_games_ytd) + " pitcher games processed!")
            self._use_base_attrib = True
            #2) Player 5G
            fileHandle.write("\nCalculating Starting Pitcher averages based on their previous 5 games....")
            player5gStartDate = self._window_end_date
            self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, player5gStartDate, self._g5_window_end_date)
            self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
            self._pitcher_window_size = len(self._ordered_historical_games)
            self._pitcher_games_5g = self._calcPitcherFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.PLAYER_AVG_5GATTRIB, MLB_dbvar.PLAYER_AVG_YTDATTRIB, fileHandle, self._g5_window_size)
            fileHandle.write("done. " + str(self._pitcher_games_5g) + " pitcher games processed!")
            #3) Player ALL
            fileHandle.write("\nCalculating Starting Pitcher averages based on ALL available historical data....")
            playerAllStartDate = self._window_end_date
            self._historical_games = self.masterDB.getTeamGames(self._game_date, team_id, None, playerAllStartDate, self._ytd_window_end_date)
            self._ordered_historical_games = self._orderTeamGameDict(self._historical_games, True)
            self._pitcher_window_size = len(self._ordered_historical_games)
            self._pitcher_games_all = self._calcPitcherFeatureStats(h_or_v, self._ordered_historical_games, MLB_dbvar.PLAYER_AVG_ALLATTRIB, MLB_dbvar.PLAYER_AVG_YTDATTRIB, fileHandle, None)
            fileHandle.write("done. " + str(self._pitcher_games_all) + " pitcher games processed!")
            self._use_base_attrib = False
        fileHandle.write("\nCalculating Starting Pitcher number of days rest since their last game....")
        self._updatePitcherDaysRest(h_or_v, self._ordered_historical_games)
        fileHandle.write("done. ")
        self._writePlayerExitBanner(fileHandle)
        
    def generateGameData(self, gameId, gameCtr):
        try:
            # Assumption 1: Game data has been read in and appropriate vars, dicts and file handles have been initialised
            # Assumption 2: _calcFeatureStats will set the skip_game flag to True if there are insufficient games to process and generateGameData will report the reason
            # Assumption 3: The calling program will check the self._skip_game flag after calling this program
                                          
            #1. sort masterdb by Date in descending order as we'll be working from most recent back
            self.masterDB.sortMasterDB(MLB_dbvar.dbvar_G_Date,False)
            #2. open team logs
            self._openTeamLogFiles()
            #3. Initialise dataframe with base information (bookie lines and V_distance travelled for the game...REALLY important it is done here)
            self._initGameData()
            if self._skip_game: return 
            self._generateTeamData(MLB_global.HOME)
            if self._skip_game: return    
            #4. Generate data for Vis team
            self._generateTeamData(MLB_global.VISITOR)
            if self._skip_game: return    
            #5. Close team log files
            self._closeTeamLogFiles()
            #6. Replace NO_DATA values with 0 (essential for outsample simulations with games near beginning of dB and to stop incorrect computations with dependent vars)
            self._setGameNoDataToZero()
            #7. Update dependent attributes
            self._updateDependentAttribs()
            #8. Store generated data for inspection purposes
            self._storeCurrentGameData()
            #9. Update dGEN output and signify that the data has been generated
            self._updateGeneratedDataSet()
            self._data_generated = True
            #10. Save generated data IF gameCtr is divisible by SAVE FACTOR
            if gameCtr % MLB_global.RESULTS_SAVE_FACTOR == 0:
                self.storeGeneratedDataSet()
                
        except:
            print("\nscionDGEN.generateGameData(): unexpected error generating game data.\n")
            raise
    
    def _calcIntermediateProb(self, _opl, _cll):
        _pDiff = _cll - _opl
        _pDelta = math.fabs(_pDiff)/2

        if _pDiff < 0:
            return _opl - _pDelta
        else:
            return _opl + _pDelta

    def spanToCLL(self):
        # This function generates a further two possible game instances, one with an intermediate moneyline and another with the closing line (so either 1 or 3 instances will be stored per game: 1 if opl and cll are equal or 3 if they're different as we'll be able to generate an intermediate line
        # For all non OPL lines, the CLT will be used for the total and total line.
        # The only columns of self._currentgame_df that will be updated by this function are: 
        #       dbvar_G_Bookie_H_MoneyLine, dbvar_G_Bookie_H_Probability, dbvar_G_Bookie_V_MoneyLine, dbvar_G_Bookie_V_Probability
        # Due to simpler more accurate maths: moneylines are converted to probabilities, transformed and then converted back to moneylines
        # This function will also update the log
        # Assumption 1: self._currentgame_df has been populated with opening lines and stats and has been stored in self._processedgames_df
        # Assumption 2: the intermediate lines will be calculated based on abs(CLL_prob - OPL_prob) / 2 for H and V separately
        # Assumption 3: This function will not be called if the game was skipped
        try:
            #1. Iniitalise key variable values
            _clt = self._getCurrentCLT()
            self._setBookieTotalToCLT() #opt already appeared with opl, so set total to clt
            gameInstances = 1 #opl already stored

            #2. Convert to probabilities
            _oplH = self._getCurrent_H_OML()
            _oplProbH = MLB_global.convertMoneyLinetoProb(_oplH)
            _oplV = self._getCurrent_V_OML()
            _oplProbV = MLB_global.convertMoneyLinetoProb(_oplV)
            _cllH = self._getCurrent_H_CML() #only needed for debug purposes
            _cllProbH = MLB_global.convertMoneyLinetoProb(_cllH)
            _cllV = self._getCurrent_V_CML() #only needed for debug purposes
            _cllProbV = MLB_global.convertMoneyLinetoProb(_cllV)
            
            #3. If cll <> opl then Calculate intermediate probabilities
            if _cllH != _oplH:
                #3.1 calc im prob
                _intProbH = self._calcIntermediateProb(_oplProbH, _cllProbH)
                _intProbV = self._calcIntermediateProb(_oplProbV, _cllProbV)
                #3.2 Convert to intermediate MoneyLines
                _intMLH = MLB_global.convertProbtoMoneyLine(_intProbH)
                _intMLV = MLB_global.convertProbtoMoneyLine(_intProbV)
                #3.3 Add intermediate line for H and V
                self._setCurrentBookieMoneyLine(MLB_global.HOME, _intMLH)
                self._setCurrentBookieMoneyLine(MLB_global.VISITOR, _intMLV)
                #3.4 Update data
                self._updateBookieTargetAttribs()
                self._updateGeneratedDataSet()
                #3.5 Add closing lines
                self._setBookieProbMLToCLL()
                #3.6 Update data
                self._updateBookieTargetAttribs()
                self._updateGeneratedDataSet()
                #3.7 Update game instances
                gameInstances = 3 #opl, intermediate, cll

            #4. Update dGEN logs (to indicate success for original OPL and also any amendments implemented here)
            self.updateGameInstances(gameInstances)
            self.updateLogStatus(MLB_global.messageGameDataSuccess)
            self.updateGameLogDataFrame()
            self.storeGameLogData()
        except:
            print("\nscionDGEN.spanToCLL(): unexpected error when spanning to CLL after core data generated.\n")
            raise
    
    def resetGenerateGameStatus(self): #important for span
        self._data_generated = False
     
    #getters
    @property
    def skip_game(self): 
        return self._skip_game
    @property
    def skip_game_reason(self):
        return self._skip_game_reason
    @property
    def data_generated(self):
        return self._data_generated
    @property
    def game_df(self):
        return self._currentgame_df
    @property
    def game_fname_csv(self):
        return self._game_fname_csv
    @property
    def home_log_fname_txt(self):
        return self._home_log_fname_txt
    @property
    def vis_log_fname_txt(self):
        return self._vis_log_fname_txt
    
'''
###Pythonic way for using getters/setters (FOR LATER)
 class C(object):
    def __init__(self):
        self._x = None

    @property
    def x(self):
        """I'm the 'x' property."""
        print("getter of x called")
        return self._x

    @x.setter
    def x(self, value):
        print("setter of x called")
        self._x = value

    @x.deleter
    def x(self):
        print("deleter of x called")
        del self._x


c = C()
c.x = 'foo'  # setter called
foo = c.x    # getter called
del c.x      # deleter called

'''