# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import time
import numpy as np
import pandas as pd
from pathlib import Path


import MLB_dbvar as MLB_dbvar
import MLB_Scion_Globals as MLB_global

####### Although the matchup file may contain more than the above subset of columns, only the matchup_CSV_Attribs subset will be read in

class scionMUP:
    def __init__(self, usr_path, mupfname):
        self.mup_path = usr_path
        self.mupfname = os.path.join(self.mup_path, mupfname) # or Path(self.system_path) / cfgfname_txt
        self._mup_date_format = '%Y%m%d'
        self._mup_date_attrib = "DATE"
        self._mup_nightgame_attrib = "NIGHTGAME"
        self._mup_vid_attrib = "VIS_ID"
        self._mup_hid_attrib = "HOM_ID"
        self._mup_vis_ml_open_attrib = "vis_ml_open"
        self._mup_vis_ml_close_attrib = "vis_ml_close"
        self._mup_hom_ml_open_attrib = "home_ml_open"
        self._mup_hom_ml_close_attrib = "home_ml_close"
        self._mup_vis_sp_id_attrib = "VIS_SP_ID"
        self._mup_hom_sp_id_attrib = "HOM_SP_ID"
        self._mup_bookietotal_attrib = "BOOKIE_TOTAL"
        self._mup_bookiemlspan_attrib = "BOOKIEHLINE_SPAN_CENTS"
        self._mup_comments_attrib = "COMMENTS"

        self._mup_cols =    [  
                                self._mup_date_attrib,
                                self._mup_nightgame_attrib,
                                self._mup_vid_attrib,
                                self._mup_hid_attrib,
                                self._mup_vis_ml_open_attrib,
                                self._mup_vis_ml_close_attrib,
                                self._mup_hom_ml_open_attrib,
                                self._mup_hom_ml_close_attrib,
                                self._mup_vis_sp_id_attrib,
                                self._mup_hom_sp_id_attrib,
                                self._mup_bookietotal_attrib,
                                self._mup_bookiemlspan_attrib,
                                self._mup_comments_attrib
                            ]
        
        self._mup_int_cols =    [  
                                    self._mup_nightgame_attrib,
                                    self._mup_vid_attrib,
                                    self._mup_hid_attrib,
                                    self._mup_vis_sp_id_attrib,
                                    self._mup_hom_sp_id_attrib,
                                ]
        
        self._mup_float_cols =  [  
                                    self._mup_vis_ml_open_attrib,
                                    self._mup_vis_ml_close_attrib,
                                    self._mup_hom_ml_open_attrib,
                                    self._mup_hom_ml_close_attrib,
                                    self._mup_bookiemlspan_attrib,
                                    self._mup_bookietotal_attrib
                                ]
        
        self._mup_str_cols =    [  
                                    self._mup_comments_attrib
                                ]
        self._mup_df = pd.DataFrame()
        self.current_mup_dict = {}
        self._mup_vis_sname_attrib = "VIS_SNAME" #this will be added to dict only
        self._mup_hom_sname_attrib = "HOM_SNAME" #rhis will be added to dict only
        
        #load and validate mups
        self._loadMUP()
        self._validateMUP()
        
    def _loadMUP(self):
        try:
            #Read data into a pd frame
            self._mup_df = pd.read_csv(self.mupfname, header=0, parse_dates=[self._mup_date_attrib], float_precision=None)
        except:
            print("\nscionMUPS._loadMUPs(): unexpected error loading the matchup file " + self.mupfname,end="\n")
            raise
    
    def _initAllCols(self):
        try:
            # Assumption: Data has been read in and redundant cols removed
            #1. Ensure data is in self._mup_date_format
            self._mup_df[self._mup_date_attrib] = pd.to_datetime(self._mup_df[self._mup_date_attrib])
            self._mup_df[self._mup_date_attrib] = self._mup_df[self._mup_date_attrib].dt.strftime(self._mup_date_format)
            #self._mup_df[self._mup_date_attrib] = self._mup_df[self._mup_date_attrib].dt.date #remove time component
            #2. Now remaining cols
            self._mup_df = MLB_global.setColType(self._mup_df, self._mup_int_cols, MLB_global.DF_COL_TYPE_INT)
            self._mup_df = MLB_global.setColType(self._mup_df, self._mup_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
            self._mup_df = MLB_global.setColType(self._mup_df, self._mup_str_cols, MLB_global.DF_COL_TYPE_STR)
        except:
            print("\nscionMUPS.initAllCols(): unexpected error initialising different column types for the matchup file " + self.mupfname,end="\n")
            raise

    def _validateMUP(self):
        #Assumes data has been loaded into _mup_df
        try:
            #1. check if any data
            num_rows = self._mup_df.shape[0]
            if not num_rows:
                print ("\nscionMUPS.validateMUPs(): No games to process!\n")
                raise Exception

            #2. Replace any blank or NaN values with NO_DATA
            self._mup_df = self._mup_df.replace(r'^\s*$', np.nan, regex=True) #replace blank with NA
            self._mup_df = self._mup_df.fillna(MLB_dbvar.NO_DATA)
            
            #3. Select only subset of columns we want as defined in self._mup_cols
            self._mup_df = self._mup_df[self._mup_df.columns.intersection(self._mup_cols)]

            #4. Initialise col types
            self._initAllCols()
            
            #5. Validate data
            for i in range(0, self._mup_df.shape[0]):
                id_val = MLB_global.convertNumpytoNative(self._mup_df[self._mup_hid_attrib].iloc[i])
                self._mup_df[self._mup_hid_attrib].iloc[i] = int(id_val)
                id_val = MLB_global.convertNumpytoNative(self._mup_df[self._mup_vid_attrib].iloc[i])
                self._mup_df[self._mup_vid_attrib].iloc[i] = int(id_val)
                #validate team id and week num
                if ((self._mup_df[self._mup_hid_attrib].iloc[i] not in MLB_dbvar.teamnumlist) or (self._mup_df[self._mup_hid_attrib].iloc[i] not in MLB_dbvar.teamnumlist)):
                    print("\nError - invalid team ID given! Please ensure team IDs are between 0 and " + str(MLB_dbvar.NUM_TEAMS-1) + "\n")
                    raise Exception
        except Exception:
            print("\nscionMUPS._validateMUPs(): unexpected error validating the matchup file " + self.mupfname,end="\n")
            raise

    def getNumMUP(self):
        #Assumes data has been loaded into _mup_df
        return self._mup_df.shape[0]
    
    def _isMUPIndexValid(self, row_index):
        isValid = True
        if row_index < 0 or row_index >= self._mup_df.shape[0]:
            isValid = False
        return isValid

    def getMUPDict(self, row_index):
        #Assumes data has been loaded into _mup_df
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.getMUPDict(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. initialise dict
            self.current_mup_dict = {}
            #3. copy specific row from self._mup_df.columns to new dataframe
            _mup_row_df = self._mup_df.iloc[row_index].copy()
            shape=_mup_row_df.shape[0]
            #4. convert to dict
            self.current_mup_dict = _mup_row_df.to_dict()
            #5. convert date to datetime
            self.current_mup_dict[self._mup_date_attrib] = datetime.strptime(self.current_mup_dict[self._mup_date_attrib], MLB_dbvar.dbvar_MLB_Date_Format).date()
            #6. add sname entries to dict
            self.current_mup_dict[self._mup_vis_sname_attrib] = MLB_dbvar.TEAM_ID_SNAME.get(int(self.current_mup_dict[self.mup_vid_attrib]))
            self.current_mup_dict[self._mup_hom_sname_attrib] = MLB_dbvar.TEAM_ID_SNAME.get(int(self.current_mup_dict[self.mup_hid_attrib]))
        except Exception:
            print("\nscionMUPS.getMUPDict(): Unexpected error encountered when converting a matchup into a dictionary!")
            raise
    
    #getters
    def getCurrentMUPDate(self):
        #return datetime.strptime(self.current_mup_dict[self._mup_date_attrib], MLB_dbvar.dbvar_MLB_Date_Format).date()
        return self.current_mup_dict[self._mup_date_attrib]
    def getCurrentMUPNightGame(self):
        return int(self.current_mup_dict[self._mup_nightgame_attrib])
    def getCurrentMUPHomeId(self):
        return int(self.current_mup_dict[self._mup_hid_attrib])
    def getCurrentMUPHomeSName(self):
        return str(self.current_mup_dict[self._mup_hom_sname_attrib])
    def getCurrentMUPHomeSPId(self):
        return int(self.current_mup_dict[self._mup_hom_sp_id_attrib])
    def getCurrentMUPVisId(self):
        return int(self.current_mup_dict[self._mup_vid_attrib])
    def getCurrentMUPVisSName(self):
        return str(self.current_mup_dict[self._mup_vis_sname_attrib])
    def getCurrentMUPVisSPId(self):
        return int(self.current_mup_dict[self._mup_vis_sp_id_attrib])
    def getCurrentMUPVisMLOpen(self):
        return int(self.current_mup_dict[self._mup_vis_ml_open_attrib])
    def getCurrentMUPVisMLClose(self):
        return int(self.current_mup_dict[self._mup_vis_ml_close_attrib])
    def getCurrentMUPHomeMLOpen(self):
        return int(self.current_mup_dict[self._mup_hom_ml_open_attrib])
    def getCurrentMUPHomeMLClose(self):
        return int(self.current_mup_dict[self._mup_hom_ml_close_attrib])
    def setCurrentMUPBOOKIETOTAL(self, opt):
        self.current_mup_dict[self._mup_bookietotal_attrib] = float(opt)
    def getCurrentMUPBOOKIETOTAL(self):
        #check if NO_DATA and if so, set to the median
        if self.current_mup_dict[self._mup_bookietotal_attrib] == MLB_dbvar.NO_DATA:
            self.setCurrentMUPBOOKIETOTAL(MLB_global.OPT_MEDIAN)
        return float(self.current_mup_dict[self._mup_bookietotal_attrib])
    def getCurrentMUPBOOKIESPAN(self):
        return float(self.current_mup_dict[self._mup_bookiemlspan_attrib])
    def getCurrentMUPComments(self):
        return str(self.current_mup_dict[self._mup_comments_attrib])
    
    #setters
    def setCurrentMUPVisMLOpen(self, newValue):
        self.current_mup_dict[self._mup_vis_ml_open_attrib] = float(newValue)
    def setCurrentMUPVisMLClose(self, newValue):
        self.current_mup_dict[self._mup_vis_ml_close_attrib] = float(newValue)
    def setCurrentMUPHomeMLOpen(self, newValue):
        self.current_mup_dict[self._mup_hom_ml_open_attrib] = float(newValue)
    def setCurrentMUPHomeMLClose(self, newValue):
        self.current_mup_dict[self._mup_hom_ml_close_attrib] = float(newValue)
    def setCurrentMUPBOOKIETOTAL(self, opt):
        self.current_mup_dict[self._mup_bookietotal_attrib] = float(opt)
    
    def getOriginalMUPBOOKIEML(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to span
        #It restores the dicts opl using that in self._mup_df 
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.getOriginalMUPBOOKIEML(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. get opl
            opl = float(self._mup_df[self.mup_bookieml_attrib].iloc[row_index])
            
        except Exception:
            print("\nscionMUPS.getOriginalMUPBOOKIEML():: Unexpected error encountered when retrieving opl for a specific matchup!")
            raise
        
        return opl
    
    def validateCurrentBOOKIESPAN(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function ensures a valid value is present for span
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.validateOPLSpan(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. validate span    
            #if self._mup_df[self._mup_bookiemlspan_attrib].iloc[row_index] == MLB_dbvar.NO_DATA:
            #    self.current_mup_dict[self._mup_bookiemlspan_attrib] = MLB_global.DEFAULT_SPAN_CENTS
             
            #2. validate span (Update 20Aug21: NO_DATA = 0 and will be ignored)
            if self._mup_df[self._mup_bookiemlspan_attrib].iloc[row_index] == MLB_dbvar.NO_DATA:
                self.current_mup_dict[self._mup_bookiemlspan_attrib] = 0
             
        except Exception:
            print("\nscionMUPS.validateCurrentBOOKIESPAN():: Unexpected error encountered when validating the opl span value for a specific matchup!")
            raise

    def getOriginalMUPBOOKIETOTAL(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to span
        #It restores the dicts opt using that in self._mup_df 
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.getOriginalMUPBOOKIETOTAL(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. get opt
            opt = float(self._mup_df[self.mup_bookietotal_attrib].iloc[row_index])
            
        except Exception:
            print("\nscionMUPS.getOriginalMUPBOOKIETOTAL():: Unexpected error encountered when retrieving opt for a specific matchup!")
            raise
        
        return opt
    
    def recoverOriginalMUPHomeId(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to highlighting team id
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.recoverOriginalMUPHomeId(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. get home id
            self.current_mup_dict[self._mup_hid_attrib] = int(self._mup_df[self._mup_hid_attrib].iloc[row_index])
            
        except Exception:
            print("\nscionMUPS.recoverOriginalMUPHomeId():: Unexpected error encountered when retrieving home team id for a specific matchup!")
            raise
    
    def recoverOriginalMUPVisId(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to highlighting team id
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.recoverOriginalMUPVisId(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. get home id
            self.current_mup_dict[self._mup_vid_attrib] = int(self._mup_df[self._mup_vid_attrib].iloc[row_index])
            
        except Exception:
            print("\nscionMUPS.recoverOriginalMUPVisId():: Unexpected error encountered when retrieving vis team id for a specific matchup!")
            raise

    def recoverOriginalMUPBOOKIEML(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to span
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.recoverOriginalMUPBOOKIEML(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. recover opl
            self.current_mup_dict[self._mup_bookieml_attrib] = float(self._mup_df[self._mup_bookieml_attrib].iloc[row_index])
                        
        except Exception:
            print("\nscionMUPS.recoverOriginalMUPBOOKIEML():: Unexpected error encountered when retrieving opl for a specific matchup!")
            raise
    
    def recoverOriginalMUPBOOKIETOTAL(self, row_index):
        #Assumes data has been loaded into _mup_df
        #This function is useful in case matchup dict has been altered due to span
        try:
            #1. check valid index
            if not self._isMUPIndexValid(row_index):
                print("\nscionMUPS.recoverOriginalMUPBOOKIETOTAL(): Error - invalid row index given to access the matchup file! Please ensure the row index is between 0 and " + str(self._mup_df.shape[0]-1) + "\n")
                raise Exception
            #2. recover opt
            self.current_mup_dict[self._mup_bookietotal_attrib] = float(self._mup_df[self._mup_bookietotal_attrib].iloc[row_index])
            
        except Exception:
            print("\nscionMUPS.recoverOriginalMUPBOOKIETOTAL():: Unexpected error encountered when retrieving opt for a specific matchup!")
            raise
    
    #getters
    @property
    def mup_date_format(self): 
        return self._mup_date_format
    @property
    def mup_date_attrib(self): 
        return self._mup_date_attrib
    @property
    def mup_nightgame_attrib(self): 
        return self._mup_nightgame_attrib
    @property
    def mup_vid_attrib(self):
        return self._mup_vid_attrib
    @property
    def mup_vis_sname_attrib(self):
        return self._mup_vis_sname_attrib
    @property
    def mup_vis_sp_id_attrib(self):
        return self._mup_vis_sp_id_attrib
    @property
    def mup_hid_attrib(self):
        return self._mup_hid_attrib
    @property
    def mup_hom_sname_attrib(self):
        return self._mup_hom_sname_attrib
    @property
    def mup_hom_sp_id_attrib(self):
        return self._mup_hom_sp_id_attrib
    @property
    def mup_vis_ml_open_attrib(self):
        return self._mup_vis_ml_open_attrib
    @property
    def mup_vis_ml_close_attrib(self):
        return self._mup_vis_ml_close_attrib
    @property
    def mup_hom_ml_open_attrib(self):
        return self._mup_hom_ml_open_attrib
    @property
    def mup_hom_ml_close_attrib(self):
        return self._mup_hom_ml_close_attrib
    @property
    def mup_bookiemlspan_attrib(self):
        return self._mup_bookiemlspan_attrib
    @property
    def mup_bookietotal_attrib(self):
        return self._mup_bookietotal_attrib
    @property
    def mup_comments_attrib(self):
        return self._mup_comments_attrib

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