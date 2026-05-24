# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
from collections import OrderedDict
import copy #for copying dicts
import time
import numpy as np
import pandas as pd
import path
from pathlib import Path

import MLB_dbvar as MLB_dbvar
import MLB_globals as MLB_global

class scionMASTERDB:
    def __init__(self, usr_path, masterdbfname):
        self.masterdb_path = usr_path
        self.masterdbfname = os.path.join(self.masterdb_path, masterdbfname) # or Path(self.system_path) / cfgfname_txt
        self._masterdb_raw_date_format = '%Y%m%d'
        self._masterdb_scion_date_format = '%Y%m%d'
        self._masterdb_df = pd.DataFrame
        self._masterdb_oldest_game = 0 #will be set when data is loaded and validated
        self._masterdb_recent_game = 0 #will be set when data is loaded and validated
        self._masterdb_games_list = []
        #load and validate data
        self._loadMASTERDB()
        self._validateMASTERDB()

    #getters
    @property
    def masterdb_df(self):
        #Assumption: validateMASTERDB will be called before this getter is
        return self._masterdb_df
    @property
    def masterdb_games_list(self):
        #Assumption: validateMASTERDB will be called before this getter is
        return self._masterdb_games_list
    @property
    def masterdb_oldest_game(self):
        #Assumption: validateMASTERDB will be called before this getter is
        return self._masterdb_oldest_game
    @property
    def masterdb_recent_game(self):
        #Assumption: validateMASTERDB will be called before this getter is
        return self._masterdb_recent_game
    @property
    def masterdb_scion_date_format(self):
        #Assumption: validateMASTERDB will be called before this getter is
        return self._masterdb_scion_date_format
    
    def _loadMASTERDB(self):
        try:
            #Read data into a pd frame
            self._masterdb_df = pd.read_csv(self.masterdbfname, header=0, parse_dates=[MLB_dbvar.dbvar_G_Date], dayfirst=False)
        except:
            print("\nscionMASTERDB._loadMASTERDB(): unexpected error loading the master database file " + self.masterdbfname,end="\n")
            raise
    
    def _initAllCols(self):
        #Unfortunately this func depends on MLB_dbvar_v8.py
        try:
            # Assumption: Data has been read in and redundant cols removed
            #1. Date first - ensure consistent with raw dumpdate type. To do this we will have to use the component cols G_Year, G_Month, G_Day
            self._masterdb_df[MLB_dbvar.dbvar_G_Date] = pd.to_datetime(dict(year=self._masterdb_df[MLB_dbvar.dbvar_G_Year], month=self._masterdb_df[MLB_dbvar.dbvar_G_Month], day=self._masterdb_df[MLB_dbvar.dbvar_G_Day]))
            self._masterdb_df[MLB_dbvar.dbvar_G_Date] = pd.to_datetime(self._masterdb_df[MLB_dbvar.dbvar_G_Date], format=self._masterdb_raw_date_format)
            self._masterdb_df[MLB_dbvar.dbvar_G_Date] = self._masterdb_df[MLB_dbvar.dbvar_G_Date].apply(lambda x: x.date()) #just store the date, discard the time
            #2. Now remaining cols
            self._masterdb_df = MLB_dbvar.InitialiseMasterMLBColumnTypes(self._masterdb_df)
            
        except:
            print("\nscionMASTERDB.initAllCols(): unexpected error initialising different column types for the master database file " + self.masterdbfname,end="\n")
            raise
    
    def _validateMASTERDB(self):
        #Assumes data has been loaded into _masterdb_df
        try:
            #1. check if any data
            num_rows = self._masterdb_df.shape[0]
            if not num_rows:
                print ("\nscionMASTERDB._validateMASTERDB(): Fatal error - no games found in the database file " + self.masterdbfname, end="\n")
                raise Exception
            #2. Initialise columns with appropriate col types
            self._initAllCols()
            #3. Identify and store oldest and most recent game dates found in database
            self._masterdb_oldest_game = self._masterdb_df[MLB_dbvar.dbvar_G_Date].min()
            self._masterdb_recent_game = self._masterdb_df[MLB_dbvar.dbvar_G_Date].max()
            #4. Sort games by date in DESCENDING order as we will be working from most recent game and back
            self.sortMasterDB(MLB_dbvar.dbvar_G_Date, False)
            #5. Remove duplicate Game Ids (shouldn't exist..but!)..keep first
            self._masterdb_df = self._masterdb_df.drop_duplicates([MLB_dbvar.dbvar_G_Id])
            #6. Extract a list of game ids from the data as this will help us keep track of which games have been processed
            self._masterdb_games_list = self._masterdb_df[MLB_dbvar.dbvar_G_Id].tolist()

        except Exception:
            print("\nscionMASTERDB.validateMASTERDB(): unexpected error validating the database file " + self.masterdbfname, end="\n")
            raise

    def _initMasterRow(self,master_copy_df):
        #iterate of columns setting the value to MLB_dbvar.NO_DATA (except date, which will be initialised to today's date with expectation it will be updated later)
        for col in MLB_dbvar.MLBdb_vars:
            if col == MLB_dbvar.dbvar_G_Date:
                master_copy_df[MLB_dbvar.dbvar_G_Date].values[0] = datetime.today()
                #remove time
                master_copy_df[MLB_dbvar.dbvar_G_Date] = pd.to_datetime(master_copy_df[MLB_dbvar.dbvar_G_Date]).dt.date
            elif col in MLB_dbvar.MLBdb_str_vars:
                master_copy_df[col].values[0] = str(MLB_dbvar.NO_DATA)
            else:
                master_copy_df[col].values[0] = MLB_dbvar.NO_DATA

        return master_copy_df
    
    def copyMasterStructure(self, _includeBlankRow=True):
        #returns a copy of the structure of the masterDB with option to include a single blank row of NO_DATA
        try:
            #a. copy one row
            _master_copy_df = self._masterdb_df.iloc[[0]].copy() #see https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.iloc.html
            #b. fill with NO_DATA
            self._initMasterRow(_master_copy_df)
            #c. initialise structure
            _master_copy_df = MLB_dbvar.InitialiseMasterMLBColumnTypes(_master_copy_df)
            #d. Get rid of blank row if _includeBlankRow = False
            if not _includeBlankRow:
                _master_copy_df = _master_copy_df[0:0]
                
        except Exception:
            print("\nscionMUPS.copyMasterStructure(): Unexpected error encountered when copying the structure of the master database!")
            raise
        
        return _master_copy_df
    
    def retrieveGames(self, col, value):
        #Given a col and value, it returns a df containing rows that match cols with that value
        return self._masterdb_df[(self._masterdb_df[col] == value)]

    def getGame(self, gameId):
        return self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]

    def gameExists(self, gameId):
        #Given a col and value, it returns a df containing rows that match cols with that value
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        if _game_df.shape[0]:
            return True
        return False
        
    def checkEnoughGames(self, window_size, team_id):
        #Given a team id and min num of games (window_size), the dbaae is checked for that team's games
        #True is returned if num team games exceeds window size, otherwise False is returned
        window_size = int(window_size)
        as_hometeam = self._masterdb_df[MLB_dbvar.dbvar_G_H_Id] == team_id
        as_visitorteam = self._masterdb_df[MLB_dbvar.dbvar_G_V_Id] == team_id
        team_games = self._masterdb_df[as_hometeam | as_visitorteam]

        if team_games.shape[0] > window_size+1:
            return True
        return False

    def getOpeningMiddleLines(self, gameId):
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        _opl = _vig = 0.0
        _opt = _optml = 0.0
        if _game_df.shape[0]:
            _opl = float(_game_df[MLB_dbvar.dbvar_G_Opening_MiddleMoneyLine].values[0])
            _vig = float(_game_df[MLB_dbvar.dbvar_G_OpeningLine_Vig].values[0])
            _opt = float(_game_df[MLB_dbvar.dbvar_G_Opening_Total].values[0])
            _optml = float(_game_df[MLB_dbvar.dbvar_G_Opening_TotalLine].values[0])
        return _opl, _vig, _opt, _optml
    
    def getClosingMiddleLines(self, gameId):
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        _cll = _vig = 0.0
        _clt = _cltml = 0.0
        if _game_df.shape[0]:
            _cll = float(_game_df[MLB_dbvar.dbvar_G_Closing_MiddleMoneyLine].values[0])
            _vig = float(_game_df[MLB_dbvar.dbvar_G_ClosingLine_Vig].values[0])
            _clt = float(_game_df[MLB_dbvar.dbvar_G_Closing_Total].values[0])
            _cltml = float(_game_df[MLB_dbvar.dbvar_G_Closing_TotalLine].values[0])
        return _cll, _vig, _clt, _cltml

    def getSPId(self, gameId, h_or_v):
        #Given a game_id and whether h or v, return relevant SP Id, assuming game exists
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        _SPId = 0
        if _game_df.shape[0]:
            if h_or_v == MLB_global.HOME:
                _SPId = int(_game_df[MLB_dbvar.dbvar_G_H_StartingPitcher_Id].values[0])
            else:
                if h_or_v == MLB_global.VISITOR:
                    _SPId = int(_game_df[MLB_dbvar.dbvar_G_V_StartingPitcher_Id].values[0])
        return _SPId

    def getRuns(self, gameId, h_or_v):
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        _runs = 0
        if _game_df.shape[0]:
            if h_or_v == MLB_global.HOME:
                _runs = float(_game_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0])
            else:
                if h_or_v == MLB_global.VISITOR:
                    _runs = float(_game_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0])
        return _runs

    def getNightGame(self, gameId):
        _game_df = self._masterdb_df[(self._masterdb_df[MLB_dbvar.dbvar_G_Id] == int(gameId))]
        _nightGame = 0
        if _game_df.shape[0]:
            _nightGame = int(_game_df[MLB_dbvar.dbvar_G_NightGame].values[0])
        return _nightGame

    def getTeamGames(self, game_date, team_id, opp_team_id=None, start_date=None, end_date=None):
        #Given a game_date to project back from (inclusively) and a team id, the masterDB will be searched and a dictionary of games returned
        #In addition, if opponent_id provided then just the games between the two teams will be returned. If a start and end_date is provided the games within a particular range will be returned.
        #The dict of games return has the following structure: "Date":[Game id,Home or Visitor (where 0=Home, 1=Visitor)]
        game_ctr = 0
        team_games_dict = {}
        
        if (start_date == None): 
            #store all game data in DB for team = can be wasteful!
            for i in range(0, self._masterdb_df.shape[0]):
                current_game_date = pd.Timestamp(self._masterdb_df[MLB_dbvar.dbvar_G_Date].iloc[i]).date()
                if(game_date >= current_game_date): #greater than OR EQUAL to so we capture the game we want to predict if it exists in DB (if we're doing retrospective prediction)
                    if (self._masterdb_df[MLB_dbvar.dbvar_G_H_Id].iloc[i] == team_id):
                        if((opp_team_id != None and opp_team_id == self._masterdb_df[MLB_dbvar.dbvar_G_V_Id].iloc[i]) or opp_team_id== None):
                            game_ctr += 1
                            team_games_dict.update({current_game_date: [self._masterdb_df[MLB_dbvar.dbvar_G_Id].iloc[i], MLB_global.HOME]})
                    elif (self._masterdb_df[MLB_dbvar.dbvar_G_V_Id].iloc[i] == team_id):
                        if((opp_team_id != None and opp_team_id == self._masterdb_df[MLB_dbvar.dbvar_G_H_Id].iloc[i]) or opp_team_id == None):
                            game_ctr += 1
                            team_games_dict.update({current_game_date: [self._masterdb_df[MLB_dbvar.dbvar_G_Id].iloc[i],MLB_global.VISITOR]})
        else:
            for i in range(0, self._masterdb_df.shape[0]):
                game_date = pd.Timestamp(self._masterdb_df[MLB_dbvar.dbvar_G_Date].iloc[i]).date()
                if (game_date >= start_date and game_date <= end_date):
                    if (team_id == self._masterdb_df[MLB_dbvar.dbvar_G_H_Id].iloc[i]):
                        if((opp_team_id!=None and opp_team_id == self._masterdb_df[MLB_dbvar.dbvar_G_V_Id].iloc[i]) or opp_team_id==None): 
                            game_ctr += 1
                            team_games_dict.update({self._masterdb_df[MLB_dbvar.dbvar_G_Date].iloc[i]: [self._masterdb_df[MLB_dbvar.dbvar_G_Id].iloc[i], MLB_global.HOME]})
                    elif (team_id == self._masterdb_df[MLB_dbvar.dbvar_G_V_Id].iloc[i]):
                        if((opp_team_id!=None and opp_team_id == self._masterdb_df[MLB_dbvar.dbvar_G_H_Id].iloc[i]) or opp_team_id==None):
                            game_ctr += 1
                            team_games_dict.update({self._masterdb_df[MLB_dbvar.dbvar_G_Date].iloc[i]: [self._masterdb_df[MLB_dbvar.dbvar_G_Id].iloc[i],MLB_global.VISITOR]})

        return copy.deepcopy(team_games_dict)
    
    def getHistoricalRunStrength(self, teamId, thresholdDate):
        #Returns gameId and run Strength given teamId and thresholdDate
        #1. Initialise some key variables
        gameId = MLB_dbvar.NO_DATA
        runStrength = MLB_dbvar.STRENGTH_WINDOW_AVG #if no strength data is available then average game strength is returned
        teamGames = {}
        orderedTeamGames = {}
        gameDate = pd.Timestamp(thresholdDate).date() #convert to timestamp.date() which is a subset of datetime

        #2. Set date window
        windowStartDate = gameDate - timedelta(days=MLB_global.WINDOW_START_DATE_OFFSET) #push back from the threshold for a fixed period of days (=window start)
        windowEndDate = gameDate - timedelta(days=1) #game immediately before threshold_date
    
        #3. Get dictionary of team games for period of interest
        teamGames = self.getTeamGames(gameDate, teamId, None, windowStartDate, windowEndDate)
        numTeamGames = len(teamGames)
        #4. Get most recent game and extract game_id and team's game strength
        if numTeamGames:
            # 4.1 Lets get most recent game from the list
            # List is LIFO and items added is chonological order so just pop last item to get most recent game in list
            orderedTeamGames = OrderedDict(sorted(teamGames.items(), reverse=False))
            k,v = dict(orderedTeamGames).popitem()
            # 3.2 Get Game Id and strength for team of interest (strength will be based on whether H or V)
            h_or_v = v[MLB_global.H_OR_V_INDEX]
            gameId = v[MLB_global.GAME_ID_INDEX]
            currentGame = self.retrieveGames(MLB_dbvar.dbvar_G_Id, gameId)
            if (h_or_v == MLB_global.HOME):
                runStrength = float(MLB_global.calcProbRatio(currentGame[MLB_dbvar.dbvar_H_Runs_Gained].values[0], currentGame[MLB_dbvar.dbvar_H_Runs_Allowed].values[0]))
            else:
                runStrength = float(MLB_global.calcProbRatio(currentGame[MLB_dbvar.dbvar_V_Runs_Gained].values[0], currentGame[MLB_dbvar.dbvar_V_Runs_Allowed].values[0]))
                
        # return game_id and team strength       
        return gameId, runStrength # We should be returning valid data but let calling program deal with MLB_dbvar.NO_DATA


    def sortMasterDB(self, colName, isAsc=True):
        self._masterdb_df.sort_values(by=[colName], ascending=isAsc)
    
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