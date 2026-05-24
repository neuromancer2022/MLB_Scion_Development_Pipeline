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

class dGENLOG: #maintains a single df log of progress and stores to two separate files (one in subfolder and other in root wd)
    def __init__(self, root_wd, dgen_subfolder_wd, logfname):
        #path and static filename
        self._log_stem_fname = str(logfname) + str(MLB_global.DGEN_LOG_FNAME)
        self.log_rootwd_fname = os.path.join(root_wd, self._log_stem_fname)
        self.log_subfolderwd_fname = os.path.join(dgen_subfolder_wd, self._log_stem_fname)
        #log attribs
        self._log_gameid_attrib = "Game_Id"
        self._log_date_attrib = "Date"
        self._log_visid_attrib = "Vis_Id"
        self._log_homeid_attrib = "Home_Id"
        self._log_gameinstances_attrib = "Instances_Stored"
        self._log_status_attrib = "Status"
        self._log_cols = [self._log_gameid_attrib, self._log_date_attrib, self._log_visid_attrib, self._log_homeid_attrib, self._log_gameinstances_attrib, self._log_status_attrib]
        self._log_int_cols = [self._log_gameid_attrib, self._log_visid_attrib, self._log_homeid_attrib, self._log_gameinstances_attrib]
        self._log_float_cols = []
        self._log_str_cols = [self._log_status_attrib]
        #dataframes
        self._log_df = pd.DataFrame(columns=self._log_cols)
		#dict for populating dataframe
        self.initLogDict()     
    
    def initAllCols(self):
		#1. Initialise df columns
        self._log_df = MLB_dbvar.setColType(self._log_df, self._log_int_cols, MLB_global.DF_COL_TYPE_INT)
        self._log_df = MLB_dbvar.setColType(self._log_df, self._log_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
        self._log_df = MLB_dbvar.setColType(self._log_df, self._log_str_cols, MLB_global.DF_COL_TYPE_STR)
    
    def initLogDict(self):
        self._log_current_game_dict = {    
                                        self._log_gameid_attrib:MLB_dbvar.NO_DATA,
                                        self._log_date_attrib:MLB_dbvar.NO_DATA,
                                        self._log_visid_attrib:MLB_dbvar.NO_DATA,
                                        self._log_homeid_attrib:MLB_dbvar.NO_DATA,
                                        self._log_gameinstances_attrib:MLB_dbvar.NO_DATA,
                                        self._log_status_attrib:""
									}
	
    def addStatusUpdate(self, updateStr):
		# Write updateStr to self._log_current_game_dict[]
        _currStr = ""		
        if self._log_current_game_dict[self._log_status_attrib] != MLB_dbvar.NO_DATA:
            _currStr = str(self._log_current_game_dict[self._log_status_attrib])
        _newStr = _currStr + str(updateStr)
        self._log_current_game_dict[self._log_status_attrib] = _newStr
    
    def updateLogDataFrame(self):
        # Assumes self._log_current_game_dict has been fully populated with data
        self._log_df = pd.concat([self._log_df,  pd.DataFrame([self._log_current_game_dict])], ignore_index=True)


    def _storeLogCSV(self, _df, _fname, _format):
        try:
            #Attempt to store verbose preds to file
            _df.to_csv(_fname, index=False, header=True, float_format=_format)
        except:
            raise
        
    def storeLogData(self):
        try:
            #Root copy 
            self._log_df.to_csv(self.log_rootwd_fname, index=False, header=True)
            #Subfolder copy 
            self._log_df.to_csv(self.log_subfolderwd_fname, index=False, header=True)
        except:
            print("dGENLOG.storeLogData(): unable to store log data " + self.log_rootwd_fname + " or " + self.log_subfolderwd_fname + "\n")
            raise
        
    def displayExitMessage(self):
        print("dGEN log report can be found in the csv file " + self.log_rootwd_fname + " and " + self.log_subfolderwd_fname + "\n")
 
    #getters for pred df col names for pred file
    @property
    def log_gameid_attrib(self): return self._log_gameid_attrib
    @property
    def log_date_attrib(self): return self._log_date_attrib
    @property 
    def log_visid_attrib(self): return self._log_visid_attrib
    @property
    def log_homeid_attrib(self): return self._log_homeid_attrib
    @property
    def log_gameinstances_attrib(self): return self._log_gameinstances_attrib
	
	#getters and setters for _log_current_game_dict
    def setCurrentGameId(self, gId):
        self._log_current_game_dict[self.log_gameid_attrib] = int(gId)
    def getCurrentGameId(self):
        return self._log_current_game_dict[self.log_gameid_attrib]
    def setCurrentGameDate(self, gDate):
        self._log_current_game_dict[self.log_date_attrib] = gDate
    def getCurrentGameDate(self):
        return self._log_current_game_dict[self.log_date_attrib]
    def setCurrentGameVisId(self, vId):
        self._log_current_game_dict[self.log_visid_attrib] = int(vId)
    def getCurrentGameVisId(self):
        return self._log_current_game_dict[self.log_visid_attrib]
    def setCurrentGameHomeId(self, hId):
        self._log_current_game_dict[self.log_homeid_attrib] = int(hId)
    def getCurrentGameInstances(self):
        return self._log_current_game_dict[self.log_gameinstances_attrib]
    def setCurrentGameInstances(self, gInstances):
        self._log_current_game_dict[self.log_gameinstances_attrib] = int(gInstances)
    
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