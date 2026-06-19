# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import pandas as pd
import copy
import math
from io import StringIO
from tabulate import tabulate
from pathlib import Path
import shlex #for splitting strings by white space but preserving words within quotes

import MLB_dbvar as MLB_dbvar
import MLB_Scion_Globals as MLB_global

class scionPREDS:
	def __init__(self, predspath, app_ver):
		#1. files and dataframes
		self._preds_timestamp = datetime.today()
		self.preds_path = predspath #will typically be cwd or results/predictions/
		# If PREDS_FOLDER_ROOTNAME is an absolute path (set via env var by run_scion.py),
		# use it directly as the subfolder — no extra hidden folder appended.
		# If it is a bare folder name (legacy default), join it to predspath as before.
		if os.path.isabs(MLB_global.PREDS_FOLDER_ROOTNAME):
			self.preds_subfolder_path = MLB_global.PREDS_FOLDER_ROOTNAME
		else:
			self.preds_subfolder_path = os.path.join(predspath, MLB_global.PREDS_FOLDER_ROOTNAME)
  		#self.preds_path = os.path.join(predspath, (MLB_global.PREDS_FOLDER_ROOTNAME + self._preds_timestamp.strftime('%Y%m%d'))) #includes subfolder
		self._usrname = os.path.split(os.path.expanduser('~'))[-1]
		self._preds_stem_fname = "MLB_Scion" + MLB_global.APP_VER_SHORT + "_" + str(self._usrname)
		self._preds_verbose_csv_fname = os.path.join(self.preds_subfolder_path, (self._preds_stem_fname + "_VERBOSE_" + self._preds_timestamp.strftime('%Y%m%d%H%M%S') + ".csv"))
		self._preds_summary_csv_fname = os.path.join(self.preds_subfolder_path, (self._preds_stem_fname + "_SUMMARY_" + self._preds_timestamp.strftime('%Y%m%d%H%M%S') + ".csv"))
		self._preds_eplays_txt_fname = os.path.join(self.preds_subfolder_path, (self._preds_stem_fname + "_ePLAYS_" + self._preds_timestamp.strftime('%Y%m%d%H%M%S') + ".txt"))
		self._preds_iplays_txt_fname = os.path.join(self.preds_subfolder_path, (self._preds_stem_fname + "_iPLAYS_" + self._preds_timestamp.strftime('%Y%m%d%H%M%S') + ".txt"))
		self._preds_ipos_txt_fname = os.path.join(self.preds_subfolder_path, (self._preds_stem_fname + "_iPOS_" + self._preds_timestamp.strftime('%Y%m%d%H%M%S') + ".txt"))
		#preds filenames that will be stored in the predspath (cwd) rather than subfolder
		self._preds_iplays_cwd_txt_fname = os.path.join(self.preds_path, (self._preds_stem_fname + "_iPLAYS" + ".txt"))
		self._preds_ipos_cwd_txt_fname = os.path.join(self.preds_path, (self._preds_stem_fname + "_iPOS" + ".txt"))
		self._preds_eplays_cwd_txt_fname = os.path.join(self.preds_path, (self._preds_stem_fname + "_ePLAYS" + ".txt"))
		self._preds_summary_cwd_csv_fname = os.path.join(self.preds_path, (self._preds_stem_fname + "_SUMMARY" + ".csv"))	
		#preds filenames that will be stored in the MLB_global.DESKTOP_PATH
		self._preds_iplays_desktop_txt_fname = os.path.join(os.path.expanduser('~'),'Desktop',(self._preds_stem_fname + "_iPLAYS" + ".txt"))
		self._preds_ipos_desktop_txt_fname = os.path.join(os.path.expanduser('~'),'Desktop',(self._preds_stem_fname + "_iPOS" + ".txt"))
		self._preds_eplays_desktop_txt_fname = os.path.join(os.path.expanduser('~'),'Desktop',(self._preds_stem_fname + "_ePLAYS" + ".txt"))
		#2. cols for pred output
		self._preds_Id_attrib = "Pred_Id"
		self._preds_date_attrib = "Date"
		self._preds_MonthWeekNum_attrib = "MonthWeekNum"
		self._preds_Bookie_Total_attrib = "BookieTotal"
		self._preds_V_Id_attrib = "V_Id"
		self._preds_V_Sname_attrib = "V_Team"
		self._preds_V_Bookie_Opening_Price_attrib = "V_Bookie_Opening_Price"
		self._preds_V_Bookie_Opening_Prob_attrib = "V_Bookie_Opening_Prob"
		self._preds_V_Bookie_Bet_Price_attrib = "V_Bookie_Bet_Price"
		self._preds_V_Bookie_Bet_Prob_attrib = "V_Bookie_Bet_Prob"
		self._preds_V_Bookie_Bet_DevigProb_attrib = "V_Bookie_Bet_DevigProb"
		self._preds_V_SP_Id_attrib = "V_SP_Id"
		self._preds_V_SP_Null_attrib = "V_SP_isNull"
		self._preds_V_WinningForm_Price_attrib = "V_WinningForm_Price"
		self._preds_V_Offense_Price_attrib = "V_MenOnBaseStrength20G_Price"
		self._preds_V_Offense_strPrice_attrib = "V_MenOnBaseStrength20G_strPrice"
		self._preds_V_Offense_StrengthCategory_attrib = "V_MenOnBaseStrength20G_StrengthCategory"
		self._preds_V_Defense_Price_attrib = "V_SP_BaseOnBallsStrikeout5G_Price"
		self._preds_V_Defense_strPrice_attrib = "V_SP_BaseOnBallsStrikeout5G_strPrice"
		self._preds_V_Defense_StrengthCategory_attrib = "V_SP_BaseOnBallsStrikeout5G_StrengthCategory"
		self._preds_H_Id_attrib = "H_Id"
		self._preds_H_Sname_attrib = "H_Team"
		self._preds_H_Bookie_Opening_Price_attrib = "H_Bookie_Opening_Price"
		self._preds_H_Bookie_Opening_Prob_attrib = "H_Bookie_Opening_Prob"
		self._preds_H_Bookie_Bet_Price_attrib = "H_Bookie_Bet_Price"
		self._preds_H_Bookie_Bet_Prob_attrib = "H_Bookie_Bet_Prob"
		self._preds_H_Bookie_Bet_DevigProb_attrib = "H_Bookie_Bet_DevigProb"
		self._preds_H_SP_Id_attrib = "H_SP_Id"
		self._preds_H_SP_Null_attrib = "H_SP_isNull"
		self._preds_H_WinningForm_Price_attrib = "H_WinningForm_Price"
		self._preds_H_Offense_Price_attrib = "H_MenOnBaseStrength20G_Price"
		self._preds_H_Offense_strPrice_attrib = "H_MenOnBaseStrength20G_strPrice"
		self._preds_H_Offense_StrengthCategory_attrib = "H_MenOnBaseStrength20G_StrengthCategory"
		self._preds_H_Defense_Price_attrib = "H_SP_BaseOnBallsStrikeout5G_Price"
		self._preds_H_Defense_strPrice_attrib = "H_SP_BaseOnBallsStrikeout5G_strPrice"
		self._preds_H_Defense_StrengthCategory_attrib = "H_SP_BaseOnBallsStrikeout5G_StrengthCategory"
		self._preds_Ens1_VoterProfile_attrib = "PM150LineStat_VoterProfile"
		self._preds_Ens1_MajorityVote_attrib = "PM150LineStat_MajorityVote"
		self._preds_Ens1_NumVoters_attrib = "PM150LineStat_NumVoters"
		self._preds_Ens1_VoteAgreement_attrib = "PM150LineStat_VoteAgreement"
		self._preds_Ens1_HProbability_attrib = "PM150LineStat_H_Probability"
		self._preds_Ens1_HProbabilityEdge_attrib = "PM150LineStat_H_ProbabilityEdge"
		self._preds_Ens1_HPrice_attrib = "PM150LineStat_H_Price"
		self._preds_Ens1_PlayPosition_attrib = "PM150LineStat_PlayPosition"
		self._preds_Ens1_PlayStake_attrib = "PM150LineStat_PlayStake"
		self._preds_Ens1_PlayPayoutMultiplier_attrib = "PM150LineStat_PlayPayoutMultiplier"
		self._preds_Ens2_VoterProfile_attrib = "PM150StatOnly_VoterProfile"
		self._preds_Ens2_MajorityVote_attrib = "PM150StatOnly_MajorityVote"
		self._preds_Ens2_NumVoters_attrib = "PM150StatOnly_NumVoters"
		self._preds_Ens2_VoteAgreement_attrib = "PM150StatOnly_VoteAgreement"
		self._preds_Ens2_HProbability_attrib = "PM150StatOnly_H_Probability"
		self._preds_Ens2_HProbabilityEdge_attrib = "PM150StatOnly_H_ProbabilityEdge"
		self._preds_Ens2_HPrice_attrib = "PM150StatOnly_H_Price"
		self._preds_Ens2_PlayPosition_attrib = "PM150StatOnly_PlayPosition"
		self._preds_Ens2_PlayStake_attrib = "PM150StatOnly_PlayStake"
		self._preds_Ens2_PlayPayoutMultiplier_attrib = "PM150StatOnly_PlayPayoutMultiplier"
		self._preds_Scion_Side_Position_attrib = "Scion_Side_Play_Position"
		self._preds_Scion_Side_Stars_attrib = "Scion_Side_Stars"
		self._preds_Scion_Side_Confidence_attrib = "Scion_Side_Play_Confidence"
		self._preds_Comments_attrib = "Comments"

		self._preds_iPos_GId_attrib = "GID"
		self._preds_iPos_V_Team_Sname_attrib = "VIS"
		self._preds_iPos_H_Team_Sname_attrib = "HOM"
		self._preds_iPos_V_Bookie_Bet_Price_attrib = "VLINE"
		self._preds_iPos_H_Bookie_Bet_Price_attrib = "HLINE"
		self._preds_iPos_Defense_HPrice_attrib = "DEF_H"
		self._preds_iPos_Offense_HPrice_attrib = "OFF_H"
		self._preds_iPos_Ens1_HPrice_attrib = "ENS_PM150LineStat_HPrice"
		self._preds_iPos_Ens2_HPrice_attrib = "ENS_PM150StatOnly_HPrice"
		self._preds_iPos_Scion_Play_attrib = "PRED"
		self._preds_iPos_Comments_attrib = "NOTES"

		self._preds_iPlay_GId_attrib = "Game_Id"
		self._preds_iPlay_BookiePricePlay_attrib = "ML_Play"
		self._preds_iPlay_V_Team_Sname_attrib = "Vis"
		self._preds_iPlay_H_Team_Sname_attrib = "Hom"
		self._preds_iPlay_Defense_HPrice_attrib = "DEF_hPrice"
		self._preds_iPlay_Offense_HPrice_attrib = "OFF_hPrice"
		self._preds_iPlay_Ens1_HPrice_attrib = "ENS_PM150LineStat_HPrice"
		self._preds_iPlay_Ens2_HPrice_attrib = "ENS_PM150StatOnly_HPrice"
		self._preds_iPlay_Confidence_attrib = "ScionConf"
		self._preds_ePlay_GId_attrib = "Game_Id"
		self._preds_ePlay_Team_Sname_attrib = "Team"
		self._preds_ePlay_BookiePrice_attrib = "ML"
		self._preds_ePlay_Position_attrib = "Play"

		#3. group cols according to verbose, summary, pos or play
		self._preds_verbose_cols =	[
										self._preds_Id_attrib,
										self._preds_date_attrib,
										self._preds_MonthWeekNum_attrib,
										self._preds_Bookie_Total_attrib,
										self._preds_V_Id_attrib,
										self._preds_V_Sname_attrib,
										self._preds_V_Bookie_Opening_Price_attrib,
										self._preds_V_Bookie_Opening_Prob_attrib,
										self._preds_V_Bookie_Bet_Price_attrib,
										self._preds_V_Bookie_Bet_Prob_attrib,
										self._preds_V_Bookie_Bet_DevigProb_attrib,
										self._preds_V_SP_Id_attrib,
										self._preds_V_SP_Null_attrib,
										self._preds_V_WinningForm_Price_attrib,
										self._preds_V_Offense_Price_attrib,
										self._preds_V_Offense_strPrice_attrib,
										self._preds_V_Offense_StrengthCategory_attrib,
										self._preds_V_Defense_Price_attrib,
										self._preds_V_Defense_strPrice_attrib,
										self._preds_V_Defense_StrengthCategory_attrib,
										self._preds_H_Id_attrib,
										self._preds_H_Sname_attrib,
										self._preds_H_Bookie_Opening_Price_attrib,
										self._preds_H_Bookie_Opening_Prob_attrib,
										self._preds_H_Bookie_Bet_Price_attrib,
										self._preds_H_Bookie_Bet_Prob_attrib,
										self._preds_H_Bookie_Bet_DevigProb_attrib,
										self._preds_H_SP_Id_attrib,
										self._preds_H_SP_Null_attrib,
										self._preds_H_WinningForm_Price_attrib,
										self._preds_H_Offense_Price_attrib,
										self._preds_H_Offense_strPrice_attrib,
										self._preds_H_Offense_StrengthCategory_attrib,
										self._preds_H_Defense_Price_attrib,
										self._preds_H_Defense_strPrice_attrib,
										self._preds_H_Defense_StrengthCategory_attrib,
										self._preds_Ens1_VoterProfile_attrib,
										self._preds_Ens1_MajorityVote_attrib,
										self._preds_Ens1_NumVoters_attrib,
										self._preds_Ens1_VoteAgreement_attrib,
										self._preds_Ens1_HProbability_attrib,
										self._preds_Ens1_HProbabilityEdge_attrib,
										self._preds_Ens1_HPrice_attrib,
										self._preds_Ens1_PlayPosition_attrib,
										self._preds_Ens1_PlayStake_attrib,
										self._preds_Ens1_PlayPayoutMultiplier_attrib,
										self._preds_Ens2_VoterProfile_attrib,
										self._preds_Ens2_MajorityVote_attrib,
										self._preds_Ens2_NumVoters_attrib,
										self._preds_Ens2_VoteAgreement_attrib,
										self._preds_Ens2_HProbability_attrib,
										self._preds_Ens2_HProbabilityEdge_attrib,
										self._preds_Ens2_HPrice_attrib,
										self._preds_Ens2_PlayPosition_attrib,
										self._preds_Ens2_PlayStake_attrib,
										self._preds_Ens2_PlayPayoutMultiplier_attrib,
										self._preds_Scion_Side_Position_attrib,
										self._preds_Scion_Side_Stars_attrib,
										self._preds_Scion_Side_Confidence_attrib,
										self._preds_Comments_attrib
									]

		self._preds_summary_cols =	[
										self._preds_Id_attrib,
										self._preds_MonthWeekNum_attrib,
										self._preds_V_Id_attrib,
										self._preds_V_Sname_attrib,
										self._preds_V_Bookie_Opening_Price_attrib,
										self._preds_V_Bookie_Bet_Price_attrib,
										self._preds_V_SP_Id_attrib,
										self._preds_V_SP_Null_attrib,
										self._preds_V_WinningForm_Price_attrib,
										self._preds_V_Offense_strPrice_attrib,
										self._preds_V_Defense_strPrice_attrib,
										self._preds_H_Id_attrib,
										self._preds_H_Sname_attrib,
										self._preds_H_Bookie_Opening_Price_attrib,
										self._preds_H_Bookie_Bet_Price_attrib,
										self._preds_H_SP_Id_attrib,
										self._preds_H_SP_Null_attrib,
										self._preds_H_WinningForm_Price_attrib,
										self._preds_H_Offense_strPrice_attrib,
										self._preds_H_Defense_strPrice_attrib,
										self._preds_Ens1_VoterProfile_attrib,
										self._preds_Ens1_VoteAgreement_attrib,
										self._preds_Ens1_HProbabilityEdge_attrib,
										self._preds_Ens1_HPrice_attrib,
										self._preds_Ens1_PlayPosition_attrib,
										self._preds_Ens1_PlayStake_attrib,
										self._preds_Ens1_PlayPayoutMultiplier_attrib,
										self._preds_Ens2_VoterProfile_attrib,
										self._preds_Ens2_VoteAgreement_attrib,
										self._preds_Ens2_HProbabilityEdge_attrib,
										self._preds_Ens2_HPrice_attrib,
										self._preds_Ens2_PlayPosition_attrib,
										self._preds_Ens2_PlayStake_attrib,
										self._preds_Ens2_PlayPayoutMultiplier_attrib,
										self._preds_Scion_Side_Position_attrib,
										self._preds_Scion_Side_Stars_attrib,
										self._preds_Scion_Side_Confidence_attrib,
										self._preds_Comments_attrib
									]

		self._preds_ipos_cols =		[
										self._preds_iPos_GId_attrib,
										self._preds_iPos_V_Team_Sname_attrib,
										self._preds_iPos_V_Bookie_Bet_Price_attrib,
										self._preds_iPos_H_Team_Sname_attrib,
										self._preds_iPos_H_Bookie_Bet_Price_attrib,
										self._preds_iPos_Defense_HPrice_attrib,
										self._preds_iPos_Offense_HPrice_attrib,
										self._preds_iPos_Ens1_HPrice_attrib,
										self._preds_iPos_Ens2_HPrice_attrib,
										self._preds_iPos_Scion_Play_attrib,
										self._preds_iPos_Comments_attrib
									]


		self._preds_iplay_cols =	[
										self._preds_iPlay_GId_attrib,
										self._preds_iPlay_BookiePricePlay_attrib,
										self._preds_iPlay_V_Team_Sname_attrib,
										self._preds_iPlay_H_Team_Sname_attrib,
										self._preds_iPlay_Defense_HPrice_attrib,
										self._preds_iPlay_Offense_HPrice_attrib,
										self._preds_iPlay_Ens1_HPrice_attrib,
										self._preds_iPlay_Ens2_HPrice_attrib,
										self._preds_iPlay_Confidence_attrib
									]

		self._preds_eplay_cols =	[
										self._preds_ePlay_GId_attrib,
										self._preds_ePlay_Team_Sname_attrib,
										self._preds_ePlay_BookiePrice_attrib,
										self._preds_ePlay_Position_attrib
									]	

		self._preds_int_cols 	=	[
										self._preds_V_Id_attrib,
										self._preds_V_SP_Id_attrib,
										self._preds_H_Id_attrib,
										self._preds_H_SP_Id_attrib,
										self._preds_Ens1_NumVoters_attrib,
										self._preds_Ens2_NumVoters_attrib,
										self._preds_Scion_Side_Stars_attrib
									]
		self._preds_float_cols 	=	[
										self._preds_MonthWeekNum_attrib,
										self._preds_Bookie_Total_attrib,
										self._preds_V_Bookie_Opening_Price_attrib,
										self._preds_V_Bookie_Opening_Prob_attrib,
										self._preds_V_Bookie_Bet_Price_attrib,
										self._preds_V_Bookie_Bet_Prob_attrib,
										self._preds_V_Bookie_Bet_DevigProb_attrib,
										self._preds_V_Offense_Price_attrib,
										self._preds_V_Defense_Price_attrib,
										self._preds_H_Bookie_Opening_Price_attrib,
										self._preds_H_Bookie_Opening_Prob_attrib,
										self._preds_H_Bookie_Bet_Price_attrib,
										self._preds_H_Bookie_Bet_Prob_attrib,
										self._preds_H_Bookie_Bet_DevigProb_attrib,
										self._preds_H_Offense_Price_attrib,
										self._preds_H_Defense_Price_attrib,
										self._preds_Ens1_VoteAgreement_attrib,
										self._preds_Ens1_HProbability_attrib,
										self._preds_Ens1_HProbabilityEdge_attrib,
										self._preds_Ens1_HPrice_attrib,
										self._preds_Ens1_PlayStake_attrib,
										self._preds_Ens1_PlayPayoutMultiplier_attrib,
										self._preds_Ens2_VoteAgreement_attrib,
										self._preds_Ens2_HProbability_attrib,
										self._preds_Ens2_HProbabilityEdge_attrib,
										self._preds_Ens2_HPrice_attrib,
										self._preds_Ens2_PlayStake_attrib,
										self._preds_Ens2_PlayPayoutMultiplier_attrib,
										self._preds_Scion_Side_Confidence_attrib,
									]

		self._preds_str_cols 	=	[
										self._preds_Id_attrib,
										self._preds_V_Sname_attrib,
										self._preds_V_Offense_strPrice_attrib,
										self._preds_V_Offense_StrengthCategory_attrib,
										self._preds_V_Defense_strPrice_attrib,
										self._preds_V_Defense_StrengthCategory_attrib,
										self._preds_H_Sname_attrib,
										self._preds_H_Offense_strPrice_attrib,
										self._preds_H_Offense_StrengthCategory_attrib,
										self._preds_H_Defense_strPrice_attrib,
										self._preds_H_Defense_StrengthCategory_attrib,
										self._preds_Ens1_VoterProfile_attrib,
										self._preds_Ens1_MajorityVote_attrib,
										self._preds_Ens1_PlayPosition_attrib,
										self._preds_Ens2_VoterProfile_attrib,
										self._preds_Ens2_MajorityVote_attrib,
										self._preds_Ens2_PlayPosition_attrib,
										self._preds_Scion_Side_Position_attrib,
										self._preds_Comments_attrib
									]

		self._preds_ipos_int_cols 	=	[]

		self._preds_ipos_float_cols =	[	
											self._preds_iPos_V_Bookie_Bet_Price_attrib,
											self._preds_iPos_H_Bookie_Bet_Price_attrib,
											self._preds_iPos_Defense_HPrice_attrib,
											self._preds_iPos_Offense_HPrice_attrib,
											self._preds_iPos_Ens1_HPrice_attrib,
											self._preds_iPos_Ens2_HPrice_attrib
										]

		self._preds_ipos_str_cols 	=	[
											self._preds_iPos_GId_attrib,
											self._preds_iPos_Scion_Play_attrib,
											self._preds_iPos_V_Team_Sname_attrib,
											self._preds_iPos_H_Team_Sname_attrib
										]

		self._preds_iplay_int_cols 	=	[]

		self._preds_iplay_float_cols =	[	
											self._preds_iPlay_Defense_HPrice_attrib,
											self._preds_iPlay_Offense_HPrice_attrib,
											self._preds_iPlay_Ens1_HPrice_attrib,
											self._preds_iPlay_Ens2_HPrice_attrib,
											self._preds_iPlay_Confidence_attrib
										]

		self._preds_iplay_str_cols 	=	[
											self._preds_iPlay_GId_attrib,
											self._preds_iPlay_BookiePricePlay_attrib,
											self._preds_iPlay_V_Team_Sname_attrib,
											self._preds_iPlay_H_Team_Sname_attrib,
											self._preds_iPlay_Confidence_attrib
										]

		self._preds_eplay_int_cols 	=	[]

		self._preds_eplay_float_cols =	[
											self._preds_ePlay_BookiePrice_attrib
										]

		self._preds_eplay_str_cols 	=	[
											self._preds_ePlay_GId_attrib,
											self._preds_ePlay_Team_Sname_attrib,
											self._preds_ePlay_Position_attrib
										]
		#6.Create dict of voting positions for each allowable ensemble (offense, defense, integoffdefense). Each dict will contain elements with following structure: 
		# {"voter id":[numerical pred, pred position]} eg self.preds_offense_vote_dict = {"M1":[0.4555, "VF"], "M2":[0.677, "HD"]} 
		# or self.preds_total_vote_dict = {"M1":[6.5, "Over"], "M2":[3.9999, "Under"]} 
		self.preds_ens1_vote_dict = {}
		self.preds_ens2_vote_dict = {}
		#7. Create a dict for a single game (excluding preds_Play variables)
		self.preds_current_game_dict = {}
		self.preds_ipos_current_game_dict = {}
		#8. Create a dict for a play
		self.preds_iplays_current_game_dict = {}
		self.preds_eplays_current_game_dict = {}
		#9. Define key dataframes
		self.preds_verbose_df = pd.DataFrame(columns=self._preds_verbose_cols)
		self.preds_summary_df = pd.DataFrame #this will actually just be a subset of verbose
		self.preds_ipos_df = pd.DataFrame(columns=self._preds_ipos_cols)
		self.preds_iplays_df = pd.DataFrame(columns=self._preds_iplay_cols)
		self.preds_eplays_df = pd.DataFrame(columns=self._preds_eplay_cols)
		#10. Flag indicating whether or not the line has been adjusted due to the span feature
		self.preds_opladjusted = False
		self.preds_Bookie_Totaladjusted = False
		#11. Create system folder for preds
		self._createPREDSFolder()
	
	def _createPREDSFolder(self):
        #Attempts to create a log folder so that files can be stored there
        #An exception will be raised if the folder cannot be created
		try:
			os.makedirs(self.preds_subfolder_path, exist_ok=True)
        
		except:
			print("\nscionPREDS._createPREDSFolder(): unexpected error creating the system folder " + str(self.preds_subfolder_path))
			raise
  
	def _getProbabilityMajorityVote(self, ens, ensProbType):
	# This traverses the relevant ens dict, counting the number of different positions and returns the key with the highest frequency
	# NoPlays must be considered a valid voter and thus if it is the majority vote, there is no play
	# 02 May 2025: new feature: add a flag that if true only generates an average based on voters that agree with the majority vote
	# 12 Jun 2026: new feature: return the median vote rather average. Note: if this is active then avgMajVotersOnly will be turned off as mutually exclusive
	# NOTE: the probability could be HWin or FaveWin so we must just return the average probability and allow the calling program to deal with what it means
		try:
			# 1. Create spread freq count dict
			_playFreqDict = {MLB_global.ACTION_NOPLAYPUSH : 0, MLB_global.ACTION_NOPLAY : 0, MLB_global.ACTION_LINE_HF : 0, MLB_global.ACTION_LINE_HD : 0, MLB_global.ACTION_LINE_VF : 0, MLB_global.ACTION_LINE_VD : 0}
			_playProbSumDict = {MLB_global.ACTION_NOPLAYPUSH : 0, MLB_global.ACTION_NOPLAY : 0, MLB_global.ACTION_LINE_HF : 0, MLB_global.ACTION_LINE_HD : 0, MLB_global.ACTION_LINE_VF : 0, MLB_global.ACTION_LINE_VD : 0}
			_validVotes = _playFreqDict.keys()
			_probList = []
			# 2. COPY the correct ens dict (we dont want to change the original)
			ens_dict = {}
			if ens == MLB_global.MODEL_PROBENS1:
				ens_dict = copy.deepcopy(self.preds_ens1_vote_dict)
			elif ens == MLB_global.MODEL_PROBENS2:
				ens_dict = copy.deepcopy(self.preds_ens2_vote_dict)
			else: #unknown
				print("Unrecognised probability ensemble!")
				raise Exception
			# 3. Ensure medianProb and avgMajVotersOnly flags are mutually exclusive (medianProb takes precedence if both true)
			medianProb = avgMajVotersOnly = MLB_global.NO #default value is to return avg of all voters
			if ensProbType == MLB_global.EnsembleProbabilityTypes.MedianAllVoters.value:
				medianProb = MLB_global.YES
			else:
				if ensProbType == MLB_global.EnsembleProbabilityTypes.AvgMajorityVotersOnly.value:
					avgMajVotersOnly = MLB_global.YES
            # 4. Now traverse dict, increasing frequency counts 
			numVotes = len(ens_dict)
			voteCtr = 0
			_avgProb = 0.0
			for k, v in ens_dict.items():
				#format of v is [pred, pos], we just want pos so just pop last item
				_vote = v.pop() #get pos
				_homProb = v.pop() #get pred
				#check if valid:
				if _vote not in _validVotes:
					print("\nError - " + str(_vote) + " is an unrecognised voting position!")
					raise Exception
				#all good, so now increment relevant dict item and increase avgSpread and add current prob to _probList
				_playFreqDict[_vote] += 1
				_playProbSumDict[_vote] += _homProb
				voteCtr += 1
				_avgProb += float(_homProb)
				_probList.append(float(_homProb))
			# 5. Check all votes counted
			if voteCtr != numVotes:
				print("\nError - not all votes have been counted. Expecting " + str(numVotes) + " but processed " + str(voteCtr))
				raise Exception
			# 6. Calc avg
			_avgProb /= voteCtr
			# 7. Get key with highest vote (need to combine NOPLAYPUSH and NOPLAY)
			_majorityVote = max(_playFreqDict.keys(), key=(lambda k: _playFreqDict[k]))
			# 8. Get desired form of probability (default is avg of all; others: median of all voters or avg of majority voters)
			if medianProb == MLB_global.YES:
				_avgProb = float(MLB_global.calcMedian(_probList))
			else:
				if avgMajVotersOnly == MLB_global.YES:
					_avgProb = _playProbSumDict[_majorityVote] / _playFreqDict[_majorityVote]
			_majorityWgt = max(_playFreqDict.items(), key=lambda k: k[1])
			_majorityWgt = _majorityWgt[1] #just get count
			_numNoPlays = _playFreqDict[MLB_global.ACTION_NOPLAYPUSH]
			_numNoPlays += _playFreqDict[MLB_global.ACTION_NOPLAY]
			if _numNoPlays >= _majorityWgt or (_majorityWgt == 1 and numVotes > 1):
				_majorityWgt = _numNoPlays
				_majorityVote = MLB_global.ACTION_NOPLAY

		except Exception:
			print("\nscionPREDS._getProbabilityMajorityVote(): error when determining majority vote amongst the spread voters in ensemble " + str(ens))
			raise
		
		return numVotes, _majorityVote, _majorityWgt, _avgProb, _numNoPlays

	def _getRunEnsModelPrediction(self, ens, modelNum):
	# New Feature 31Jan2022: This traverses the relevant spread ens dict, to identify and return the run prediction of a specfic model
	# Assumption: This function is called AFTER _getEnsembleAverageRuns has been called for the relevant ensemble
	# Input: ens and modelNum
	# Return: boolean flag indicating whether model was found, run prediction of model if found (will be 0.0 if not found)
		try:
			# 1. Check valid dict
			ens_dict = {}
			if ens == MLB_global.MODEL_PROBENS1:
				ens_dict = copy.deepcopy(self.preds_ens1_vote_dict)
			elif ens == MLB_global.MODEL_PROBENS2:
				ens_dict = copy.deepcopy(self.preds_ens2_vote_dict)
			else: #unknown
				print("Unrecognised run ensemble!")
				raise Exception
			# 2. Now traverse dict, find model and return pos
			_modelFound = False
			_modelPred = 0.0
			for k, v in ens_dict.items():
				#check if we've found desired model and thus position
				if modelNum == k:
					#format of v is [pred, pos], we just want pos so just pop last item
					_modelPred = v.pop() #get pred
					_modelFound = True
					break
 
		except Exception:
			print("\nscionPREDS._getRunEnsModelPrediction(): error when retrieving a run prediction for a specific model within the ensemnble " + str(ens))
			raise
		
		return _modelFound, _modelPred
	
	def _getEnsembleAverageRuns(self, ens):
		# This traverses the relevant ens dict and returns the average run prediction in the ensemble
			try:
				# 1. COPY the correct ens dict (we dont want to change the original)
				ens_dict = {}
				if ens == MLB_global.MODEL_VRUNENS:
					ens_dict = copy.deepcopy(self.preds_C3vrun_Vote_dict)
				elif ens == MLB_global.MODEL_HRUNENS:
					ens_dict = copy.deepcopy(self.preds_C1hrun_Vote_dict)
				else: #unknown
					print("Unrecognised run ensemble!")
					raise Exception
				# 2. Now traverse dict, increasing frequency counts 
				numVotes = len(ens_dict)
				voteCtr = 0
				_avgRuns = 0.0
				for k, v in ens_dict.items():
					#format of v is [pred, pos], we just want pos so just pop last item
					_vote = v.pop() #get pos (not really used)
					_pred = v.pop() #get pred
					voteCtr += 1
					_avgRuns += float(_pred)
				# 4. Check all votes counted
				if voteCtr != numVotes:
					print("\nError - not all votes have been counted. Expecting " + str(numVotes) + " but processed " + str(voteCtr))
					raise Exception
				# 5. Calc avg
				if voteCtr > 0:
					_avgRuns /= voteCtr
	
			except Exception:
				print("\nscionPREDS._getEnsembleAverageRuns(): error when determining run average for ensemble " + str(ens))
				raise
			
			return numVotes, _avgRuns

	def _highlight_text(self, text, highlightSym, numSym=None):
		if numSym == 0:
			return text
		if numSym == None:
			numSym = 1
		highlighted_text = ""
		for i in range(0, numSym):
			highlighted_text += highlightSym
		highlighted_text += " " + text + " "
		for i in range(0, numSym):
			highlighted_text += highlightSym
		
		return highlighted_text

	def _convertNestedList2String(self, nlist):
		list_str = [' '.join([str(elem) for elem in sublist]) for sublist in nlist]
		return list_str
	
	def _convertDict2NestedList(self, dict):
		nlist = [[k, v] for k,v in dict.items()]
		return nlist

	def _convertEnsDict2Str(self, ens_dict):
		nlist = self._convertDict2NestedList(ens_dict)
		nlist_str = self._convertNestedList2String(nlist)
		return nlist_str

	def _updateCurrentGameVoterProfiles(self, ens):
		#A1) assumes each ens dict contains full complement of data and in the following form:
		# {"voter id":[numerical pred, pred position]} eg self.preds_offense_vote_dict = {"M22":[0.2345, "VF"], "M23":[0.51864, "HD"]}
		#A2) Each dict will be converted to a nested list and then a flattened string
		#A3) The relevant voter profile entry in self.preds_current_game_dict will then be updated
		try:
			ens_str = ""
			if ens == MLB_global.MODEL_PROBENS1:
				ens_str = self._convertEnsDict2Str(self.preds_ens1_vote_dict)
				self.preds_current_game_dict[self._preds_Ens1_VoterProfile_attrib] = ens_str
			elif ens == MLB_global.MODEL_PROBENS2:
				ens_str = self._convertEnsDict2Str(self.preds_ens2_vote_dict)
				self.preds_current_game_dict[self._preds_Ens2_VoterProfile_attrib] = ens_str
			else:
				print("\nUnrecognised ensemble " + str(ens) + "!")
				raise Exception
		except Exception:
			print("\nscionPREDS._updateCurrentGameVoterProfiles(): error when updating voter profile for the " + str(ens) + " ensemble.")
			raise
			
	def _storePredsCSV(self, _df, _fname, colOrderList):
		try:
			#Attempt to store verbose preds to file
			#_df.to_csv(_fname, index=False, header=True, float_format=_format)
			_df.to_csv(_fname, index=False, header=True, columns=colOrderList)
		except:
			raise

	def addComment(self, commentStr, predsPlayComment=False, onlypredsPlayComment=False):
		# Write commentStr to main preds file. If predsPlayComment is True then also write commentStr to the predsPlay dict
		#a. Check new comment has something useful
		_newComm = str(commentStr)
		_newData = False
		#1. validate existing comments
		_currStr = str(self.getPreds_Comments())
		if str(MLB_dbvar.NO_DATA) in _currStr :
			_currStr = ""
		#2. check if we have new comments
		if str(MLB_dbvar.NO_DATA) not in _newComm and len(_newComm) and commentStr not in _currStr:
			_newData = True
		else:
			_newComm = _currStr
		#3. Update comments if we have new data
		if _newData:
			_newStr = _currStr + _newComm
			if not onlypredsPlayComment:
				self.setPreds_Comments(_newStr)
			else:
				#self.setPreds_iPlay_Comments(_newStr)
				return
   
	def initAllCols(self):
		#1. Initialise verbose df columns (note _preds_summary_df will just be a subset of verbose)
		self.preds_verbose_df = MLB_global.setColType(self.preds_verbose_df, self._preds_int_cols, MLB_global.DF_COL_TYPE_INT)
		self.preds_verbose_df = MLB_global.setColType(self.preds_verbose_df, self._preds_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
		self.preds_verbose_df = MLB_global.setColType(self.preds_verbose_df, self._preds_str_cols, MLB_global.DF_COL_TYPE_STR)
		#2. Initialise ipos df cols
		self.preds_ipos_df = MLB_global.setColType(self.preds_ipos_df, self._preds_ipos_int_cols, MLB_global.DF_COL_TYPE_INT)
		self.preds_ipos_df = MLB_global.setColType(self.preds_ipos_df, self._preds_ipos_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
		self.preds_ipos_df = MLB_global.setColType(self.preds_ipos_df, self._preds_ipos_str_cols, MLB_global.DF_COL_TYPE_STR)
		#3. Initialise iplays df columns
		self.preds_iplays_df = MLB_global.setColType(self.preds_iplays_df, self._preds_iplay_int_cols, MLB_global.DF_COL_TYPE_INT)
		self.preds_iplays_df = MLB_global.setColType(self.preds_iplays_df, self._preds_iplay_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
		self.preds_iplays_df = MLB_global.setColType(self.preds_iplays_df, self._preds_iplay_str_cols, MLB_global.DF_COL_TYPE_STR)
		#4. Initialise eplays df columns
		self.preds_eplays_df = MLB_global.setColType(self.preds_eplays_df, self._preds_eplay_int_cols, MLB_global.DF_COL_TYPE_INT)
		self.preds_eplays_df = MLB_global.setColType(self.preds_eplays_df, self._preds_eplay_float_cols, MLB_global.DF_COL_TYPE_FLOAT)
		self.preds_eplays_df = MLB_global.setColType(self.preds_eplays_df, self._preds_eplay_str_cols, MLB_global.DF_COL_TYPE_STR)
	
	def initPredsDict(self):
		self.preds_current_game_dict =	{
											self._preds_Id_attrib:MLB_dbvar.NO_DATA,
											self._preds_date_attrib:MLB_dbvar.NO_DATA,
											self._preds_MonthWeekNum_attrib:MLB_dbvar.NO_DATA,
											self._preds_Bookie_Total_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Id_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Sname_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Bookie_Opening_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Bookie_Opening_Prob_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Bookie_Bet_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Bookie_Bet_Prob_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Bookie_Bet_DevigProb_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_SP_Id_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_SP_Null_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_WinningForm_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Offense_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Offense_strPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Offense_StrengthCategory_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Defense_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Defense_strPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_V_Defense_StrengthCategory_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Id_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Sname_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Bookie_Opening_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Bookie_Opening_Prob_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Bookie_Bet_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Bookie_Bet_Prob_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Bookie_Bet_DevigProb_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_SP_Id_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_SP_Null_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_WinningForm_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Offense_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Offense_strPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Offense_StrengthCategory_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Defense_Price_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Defense_strPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_H_Defense_StrengthCategory_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_VoterProfile_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_MajorityVote_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_NumVoters_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_VoteAgreement_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_HProbability_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_HProbabilityEdge_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_HPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_PlayPosition_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_PlayStake_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens1_PlayPayoutMultiplier_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_VoterProfile_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_MajorityVote_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_NumVoters_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_VoteAgreement_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_HProbability_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_HProbabilityEdge_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_HPrice_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_PlayPosition_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_PlayStake_attrib:MLB_dbvar.NO_DATA,
											self._preds_Ens2_PlayPayoutMultiplier_attrib:MLB_dbvar.NO_DATA,
											self._preds_Scion_Side_Position_attrib:MLB_dbvar.NO_DATA,
											self._preds_Scion_Side_Stars_attrib:MLB_dbvar.NO_DATA,
											self._preds_Scion_Side_Confidence_attrib:MLB_dbvar.NO_DATA,
											self._preds_Comments_attrib:MLB_dbvar.NO_DATA
										}

	def initPredsPosDict(self):
		self.preds_ipos_current_game_dict =	{
													self._preds_iPos_GId_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_V_Team_Sname_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_H_Team_Sname_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_V_Bookie_Bet_Price_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_H_Bookie_Bet_Price_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Defense_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Offense_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Ens1_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Ens2_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Scion_Play_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPos_Comments_attrib:str(MLB_dbvar.NO_DATA)
												}

	def initPredsPlayDict(self):
		self.preds_iplays_current_game_dict =	{
													self._preds_iPlay_GId_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_BookiePricePlay_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_V_Team_Sname_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_H_Team_Sname_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_Defense_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_Offense_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_Ens1_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_Ens2_HPrice_attrib:str(MLB_dbvar.NO_DATA),
													self._preds_iPlay_Confidence_attrib:str(MLB_dbvar.NO_DATA)
												}

		self.preds_eplays_current_game_dict =	{
													self._preds_ePlay_GId_attrib:MLB_dbvar.NO_DATA,
													self._preds_ePlay_Team_Sname_attrib:MLB_dbvar.NO_DATA,
													self._preds_ePlay_Position_attrib:MLB_dbvar.NO_DATA
												}

	def initVoterDicts(self):
		self.preds_ens1_vote_dict = {}
		self.preds_ens2_vote_dict = {}

	def initAllDicts(self):
		self.initVoterDicts()
		self.initPredsDict()
		self.initPredsPosDict()
		self.initPredsPlayDict()

	def _createPredId(self, isExtended=True):
		#Assumption 1: base data is available
		#This func might be called from Scion for skipped games
		_dateStr = self.getPreds_date()
		_monthweek = self.getPreds_monthweek()
		_vSname = self.getPreds_V_Sname()
		_hSname = self.getPreds_H_Sname()
		_hBetLine = self.getPreds_H_Bookie_Bet_Price()
		if isExtended:
			_predId = str(_dateStr.strftime(MLB_global.DATE_F) + "_MWK" + str(_monthweek) + "_" + _vSname + "@" + _hSname + "_" + str(_hBetLine))
		else:
			_predId = str(_dateStr.strftime(MLB_global.DATE_F) + "_" + _vSname + "@" + _hSname)
		return _predId
		
	def initPredsALL(self, mupsDB):
		self.initAllDicts()
		_gameDate = mupsDB.getCurrentMUPDate()
		_month = _gameDate.month
		_day = _gameDate.day
		self.setPreds_date(_gameDate)
		self.setPreds_monthweek(MLB_dbvar.createMonthWeek(_month, _day))
		self.setPreds_Bookie_Total(mupsDB.getCurrentMUPOverClose())
		_hPrice = mupsDB.getCurrentMUPHomeMLOpen()
		_vPrice = mupsDB.getCurrentMUPVisMLOpen()
		_hProb = MLB_global.convertMoneyLinetoProb(_hPrice)
		_vProb = MLB_global.convertMoneyLinetoProb(_vPrice)
		self.setPreds_V_Bookie_Opening_Price(_vPrice)
		self.setPreds_V_Bookie_Opening_Prob(_vProb)
		self.setPreds_H_Bookie_Opening_Price(_hPrice)
		self.setPreds_H_Bookie_Opening_Prob(_hProb)
		_hPrice = mupsDB.getCurrentMUPHomeMLClose()
		_vPrice = mupsDB.getCurrentMUPVisMLClose()
		_hProb = MLB_global.convertMoneyLinetoProb(_hPrice)
		_vProb = MLB_global.convertMoneyLinetoProb(_vPrice)
		self.setPreds_V_Bookie_Bet_Price(_vPrice)
		self.setPreds_V_Bookie_Bet_Prob(_vProb)
		self.setPreds_H_Bookie_Bet_Price(_hPrice)
		self.setPreds_H_Bookie_Bet_Prob(_hProb)
		self.setPreds_V_Id(mupsDB.getCurrentMUPVisId())
		self.setPreds_V_Sname(mupsDB.getCurrentMUPVisSName())
		self.setPreds_V_SP_Id(mupsDB.getCurrentMUPVisSPId())
		self.setPreds_H_Id(mupsDB.getCurrentMUPHomeId())
		self.setPreds_H_Sname(mupsDB.getCurrentMUPHomeSName())
		self.setPreds_H_SP_Id(mupsDB.getCurrentMUPHomeSPId())
		self.setPreds_Scion_Side_Stars(MLB_global.getNumStars(MLB_global.ModelConfidenceTypes.ZEROSTAR))
		#create and set id
		_predId = self._createPredId()
		self.setPreds_Id(_predId)
		#init data for iPos
		_predId = self._createPredId(False)
		self.setPreds_iPos_GId(_predId)
		self.setPreds_iPos_V_Team_Sname(mupsDB.getCurrentMUPVisSName())
		self.setPreds_iPos_H_Team_Sname(mupsDB.getCurrentMUPHomeSName())
		self.setPreds_iPos_V_Bookie_Price(_vPrice)
		self.setPreds_iPos_H_Bookie_Price(_hPrice)
		self.setPreds_iPos_Scion_Play(MLB_global.ACTION_NOPLAY) #this is important as if there's a play, predsPlay func will update

	#Setters
	def setPreds_Id(self, newValue):self.preds_current_game_dict[self._preds_Id_attrib] = newValue
	def setPreds_date(self, newValue):self.preds_current_game_dict[self._preds_date_attrib] = newValue
	def setPreds_monthweek(self, newValue):self.preds_current_game_dict[self._preds_MonthWeekNum_attrib] = newValue
	def setPreds_Bookie_Total(self, newValue):self.preds_current_game_dict[self._preds_Bookie_Total_attrib] = newValue
	def setPreds_V_Id(self, newValue):self.preds_current_game_dict[self._preds_V_Id_attrib] = newValue
	def setPreds_V_Sname(self, newValue):self.preds_current_game_dict[self._preds_V_Sname_attrib] = newValue
	def setPreds_V_Bookie_Opening_Price(self, newValue):self.preds_current_game_dict[self._preds_V_Bookie_Opening_Price_attrib] = newValue
	def setPreds_V_Bookie_Opening_Prob(self, newValue):self.preds_current_game_dict[self._preds_V_Bookie_Opening_Prob_attrib] = newValue
	def setPreds_V_Bookie_Bet_Price(self, newValue):self.preds_current_game_dict[self._preds_V_Bookie_Bet_Price_attrib] = newValue
	def setPreds_V_Bookie_Bet_Prob(self, newValue):self.preds_current_game_dict[self._preds_V_Bookie_Bet_Prob_attrib] = newValue
	def setPreds_V_Bookie_Bet_DevigProb(self, newValue):self.preds_current_game_dict[self._preds_V_Bookie_Bet_DevigProb_attrib] = newValue
	def setPreds_V_SP_Id(self, newValue):self.preds_current_game_dict[self._preds_V_SP_Id_attrib] = newValue
	def setPreds_V_SP_Null(self, newValue):self.preds_current_game_dict[self._preds_V_SP_Null_attrib] = newValue
	def setPreds_V_WinningForm_Price(self, newValue):self.preds_current_game_dict[self._preds_V_WinningForm_Price_attrib] = newValue
	def setPreds_V_OffensePrice(self, newValue):self.preds_current_game_dict[self._preds_V_Offense_Price_attrib] = newValue
	def setPreds_V_OffenseStrPrice(self, newValue):self.preds_current_game_dict[self._preds_V_Offense_strPrice_attrib] = newValue
	def setPreds_V_Offense_StrengthCategory(self, newValue):self.preds_current_game_dict[self._preds_V_Offense_StrengthCategory_attrib] = newValue
	def setPreds_V_DefensePrice(self, newValue):self.preds_current_game_dict[self._preds_V_Defense_Price_attrib] = newValue
	def setPreds_V_DefenseStrPrice(self, newValue):self.preds_current_game_dict[self._preds_V_Defense_strPrice_attrib] = newValue
	def setPreds_V_DefenseStrengthCategory(self, newValue):self.preds_current_game_dict[self._preds_V_Defense_StrengthCategory_attrib] = newValue
	def setPreds_H_Id(self, newValue):self.preds_current_game_dict[self._preds_H_Id_attrib] = newValue
	def setPreds_H_Sname(self, newValue):self.preds_current_game_dict[self._preds_H_Sname_attrib] = newValue
	def setPreds_H_Bookie_Opening_Price(self, newValue):self.preds_current_game_dict[self._preds_H_Bookie_Opening_Price_attrib] = newValue
	def setPreds_H_Bookie_Opening_Prob(self, newValue):self.preds_current_game_dict[self._preds_H_Bookie_Opening_Prob_attrib] = newValue
	def setPreds_H_Bookie_Bet_Price(self, newValue):self.preds_current_game_dict[self._preds_H_Bookie_Bet_Price_attrib] = newValue
	def setPreds_H_Bookie_Bet_Prob(self, newValue):self.preds_current_game_dict[self._preds_H_Bookie_Bet_Prob_attrib] = newValue
	def setPreds_H_Bookie_Bet_DevigProb(self, newValue):self.preds_current_game_dict[self._preds_H_Bookie_Bet_DevigProb_attrib] = newValue
	def setPreds_H_SP_Id(self, newValue):self.preds_current_game_dict[self._preds_H_SP_Id_attrib] = newValue
	def setPreds_H_SP_Null(self, newValue):self.preds_current_game_dict[self._preds_H_SP_Null_attrib] = newValue
	def setPreds_H_WinningForm_Price(self, newValue):self.preds_current_game_dict[self._preds_H_WinningForm_Price_attrib] = newValue
	def setPreds_H_OffensePrice(self, newValue):self.preds_current_game_dict[self._preds_H_Offense_Price_attrib] = newValue
	def setPreds_H_OffenseStrPrice(self, newValue):self.preds_current_game_dict[self._preds_H_Offense_strPrice_attrib] = newValue
	def setPreds_H_Offense_StrengthCategory(self, newValue):self.preds_current_game_dict[self._preds_H_Offense_StrengthCategory_attrib] = newValue
	def setPreds_H_DefensePrice(self, newValue):self.preds_current_game_dict[self._preds_H_Defense_Price_attrib] = newValue
	def setPreds_H_DefenseStrPrice(self, newValue):self.preds_current_game_dict[self._preds_H_Defense_strPrice_attrib] = newValue
	def setPreds_H_DefenseStrengthCategory(self, newValue):self.preds_current_game_dict[self._preds_H_Defense_StrengthCategory_attrib] = newValue
	def setPreds_Ens1_VoterProfile(self, newValue):self.preds_current_game_dict[self._preds_Ens1_VoterProfile_attrib] = newValue
	def setPreds_Ens1_MajorityVote(self, newValue):self.preds_current_game_dict[self._preds_Ens1_MajorityVote_attrib] = newValue
	def setPreds_Ens1_NumVoters(self, newValue):self.preds_current_game_dict[self._preds_Ens1_NumVoters_attrib] = newValue
	def setPreds_Ens1_VoteAgreement(self, newValue):self.preds_current_game_dict[self._preds_Ens1_VoteAgreement_attrib] = newValue
	def setPreds_Ens1_HWinProb(self, newValue):self.preds_current_game_dict[self._preds_Ens1_HProbability_attrib] = newValue
	def setPreds_Ens1_HProbabilityEdge(self, newValue):self.preds_current_game_dict[self._preds_Ens1_HProbabilityEdge_attrib] = newValue
	def setPreds_Ens1_HWinPrice(self, newValue):self.preds_current_game_dict[self._preds_Ens1_HPrice_attrib] = newValue
	def setPreds_Ens1_PlayPosition(self, newValue):self.preds_current_game_dict[self._preds_Ens1_PlayPosition_attrib] = newValue
	def setPreds_Ens1_PlayStake(self, newValue):self.preds_current_game_dict[self._preds_Ens1_PlayStake_attrib] = newValue
	def setPreds_Ens1_PlayPayoutMultiplier(self, newValue):self.preds_current_game_dict[self._preds_Ens1_PlayPayoutMultiplier_attrib] = newValue
	def setPreds_Ens2_VoterProfile(self, newValue):self.preds_current_game_dict[self._preds_Ens2_VoterProfile_attrib] = newValue
	def setPreds_Ens2_MajorityVote(self, newValue):self.preds_current_game_dict[self._preds_Ens2_MajorityVote_attrib] = newValue
	def setPreds_Ens2_NumVoters(self, newValue):self.preds_current_game_dict[self._preds_Ens2_NumVoters_attrib] = newValue
	def setPreds_Ens2_VoteAgreement(self, newValue):self.preds_current_game_dict[self._preds_Ens2_VoteAgreement_attrib] = newValue
	def setPreds_Ens2_HWinProb(self, newValue):self.preds_current_game_dict[self._preds_Ens2_HProbability_attrib] = newValue
	def setPreds_Ens2_HProbabilityEdge(self, newValue):self.preds_current_game_dict[self._preds_Ens2_HProbabilityEdge_attrib] = newValue
	def setPreds_Ens2_HWinPrice(self, newValue):self.preds_current_game_dict[self._preds_Ens2_HPrice_attrib] = newValue
	def setPreds_Ens2_PlayPosition(self, newValue):self.preds_current_game_dict[self._preds_Ens2_PlayPosition_attrib] = newValue
	def setPreds_Ens2_PlayStake(self, newValue):self.preds_current_game_dict[self._preds_Ens2_PlayStake_attrib] = newValue
	def setPreds_Ens2_PlayPayoutMultiplier(self, newValue):self.preds_current_game_dict[self._preds_Ens2_PlayPayoutMultiplier_attrib] = newValue
	def setPreds_Scion_Side_Position(self, newValue):self.preds_current_game_dict[self._preds_Scion_Side_Position_attrib] = newValue
	def setPreds_Scion_Side_Stars(self, newValue):self.preds_current_game_dict[self._preds_Scion_Side_Stars_attrib] = newValue
	def setPreds_Scion_Side_Confidence(self, newValue):self.preds_current_game_dict[self._preds_Scion_Side_Confidence_attrib] = newValue
	def setPreds_Comments(self, newValue):
		self.preds_current_game_dict[self._preds_Comments_attrib] = newValue
		self.setPreds_iPos_Comments(newValue)
	#iPOS
	def setPreds_iPos_GId(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_GId_attrib] = newValue
	def setPreds_iPos_V_Team_Sname(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_V_Team_Sname_attrib] = newValue
	def setPreds_iPos_H_Team_Sname(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_H_Team_Sname_attrib] = newValue
	def setPreds_iPos_V_Bookie_Price(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_V_Bookie_Bet_Price_attrib] = newValue
	def setPreds_iPos_H_Bookie_Price(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_H_Bookie_Bet_Price_attrib] = newValue
	def setPreds_iPos_Defense_HPrice(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_Defense_HPrice_attrib] = newValue
	def setPreds_iPos_Offense_HPrice(self, newValue):self.preds_ipos_current_game_dict[self._preds_iPos_Offense_HPrice_attrib] = newValue
	def setPreds_iPos_Ens1_HPrice(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_Ens1_HPrice_attrib] = newValue
	def setPreds_iPos_Ens2_HPrice(self, newValue):self.preds_ipos_current_game_dict[self._preds_iPos_Ens2_HPrice_attrib] = newValue
	def setPreds_iPos_Scion_Play(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_Scion_Play_attrib] = newValue
	def setPreds_iPos_Comments(self, newValue):self.preds_ipos_current_game_dict[self.preds_iPos_Comments_attrib] = newValue
	#Plays
	def setPreds_iPlay_GId(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_GId_attrib] = newValue
	def setPreds_iPlay_BookiePricePlay(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_BookiePricePlay_attrib] = newValue
	def setPreds_iPlay_V_Team_Sname(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_V_Team_Sname_attrib] = newValue
	def setPreds_iPlay_H_Team_Sname(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_H_Team_Sname_attrib] = newValue
	def setPreds_iPlay_Defense_HPrice(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_Defense_HPrice_attrib] = newValue
	def setPreds_iPlay_Offense_HPrice(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_Offense_HPrice_attrib] = newValue
	def setPreds_iPlay_Ens1_HPrice(self, newValue):self.preds_iplays_current_game_dict[self._preds_iPlay_Ens1_HPrice_attrib] = newValue
	def setPreds_iPlay_Ens2_HPrice(self, newValue):self.preds_iplays_current_game_dict[self._preds_iPlay_Ens2_HPrice_attrib] = newValue
	def setPreds_iPlay_Confidence(self, newValue):self.preds_iplays_current_game_dict[self.preds_iPlay_Confidence_attrib] = newValue
	def setPreds_ePlay_GId(self, newValue):self.preds_eplays_current_game_dict[self.preds_ePlay_GId_attrib] = newValue
	def setPreds_ePlay_Team_Sname(self, newValue):self.preds_eplays_current_game_dict[self.preds_ePlay_Team_Sname_attrib] = newValue
	def setPreds_ePlay_BookiePrice(self, newValue):self.preds_eplays_current_game_dict[self.preds_ePlay_BookiePrice_attrib] = newValue
	def setPreds_ePlay_Position(self, newValue):self.preds_eplays_current_game_dict[self.preds_ePlay_Position_attrib] = newValue
	# Getters
	def getPreds_Id(self): return self.preds_current_game_dict[self._preds_Id_attrib]
	def getPreds_date(self): return self.preds_current_game_dict[self._preds_date_attrib]
	def getPreds_monthweek(self): return self.preds_current_game_dict[self._preds_MonthWeekNum_attrib]
	def getPreds_opt(self): return self.preds_current_game_dict[self._preds_Bookie_Total_attrib]
	def getPreds_V_Id(self): return self.preds_current_game_dict[self._preds_V_Id_attrib]
	def getPreds_V_Sname(self): return self.preds_current_game_dict[self._preds_V_Sname_attrib]
	def getPreds_V_Bookie_Opening_Price(self): return self.preds_current_game_dict[self._preds_V_Bookie_Opening_Price_attrib]
	def getPreds_V_Bookie_Opening_Prob(self): return self.preds_current_game_dict[self._preds_V_Bookie_Opening_Prob_attrib]
	def getPreds_V_Bookie_Bet_Price(self): return self.preds_current_game_dict[self._preds_V_Bookie_Bet_Price_attrib]
	def getPreds_V_Bookie_Bet_Prob(self): return self.preds_current_game_dict[self._preds_V_Bookie_Bet_Prob_attrib]
	def getPreds_V_Bookie_Bet_DevigProb(self): return self.preds_current_game_dict[self._preds_V_Bookie_Bet_DevigProb_attrib]
	def getPreds_V_SP_Id(self): return self.preds_current_game_dict[self._preds_V_SP_Id_attrib]
	def getPreds_V_SP_Null(self): return self.preds_current_game_dict[self._preds_V_SP_Null_attrib]
	def getPreds_V_WinningForm_Price(self): return self.preds_current_game_dict[self._preds_V_WinningForm_Price_attrib]
	def getPreds_V_OffensePrice(self): return self.preds_current_game_dict[self._preds_V_Offense_Price_attrib]
	def getPreds_V_OffenseStrPrice(self): return self.preds_current_game_dict[self._preds_V_Offense_strPrice_attrib]
	def getPreds_V_Offense_StrengthCategory(self): return self.preds_current_game_dict[self._preds_V_Offense_StrengthCategory_attrib]
	def getPreds_V_DefensePrice(self): return self.preds_current_game_dict[self._preds_V_Defense_Price_attrib]
	def getPreds_V_DefenseStrPrice(self): return self.preds_current_game_dict[self._preds_V_Defense_strPrice_attrib]
	def getPreds_V_DefenseStrengthCategory(self): return self.preds_current_game_dict[self._preds_V_Defense_StrengthCategory_attrib]
	def getPreds_H_Id(self): return self.preds_current_game_dict[self._preds_H_Id_attrib]
	def getPreds_H_Sname(self): return self.preds_current_game_dict[self._preds_H_Sname_attrib]
	def getPreds_H_Bookie_Opening_Price(self): return self.preds_current_game_dict[self._preds_H_Bookie_Opening_Price_attrib]
	def getPreds_H_Bookie_Opening_Prob(self): return self.preds_current_game_dict[self._preds_H_Bookie_Opening_Prob_attrib]
	def getPreds_H_Bookie_Bet_Price(self): return self.preds_current_game_dict[self._preds_H_Bookie_Bet_Price_attrib]
	def getPreds_H_Bookie_Bet_Prob(self): return self.preds_current_game_dict[self._preds_H_Bookie_Bet_Prob_attrib]
	def getPreds_H_Bookie_Bet_DevigProb(self): return self.preds_current_game_dict[self._preds_H_Bookie_Bet_DevigProb_attrib]
	def getPreds_H_SP_Id(self): return self.preds_current_game_dict[self._preds_H_SP_Id_attrib]
	def getPreds_H_SP_Null(self): return self.preds_current_game_dict[self._preds_H_SP_Null_attrib]
	def getPreds_H_WinningForm_Price(self): return self.preds_current_game_dict[self._preds_H_WinningForm_Price_attrib]
	def getPreds_H_OffensePrice(self): return self.preds_current_game_dict[self._preds_H_Offense_Price_attrib]
	def getPreds_H_OffenseStrPrice(self): return self.preds_current_game_dict[self._preds_H_Offense_strPrice_attrib]
	def getPreds_H_Offense_StrengthCategory(self): return self.preds_current_game_dict[self._preds_H_Offense_StrengthCategory_attrib]
	def getPreds_H_DefensePrice(self): return self.preds_current_game_dict[self._preds_H_Defense_Price_attrib]
	def getPreds_H_DefenseStrPrice(self): return self.preds_current_game_dict[self._preds_H_Defense_strPrice_attrib]
	def getPreds_H_DefenseStrengthCategory(self): return self.preds_current_game_dict[self._preds_H_Defense_StrengthCategory_attrib]
	def getPreds_Ens1_VoterProfile(self): return self.preds_current_game_dict[self._preds_Ens1_VoterProfile_attrib]
	def getPreds_Ens1_MajorityVote(self): return self.preds_current_game_dict[self._preds_Ens1_MajorityVote_attrib]
	def getPreds_Ens1_NumVoters(self): return self.preds_current_game_dict[self._preds_Ens1_NumVoters_attrib]
	def getPreds_Ens1_VoteAgreement(self): return self.preds_current_game_dict[self._preds_Ens1_VoteAgreement_attrib]
	def getPreds_Ens1_HWinProb(self): return self.preds_current_game_dict[self._preds_Ens1_HProbability_attrib]
	def getPreds_Ens1_HProbabilityEdge(self): return self.preds_current_game_dict[self._preds_Ens1_HProbabilityEdge_attrib]
	def getPreds_Ens1_HWinPrice(self): return self.preds_current_game_dict[self._preds_Ens1_HPrice_attrib]
	def getPreds_Ens1_PlayPosition(self): return self.preds_current_game_dict[self._preds_Ens1_PlayPosition_attrib]
	def getPreds_Ens1_PlayStake(self): return self.preds_current_game_dict[self._preds_Ens1_PlayStake_attrib]
	def getPreds_Ens2_PlayPayoutMultiplier(self): return self.preds_current_game_dict[self._preds_Ens2_PlayPayoutMultiplier_attrib]
	def getPreds_Ens2_VoterProfile(self): return self.preds_current_game_dict[self._preds_Ens2_VoterProfile_attrib]
	def getPreds_Ens2_MajorityVote(self): return self.preds_current_game_dict[self._preds_Ens2_MajorityVote_attrib]
	def getPreds_Ens2_NumVoters(self): return self.preds_current_game_dict[self._preds_Ens2_NumVoters_attrib]
	def getPreds_Ens2_VoteAgreement(self): return self.preds_current_game_dict[self._preds_Ens2_VoteAgreement_attrib]
	def getPreds_Ens2_HWinProb(self): return self.preds_current_game_dict[self._preds_Ens2_HProbability_attrib]
	def getPreds_Ens2_HProbabilityEdge(self): return self.preds_current_game_dict[self._preds_Ens2_HProbabilityEdge_attrib]
	def getPreds_Ens2_HWinPrice(self): return self.preds_current_game_dict[self._preds_Ens2_HPrice_attrib]
	def getPreds_Ens2_PlayPosition(self): return self.preds_current_game_dict[self._preds_Ens2_PlayPosition_attrib]
	def getPreds_Ens2_PlayStake(self): return self.preds_current_game_dict[self._preds_Ens2_PlayStake_attrib]
	def getPreds_Ens2_PlayPayoutMultiplier(self): return self.preds_current_game_dict[self._preds_Ens2_PlayPayoutMultiplier_attrib]
	def getPreds_Scion_Side_Position(self): return self.preds_current_game_dict[self._preds_Scion_Side_Position_attrib]
	def getPreds_Scion_Side_Stars(self): return self.preds_current_game_dict[self._preds_Scion_Side_Stars_attrib]
	def getPreds_Scion_Side_Confidence(self): return self.preds_current_game_dict[self._preds_Scion_Side_Confidence_attrib]
	def getPreds_Comments(self): return self.preds_current_game_dict[self._preds_Comments_attrib]
	#iPOS
	def getPreds_iPos_GId(self): return self.preds_ipos_current_game_dict[self.preds_iPos_GId_attrib]
	def getPreds_iPos_V_Team_Sname(self): return self.preds_ipos_current_game_dict[self.preds_iPos_V_Team_Sname_attrib]
	def getPreds_iPos_H_Team_Sname(self): return self.preds_ipos_current_game_dict[self.preds_iPos_H_Team_Sname_attrib]
	def getPreds_iPos_V_Bookie_Price(self): return self.preds_ipos_current_game_dict[self.preds_iPos_V_Bookie_Bet_Price_attrib]
	def getPreds_iPos_H_Bookie_Price(self): return self.preds_ipos_current_game_dict[self.preds_iPos_H_Bookie_Bet_Price_attrib]
	def getPreds_iPos_Defense_HPrice(self): return self.preds_ipos_current_game_dict[self.preds_iPos_Defense_HPrice_attrib]
	def getPreds_iPos_Offense_HPrice(self): return self.preds_ipos_current_game_dict[self._preds_iPos_Offense_HPrice_attrib]
	def getPreds_iPos_Ens1_HPrice(self): return self.preds_ipos_current_game_dict[self.preds_iPos_Ens1_HPrice_attrib]
	def getPreds_iPos_Ens2_HPrice(self): return self.preds_ipos_current_game_dict[self._preds_iPos_Ens2_HPrice_attrib]
	def getPreds_iPos_Scion_Play(self): return self.preds_ipos_current_game_dict[self.preds_iPos_Scion_Play_attrib]
	def getPreds_iPos_Comments(self): return self.preds_ipos_current_game_dict[self._preds_iPos_Comments_attrib]
	#Plays
	def getPreds_iPlay_GId(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_GId_attrib]
	def getPreds_iPlay_V_Team_Sname(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_V_Team_Sname_attrib]
	def getPreds_iPlay_H_Team_Sname(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_H_Team_Sname_attrib]
	def getPreds_iPlay_BookiePricePlay(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_BookiePricePlay_attrib]
	def getPreds_iPlay_Defense_HPrice(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_Defense_HPrice_attrib]
	def getPreds_iPlay_Offense_HPrice(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_Offense_HPrice_attrib]
	def getPreds_iPlay_Ens1_HPrice(self):return self.preds_iplays_current_game_dict[self._preds_iPlay_Ens1_HPrice_attrib]
	def getPreds_iPlay_Ens2_HPrice(self):return self.preds_iplays_current_game_dict[self._preds_iPlay_Ens2_HPrice_attrib]
	def getPreds_iPlay_Confidence(self):return self.preds_iplays_current_game_dict[self.preds_iPlay_Confidence_attrib]
	def getPreds_ePlay_GId(self):return self.preds_eplays_current_game_dict[self.preds_ePlay_GId_attrib]
	def getPreds_ePlay_Team_Sname(self):return self.preds_eplays_current_game_dict[self.preds_ePlay_Team_Sname_attrib]
	def getPreds_ePlay_BookiePrice(self):return self.preds_eplays_current_game_dict[self.preds_ePlay_BookiePrice_attrib]
	def getPreds_ePlay_Position(self):return self.preds_eplays_current_game_dict[self.preds_ePlay_Position_attrib]

	def setOPLAdjustedFlag(self):
		self.preds_opladjusted = True
	def resetOPLAdjustedFlag(self):
		self.preds_opladjusted = False
	def getOPLAdjustedFlag(self):
		return self.preds_opladjusted
		
	def updateVerboseDataFrame(self):
		# Assumes preds_current_game_dict has been fully populated with data
		self.preds_verbose_df = pd.concat([self.preds_verbose_df, pd.DataFrame([self.preds_current_game_dict])])

	def updateiPosDataFrame(self):
		_noteStr = self.getPreds_iPos_Comments()
		if _noteStr == str(MLB_dbvar.NO_DATA):
			self.setPreds_iPos_Comments('')
		self.preds_ipos_df = pd.concat([self.preds_ipos_df, pd.DataFrame([self.preds_ipos_current_game_dict])])

	def _createSummaryDataFrame(self):
		self.preds_summary_df = self.preds_verbose_df.copy()
		self.preds_summary_df = self.preds_summary_df[[col for col in self.preds_summary_df.columns if col in self._preds_summary_cols]] 
		#ensure order of cola correct
		self.preds_summary_df = self.preds_summary_df.loc[:, self._preds_summary_cols]
	
	def _updatePlaysDataFrame(self):
		self.preds_iplays_df = pd.concat([self.preds_iplays_df, pd.DataFrame([self.preds_iplays_current_game_dict])])
		self.preds_eplays_df = pd.concat([self.preds_eplays_df, pd.DataFrame([self.preds_eplays_current_game_dict])])
	
	def storeVerbosePreds(self):
		try:
			#Attempt to store verbose preds to file
			#Set column specific precision:
			# https://stackoverflow.com/questions/20003290/output-different-precision-by-column-with-pandas-dataframe-to-csv
			self.preds_verbose_df[self._preds_MonthWeekNum_attrib] = self.preds_verbose_df[self._preds_MonthWeekNum_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Bookie_Total_attrib] = self.preds_verbose_df[self._preds_Bookie_Total_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_V_Bookie_Opening_Price_attrib] = self.preds_verbose_df[self._preds_V_Bookie_Opening_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_V_Bookie_Opening_Prob_attrib] = self.preds_verbose_df[self._preds_V_Bookie_Opening_Prob_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_V_WinningForm_Price_attrib] = self.preds_verbose_df[self._preds_V_WinningForm_Price_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_V_Offense_Price_attrib] = self.preds_verbose_df[self._preds_V_Offense_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_V_Defense_Price_attrib] = self.preds_verbose_df[self._preds_V_Defense_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_H_Bookie_Opening_Price_attrib] = self.preds_verbose_df[self._preds_H_Bookie_Opening_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_H_Bookie_Opening_Prob_attrib] = self.preds_verbose_df[self._preds_H_Bookie_Opening_Prob_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_H_WinningForm_Price_attrib] = self.preds_verbose_df[self._preds_H_WinningForm_Price_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_H_Offense_Price_attrib] = self.preds_verbose_df[self._preds_H_Offense_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_H_Defense_Price_attrib] = self.preds_verbose_df[self._preds_H_Defense_Price_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens1_HProbability_attrib] = self.preds_verbose_df[self._preds_Ens1_HProbability_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens1_HProbabilityEdge_attrib] = self.preds_verbose_df[self._preds_Ens1_HProbabilityEdge_attrib].map(lambda x: '{:.5f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens1_HPrice_attrib] = self.preds_verbose_df[self._preds_Ens1_HPrice_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens1_VoteAgreement_attrib] = self.preds_verbose_df[self._preds_Ens1_VoteAgreement_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens2_HProbability_attrib] = self.preds_verbose_df[self._preds_Ens2_HProbability_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens2_HProbabilityEdge_attrib] = self.preds_verbose_df[self._preds_Ens2_HProbabilityEdge_attrib].map(lambda x: '{:.5f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens2_HPrice_attrib] = self.preds_verbose_df[self._preds_Ens2_HPrice_attrib].map(lambda x: '{:.1f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Ens2_VoteAgreement_attrib] = self.preds_verbose_df[self._preds_Ens2_VoteAgreement_attrib].map(lambda x: '{:.2f}'.format(float(x)))
			self.preds_verbose_df[self._preds_Scion_Side_Confidence_attrib] = self.preds_verbose_df[self._preds_Scion_Side_Confidence_attrib].map(lambda x: '{:.3f}'.format(float(x)))
			#Store to CSV
			self._storePredsCSV(self.preds_verbose_df,self._preds_verbose_csv_fname,self._preds_verbose_cols)
		except:
			print("\nscionPREDS.storeVerbosePreds(): Fatal error writing prediction data to " + self._preds_verbose_csv_fname)
			raise

	def storeSummaryPreds(self):
		try:
			#1. create summary dataframe
			self._createSummaryDataFrame()
			#2. store its data to file
			self._storePredsCSV(self.preds_summary_df,self._preds_summary_csv_fname,self._preds_summary_cols)
			#3. store summary file in cwd
			self._storePredsCSV(self.preds_summary_df,self._preds_summary_cwd_csv_fname,self._preds_summary_cols)
		except:
			print("\nscionPREDS.storeSummaryPreds(): Fatal error writing prediction data to " + self._preds_summary_csv_fname)
			raise

	def _storeAsMarkdownTxt(self, _preds_df, colList, _predsFname):
		try:
			_preds_df = _preds_df[colList]
			with open(_predsFname, 'w') as predsFile:
				predsFile.write(_preds_df.to_markdown() + "\n")
			predsFile.close()
		except:
			print("\nscionPREDS._storeAsMarkdownTxt(): Fatal error writing plays data to " + _predsFname)
			raise

	def setPlayPredsIndices(self):
		#Set index so start from 1
		self.preds_eplays_df = self.preds_eplays_df.reset_index()
		self.preds_eplays_df.index = self.preds_eplays_df.index + 1
		self.preds_iplays_df = self.preds_iplays_df.reset_index()
		self.preds_iplays_df.index = self.preds_iplays_df.index + 1
		self.preds_ipos_df = self.preds_ipos_df.reset_index()
		self.preds_ipos_df.index = self.preds_ipos_df.index + 1
			
	def storePredsAsMarkdown(self):
		try:
			#set self.preds_iposml_df to be selected subset of ipos
			#self.preds_iposml_df = self.preds_ipos_df.copy()
			#self.preds_iposml_df = self.preds_iposml_df.drop(columns=[col for col in self.preds_iposml_df if col not in self._preds_iposml_cols], inplace=False)
			#self.preds_iposml_df = self.preds_iposml_df.reindex(columns=self._preds_iposml_cols)
			# preds_iposml_txt_fname
			#Store to preds folder
			self._storeAsMarkdownTxt(self.preds_eplays_df, self._preds_eplay_cols, self._preds_eplays_txt_fname)
			self._storeAsMarkdownTxt(self.preds_iplays_df, self._preds_iplay_cols, self._preds_iplays_txt_fname)
			self._storeAsMarkdownTxt(self.preds_ipos_df, self._preds_ipos_cols, self._preds_ipos_txt_fname)
			#self._storeAsMarkdownTxt(self.preds_iposml_df, self._preds_iposml_cols, self._preds_iposml_txt_fname)
			#Store to cwd
			self._storeAsMarkdownTxt(self.preds_eplays_df, self._preds_eplay_cols, self._preds_eplays_cwd_txt_fname)
			self._storeAsMarkdownTxt(self.preds_iplays_df, self._preds_iplay_cols, self._preds_iplays_cwd_txt_fname)
			self._storeAsMarkdownTxt(self.preds_ipos_df, self._preds_ipos_cols, self._preds_ipos_cwd_txt_fname)
			#self._storeAsMarkdownTxt(self.preds_iposml_df, self._preds_iposml_cols, self._preds_iposml_cwd_txt_fname)
			#Store to Desktop
			#self._storeAsMarkdownTxt(self.preds_eplays_df, self._preds_eplay_cols, self._preds_eplays_desktop_txt_fname)
			#self._storeAsMarkdownTxt(self.preds_iplays_df, self._preds_iplay_cols, self._preds_iplays_desktop_txt_fname)

		except:
			print("\nscionPREDS.storePredsAsMarkdown(): Fatal error writing preds to markdown text files!")
			raise

	def displayPreds(self):
		print("\n")
		#print(self.preds_playonly_df.to_string(index=False))
		#self.preds_iplays_df = self.preds_iplays_df[self._preds_iplay_cols]
		self.preds_ipos_df = self.preds_ipos_df[self._preds_ipos_cols] #get rid of index col
		print(self.preds_ipos_df.to_markdown(tablefmt="grid"))
  
	def displayExitMessage(self):
		print ("\nFor details, please review the following files:")
		print("Summary results can be found in the file " + self._preds_summary_csv_fname)
		print("Verbose results can be found in the file " + self._preds_verbose_csv_fname)
		print("Tracking report can be found in the file " + self._preds_ipos_cwd_txt_fname)
		print("Plays for EXTERNAL bettors can be found in the file " + self._preds_eplays_cwd_txt_fname)
		print("Plays for INTERNAL bettors can be found in the file " + self._preds_iplays_cwd_txt_fname + "\n")

	def getBookieOpeningPrice(self, _sidePos):
		# get remaining info for side play based on Scion side position and the bookie's position
		try:
			if _sidePos == MLB_global.ACTION_LINE_HF or _sidePos == MLB_global.ACTION_LINE_HD:
				return self.getPreds_H_Bookie_Opening_Price()
			else:
				return self.getPreds_V_Bookie_Opening_Price()
		except Exception:
			print("\nscionPREDS.getBookieOpeningPrice(): Unexpected error encountered when getting bookie opening price for Scion play!")
			raise

	def getBookiePrice(self, _sidePos):
		# get remaining info for side play based on Scion side position and the bookie's position
		try:
			if _sidePos == MLB_global.ACTION_LINE_HF or _sidePos == MLB_global.ACTION_LINE_HD:
				return self.getPreds_H_Bookie_Bet_Price()
			else:
				return self.getPreds_V_Bookie_Bet_Price()
		except Exception:
			print("\nscionPREDS.getBookiePrice(): Unexpected error encountered when getting bookie betprice for Scion play!")
			raise

	def getTeamNamePlay(self, _sidePos):
		# get remaining info for side play based on Scion side position and the bookie's position
		try:
			if _sidePos == MLB_global.ACTION_LINE_HF or _sidePos == MLB_global.ACTION_LINE_HD:
				return self.getPreds_H_Sname()
			else:
				return self.getPreds_V_Sname()
		except Exception:
			print("\nscionPREDS.getTeamNamePlay(): Unexpected error encountered when returning name of the team Scion is playing on!")
			raise

	def getBookiePricePlay(self, _sidePos):
		try:
			if _sidePos == MLB_global.ACTION_LINE_HF or _sidePos == MLB_global.ACTION_LINE_HD:
				_bookiePricePlay = f"{self.getPreds_H_Bookie_Bet_Price():.1f}"
			else:
				_bookiePricePlay = f"{self.getPreds_V_Bookie_Bet_Price():.1f}"
			_bookiePricePlay += (" " + _sidePos)
			#check whether we need to annotate it with 1, 3 or 5 stars
			_numStars = self.getPreds_Scion_Side_Stars()
			if _numStars:
				_starStr = MLB_global.genStarStr(_numStars)
				_bookiePricePlay = _starStr + " " + _bookiePricePlay + " " + _starStr

		except Exception:
			print("\nscionPREDS.getBookiePricePlay(): Unexpected error encountered when combining bookie price and Scion play position!")
			raise

		return _bookiePricePlay
	
	def getPlayTeamData(self, h_or_v):
		# get remaining info for side play based on Scion side position and the bookie's position
		try:
			_tSname = _strCat = _tOffPrice = _tDefPrice = ""
			_tElite = False
			if h_or_v == MLB_global.HOME:
				#a. get team name
				_tSname = self.getPreds_H_Sname()
				#b. get H_SP_BoBSORatio price and indicate whether or not elite
				_tDefPrice = f"{round(self.getPreds_H_DefensePrice()):.0f}"
				_strCat = self.getPreds_H_DefenseStrengthCategory()
				_tElite = MLB_global.isElite(_strCat)
				if _tElite:
					_tDefPrice += (" " + MLB_global.TEXT_HIGHLIGHT_DELIMITER2)
				#c. get mob price, category and indicate whether or not elite
				_tOffPrice = f"{round(self.getPreds_H_OffensePrice()):.0f}"
				_strCat = self.getPreds_H_Offense_StrengthCategory()
				_tElite = MLB_global.isElite(_strCat)
				if _tElite:
					_tOffPrice += (" " + MLB_global.TEXT_HIGHLIGHT_DELIMITER2)
			else:
				#a. get team name
				_tSname = self.getPreds_V_Sname()
				#b. get V_SP_BoBSORatio price and indicate whether or not elite
				_tDefPrice = f"{round(self.getPreds_V_DefensePrice()):.0f}"
				_strCat = self.getPreds_V_DefenseStrengthCategory()
				_tElite = MLB_global.isElite(_strCat)
				if _tElite:
					_tDefPrice += (" " + MLB_global.TEXT_HIGHLIGHT_DELIMITER2)
				#c. get mob price, category and indicate whether or not elite
				_tOffPrice = f"{round(self.getPreds_V_OffensePrice()):.0f}"
				_strCat = self.getPreds_V_Offense_StrengthCategory()
				_tElite = MLB_global.isElite(_strCat)
				if _tElite:
					_tOffPrice += (" " + MLB_global.TEXT_HIGHLIGHT_DELIMITER2)
				
		except Exception:
			print("\nscionPREDS.getPlayTeamData(): Unexpected error encountered when getting information for " + _tSname)
			raise

		return _tSname, _tDefPrice, _tOffPrice

	def updateiPosNoPlayPrices(self):
		#Purpose: update iPos prices (offense, defense and ensemble) when there is no play
		#Assumption 1: self.preds_current_game_dict is FULLY populated with valid data
		#Assumption 2: the play position has been calculated and it is No Play
		#Assumption 3: iPos primitives and Comments have already been populated
		try:
			#1. Initi variables
			_sidePos = self.getPreds_Scion_Side_Position()
			#2. Check if we have a play to store (only Side plays are active in this version)
			if _sidePos != MLB_global.ACTION_NOPLAY:
				return
			#3. Store No Play prices
			_tDefPrice = f"{round(self.getPreds_H_DefensePrice()):.0f}"
			_tOffPrice = f"{round(self.getPreds_H_OffensePrice()):.0f}"
			_ens1Price = round(self.getPreds_Ens1_HWinPrice())
			self.setPreds_iPos_Scion_Play(MLB_global.ACTION_NOPLAY) #just to be sure its there!
			self.setPreds_iPos_Defense_HPrice(_tDefPrice)
			self.setPreds_iPos_Offense_HPrice(_tOffPrice)
			self.setPreds_iPos_Ens1_HPrice(_ens1Price)
		except Exception:
			print("\nscionPREDS.updateiPosNoPlayPrices(): Unexpected error encountered when updating the iPos dictionary.")
			raise

	def getPreds_OffDef_HPrice(self):
		#Purpose: gets off and def h prices, converts to probabilities, averages them and converts back to prices
		#Assumption 1: self.preds_current_game_dict is FULLY populated with valid data
		try:
			#1. Initialise variables
			_tDefPrice = self.getPreds_H_DefensePrice()
			_tOffPrice = self.getPreds_H_OffensePrice()
			#2. Convert to probabilities
			_tDefProb = MLB_global.convertMoneyLinetoProb(_tDefPrice)
			_tOffProb = MLB_global.convertMoneyLinetoProb(_tOffPrice)
			#3. Calc average probability
			_tOffDefProb = (_tDefProb + _tOffProb) / 2
			#4, Convert probability to price
			_tOffDefPrice = MLB_global.convertProbtoMoneyLine(_tOffDefProb)
			
		except Exception:
			print("\nscionPREDS.getPreds_OffDef_HPrice(): Unexpected error encountered when calculating the offdef home price.")
			raise

		return _tOffDefPrice

	def updatePredPlayDict(self, sysCfgObj, _mupComments=False):
		#Purpose: records a play in the PlayDict if either or both a win prediction and totals prediction is available (otherwise the dictionaries are initialised)
		#Assumption 1: self.preds_current_game_dict is FULLY populated with valid data
		#Assumption 2: sysCfgObj provides access to max threshold
		#Assumption 3: Only G2 FaveWin prob prediction supported
		#Assumption 4: Off, Def and OffDef prices MUST be Home team prices!
		#Assumption 5: totals are not implemented
		try:
			#1. Initi variables
			_storePlay = True
			if _mupComments and str(MLB_dbvar.NO_DATA) not in _mupComments: 
				_playComments = _mupComments 
			else: 
				_playComments = ""
			_playSide = True
			_sidePos = self.getPreds_Scion_Side_Position()
			_sideConf = self.getPreds_Scion_Side_Confidence()
			_homeOffDefPrice = self.getPreds_OffDef_HPrice()

			#2. Check if we have a play to store (only Side plays are active in this version)
			if _sidePos == MLB_global.ACTION_NOPLAY or _sidePos == MLB_global.ACTION_NOPLAYPUSH or _sidePos == MLB_global.ACTION_NOPLAYGAP:
				_playSide = False
				_storePlay = False

			#3. If we have a side and/or total play, let's store it
			if _storePlay:
				self.setPreds_iPlay_GId(self.getPreds_Id())
				_ePlays_GId = self._createPredId(False)
				self.setPreds_ePlay_GId(_ePlays_GId)
				#2.1 Add comments from MUPS if any (as we might update them further down)
				self.addComment(_playComments, True, True)
				#2.2 Store side play data
				if _playSide:
					#store off, def and scion positions and confidence
					_pricePlay = self.getBookiePricePlay(_sidePos)
					self.setPreds_iPlay_BookiePricePlay(_pricePlay)
					self.setPreds_iPos_Scion_Play(_pricePlay)
					self.setPreds_iPlay_Ens1_HPrice(round(self.getPreds_Ens1_HWinPrice()))
					self.setPreds_iPos_Ens1_HPrice(round(self.getPreds_Ens1_HWinPrice()))
					self.setPreds_iPlay_Confidence(_sideConf)
					#store KEY home team prices (incl off, def, offdef)
					_tSname, _tDefPrice, _tOffPrice = self.getPlayTeamData(MLB_global.HOME)
					self.setPreds_iPlay_H_Team_Sname(_tSname)
					self.setPreds_iPlay_Defense_HPrice(_tDefPrice)
					self.setPreds_iPlay_Offense_HPrice(_tOffPrice)
					self.setPreds_iPos_Defense_HPrice(_tDefPrice)
					self.setPreds_iPos_Offense_HPrice(_tOffPrice)
					#get Vis play data
					_tSname, _tDefPrice, _tOffPrice = self.getPlayTeamData(MLB_global.VISITOR)
					self.setPreds_iPlay_V_Team_Sname(_tSname)
					#Store ePlay info
					self.setPreds_ePlay_Team_Sname(self.getTeamNamePlay(_sidePos))
					self.setPreds_ePlay_BookiePrice(self.getBookiePrice(_sidePos))
					self.setPreds_ePlay_Position(_sidePos)
				#2.3. Update df and initialise dict for next game
				self._updatePlaysDataFrame() 
				self.initPredsPlayDict()

		except Exception:
			print("\nscionPREDS.updatePredPlayDict(): Unexpected error encountered when updating the Play dictionary.")
			raise

	def applyMajorityVote(self, ens, sysCfgObj):
    # This function applies the majorityVote func to all ens for the relevant task and updates the relevant class fields
	# Assumption: 1. predsObj contains HLine, VLine (incl deVigged probabilities) and the relevant ensemble probabilities for the current game
	#			  2. cfgObj contains target (eg B1 HomeWin, G2 FaveWin)
		try:
			#update voter profiles in pred file
			self._updateCurrentGameVoterProfiles(ens)
			numVoters = 0
			numNoPlays = 0
			majorityVote = ""
			majorityWgt = 0.0
			avgProb = avgHomProb = 0.0
			ensProbType = int(sysCfgObj.getSysProbEnsProbType())
			target = sysCfgObj.getCurrentModelTarget()
			vPrice = self.getPreds_V_Bookie_Bet_Price()
			hPrice = self.getPreds_H_Bookie_Bet_Price()
			hProb = self.getPreds_H_Bookie_Bet_Prob()
			vProb = self.getPreds_V_Bookie_Bet_Prob()	
			hDevigProb = MLB_global.calcDeVigProb(hProb, vProb, h_or_v=MLB_global.HOME)
			if ens not in MLB_global.MODEL_PROBENS:
				print("\nUnrecognised ensemble " + str(ens) + "! Please review Scion configuration files to ensure only active ensembles are used.")
				raise Exception
			else:
				numVoters, majorityVote, majorityWgt, avgProb, numNoPlays  = self._getProbabilityMajorityVote(ens,ensProbType)
				if target == "B1": #HWin
					avgHomProb = avgProb
				elif  target == "B2": #VWin
					avgHomProb = 1 - avgProb
				else:#Must be G2 Fave Win
					if hPrice <= vPrice: #HF
						avgHomProb = avgProb
					else:
						avgHomProb = 1 - avgProb

				if ens == MLB_global.MODEL_PROBENS1: 
					self.setPreds_Ens1_HWinProb(avgHomProb)
					self.setPreds_Ens1_HProbabilityEdge(round(float(avgHomProb - hDevigProb),5))
					self.setPreds_Ens1_HWinPrice(MLB_global.convertProbtoMoneyLine(avgHomProb))
					self.setPreds_Ens1_MajorityVote(majorityVote)
					self.setPreds_Ens1_PlayPosition(majorityVote) #This might change to No Play if CLL thresholds are not met
					self.setPreds_Ens1_NumVoters(numVoters)
					self.setPreds_Ens1_VoteAgreement(round(float(majorityWgt/numVoters),2))
				elif ens == MLB_global.MODEL_PROBENS2: 
					self.setPreds_Ens2_HWinProb(avgHomProb)
					self.setPreds_Ens2_HProbabilityEdge(round(float(avgHomProb - hDevigProb),5))
					self.setPreds_Ens2_HWinPrice(MLB_global.convertProbtoMoneyLine(avgHomProb))
					self.setPreds_Ens2_MajorityVote(majorityVote)
					self.setPreds_Ens2_PlayPosition(majorityVote) #This might change to No Play if CLL thresholds are not met
					self.setPreds_Ens2_NumVoters(numVoters)
					self.setPreds_Ens2_VoteAgreement(round(float(majorityWgt/numVoters),2))
				else: #unknown
					print("Unknown ensemble!")
					raise
		except Exception:
			print("\nscionPREDS.applyMajorityVote(): error when determining majority vote amongst the " + str(ens) + " voters")
			raise

	def updateVoterDict(self, ens, modelCode, predValue, predPosition):
    #Assumption 1: probabilities and thus prices MUST be with respect to the home team (as the bookieline we evaluate is w.r.t home team)
	#Structure {"M22":[0.68324, "HF"], "M23":[0.4899964, "VD"]}

		try:
			#1. create dict item
			dictKey = modelCode
			dictItem = [predValue, predPosition]
			#2. update relevant dict
			if ens not in MLB_global.MODEL_PROBENS:
				print("\nUnrecognised ensemble " + str(ens) + "! Please review Scion configuration files to ensure only active ensembles are used.")
				raise Exception
			else:
				if ens == MLB_global.MODEL_PROBENS1:
					self.preds_ens1_vote_dict[dictKey] = copy.deepcopy(dictItem)
				elif ens == MLB_global.MODEL_PROBENS2:
					self.preds_ens2_vote_dict[dictKey] = copy.deepcopy(dictItem)
				else:
					print("Unknown ensemble!")
					raise Exception
		except Exception:
			print("\nscionPREDS.updateVoterDict(): error updating the dict for the following ensemble: " + str(ens))
			raise

	#getters for pred df col names for pred file
	@property
	def preds_verbose_csv_fname(self):return self._preds_verbose_csv_fname
	@property
	def preds_summary_csv_fname(self):return self._preds_summary_csv_fname
	@property
	def preds_eplays_txt_fname(self):return self._preds_eplays_txt_fname
	@property
	def preds_iplays_txt_fname(self):return self._preds_iplays_txt_fname
	@property
	def preds_iplays_cwd_txt_fname(self):return self._preds_iplays_cwd_txt_fname
	@property
	def preds_eplays_cwd_txt_fname(self):return self._preds_eplays_cwd_txt_fname
	@property
	def preds_iplays_desktop_txt_fname(self):return self._preds_iplays_desktop_txt_fname
	@property
	def preds_eplays_desktop_txt_fname(self):return self._preds_eplays_desktop_txt_fname
	@property
	def preds_Id_attrib(self): return self._preds_Id_attrib
	@property
	def preds_date_attrib(self): return self._preds_date_attrib
	@property
	def preds_Bookie_Total_attrib(self): return self._preds_Bookie_Total_attrib
	@property
	def preds_V_Id_attrib(self): return self._preds_V_Id_attrib
	@property
	def preds_V_Sname_attrib(self): return self._preds_V_Sname_attrib
	@property
	def preds_V_Bookie_Opening_Price_attrib(self): return self._preds_V_Bookie_Opening_Price_attrib
	@property
	def preds_V_Bookie_Opening_Prob_attrib(self): return self._preds_V_Bookie_Opening_Prob_attrib
	@property
	def preds_V_SP_Id_attrib(self): return self._preds_V_SP_Id_attrib
	@property
	def preds_V_SP_Null_attrib(self): return self._preds_V_SP_Null_attrib
	@property
	def preds_V_WinningForm_Price_attrib(self): return self._preds_V_WinningForm_Price_attrib
	@property
	def preds_V_Offense_Price_attrib(self): return self._preds_V_Offense_Price_attrib
	@property
	def preds_V_Offense_strPrice_attrib(self): return self._preds_V_Offense_strPrice_attrib
	@property
	def preds_V_Offense_StrengthCategory_attrib(self): return self._preds_V_Offense_StrengthCategory_attrib
	@property
	def preds_H_Id_attrib(self): return self._preds_H_Id_attrib
	@property
	def preds_H_Sname_attrib(self): return self._preds_H_Sname_attrib
	@property
	def preds_H_Bookie_Opening_Price_attrib(self): return self._preds_H_Bookie_Opening_Price_attrib
	@property
	def preds_H_Bookie_Opening_Prob_attrib(self): return self._preds_H_Bookie_Opening_Prob_attrib
	@property
	def preds_H_SP_Id_attrib(self): return self._preds_H_SP_Id_attrib
	@property
	def preds_H_SP_Null_attrib(self): return self._preds_H_SP_Null_attrib
	@property
	def preds_H_WinningForm_Price_attrib(self): return self._preds_H_WinningForm_Price_attrib
	@property
	def preds_H_Offense_Price_attrib(self): return self._preds_H_Offense_Price_attrib
	@property
	def preds_H_Offense_strPrice_attrib(self): return self._preds_H_Offense_strPrice_attrib
	@property
	def preds_H_Offense_StrengthCategory_attrib(self): return self._preds_H_Offense_StrengthCategory_attrib
	@property
	def preds_Ens1_VoterProfile_attrib(self): return self._preds_Ens1_VoterProfile_attrib
	@property
	def preds_Ens1_MajorityVote_attrib(self): return self._preds_Ens1_MajorityVote_attrib
	@property
	def preds_Ens1_NumVoters_attrib(self): return self._preds_Ens1_NumVoters_attrib
	@property
	def preds_Ens1_VoteAgreement_attrib(self): return self._preds_Ens1_VoteAgreement_attrib
	@property
	def preds_Ens1_PlayPosition_attrib(self): return self._preds_Ens1_PlayPosition_attrib
	@property
	def preds_Ens1_PlayStake_attrib(self): return self._preds_Ens1_PlayStake_attrib
	@property
	def preds_Ens1_PlayPayoutMultiplier_attrib(self): return self._preds_Ens1_PlayPayoutMultiplier_attrib
	@property
	def preds_Ens1_HProbability_attrib(self): return self._preds_Ens1_HProbability_attrib
	@property
	def preds_Ens1_HProbabilityEdge_attrib(self): return self._preds_Ens1_HProbabilityEdge_attrib
	@property
	def preds_Ens1_HPrice_attrib(self): return self._preds_Ens1_HPrice_attrib
	@property
	def preds_Ens2_VoterProfile_attrib(self): return self._preds_Ens2_VoterProfile_attrib
	@property
	def preds_Ens2_MajorityVote_attrib(self): return self._preds_Ens2_MajorityVote_attrib
	@property
	def preds_Ens2_NumVoters_attrib(self): return self._preds_Ens2_NumVoters_attrib
	@property
	def preds_Ens2_VoteAgreement_attrib(self): return self._preds_Ens2_VoteAgreement_attrib
	@property
	def preds_Ens2_PlayPosition_attrib(self): return self._preds_Ens2_PlayPosition_attrib
	@property
	def preds_Ens2_PlayStake_attrib(self): return self._preds_Ens2_PlayStake_attrib
	@property
	def preds_Ens2_PlayPayoutMultiplier_attrib(self): return self._preds_Ens2_PlayPayoutMultiplier_attrib
	@property
	def preds_Ens2_HProbability_attrib(self): return self._preds_Ens2_HProbability_attrib
	@property
	def preds_Ens2_HProbabilityEdge_attrib(self): return self._preds_Ens2_HProbabilityEdge_attrib
	@property
	def preds_Ens2_HPrice_attrib(self): return self._preds_Ens2_HPrice_attrib
	@property
	def preds_Scion_Side_Position_attrib(self): return self._preds_Scion_Side_Position_attrib
	@property
	def preds_Scion_Side_Stars_attrib(self): return self._preds_Scion_Side_Stars_attrib
	@property
	def preds_Scion_Side_Confidence_attrib(self): return self._preds_Scion_Side_Confidence_attrib
	@property
	def preds_Comments_attrib(self): return self._preds_Comments_attrib
	@property
	def preds_iPos_GId_attrib(self):return self._preds_iPos_GId_attrib
	@property	
	def preds_iPos_V_Team_Sname_attrib(self):return self._preds_iPos_V_Team_Sname_attrib
	@property	
	def preds_iPos_H_Team_Sname_attrib(self):return self._preds_iPos_H_Team_Sname_attrib
	@property		
	def preds_iPos_V_Bookie_Bet_Price_attrib(self):return self._preds_iPos_V_Bookie_Bet_Price_attrib
	@property		
	def preds_iPos_H_Bookie_Bet_Price_attrib(self):return self._preds_iPos_H_Bookie_Bet_Price_attrib
	@property		
	def preds_iPos_Defense_HPrice_attrib(self):return self._preds_iPos_Defense_HPrice_attrib
	@property		
	def preds_iPos_Offense_HPrice_attrib(self):return self._preds_iPos_Offense_HPrice_attrib
	@property		
	def preds_iPos_Ens1_HPrice_attrib(self):return self._preds_iPos_Ens1_HPrice_attrib
	@property		
	def preds_iPos_Scion_Play_attrib(self):return self._preds_iPos_Scion_Play_attrib
	@property		
	def preds_iPos_Comments_attrib(self):return self._preds_iPos_Comments_attrib
	@property
	def preds_iPlay_GId_attrib(self):return self._preds_iPlay_GId_attrib
	@property	
	def preds_iPlay_V_Team_Sname_attrib(self):return self._preds_iPlay_V_Team_Sname_attrib
	@property	
	def preds_iPlay_H_Team_Sname_attrib(self):return self._preds_iPlay_H_Team_Sname_attrib
	@property		
	def preds_iPlay_BookiePricePlay_attrib(self):return self._preds_iPlay_BookiePricePlay_attrib
	@property		
	def preds_iPlay_Defense_HPrice_attrib(self):return self._preds_iPlay_Defense_HPrice_attrib
	@property		
	def preds_iPlay_Offense_HPrice_attrib(self):return self._preds_iPlay_Offense_HPrice_attrib
	@property		
	def preds_iPlay_Ens1_HPrice_attrib(self):return self._preds_iPlay_Ens1_HPrice_attrib
	@property		
	def preds_iPlay_Confidence_attrib(self):return self._preds_iPlay_Confidence_attrib
	@property		
	def preds_ePlay_GId_attrib(self):return self._preds_ePlay_GId_attrib
	@property		
	def preds_ePlay_Team_Sname_attrib(self):return self._preds_ePlay_Team_Sname_attrib
	@property		
	def preds_ePlay_BookiePrice_attrib(self):return self._preds_ePlay_BookiePrice_attrib
	@property		
	def preds_ePlay_Position_attrib(self):return self._preds_ePlay_Position_attrib
	"""
	Pythonic way for using getters/setters (FOR LATER)
	class C(object):
		def __init__(self):
			self._x = None

		@property
		def x(self):
			#I'm the 'x' property.
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
		
	"""