import sys, traceback # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
from collections import Counter
import copy #for copying dicts
import time
import argparse
import csv
import pandas as pd
import numpy as np
import math
import json
from scipy.stats import iqr
import path
from pathlib import Path
import shlex #for splitting strings by white space but preserving words within quotes
import enum
import MLB_dbvar as MLB_dbvar
import MLB_globals as MLB_global
# pylint: disable=c0301

# Define key global vars
APP_VER = "V26.05"
APP_NAME = "MLB dNullPitcher" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2026" 
APP_RUNTIME = datetime.today() #default is now
#Print opening banner to console
print("\n"+ APP_BANNER + "\n" + APP_OWNER + "\n")
NO_DATA = -1000000

class dinitNullPitcher:
	"""Initialise object with key information"""
	def __init__(self, inputfname_csv, repfname_json, output_fname_csv):
		self._cwd = os.getcwd()
		self.ipfnamecsv = inputfname_csv
		self.repfnamejson = repfname_json
		self.opfnamecsv = output_fname_csv
		self._inputfname_csv = os.path.join(self._cwd, self.ipfnamecsv)
		self._spavgdictfname_json = os.path.join(self._cwd, self.repfnamejson)
		self._outputfname = os.path.join(self._cwd, self.opfnamecsv)		
		self._repspcolval_dict = {} #will store col name/val pairs
		self._input_df = pd.DataFrame
		self._output_df = pd.DataFrame

	def _replaceZEROColumnWithMidPoint(self, df, colList, midPoint):
        # Iteration like this is slow but expedient
		for col in colList:
			df[col] = df[col].replace(0, midPoint)

		return df
	
	def _replaceNANwithMidPoint(self, inputdata_df, midPoint):
        # Replace all NAN values that might have resulted from previous calculations to 0.5
		inputdata_df = inputdata_df.replace('',np.nan).fillna(float(midPoint))

		return inputdata_df

	def _replaceNullSPWithTeamAvg(self, h_v_status, inputdata_df):
		try:
			#VERSION 3: 12th March 2024
			# New rule: As zeros for particular features can be important indicator of strength/weakness then a Null starting pitcher is one that has zeros for ALL of the following features:
			#           Number of Pitches, Innings Pitched, Strikes

			#1. Get number of teams
			_numTeams = MLB_dbvar.NUM_TEAMS
			#2. Cycle through all teams and replace SP zeros with team averages for H or V as determined by h_v_status
			for i in range(0, _numTeams):
				#For team i:
				#Get SP averages
				_teamID = str(i)
				_teamSPavgdict = self._repspcolval_dict[_teamID].copy()
				_teamSPavgdict = _teamSPavgdict[0] #get dict from list
				#Replace zeros with SP averages For current team, process relevant 
				if h_v_status == MLB_global.HOME:
					#1. set mask that determines whether or not a pitcher is considered a 'null pitcher'
					_mask = (inputdata_df[MLB_dbvar.dbvar_G_H_Id] == i) & (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD] == 0) & (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD] == 0) & (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD] == 0)
					#2. Process _All SP vars
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))					
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))
					#3. Process _YTD SP vars
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))
					#4. Process _5G SP vars
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G] = inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))
				else: #Visitor
					#1. set mask that determines whether or not a pitcher is considered a 'null pitcher'
					_mask = (inputdata_df[MLB_dbvar.dbvar_G_V_Id] == i) & (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD] == 0) & (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD] == 0) & (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] == 0)
					#2. Process _All SP vars
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))					
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))
					#3. Process _YTD SP vars
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))
					#4. Process _5G SP vars
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_SCOREATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKEOUTATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_BASEONBALLSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_HITSATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_NUMPITCHESATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_INNINGSPITCHEDATTRIB]))
					inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G] = inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G].mask(_mask, float(_teamSPavgdict[MLB_dbvar.SP_STRIKESATTRIB]))

		except Exception:
			print("\n\n_replaceNullSPWithTeamAvg() : Unexpected error replacing starting pitcher zero values with team averages!")
			self._errorReport()

		return inputdata_df

	def _updateRatioAttribs(self, inputdata_df):
		#the following works for dGEN as dGEN refers to a single value for H and V rather than a series
		#inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_All] = MLB_global.calcRatio(inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All], inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All])
		# Use replace to capture +/- negative infinity. See https://itecnote.com/tecnote/python-handling-division-by-zero-in-pandas-calculations/
		
		#1. Calculate H ratios
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_All] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_All] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G]).replace((np.inf, -np.inf), (0, 0))

		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD] / inputdata_df[MLB_dbvar.dbvar_H_Runs_Allowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StrikeoutsGained_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD] / inputdata_df[MLB_dbvar.dbvar_H_WalksAllowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_H_HitsAllowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD] / inputdata_df[MLB_dbvar.dbvar_H_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD] / inputdata_df[MLB_dbvar.dbvar_H_Innings]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_H_Strikes_YTD]).replace((np.inf, -np.inf), (0, 0))
		
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G] / inputdata_df[MLB_dbvar.dbvar_H_Runs_Allowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_H_StrikeoutsGained_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G] / inputdata_df[MLB_dbvar.dbvar_H_WalksAllowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_H_HitsAllowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G] / inputdata_df[MLB_dbvar.dbvar_H_NP_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G] / inputdata_df[MLB_dbvar.dbvar_H_Innings]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_H_Strikes_5G]).replace((np.inf, -np.inf), (0, 0))

		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_All]).replace((np.inf, -np.inf), (0, 0))
		
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD]).replace((np.inf, -np.inf), (0, 0))
		#2. Calculate V ratios
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_All] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_All] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G]).replace((np.inf, -np.inf), (0, 0))

		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD] / inputdata_df[MLB_dbvar.dbvar_V_Runs_Allowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StrikeoutsGained_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] / inputdata_df[MLB_dbvar.dbvar_V_WalksAllowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_V_HitsAllowed_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD] / inputdata_df[MLB_dbvar.dbvar_V_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD] / inputdata_df[MLB_dbvar.dbvar_V_Innings]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_V_Strikes_YTD]).replace((np.inf, -np.inf), (0, 0))
		
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G] / inputdata_df[MLB_dbvar.dbvar_V_Runs_Allowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_V_StrikeoutsGained_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] / inputdata_df[MLB_dbvar.dbvar_V_WalksAllowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_V_HitsAllowed_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G] / inputdata_df[MLB_dbvar.dbvar_V_NP_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G] / inputdata_df[MLB_dbvar.dbvar_V_Innings]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_V_Strikes_5G]).replace((np.inf, -np.inf), (0, 0))

		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_All]).replace((np.inf, -np.inf), (0, 0))
		
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD]).replace((np.inf, -np.inf), (0, 0))
        
        #Replace any NANs with midpoint (1)
		inputdata_df = self._replaceNANwithMidPoint(inputdata_df,1)
		
		return inputdata_df
		
	def _updateWalksHitsAllowedPerInningAttribs(self, inputdata_df):
        #1. HOME WHIP
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_All] + inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_All] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD] + inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G] + inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD] / inputdata_df[MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G] / inputdata_df[MLB_dbvar.dbvar_H_WalksHitsAllowedPerInning_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G] / inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD]).replace((np.inf, -np.inf), (0, 0))
		#2. VIS WHIP
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_All] + inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_All] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] + inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] + inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD] / inputdata_df[MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_YTD]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G] / inputdata_df[MLB_dbvar.dbvar_V_WalksHitsAllowedPerInning_5G]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All]).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G] / inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD]).replace((np.inf, -np.inf), (0, 0))
		#Replace any NANs with midpoint (1)
		inputdata_df = self._replaceNANwithMidPoint(inputdata_df,1)
		
		return inputdata_df

	def _updateProbabilityRatioAttribs(self, inputdata_df):
		# Individual H and V prob ratios
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD] / (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G] / (inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD]+inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G]+inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G])).replace((np.inf, -np.inf), (0, 0))
		# VHRatios
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio])).replace((np.inf, -np.inf), (0, 0))
		# YTD
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD])).replace((np.inf, -np.inf), (0, 0))
		# 5G
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		#03Jun2025: Bugfix: VHRatio_SP_BoBSORatio_5G was using YTD components. This has been corrected to use 5G components.
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Score_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Score_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Score_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutAccuracy_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutAccuracy_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Hits_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Hits_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Hits_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NP_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NP_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NP_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_Strikes_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_Strikes_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_Strikes_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeAccuracy_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeAccuracy_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_ScoreImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_ScoreImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeoutsImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeoutsImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBallsImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBallsImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_HitsImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_HitsImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_NPImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_NPImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_NPImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_InningsPitchedImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_InningsPitchedImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_StrikeImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_StrikeImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G] = (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G] / (inputdata_df[MLB_dbvar.dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G]+inputdata_df[MLB_dbvar.dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G])).replace((np.inf, -np.inf), (0, 0))
		#Replace any NANs or Zeroes with midpoint (0.5)
		inputdata_df = self._replaceNANwithMidPoint(inputdata_df,0.5)
		#Ensure VHRatios cannot be zero i.e. set to the midpoint of 0.5
		inputdata_df = self._replaceZEROColumnWithMidPoint(inputdata_df,MLB_dbvar.MLBdb_VHRatio_vars,0.5)
		
		return inputdata_df
        
	def _processInputData(self):
		#Assumption 1: self._input_df stores current data
		#Assumption 2: self.spavgdict_json contains SP Average data in team order
		try:
			# 1. Copy input_data and store in output_data
			self._output_df = self._input_df.copy()
			# 2. Process Home SP
			print("Searching for HOME null pitchers and replacing their zero values with team-based averages ...",end="", flush=True)
			_h_v_status = MLB_global.HOME
			self._output_df = self._replaceNullSPWithTeamAvg(_h_v_status, self._output_df)
			print("done.", flush=True)
			# 3. Process Vis SP
			print("Searching for VISITOR null pitchers and replacing their zero values with team-based averages ...",end="", flush=True)
			_h_v_status = MLB_global.VISITOR
			self._output_df = self._replaceNullSPWithTeamAvg(_h_v_status, self._output_df)
			print("done.", flush=True)
			# 4. Updating standard ratio variables
			print("Updating relevant pitcher ratio features ...",end="", flush=True)
			self._output_df = self._updateRatioAttribs(self._output_df)
			print("done.", flush=True)
			# 5. Updating WHIP ratio variables
			print("Updating relevant pitcher WHIP ratio features ...",end="", flush=True)
			self._output_df = self._updateWalksHitsAllowedPerInningAttribs(self._output_df)
			print("done.", flush=True)
			# 6. Updating probability ratio variables
			print("Updating probability-based pitcher ratio features ...",end="", flush=True)
			self._output_df = self._updateProbabilityRatioAttribs(self._output_df)
			print("done.", flush=True)
			
			print("\n")
		
		except Exception:
			print("\n\n_processInputData() : Unexpected error processing " + self.ipfnamecsv + "!")
			self._errorReport()

	def _storeOutputData(self):
		try:
			#a. Store data 
			print("Storing the results data in " + str(self.opfnamecsv) + "...",end="", flush=True)
			self._output_df.to_csv(self._outputfname, encoding = "utf-8", index=False)
			#b. Done
			print("done.", flush=True)
			
		except Exception:
			print("\n\n_storeOutputData() : Unexpected error storing the resulting output data to file " + str(self.opfnamecsv),end="")
			self._errorReport()
			
	def _loadData(self):
		try:  
			#a. Load input data
			#Determine character encoding: go to https://www.kaggle.com/code/paultimothymooney/how-to-resolve-a-unicodedecodeerror-for-a-csv-file/notebook 
			#For diff between UTF-8 and ISO-8859-1 see https://stackoverflow.com/questions/7048745/what-is-the-difference-between-utf-8-and-iso-8859-1 
			#On mac it is: ISO-8859-1
			self._input_df = pd.read_csv(self._inputfname_csv, encoding = "ISO-8859-1", header=0)
			print("Input data loaded successfully.", flush=True)
			#b. Load sp average data and store in dict
			with open(self._spavgdictfname_json, encoding = "ISO-8859-1") as dict_file:
				self._repspcolval_dict = json.loads(dict_file.read())
			print("JSON file containing team-based pitcher averages loaded successfully.", flush=True)
		except:
			print("\n\n_loadData(): Fatal error loading the input data (" + self.ipfnamecsv + ") or the pitcher averages file (" + self.repfnamejson + ").",end="")
			self._errorReport()

	def _errorReport(self):
		print (" Please review and address any issues highlighted in the report below.\n\n")
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
		sys.exit(0)

	def Run(self):
		self._loadData()
		self._processInputData()
		self._storeOutputData()

def ReadCommandLineArguments():
  parser = argparse.ArgumentParser(description=APP_NAME + " finds 'null starting pitchers', those with np_ytd, ip_ytd and strikes_ytd equal to 0, and replaces them with the team-level insample averages. Any NAN values are set to a mid point eg 1 for ratios and 0.5 for prob ratios.")
  parser.add_argument("-i", "--usrInputfname", help="name of the csv file containing the input data which may have null starting pitchers.", required = True)
  parser.add_argument("-r", "--usrReplacefname", help="name of the JSON file containing the team-based averages for the starting pitcher variables. This file must be union friendly with the starting pitcher primitives found in the input data.", required = True)
  parser.add_argument("-o", "--usrOutputfname", help="name of the filename where the modified input data will be stored.", required = True)
  argument = parser.parse_args() #program will terminate if incorrect options given
  return dinitNullPitcher(argument.usrInputfname, argument.usrReplacefname, argument.usrOutputfname)
  
if __name__ == '__main__':
  dinitNullPitcher_job = ReadCommandLineArguments()
  dinitNullPitcher_job.Run()
  print ("\n"+APP_NAME+" completed successfully.\n")