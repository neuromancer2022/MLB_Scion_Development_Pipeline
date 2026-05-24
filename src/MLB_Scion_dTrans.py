# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
import copy #for copying dicts
from collections import Counter
import json
import time
import math
import numpy as np
import pandas as pd
from pathlib import Path
import enum

import MLB_dbvar as MLB_dbvar
import MLB_Scion_Cfg as MLB_cfg
import MLB_Scion_Globals as MLB_global
import MLB_Scion_Preds as MLB_preds
import MLB_Scion_MasterDB as MLB_masterdb
import MLB_Scion_Mups as MLB_matchup

""" This class can apply the following transformations to dGEN data: standardise numerical variables, convert categorical to numerical variables (including one-hot and gray codes), select specific col subsets """
# Using enum class create enumerations
   
class scionDTRANS:
    def __init__(self, wd, gamedata_df, masterDBobj, mupObj, cfgObj):
        #path
        self.dtrans_wd = wd #working directory where files or subfolders will be created and stored fot debug info
        #control flags
        self._skip_game = False
        self._skip_game_reason = ""
        self._features_selected = False
        self._features_scaled = False  # This is performanced ONCE per MODEL (As in the future, models can have different scales)
        self._features_categvars_transformed = False # This is performanced ONCE per MODEL (As in the future models can have different categ transformations)
        self._maskdata_loaded = False
        self._gamedata_stored = False
        #dataframes
        self._game_df = gamedata_df.copy() #The passed game_df should typically be the SAME for each model within a matchup (as it represents the full available data for that matchup..and different models take different slices, use diff scaling etc)
        self._scaled_game_df = pd.DataFrame #this will start as a copy of self._game_df once game_df has had irrelevant cols removed
        self._scaled_categvartrans_game_df = pd.DataFrame #this will start as a copy of self._scaled_game_df once it has been processed
        self._feature_insample_stats_df = pd.DataFrame
        self._feature_mask_df = pd.DataFrame
        self._feature_categvar_mask_df = pd.DataFrame
        self._target_insample_stats_df = pd.DataFrame
        #data, mup and cfg objs
        self.masterDB = masterDBobj
        self.mupDB = mupObj
        self.modelCFG = cfgObj #this can be added at a later date (eg genGameData)
        #fnames (for files to be stored in log folder)
        self._scaled_game_fname_csv = "" #with G_Id
        self._scaled_categvartrans_game_fname_csv = "" #with G_Id
        self._scaled_game_fname_decisiontree_csv = "" #no G_Id
        #fnames (for files to be stored in the task's system folder)
        self._scaled_categvartrans_game_fname_decisiontree_csv = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.getSysDTIpPatternCSV()) # csv and data with no G_Id
        self._scaled_categvartrans_game_fname_decisiontree_csv = os.path.join(self.modelCFG.system_path, self._scaled_categvartrans_game_fname_decisiontree_csv) # csv and data with no G_Id
        self._teppernet_pattern_txt = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.getSysNNIpPatternTxt()) # csv and data with no G_Id
        self._teppernet_pattern_txt = os.path.join(self.modelCFG.system_path, self._teppernet_pattern_txt) # csv and data with no G_Id
        #file handles
        self._teppernet_fh = ""
        #game dicts
        self._games = {}
        self._catvar_data_json = {}
        self._catvar_values_dict = {}
        self._catvar_cols_dict = {}
        #lists
        self._desiredFeatures = []
        self._continuousFeatures = []
        self._categFeatures = []
		#init vars from mupDB and cfgObj
        self._game_date = self.mupDB.getCurrentMUPDate()
        self._home_id = self.mupDB.getCurrentMUPHomeId()
        self._vis_id = self.mupDB.getCurrentMUPVisId()
        self._opmidl = self.mupDB.getCurrentMUPBOOKIEML()
        self._opvig = self.mupDB.getCurrentMUPBookieVig()
        self._opt = self.mupDB.getCurrentMUPBOOKIETOTAL()
        self._categ_insitu = int(self.modelCFG.getCurrentModelCategInsitu())
        self._categvar_bit_min = int(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_categvarval_min_attrib])
        self._categvar_bit_max = int(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_categvarval_max_attrib])
        self._nn_GId_nl = int(self.modelCFG.getSysNNGidNL())
        self._nn_bit_sep = str(self.modelCFG.getSysNNBitSep()).lower()
        self._feature_select_mask_fname_csv = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_mask_fname_attrib])
        self._feature_select_mask_fname_csv = os.path.join(self.modelCFG.system_path, self._feature_select_mask_fname_csv)
        self._feature_categvar_mask_fname_csv = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_categvar_mask_fname_attrib])
        self._feature_categvar_mask_fname_csv = os.path.join(self.modelCFG.system_path, self._feature_categvar_mask_fname_csv)
        self._feature_insample_stats_fname_csv = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_varstats_fname_attrib])
        self._feature_insample_stats_fname_csv = os.path.join(self.modelCFG.system_path, self._feature_insample_stats_fname_csv)
        self._target_insample_stats_fname_csv = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_op_varstats_fname_attrib])
        self._target_insample_stats_fname_csv = os.path.join(self.modelCFG.system_path, self._target_insample_stats_fname_csv)
        self._inputdict_fname_json = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_ip_categvar_jsonlookup_fname_attrib])
        self._inputdict_fname_json = os.path.join(self.modelCFG.system_path, self._inputdict_fname_json)
        self._model_results_fname = os.path.join(self.modelCFG.task_model_settings[self.modelCFG.cfg_task_dir_attrib], self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_op_result_fname_attrib])
        self._model_results_fname = os.path.join(self.modelCFG.system_path, self._model_results_fname)
    
    def _isUnionFriendly(self, fulldata_df, subsetdata_df):
		# subsetdata_df (eg an input mask) cols must be a subset of fulldata_df (eg master dataset) cols otherwise they are not considered union friendly
        _fullcols = fulldata_df.columns
        _subsetcols = fulldata_df.columns
        union_friendly = False
        #check if subsetcols list is a subset of fullcols list
        union_friendly = set(_subsetcols) <= set(_fullcols)
		
        return union_friendly

    def _loadMaskData(self):
        try:
            #input feature mask: load and validate
            self._feature_mask_df = pd.read_csv(self._feature_select_mask_fname_csv, header=0)
            self._feature_categvar_mask_df = pd.read_csv(self._feature_categvar_mask_fname_csv, header=0)
            #fill any empty cells with a known 'missing' value
            self._feature_mask_df = self._feature_mask_df.fillna(MLB_dbvar.NO_DATA)
            self._feature_categvar_mask_df = self._feature_categvar_mask_df.fillna(MLB_dbvar.NO_DATA)
            #the masks MUST be union friendly with the game data
            #verify mask data is union friendly with game data
            _isUnionFriendly = self._isUnionFriendly(self._game_df, self._feature_mask_df)
            if not _isUnionFriendly:
                print("\nError! The feature mask is not union friendly with the game data!")
                raise Exception
            _isUnionFriendly = self._isUnionFriendly(self._game_df, self._feature_categvar_mask_df)
            if not _isUnionFriendly:
                print("\nError! The categorical feature mask is not union friendly with the game data!")
                raise Exception
			#all okay	
            self._maskdata_loaded = True
        except Exception:
            print("\nscionDTRANS._loadMaskData(): error when creating and validating mask data please ensure the mask files exist, are aligned with the game data and the configuration settings are correct.\n")
            raise

    def _loadBitRepDict(self):
        try:
            #load bit rep dict (in json format)
            self._catvar_data_json = {}
            self._catvar_values_dict = {}
            #open json file and extract into dict
            with open(self._inputdict_fname_json, encoding='utf-8') as dict_file:
                self._catvar_data_json = json.loads(dict_file.read())
        except Exception:
            print("\nscionDTRANS._loadBitRepDict(): error when reading and parsing the bit rep dictionary stored in the JSON file: " + str(self._inputdict_fname_json) + ".\n")
            raise

    def _getPlayerIDBitRep(self, idValue):
        try:
            _bit_rep = ""
            _limit = 1 << MLB_dbvar.PLAYERID_BITSIZE
            if idValue > _limit:
                raise Exception
            else:
                _gray = idValue^(idValue >> 1)
                _bit_rep = "{0:0{1}b}".format(_gray, MLB_dbvar.PLAYERID_BITSIZE) # do not include comma after (gray,n) as we want string not   

        except Exception:
            print("\nscionDTRANS._getPlayerIDBitRep(): value for player ID exceeds the maximum value that can be represented with " + MLB_dbvar.PLAYERID_BITSIZE + " bits.\n")
            raise
            
        return _bit_rep

    def _getFeaturesList(self, df, indicatorValue):
        #Assumption: we only need check the first row for each col
        featureList = []
        for (colName, colData) in df.items():
            for (_, colValue) in colData.items():
                colValue = str(colValue)
                indicatorValue = str(indicatorValue)
                if colValue == indicatorValue:
                    featureList.append(colName)
                    break #only bothered about first value
        return featureList

    def _selectDesiredGameFeatures(self):
        # This function selects desired game features in self._game_df using the feature mask self._feature_mask_df
        # The result is a modified self._game_df
        # Assumption: self._feature_mask_df has been populated; it only has only ONE row and columns with row value == MLB_global.MASK_ON belong to list of desiredFeatures
        try:
            #1. check if mask data has been loaded and if not, load it
            if not self._maskdata_loaded:
                self._loadMaskData()
            #2. all good, so lets iterate through the mask and add cols to list where cols equal to MLB_global.MASK
            self._desiredFeatures = self._getFeaturesList(self._feature_mask_df, MLB_global.MASK_ON)
            #3. now modify _game_df such that it only contains the desired cols
            self._game_df = self._game_df.drop(columns=[col for col in self._game_df if col not in self._desiredFeatures])
            #4. confirm features selected
            self._features_selected = True
            #5. check correct number of features have been extracted
            _numFeatures = self._game_df.shape[1]
            _desiredNumFeatures = int(self.modelCFG.getCurrentModelNumIPFeatures())
            if _numFeatures != _desiredNumFeatures:
                print("\nError! There is a mismatch between the number of features deduced from the input mask and those specificed in the configuration file - please check both and ensure they agree!")
                raise Exception

        except Exception:
            print("\nscionDTRANS._selectDesiredGameFeatures(): error selecting the desired features from the game data using the feature mask.\n")
            raise

    def _populateContinuousFeaturesList(self, indicatorValue):
        # This function stores the continuous features from self._scaled_game_df as indicated by the first row of each variable in self._feature_insample_stats_df
        # The result is a populated self._continuousFeatures list with the col names of the continuous vars in self._scaled_game_df
        # Assumption 1: desired features have been selected; insample_stats_df has been loaded with values
        # Assumption 2: non-continous variables in insample_stats_df have been initialised with a known value (MLB_dbvar.NO_DATA)
        # Assumption 3: we only need check the first row of each variable in insample_stats_df to know whether it is a continuous variable
        try:
            #Get 
            self._continuousFeatures = []
            for (colName, colData) in self._feature_insample_stats_df.items():
                for (_, colValue) in colData.items():
                    if colValue != indicatorValue:
                        self._continuousFeatures.append(colName)
                        break #only bothered about first value 
                    
        except Exception:
            print("\nscionDTRANS._populateContinuousFeaturesList(): error identifying continuous variables using the available statistics data.\n")
            raise
        
    def _scaleFeature(self, scaleType, colName, unscaledValue):
        # Assumption self._feature_insample_stats_df has been successfully populated
        # LIMITATION: we are only using the DEFAULT scaling method as indicated by self.modelCFG.cfg_sys_defaultscale_attrib
        
        #stats indices for colStatistics    
        #_minIndex = 0
        _avgIndex = 1
        #_medianIndex = 2
        #_maxIndex = 3
        _stdevIndex = 4
        _scaledValue = 0.0
        
        try:
            #1. Check if scaleType is 4 (vanilla standardisation) and raise Exception if not (AS CURRENT VER OF SCION ONLY SUPPORTS Standardisation)
            if scaleType != MLB_global.ScaleTypes.Standardize.value:
                    print("\nError! The current version of MLB Scion only supports vanilla standardisation of continuous variables, please ensure that the system config setting for the default scale is set to 4!")
                    raise Exception
                
            #2. Scale value
            _avg = round(float(self._feature_insample_stats_df[colName].values[_avgIndex]),MLB_global.NN_DP_PRECISION)
            _stdev = round(float(self._feature_insample_stats_df[colName].values[_stdevIndex]),MLB_global.NN_DP_PRECISION)
            if _avg == MLB_dbvar.NO_DATA or _stdev == MLB_dbvar.NO_DATA:
                    print("\nScaling error! NO_DATA was found instead of a statistic - please review statistics file!")
                    raise Exception
                
            _scaledValue = round(float((unscaledValue - _avg) / _stdev),MLB_global.NN_DP_PRECISION)
        
        except Exception:
            print("\nscionDTRANS._scaleFeature(): error scaling continuous variable " + colName + " using the statistics data stored in " + str(self._feature_insample_stats_fname_csv) + ".\n")
            raise
        
        return _scaledValue
        
    def _scaleContinuousFeatures(self):
        # This function scales the desired game features in self._scaled_game_df (which initially consists of unscaled data). 
        # To acheive this: self._feature_insample_stats_df will be populated using the model statistics provided in self._feature_insample_stats_fname_csv
        # The result is: a modified self._scaled_game_df, self._features_scaled set to True (assuming success)
        # ASSUMPTION: self._scaled_game_df only has one row
        # LIMITATION: we are only using the DEFAULT scaling method as indicated by self.modelCFG.cfg_sys_defaultscale_attrib
        #                        For future iterations of Scion, it is likely we will have a different scaling type per model which will be indicated by new model var: self.modelCFG._cfg_variable_settings[self.cfg_task_model_scaletype_attrib]
        try:
            #1. check if mask data has been loaded and if not, load it
            if not self._maskdata_loaded:
                self._loadMaskData()
            #2. Check if desired features selected (as we dont want to process features unnecessarily ), if not, select them
            if not self._features_selected:
                self._selectDesiredGameFeatures()
            #3. load stats and fill empty cells with known value
            self._feature_insample_stats_df = pd.read_csv(self._feature_insample_stats_fname_csv, header=0)
            self._feature_insample_stats_df = self._feature_insample_stats_df.fillna(MLB_dbvar.NO_DATA)
            #4. initialise scaled_data_df
            self._scaled_game_df = self._game_df.copy()
            #5. all good, get list of continuous variables
            self._populateContinuousFeaturesList(MLB_dbvar.NO_DATA)
            #6. iterate over scale continuous variables found in self._scaled_game_df
            # CURRENT VERSION ONLY RECOGNISES ONE SCALE TYPE i.e. self.modelCFG.cfg_sys_defaultscale_attrib
            _scale_type =  int(self.modelCFG.getSysDefaultScale())
            for (colName, colData) in self._scaled_game_df.items():
                if colName in self._continuousFeatures:
                    #we have a continuous feature so scale it!
                    unscaledValue = float(self._scaled_game_df[colName].values[0])
                    self._scaled_game_df[colName].values[0] = self._scaleFeature(_scale_type, colName, unscaledValue)
            #7. confirm features scaled
            self._features_scaled = True
        
        except Exception:
            print("\nscionDTRANS._scaleContinuousFeatures(): error scaling the desired continuous features using the model's statistics file. Please check the correct stats file exists and the relevant model instructions are in the configuration file.\n")
            raise

    def _addCategoricalValueCols(self, colName, categValue):
    # For each categ variable in self._categFeatures expand the column according to the number of possible values as dictated by json file
    # The dict self._catvar_cols_dict will be updated accordingly (structure is {"CategVar1Name":["col1","col2"..."coln"], "CategVar2Name":["col1","col2"..."coln"]})
    # The purpose of the dict is to enable us to position the categ val cols within a specific position of the dataframe rather than just appending at the end
    #
    # Assumption 1: self._categFeatures list has been populated; new categcol value cols are to be added to the end of the frame
    # Assumption 2: the bit rep for ALL categ vars EXCEPT Starting Pitcher Ids are contained in the json file (a different func will be called for SP Id)
    # Assumption 3: Categ vars will be added to the end of the dataframe as it is expected that a separate func will be used to order them afterwards (THIS IS DIFFERENT TO MLB)
    # Note: we need to add the new categ val columns to self._scaled_categvartrans_game_df
        try:
            #1. get dict of values for categ variable colName (as self._catvar_data_json is a  nested dict)
            self._catvar_values_dict = self._catvar_data_json[colName]
            self._catvar_values_dict = self._catvar_values_dict[0] #this copies the data without affecting original dicts in json (unlike pop)
            _categValColsList = [] #This will store the list of values for current categ var so we can add to self._catvar_cols_dict
            #2. get bit rep for current categValue
            if not isinstance(categValue, str):
                categValue = f"{str(categValue)}" #all keys are strings
            bitRep = str(self._catvar_values_dict.get(categValue, MLB_dbvar.NO_DATA))
            #3. check if valid bit-rep exists, if not exit otherwise expand columns according to the number of bits
            if bitRep == MLB_dbvar.NO_DATA:
                raise Exception
            else:
                #3.1 calc number of bits (categ values) and IF > 1 then add new col for each bit with colName_<count>
                ctr = 1
                numCols = len(bitRep)
                if numCols > ctr:
                    for bitIndex in range(numCols):
                        #3.1.1 create new col
                        newCol = colName+"_"+str(ctr)
                        self._scaled_categvartrans_game_df[newCol] = 0.0 #expand original df
                        _categValColsList.append(newCol) 
                        ctr += 1
                        #3.1.2 populate new col
                        #get bit value for current categ value 'bit'
                        bitValue = float(bitRep[bitIndex])
                        #set to bit value to desired range
                        if bitValue == 0.0 and self._categvar_bit_min != bitValue:
                            bitValue = self._categvar_bit_min
                        else:
                            if bitValue == 1.0 and self._categvar_bit_max != bitValue:
                                bitValue = self._categvar_bit_max
                        #update col value
                        self._scaled_categvartrans_game_df[newCol].values[0] = bitValue
                #3.2 add col entry to self._catvar_cols_dict
                self._catvar_cols_dict[colName] = _categValColsList
        except Exception:
            print("\nscionDTRANS._addCategoricalValueCols(): error encounted expanding and populating the input dataframe for categorical variable: " + str(colName))
            raise

    def _expandAndPopulateCategVarCols(self):
    # For each categ variable in self._categFeatures expand the column according to the number of possible values as dictated by json file
    # Assumption: self._categFeatures list has been populated and is in desired order; each new set of categ var value cols will be added to end of the dataframe
        try:
            #a. iterate over columns of the feature: 
            #   find categorical col, go to FIRST value in series, determine length and expand cols accordingly
            _tmp_game_df = self._scaled_categvartrans_game_df.copy() #we need to copy so we can iterate over the copy and change the original!!!
            self._catvar_cols_dict = {} # we will build this up to use later. Structure is {"CategVar1Name":["col1","col2"..."coln"], "CategVar2Name":["col1","col2"..."coln"]}
            for (colName, colData) in _tmp_game_df.items():
                if colName in self._categFeatures:
                    #i. we have a categorical variable and now need to read a value and expand the dataframe (we only need one row to do this)
                    for (_, categValue) in colData.items():
                        self._addCategoricalValueCols(colName, categValue)
                        
        except Exception:
            print("\nscionDTRANS._expandCategVarCols(): error encounted expanding the input dataframe to accommodate categorical variable: " + str(colName) + " using value " + str(categValue))
            raise
 
    def _orderCategVarCols(self):
    # Order self._scaled_categvartrans_game_df such that expanded categ var cols are in the same position as original categ var rather than at end of df
    # Assumption 1: self._scaled_categvartrans_game_df contains full data for current gmakedirsame, including separate cols for categ values
    # Assumption 2: self._catvar_cols_dict contains a record of each categorical var and their respective component cols
    # Assumption 3: self._game_df contains only desired features and in the desired order
        try:
            #a. Create a list of ordered columns and a list to store revised col list
            _orderedCols = self._game_df.columns.values.tolist()
            _newOrderedCols = []
            #b. Process each item in _orderedCols and check if in self._catvar_cols_dict; if not, add col to _newOrderedCols, otherwise add the dict value (which is a list) to _newOrderedCols
            for item in _orderedCols:
                if item in self._catvar_cols_dict:
                    #append list value (categ val cols RATHER categ var name) to _newOrderedCols
                    _dictListCopy = copy.deepcopy(self._catvar_cols_dict[item])
                    _newOrderedCols = _newOrderedCols + _dictListCopy
                else: #just add item to list
                    _newOrderedCols.append(item)
            #c. Remove original categ vars from self._scaled_categvartrans_game_df
            self._scaled_categvartrans_game_df = self._scaled_categvartrans_game_df.drop(columns=[col for col in self._scaled_categvartrans_game_df if col in self._categFeatures])
            #d. Finally, order self._scaled_categvartrans_game_df as per _newOrderedCols
            self._scaled_categvartrans_game_df = self._scaled_categvartrans_game_df[list(_newOrderedCols)]
            _orderedCols = self._scaled_categvartrans_game_df.columns.values.tolist()
        except Exception:
            print("\nscionDTRANS._orderCategVarCols(): error encounted whilst ordering dataframe according to original position of categorical variables")
            raise

    def _transformCategoricalFeatures(self):
        # This function tranforms the categorical features in self._scaled_game_df (which must have already had unwanted cols removed and had continuous vars scaled)
        # The 
        # The result is self._scaled_categvartrans_game_df which contains selected categ vars whose values have been transformed into bit patterns
        # Assumption: 
        try:
            #1. check if mask data has been loaded and if not, load it
            if not self._maskdata_loaded:
                self._loadMaskData()
            #2. Check if desired features selected (as we dont want to process features unnecessarily )
            if not self._features_selected:
                self._selectDesiredGameFeatures()
            #3. Check if data has been scaled
            if not self._features_scaled:
                self._scaleContinuousFeatures()
            #4. All good so make a copy of the scaled data; this copy will be transformed and for them  feature pattern for the machine learning models
            self._scaled_categvartrans_game_df = self._scaled_game_df.copy()
            #5. Get categ features from self._scaled_categvartrans_game_df using self._feature_categvar_mask_df and store col names in self._categFeatures
            self._categFeatures = self._getFeaturesList(self._feature_categvar_mask_df, MLB_global.MASK_ON)
            #6 If there are not categFeatures then return
            if not len(self._categFeatures): return
            #7. We have categ vars, so contunue. Open and read in bit rep dictionary
            self._loadBitRepDict()
            #8. Expand self._scaled_categvartrans_game_df with valueCols for each categ var
            self._expandAndPopulateCategVarCols()
            #9. Based on self._categ_insitu, either maintain continuous/categ split or have categ val vars in place of parent categ var
            if self._categ_insitu == MLB_global.YES:
                self._orderCategVarCols() #keep categ vars in situ (their original order rather end of the df)
            else:
                self._scaled_categvartrans_game_df = self._scaled_categvartrans_game_df.drop(columns=[col for col in self._scaled_categvartrans_game_df if col in self._categFeatures])
            #10. Confirm categorical variables have been processed
            self._features_categvars_transformed = True
			
        except Exception:
            print("\nscionDTRANS._transformCategoricalFeatures(): Fatal error encountered when preprocessing categorical variables.")
            raise

    def _storeDecisionTreeData(self):
        #Assumption: Remove game id col if it exists before writing to csv
        try: #This is not strictly necessary in the sense that the inputmask could drop G_Id but anyways...
            _tmp_game_df = self._scaled_categvartrans_game_df.copy()
            if MLB_dbvar.dbvar_G_Id in _tmp_game_df.columns:
                _tmp_game_df = _tmp_game_df.drop(columns=MLB_dbvar.dbvar_G_Id)
            #remove any existing file first     
            if os.path.isfile(self._scaled_categvartrans_game_fname_decisiontree_csv):
                os.remove(self._scaled_categvartrans_game_fname_decisiontree_csv)
            #write to csv
            _tmp_game_df.to_csv(self._scaled_categvartrans_game_fname_decisiontree_csv, index=False,float_format='%.9f')
            
        except Exception:
            print("\nscionDTRANS._storeDecisionTreeData(): unexpected error storing transformed game data for the decision tree.\n")
            raise

    def _storeTepperNNetData(self):
        #Input: self._scaled_categvartrans_game_df, self._nn_GId_nl, self._nn_bit_sep
        #Ouput: self._scaled_categvartrans_game_df stored in text file self._teppernet_pattern_txt (using self._teppernet_fh)
        #Assumption 1: Features have been fully transformed (selected, scaled and categ values processes)
        #Assumption 2: Tepper format just requires us to: i) check whether or not G_Id needs to be printed on a separate line ii) use specified bit separator
        try:
            #1. get bit sep (which should already have been validated by the config module)
            _bitSepSymbol = self.modelCFG.getBitSepChar()    
            #2. create file
            #remove any existing file first     
            if os.path.isfile(self._teppernet_pattern_txt):
                os.remove(self._teppernet_pattern_txt)
            #create
            self._teppernet_fh = open(self._teppernet_pattern_txt, "wt")
            #3. Iterate over rows and cols of self._scaled_categvartrans_game_df
            numRows = self._scaled_categvartrans_game_df.shape[0]
            numCols = self._scaled_categvartrans_game_df.shape[1]
            for row_index in range(0, numRows):
                cellValue = 0.0
                feature_line = ""
                numFeatures = 0
                for col_index in range(0, numCols):
                    cellValue = self._scaled_categvartrans_game_df.iloc[row_index, col_index]
                    # do we need to store first feature on separate line?
                    colName = self._scaled_categvartrans_game_df.columns[col_index]
                    if colName == MLB_dbvar.dbvar_G_Id and self._nn_GId_nl == MLB_global.YES:
                        cellValue = self._scaled_categvartrans_game_df.iloc[row_index, col_index]
                        self._teppernet_fh.write('%02d\n' % cellValue)
                    else:
                        # add it to the feature line
                        if numFeatures < numCols-1:
                            feature_line += str(cellValue) + _bitSepSymbol
                        else:
                            feature_line += str(cellValue)
                    numFeatures += 1
                #3.1 Check we have processed the correct number of feature cols
                if numFeatures != numCols:
                    print("\nError - the number of feature variables processed do not match the number of features in the dataframe.", flush=True)
                    raise Exception
                #3.2 All good, so store the feature_line in the text file
                self._teppernet_fh.write(feature_line)
            #4. close file
            self._teppernet_fh.close()
            
        except Exception:
            self._teppernet_fh.close()
            print("\nscionDTRANS._storeTepperNNetData(): fatal error storing transformed game data for the neural net.\n")
            raise

    def _createDTRANSFolder(self):
        #Attempts to create a log folder so that files can be stored there
        #An exception will be raised if the folder cannot be created
        try:
            os.makedirs(self.dtrans_wd, exist_ok=True)    
        except:
            print("\nscionDTRANS._createDTRANSFolder(): unexpected error creating the system folder " + str(self.dtrans_wd))
            raise
	   
    def _storeGameData(self, task_type, task_count, task_target):
        #Assumption: Data has been geenrated and categorical variables dealt with BEFORE this function is called
        # Task information must be provided
        try:
            #create dGEN subfolder
            self._createDTRANSFolder()
            #create filenames for log files
            _modelCode = self.modelCFG.getCurrentModelCode()
            now = datetime.today()
            self._scaled_game_fname_csv = MLB_global.LOG_FNAME_STEM + str(task_type) + str(task_count) + "_" + str(task_target) + str(_modelCode) + "_H_" + str(self._home_id) + "_V_" + str(self._vis_id) + "_" + self._game_date.strftime('%Y%m%d') + "_SCALEDATA_" + now.strftime('%Y%m%d%H%M%S') + ".csv"
            self._scaled_game_fname_csv = os.path.join(self.dtrans_wd, self._scaled_game_fname_csv) 
            self._scaled_categvartrans_game_fname_csv = MLB_global.LOG_FNAME_STEM + str(task_type) + str(task_count) + "_" + str(task_target) + str(_modelCode) + "_H_" + str(self._home_id) + "_V_" + str(self._vis_id) + "_" + self._game_date.strftime('%Y%m%d') + "_SCALECATEGDATA_" + now.strftime('%Y%m%d%H%M%S') + ".csv"
            self._scaled_categvartrans_game_fname_csv = os.path.join(self.dtrans_wd, self._scaled_categvartrans_game_fname_csv)
            #store pattern data for inspection and use by the model
            #a. for inspection
            self._scaled_game_df.to_csv(self._scaled_game_fname_csv, index=False,float_format='%.9f')
            self._scaled_categvartrans_game_df.to_csv(self._scaled_categvartrans_game_fname_csv, index=False,float_format='%.9f')
            #b. for model use
            if self.modelCFG.task_model_settings[self.modelCFG.cfg_task_model_type_attrib] == MLB_global.ModelTypes.NN.name:
                self._storeTepperNNetData()
            else: #must be decision tree!
                self._storeDecisionTreeData()
            #c. signal game data stored
            self._gamedata_stored = True
                                     
        except Exception:
            print("\nscionDTRANS._storeGameData(): unexpected error storing generated game data to txt or csv files.\n")
            raise
	 
    def rescaleFeature(self, scaleType, colName, scaledValue):
        # Assumption self._feature_insample_stats_df has been successfully populated and scaledValue is a standardised value
        # LIMITATION: we are only using the DEFAULT scaling method as indicated by self.modelCFG.cfg_sys_defaultscale_attrib
        
        #stats indices for colStatistics    
        #_minIndex = 0
        _avgIndex = 1
        #_medianIndex = 2
        #_maxIndex = 3
        _stdevIndex = 4
        _rescaledValue = 0.0
        try:
            #1. Check if scaleType is 4 (vanilla standardisation) and raise Exception if not (AS CURRENT VER OF SCION ONLY SUPPORTS Standardisation)
            if scaleType != MLB_global.ScaleTypes.Standardize.value:
                    print("\nError! The current version of MLB Scion only supports vanilla standardisation of continuous variables, please ensure that the system config setting for the default scale is set to 4!")
                    raise Exception
            #2. Rescale value
            _avg = round(float(self._feature_insample_stats_df[colName].values[_avgIndex]),MLB_global.NN_DP_PRECISION)
            _stdev = round(float(self._feature_insample_stats_df[colName].values[_stdevIndex]),MLB_global.NN_DP_PRECISION)
            if _avg == MLB_dbvar.NO_DATA or _stdev == MLB_dbvar.NO_DATA:
                print("\nRescaling error! NO_DATA was found instead of a statistic - please review statistics file!")
                raise Exception
            _rescaledValue = round(float(scaledValue * _stdev + _avg ),MLB_global.NN_DP_PRECISION)
        except Exception:
            print("\nscionDTRANS._rescaleFeature(): error scaling continuous variable " + colName + " using the statistics data stored in " + str(self._feature_insample_stats_fname_csv) + ".\n")
            raise
        
        return _rescaledValue
 
    def minmaxnormFeature(self, rawValue, minValue, maxValue):
        # Simply returns min-max norm of rawValue
        return float((rawValue-minValue)/(maxValue-minValue))

    def limitFeature(self, rawValue, minValue, maxValue):
        # Simply returns rawValue within min and maxValue inclusive
        if rawValue < minValue:
            return minValue
        elif rawValue > maxValue:
            return maxValue
        else:
            return rawValue
        
    def transformGameData(self, task_type, task_count, task_target):
        try:
            self._loadMaskData()
            self._selectDesiredGameFeatures()
            self._scaleContinuousFeatures()
            self._transformCategoricalFeatures()
            self._storeGameData(task_type, task_count, task_target)
            
        except Exception:
            _visName = str(self.mupDB.getCurrentMUPVisSName())
            _homName = str(self.mupDB.getCurrentMUPHomeSName())
            print("\nscionDTRANS.transformGameData(): unable to transform features for matchup [ " + str(self._game_date.strftime('%Y%m%d')) + " | " + _visName + " @ " +  _homName + " ]")
            print("Task: " + str(task_type) + " ---> Model Number: " + str(task_count) + " ---> Target: " + str(task_target))
            raise

    #getters
    @property
    def skip_game(self): 
        return self._skip_game
    @property
    def skip_game_reason(self):
        return self._skip_game_reason
    @property
    def desiredFeatures(self):
        return self._desiredFeatures
    @property
    def features_selected(self):
        return self._features_selected
    @property
    def categ_features(self):
        return self._categFeatures
    @property
    def data_scaled(self):
        return self._features_scaled
    @property
    def data_categvars_transformed(self):
        return self._features_categvars_transformed
    @property
    def maskdata_loaded(self):
        return self._maskdata_loaded
    @property
    def game_df(self):
        return self._game_df
    @property
    def scaled_game_df(self):
        return self._scaled_game_df
    @property
    def scaled_categvartrans_game_df(self):
        return self._scaled_categvartrans_game_df
    @property
    def feature_insample_stats_df(self):
        return self._feature_insample_stats_df
    @property
    def target_insample_stats_df(self):
        return self._target_insample_stats_df
    @property
    def feature_mask_df(self):
        return self._feature_mask_df
    @property
    def feature_categvar_mask_df(self):
        return self._feature_categvar_mask_df
    @property
    def scaled_game_fname_csv(self):
        return self._scaled_game_fname_csv
    @property
    def scaled_categvartrans_game_fname_csv(self):
        return self._scaled_categvartrans_game_fname_csv
    @property
    def scaled_game_fname_decisiontree_csv(self):
        return self._scaled_game_fname_decisiontree_csv
    @property
    def scaled_categvartrans_game_fname_decisiontree_csv(self):
        return self._scaled_categvartrans_game_fname_decisiontree_csv
    @property
    def teppernet_pattern_txt(self):
        return self._teppernet_pattern_txt
    @property
    def teppernet_fh(self):
        return self._teppernet_fh
    @property
    def games(self):
        return self._games
    @property
    def catvar_data_json(self):
        return self._catvar_data_json
    @property
    def catvar_dict(self):
        return self._catvar_values_dict
    @property
    def cols_to_drop(self):
        return self._cols_to_drop
    @property
    def categ_features(self):
        return self._categFeatures
    @property
    def game_date(self):
        return self._game_date
    @property
    def home_id(self):
        return self._home_id
    @property
    def vis_id(self):
        return self._vis_id
    @property
    def opmidl(self):
        return self._opmidl
    @property
    def opvig(self):
        return self._opvig
    @property
    def opt(self):
        return self._opt
    @property
    def categvar_bit_min(self):
        return self._categvar_bit_min
    @property
    def categvar_bit_max(self):
        return self._categvar_bit_max
    @property
    def feature_select_mask_fname_csv(self):
        return self._feature_select_mask_fname_csv
    @property
    def feature_categvar_mask_fname_csv(self):
        return self._feature_categvar_mask_fname_csv
    @property
    def inputdict_fname_json(self):
        return self._inputdict_fname_json
    @property
    def model_results_fname(self):
        return self._model_results_fname   

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