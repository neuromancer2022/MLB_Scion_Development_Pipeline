# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import time
import numpy as np
import pandas as pd
from pathlib import Path

import MLB_dbvar as MLB_dbvar
import MLB_globals as MLB_global

class scionGTP:
    def __init__(self, usr_path, gtpfname):
        self.gtp_path = usr_path
        self.gtpfname = os.path.join(self.gtp_path, gtpfname) # or Path(self.system_path) / cfgfname_txt
        self._gtp_date_format = '%Y%m%d'
        self._gtp_gameid_attrib = "GAME_ID"
        self._gtp_date_attrib = "DATE"
        self._gtp_hid_attrib = "HOM_ID"
        self._gtp_vid_attrib = "VIS_ID"
        self._gtp_cols = [self._gtp_gameid_attrib, self._gtp_date_attrib, self._gtp_hid_attrib,	self._gtp_vid_attrib]
        self._gtp_int_cols = [self._gtp_gameid_attrib, self._gtp_hid_attrib, self._gtp_vid_attrib]
        self._gtp_float_cols = []
        self._gtp_str_cols = []
        self._gtp_df = pd.DataFrame()
        self.current_gtp_dict = {}
        self._gtp_vis_sname_attrib = "VIS_SNAME" #this will be added to dict only
        self._gtp_hom_sname_attrib = "HOM_SNAME" #rhis will be added to dict only
        
        #load and validate gtps
        self._loadGTP()
        self._validateGTP()
        
    def _loadGTP(self):
        try:
            #Read data into a pd frame
            self._gtp_df = pd.read_csv(self.gtpfname, header=0, parse_dates=[self._gtp_date_attrib], dayfirst = False, float_precision=None)
        except:
            print("\nscionGTP._loadGTPs(): unexpected error loading the 'games to process' file " + self.gtpfname,end="\n")
            raise
    
    def _initAllCols(self):
        try:
            # Assumption: Data has been read in and redundant cols removed
            #1. Date first
            self._gtp_df[self._gtp_date_attrib] = pd.to_datetime(self._gtp_df[self._gtp_date_attrib], format=self._gtp_date_format)
            self._gtp_df[self._gtp_date_attrib] = self._gtp_df[self._gtp_date_attrib].apply(lambda x: x.date()) #just store the date, discard the time
            #2. Now remaining cols
            self._gtp_df = MLB_global.setColType(self._gtp_df, self._gtp_int_cols, MLB_global.DF_COL_TYPE_INT)
            self._gtp_df = MLB_global.setColType(self._gtp_df, self._gtp_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
            self._gtp_df = MLB_global.setColType(self._gtp_df, self._gtp_str_cols, MLB_global.DF_COL_TYPE_STR)
        except:
            print("\nscionGTP.initAllCols(): unexpected error initialising different column types for the 'games to process' file " + self.gtpfname,end="\n")
            raise

    def _validateGTP(self):
        #Assumes data has been loaded into _gtp_df
        try:
            #1. check if any data
            num_rows = self._gtp_df.shape[0]
            if not num_rows:
                print ("\nscionGTP.validateGTPs(): No games to process!\n")
                raise Exception

            #2. Replace any blank or NaN values with NO_DATA
            self._gtp_df = self._gtp_df.replace(r'^\s*$', np.nan, regex=True) #replace blank with NA
            self._gtp_df = self._gtp_df.fillna(MLB_dbvar.NO_DATA)
            
            #3. Select only subset of columns we want as defined in self._gtp_cols
            self._gtp_df = self._gtp_df[self._gtp_df.columns.intersection(self._gtp_cols)]

            #4. Initialise col types
            self._initAllCols()
            
            #5. Validate data
            for i in range(0, self._gtp_df.shape[0]):
                id_val = MLB_global.convertNumpytoNative(self._gtp_df[self._gtp_hid_attrib].iloc[i])
                self._gtp_df[self._gtp_hid_attrib].iloc[i] = int(id_val)
                id_val = MLB_global.convertNumpytoNative(self._gtp_df[self._gtp_vid_attrib].iloc[i])
                self._gtp_df[self._gtp_vid_attrib].iloc[i] = int(id_val)
                #validate team id and week num
                if ((self._gtp_df[self._gtp_hid_attrib].iloc[i] not in MLB_dbvar.teamnumlist) or (self._gtp_df[self._gtp_hid_attrib].iloc[i] not in MLB_dbvar.teamnumlist)):
                    print("\nError - invalid team ID given! Please ensure team IDs are between 0 and " + str(MLB_dbvar.NUM_TEAMS-1) + "\n")
                    raise Exception
        except Exception:
            print("\nscionGTP._validateGTPs(): unexpected error validating the 'games to process' file " + self.gtpfname,end="\n")
            raise

    def getGTP(self):
        #returns self.gtpfname without any file extension
        return self.gtpfname

    def getGTPFnameNOExt(self):
        #returns self.gtpfname without any path or file extension
        return Path(self.gtpfname).stem

    def getGTPFnameNOPATH(self):
        #returns self.gtpfname without any file extension
        return os.path.basename(self.gtpfname)
    
    def getNumGTP(self):
        #Assumes data has been loaded into _gtp_df
        return self._gtp_df.shape[0]
    
    def _isGTPIndexValid(self, row_index):
        isValid = True
        if row_index < 0 or row_index >= self._gtp_df.shape[0]:
            isValid = False
        return isValid

    def getGTPDict(self, row_index):
        #Assumes data has been loaded into _gtp_df
        try:
            #1. check valid index
            if not self._isGTPIndexValid(row_index):
                print("\nscionGTP.getGTPDict(): Error - invalid row index given to access the gtp file! Please ensure the row index is between 0 and " + str(self._gtp_df.shape[0]-1) + "\n")
                raise Exception
            #2. initialise dict
            self.current_gtp_dict = {}
            #3. copy specific row from self._gtp_df.columns to new dataframe
            _gtp_row_df = self._gtp_df.iloc[row_index].copy()
            shape=_gtp_row_df.shape[0]
            #4. covert to dict
            self.current_gtp_dict = _gtp_row_df.to_dict()
            #5. add sname entries to dict
            self.current_gtp_dict[self._gtp_vis_sname_attrib] = MLB_dbvar.TEAM_ID_SNAME.get(int(self.current_gtp_dict[self.gtp_vid_attrib]))
            self.current_gtp_dict[self._gtp_hom_sname_attrib] = MLB_dbvar.TEAM_ID_SNAME.get(int(self.current_gtp_dict[self.gtp_hid_attrib]))
        except Exception:
            print("\nscionGTP.getGTPDict(): Unexpected error encountered when converting a game into a dictionary!")
            raise
    
    def getCurrentGTPGameId(self):
        return self.current_gtp_dict[self.gtp_gameid_attrib]
    def getCurrentGTPDate(self):
        return self.current_gtp_dict[self.gtp_date_attrib]
    def getCurrentGTPHomeId(self):
        return int(self.current_gtp_dict[self.gtp_hid_attrib])
    def getCurrentGTPHomeSName(self):
        return str(self.current_gtp_dict[self.gtp_hom_sname_attrib])
    def getCurrentGTPVisId(self):
        return int(self.current_gtp_dict[self.gtp_vid_attrib])
    def getCurrentGTPVisSName(self):
        return str(self.current_gtp_dict[self.gtp_vis_sname_attrib])
        
    #getters
    @property
    def gtp_gameid_attrib(self): 
        return self._gtp_gameid_attrib
    @property
    def gtp_date_format(self): 
        return self._gtp_date_format
    @property
    def gtp_date_attrib(self): 
        return self._gtp_date_attrib
    @property
    def gtp_vid_attrib(self):
        return self._gtp_vid_attrib
    @property
    def gtp_vis_sname_attrib(self):
        return self._gtp_vis_sname_attrib
    @property
    def gtp_hid_attrib(self):
        return self._gtp_hid_attrib
    @property
    def gtp_hom_sname_attrib(self):
        return self._gtp_hom_sname_attrib
    
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