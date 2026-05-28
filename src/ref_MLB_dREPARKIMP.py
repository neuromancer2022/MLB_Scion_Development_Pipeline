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
from pathlib import Path
import shlex #for splitting strings by white space but preserving words within quotes
import enum
import MLB_dbvar as MLB_dbvar
import MLB_globals as MLB_global
# pylint: disable=c0301

# Define key global vars
APP_VER = "V26.05"
APP_NAME = "MLB_dREPARKIF" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2026" 
APP_RUNTIME = datetime.today() #default is now
#Print opening banner to console
print("\n"+ APP_BANNER + "\n" + APP_OWNER + "\n")
NO_DATA = -1000000

class dREPARKIF:
	"""Initialise object with key information"""
	def __init__(self, inputfname_csv, repfname_json, output_fname_csv):
		self._cwd = os.getcwd()
		self.ipfnamecsv = inputfname_csv
		self.repfnamejson = repfname_json
		self.opfnamecsv = output_fname_csv
		self._inputfname_csv = os.path.join(self._cwd, self.ipfnamecsv)
		self._parkifdictfname_json = os.path.join(self._cwd, self.repfnamejson)
		self._outputfname = os.path.join(self._cwd, self.opfnamecsv)		
		self._teamparkif_dict = {} #will store col name/val pairs
		self._input_df = pd.DataFrame
		self._output_df = pd.DataFrame

	def _insertTeamParkImpactFactor(self, h_v_status, inputdata_df):
		try:
			#1. Get number of teams
			_numTeams = MLB_dbvar.NUM_TEAMS
			#2. Cycle through all teams and replace SP zeros with team averages for H or V as determined by h_v_status
			for i in range(0, _numTeams):
				#For team i:
				#Get park impact factor
				_teamID = str(i)
				_teamparkifValue = float(self._teamparkif_dict[_teamID])
				#Insert park impact factors in the existing data for _teamID
				if h_v_status == MLB_global.HOME:
					inputdata_df.loc[inputdata_df[MLB_dbvar.dbvar_G_H_Id] == int(_teamID), MLB_dbvar.dbvar_G_H_ParkImpactFactor] = _teamparkifValue
				else:
					inputdata_df.loc[inputdata_df[MLB_dbvar.dbvar_G_V_Id] == int(_teamID),MLB_dbvar.dbvar_G_V_ParkImpactFactor] = _teamparkifValue
		except Exception:
			print("\n\n_insertTeamParkImpactFactor() : Unexpected error inserting team park impact factor!")
			self._errorReport()

		return inputdata_df

	def _updateProbabilityRatioAttribs(self, inputdata_df):
		#the following works for dGEN as dGEN refers to a single value for H and V rather than a series
		#inputdata_df[MLB_dbvar.dbvar_G_VHRatio_ParkImpactFactor] = MLB_global.calcProbRatio(inputdata_df[MLB_dbvar.dbvar_G_V_ParkImpactFactor], inputdata_df[MLB_dbvar.dbvar_G_H_ParkImpactFactor])
		# Use replace to capture +/- negative infinity. See https://itecnote.com/tecnote/python-handling-division-by-zero-in-pandas-calculations/
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_ParkImpactFactor] = (inputdata_df[MLB_dbvar.dbvar_G_V_ParkImpactFactor] / (inputdata_df[MLB_dbvar.dbvar_G_V_ParkImpactFactor]+inputdata_df[MLB_dbvar.dbvar_G_H_ParkImpactFactor])).replace((np.inf, -np.inf), (0, 0))
		inputdata_df[MLB_dbvar.dbvar_G_VHRatio_ParkImpactFactor] = inputdata_df[MLB_dbvar.dbvar_G_VHRatio_ParkImpactFactor].replace('',np.nan).fillna(0.5)
		return inputdata_df
      
	def _processInputData(self):
		#Assumption 1: self._input_df stores current data
		#Assumption 2: self._teamparkif_dict contains team park impact factors
		try:
			# 1. Copy input_data and store in output_data
			self._output_df = self._input_df.copy()
			# 2. Process Home 
			print("Inserting park impact factors for the HOME team features ...",end="", flush=True)
			_h_v_status = MLB_global.HOME
			self._output_df = self._insertTeamParkImpactFactor(_h_v_status, self._output_df)
			print("done.", flush=True)
			# 3. Process Vis
			print("Inserting park impact factors for the VISITOR team features ...",end="", flush=True)
			_h_v_status = MLB_global.VISITOR
			self._output_df = self._insertTeamParkImpactFactor(_h_v_status, self._output_df)
			print("done.", flush=True)
			# 4. Updating probability ratio features
			print("Updating probability-based park impact factor ratios ...",end="", flush=True)
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
			#2. Load JSON file and store in dict
			with open(self._parkifdictfname_json, encoding = "ISO-8859-1") as dict_file:
				self._teamparkif_dict = json.loads(dict_file.read())
			self._teamparkif_dict = self._teamparkif_dict[MLB_dbvar.PARKIF_CNAME]
			self._teamparkif_dict = self._teamparkif_dict[0] #GET DICT FROM LIST
			print("JSON file containing team park impact factors loaded successfully.", flush=True)
		except:
			print("\n\n_loadData(): Fatal error loading the input data (" + self.ipfnamecsv + ") or the park impact factors file (" + self._parkifdictfname_json + ").",end="")
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
  parser = argparse.ArgumentParser(description="dREPARKIF seeds the primitive features relating to the team park impact factor with averages and then updates the relevant compound/calculated features.")
  parser.add_argument("-i", "--usrInputfname", help="name of the csv file containing the input data which has missing park impact factor information.", required = True)
  parser.add_argument("-r", "--usrReplacefname", help="name of the JSON file containing the team-based park impact factor values (one value per team).", required = True)
  parser.add_argument("-o", "--usrOutputfname", help="name of the file where the modified input data will be stored.", required = True)
  argument = parser.parse_args() #program will terminate if incorrect options given
  return dREPARKIF(argument.usrInputfname, argument.usrReplacefname, argument.usrOutputfname)
  
if __name__ == '__main__':
  dREPARKIF_job = ReadCommandLineArguments()
  dREPARKIF_job.Run()
  print ("\n"+APP_NAME+" completed successfully.\n")

  """

FEATURES MODIFIED VIA MLB_dREPARKIMP.PY
=======================================
dbvar_G_H_ParkImpactFactor
dbvar_G_V_ParkImpactFactor
dbvar_G_VHRatio_ParkImpactFactor

  
  
  """


