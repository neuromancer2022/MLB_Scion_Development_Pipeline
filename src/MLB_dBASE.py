#import path
import sys, traceback # only needed to determine Python version number
from sys import stdout
import os
import numpy as np
import pandas as pd
import math
from datetime import datetime, date, time, timedelta
from collections import OrderedDict
import argparse
import functools 

import MLB_dbvar as MLB_dbvar
import MLB_dumpvar as MLB_dumpvar
import MLB_globals as MLB_global

# Define key global vars
APP_VER = "V25.05 (Standard Edition)"
APP_NAME = "MLB dBase Update Tool" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2025" 
cwd = os.getcwd()
            
GAME_ID_INDEX = 0  # relates to index of value in main dictionary
H_OR_V_INDEX = 1  # relates to index of value in main dictionary
HOME = 0
VISITOR = 1
teamnumlist = range(MLB_dbvar.NUM_TEAMS)  # create list of team ids i.e 0 to 29

SLEEPLEN = 3
RESULT_FNAME_EXT = ".csv"
VAR_WORD_SEP = "_"

print("\n"+ APP_BANNER + "\n" + APP_OWNER + "\n")

def _errorReport():
    print("Review the error report below and resolve any issues.\n")
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

def updateDateAttribs(game_df):
#ASSUMPTION: date value is stored
#https://stackoverflow.com/questions/49204453/how-can-i-get-year-month-day-from-a-numpy-datetime64 
    #Get date (which must originally have been a string) and convert to dt
    gameDate = str(game_df[MLB_dbvar.dbvar_G_Date].values[0])
    date_obj = datetime.strptime(game_df[MLB_dbvar.dbvar_G_Date].values[0], MLB_dumpvar.dump_date_Format)
    date_obj_dt = date_obj.date()
    #date_obj = datetime.strptime(gameDate, NFL_dbvar.dbvar_Date_Format)
    #date_obj = date_obj.date()
    #G_Year
    fieldName=MLB_dbvar.dbvar_G_Year
    fieldValue=int(date_obj_dt.year)
    game_df[fieldName].values[0] = fieldValue
    #G_Month
    fieldName=MLB_dbvar.dbvar_G_Month
    fieldValue=int(date_obj_dt.month)
    _month = game_df[fieldName].values[0] = fieldValue
    #G_Day
    fieldName=MLB_dbvar.dbvar_G_Day
    fieldValue=int(date_obj_dt.day)
    _day = game_df[fieldName].values[0] = fieldValue
    #G_MonthWeek (synthetic float Month.WeekNum eg 2nd week of Dec = 12.2)
    fieldName=MLB_dbvar.dbvar_G_MonthWeek
    fieldValue = float(MLB_dbvar.createMonthWeek(_month,_day))
    game_df[fieldName].values[0] = fieldValue
    return game_df

def updatePrimitiveFeatures(game_df, dump_df, dump_row_index):
    #Primitives are taken directly from dumpvar
    ################## GAME INFO ################################
     # G_Id
    fieldName=MLB_dbvar.dbvar_G_Id
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_game_id].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)  #
    # G_Date
    fieldName=MLB_dbvar.dbvar_G_Date
    fieldValue=dump_df[MLB_dumpvar.dumpvar_date].iloc[dump_row_index]
    game_df[fieldName].values[0] = fieldValue
    # G_Opening_MiddleMoneyLine
    fieldName=MLB_dbvar.dbvar_G_Opening_MiddleMoneyLine
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_opening_mline].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_OpeningLine_Vig
    fieldName=MLB_dbvar.dbvar_G_OpeningLine_Vig
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_ovig].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Closing_MiddleMoneyLine
    fieldName=MLB_dbvar.dbvar_G_Closing_MiddleMoneyLine
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_closing_mline].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_ClosingLine_Vig
    fieldName=MLB_dbvar.dbvar_G_ClosingLine_Vig
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_cvig].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Middle_MoneyLine (appears to be a duplicate of G_Opening_MiddleMoneyLine as opening_mline = middle_mline)
    fieldName=MLB_dbvar.dbvar_G_Middle_MoneyLine
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_middle_mline].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Opening_Total
    fieldName=MLB_dbvar.dbvar_G_Opening_Total
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_opening_total_spread].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Opening_TotalLine
    fieldName=MLB_dbvar.dbvar_G_Opening_TotalLine
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_opening_total_line].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Closing_Total
    fieldName=MLB_dbvar.dbvar_G_Closing_Total
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_closing_total_spread].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Closing_TotalLine
    fieldName=MLB_dbvar.dbvar_G_Closing_TotalLine
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_closing_total_line].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_NightGame
    fieldName=MLB_dbvar.dbvar_G_NightGame
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_nightgame].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    ################## HOME ################################
    # G_H_Id 
    fieldName=MLB_dbvar.dbvar_G_H_Id
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_hom_id].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)  #
    # G_H_League
    fieldName=MLB_dbvar.dbvar_G_H_League
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_home_league].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)  #
    # H_Innings
    fieldName=MLB_dbvar.dbvar_H_Innings
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_home_inn].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # H_Runs_Gained
    fieldName=MLB_dbvar.dbvar_H_Runs_Gained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Runs_Allowed
    fieldName=MLB_dbvar.dbvar_H_Runs_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Runs_5InningsGained
    fieldName=MLB_dbvar.dbvar_H_Runs_5InningsGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Runs_5InningsAllowed
    fieldName=MLB_dbvar.dbvar_H_Runs_5InningsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_OutsPitched
    fieldName=MLB_dbvar.dbvar_H_OutsPitched
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_number_of_outs_pitched].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StrikeoutsAllowed
    fieldName=MLB_dbvar.dbvar_H_StrikeoutsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StrikeoutsGained
    fieldName=MLB_dbvar.dbvar_H_StrikeoutsGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Hits
    fieldName=MLB_dbvar.dbvar_H_Hits
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hits].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Hits_Allowed
    fieldName=MLB_dbvar.dbvar_H_HitsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hits].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_SP_HitsAllowed
    fieldName=MLB_dbvar.dbvar_H_SP_HitsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_hit].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_WalksAllowed
    fieldName=MLB_dbvar.dbvar_H_WalksAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_walks].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_WalksGained
    fieldName=MLB_dbvar.dbvar_H_WalksGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_walks].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_HomeRuns
    fieldName=MLB_dbvar.dbvar_H_HomeRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hruns].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_HomeRuns_Allowed
    fieldName=MLB_dbvar.dbvar_H_HomeRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hruns].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_5thInnScore
    fieldName=MLB_dbvar.dbvar_H_5thInnScore
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Duration
    fieldName=MLB_dbvar.dbvar_H_Duration
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_home_inn].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_NP
    fieldName=MLB_dbvar.dbvar_H_NP
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_np].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_Strikes
    fieldName=MLB_dbvar.dbvar_H_Strikes
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_strikes].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_LeftOnBase
    fieldName=MLB_dbvar.dbvar_H_LeftOnBase
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_lob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_2BRuns
    fieldName=MLB_dbvar.dbvar_H_2BRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_2b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_2BRuns_Allowed
    fieldName=MLB_dbvar.dbvar_H_2BRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_2b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_3BRuns
    fieldName=MLB_dbvar.dbvar_H_3BRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_3b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_3BRuns_Allowed
    fieldName=MLB_dbvar.dbvar_H_3BRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_3b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_ErrorMade
    fieldName=MLB_dbvar.dbvar_H_ErrorMade
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_err].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_ErrorForced
    fieldName=MLB_dbvar.dbvar_H_ErrorForced
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_err].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_HitsByPitch
    fieldName=MLB_dbvar.dbvar_H_HitsByPitch
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hbp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_HitsByPitch_Allowed
    fieldName=MLB_dbvar.dbvar_H_HitsByPitch_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hbp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_DoublePlays_Gained
    fieldName=MLB_dbvar.dbvar_H_DoublePlays_Gained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_home_dp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_DoublePlays_Allowed
    fieldName=MLB_dbvar.dbvar_H_DoublePlays_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_dp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_ReliefPitchers
    fieldName=MLB_dbvar.dbvar_H_ReliefPitchers
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_home_relief_pitchers].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # G_H_StartingPitcher_Id
    fieldName=MLB_dbvar.dbvar_G_H_StartingPitcher_Id
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_id].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)
    #NOTE For stats, YTD will act as base / primitives for All and _5G (YTD seeded with spot values from dump and then dGEN and Scion will calc averages)
    # H_StartingPitcher_Score 
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Score_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_StrikeOuts
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikeouts_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_BaseOnBalls
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_BaseOnBalls_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_bb].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_Hits
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Hits_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_hit].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_NP
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_NP_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_sp_np].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_InningsPitched
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_InningsPitched_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_h_sp_ip].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # H_StartingPitcher_Strikes
    fieldName=MLB_dbvar.dbvar_H_StartingPitcher_Strikes_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_h_sp_st].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    
    ################## VISITOR ################################
    # G_V_Id 
    fieldName=MLB_dbvar.dbvar_G_V_Id
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_vis_id].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)  #
    # G_V_League
    fieldName=MLB_dbvar.dbvar_G_V_League
    fieldValue=int(dump_df[MLB_dumpvar.dumpvar_visitor_league].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)  #
    # V_Innings
    fieldName=MLB_dbvar.dbvar_V_Innings
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_inn].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # V_Runs_Gained
    fieldName=MLB_dbvar.dbvar_V_Runs_Gained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Runs_Allowed
    fieldName=MLB_dbvar.dbvar_V_Runs_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Runs_5InningsGained
    fieldName=MLB_dbvar.dbvar_V_Runs_5InningsGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Runs_5InningsAllowed
    fieldName=MLB_dbvar.dbvar_V_Runs_5InningsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_OutsPitched
    fieldName=MLB_dbvar.dbvar_V_OutsPitched
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_number_of_outs_pitched].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StrikeoutsAllowed
    fieldName=MLB_dbvar.dbvar_V_StrikeoutsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StrikeoutsGained
    fieldName=MLB_dbvar.dbvar_V_StrikeoutsGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Hits
    fieldName=MLB_dbvar.dbvar_V_Hits
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hits].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Hits_Allowed
    fieldName=MLB_dbvar.dbvar_V_HitsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hits].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Walks_Allowed
    fieldName=MLB_dbvar.dbvar_V_WalksAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_walks].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Walks_Gained
    fieldName=MLB_dbvar.dbvar_V_WalksGained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_walks].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_HomeRuns
    fieldName=MLB_dbvar.dbvar_V_HomeRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hruns].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_HomeRuns_Allowed
    fieldName=MLB_dbvar.dbvar_V_HomeRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hruns].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_5thInnScore
    fieldName=MLB_dbvar.dbvar_V_5thInnScore
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_5th_inn_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Duration
    fieldName=MLB_dbvar.dbvar_V_Duration
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_inn].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_NP
    fieldName=MLB_dbvar.dbvar_V_NP
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_np].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Strikes
    fieldName=MLB_dbvar.dbvar_V_Strikes
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_strikes].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_LeftOnBase
    fieldName=MLB_dbvar.dbvar_V_LeftOnBase
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_lob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_2BRuns
    fieldName=MLB_dbvar.dbvar_V_2BRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_2b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_2BRuns_Allowed
    fieldName=MLB_dbvar.dbvar_V_2BRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_2b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_3BRuns
    fieldName=MLB_dbvar.dbvar_V_3BRuns
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_3b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_3BRuns_Allowed
    fieldName=MLB_dbvar.dbvar_V_3BRuns_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_3b].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Error
    fieldName=MLB_dbvar.dbvar_V_ErrorMade
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_err].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_Error_Allowed
    fieldName=MLB_dbvar.dbvar_V_ErrorForced
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_err].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_HitsByPitch
    fieldName=MLB_dbvar.dbvar_V_HitsByPitch
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_hbp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_HitsByPitch_Allowed
    fieldName=MLB_dbvar.dbvar_V_HitsByPitch_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_hbp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_SP_HitsAllowed
    fieldName=MLB_dbvar.dbvar_V_SP_HitsAllowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_hit].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_DoublePlays
    fieldName=MLB_dbvar.dbvar_V_DoublePlays_Gained
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_dp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_DoublePlays_Allowed
    fieldName=MLB_dbvar.dbvar_V_DoublePlays_Allowed
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_home_dp].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_ReliefPitchers
    fieldName=MLB_dbvar.dbvar_V_ReliefPitchers
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_visitor_relief_pitchers].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # G_V_StartingPitcher_Id
    fieldName=MLB_dbvar.dbvar_G_V_StartingPitcher_Id
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_id].iloc[dump_row_index])
    game_df[fieldName].values[0] = int(fieldValue)
    #NOTE For stats, YTD will act as base / primitives for All and _5G (YTD seeded with spot values from dump and then dGEN and Scion will calc averages)
    # V_StartingPitcher_Score 
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Score_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_score].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_StrikeOuts
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikeouts_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_so].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_BaseOnBalls
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_BaseOnBalls_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_bb].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_Hits
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Hits_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_hit].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_NP
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_NP_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_sp_np].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_InningsPitched
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_InningsPitched_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_v_sp_ip].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # V_StartingPitcher_Strikes
    fieldName=MLB_dbvar.dbvar_V_StartingPitcher_Strikes_YTD
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_v_sp_st].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    
    ################## Ivan features ################################
    # G_Ivan_BP_OffenseProbability
    fieldName=MLB_dbvar.dbvar_G_Ivan_BP_OffenseProbability
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_ivanbp_offensehprob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Ivan_BP_DefenseProbability 
    fieldName=MLB_dbvar.dbvar_G_Ivan_BP_DefenseProbability
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_ivanbp_defensehprob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Ivan_BP_NullProbability
    fieldName=MLB_dbvar.dbvar_G_Ivan_BP_NullProbability
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_ivanbp_nullhprob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    # G_Ivan_BP_NoLineProbability
    fieldName=MLB_dbvar.dbvar_G_Ivan_BP_NoLineProbability
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_ivanbp_nolinehprob].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)  #
    return game_df

def _updateTeamLines(game_df):
    #Assumption: Update_Primitive_Features() have seeded line primitives (opl/cll MiddleLines and vig)
    #Init vars
    _opmiddleLine = float(game_df[MLB_dbvar.dbvar_G_Opening_MiddleMoneyLine].values[0])
    _opVig = float(game_df[MLB_dbvar.dbvar_G_OpeningLine_Vig].values[0])
    _clmiddleLine = float(game_df[MLB_dbvar.dbvar_G_Closing_MiddleMoneyLine].values[0])
    _clVig = float(game_df[MLB_dbvar.dbvar_G_ClosingLine_Vig].values[0])
    #OPLs
    _hPrice, _vPrice = MLB_global.ConvertMiddleLineToPrices(_opmiddleLine, _opVig)
    _hProb = MLB_global.convertMoneyLinetoProb(_hPrice)
    _vProb = MLB_global.convertMoneyLinetoProb(_vPrice)
    game_df[MLB_dbvar.dbvar_G_H_Opening_MoneyLine].values[0] = float(_hPrice)
    game_df[MLB_dbvar.dbvar_G_H_OpeningProbabilityLine].values[0] = float(_hProb)
    game_df[MLB_dbvar.dbvar_G_V_Opening_MoneyLine].values[0] = float(_vPrice)
    game_df[MLB_dbvar.dbvar_G_V_OpeningProbabilityLine].values[0] = float(_vProb)
    #CLLs
    _hPrice, _vPrice = MLB_global.ConvertMiddleLineToPrices(_clmiddleLine, _clVig)
    _hProb = MLB_global.convertMoneyLinetoProb(_hPrice)
    _vProb = MLB_global.convertMoneyLinetoProb(_vPrice)
    game_df[MLB_dbvar.dbvar_G_H_Closing_MoneyLine].values[0] = float(_hPrice)
    game_df[MLB_dbvar.dbvar_G_H_ClosingProbabilityLine].values[0] = float(_hProb)
    game_df[MLB_dbvar.dbvar_G_V_Closing_MoneyLine].values[0] = float(_vPrice)
    game_df[MLB_dbvar.dbvar_G_V_ClosingProbabilityLine].values[0] = float(_vProb)

    return game_df

def updateDependentFeatures(game_df, dump_df, dump_row_index):
    #ASSUMPTION: all primitive attribs MUST already have been assigned a value
    ################## GAME-LEVEL ################################
    # Components of Date
    game_df = updateDateAttribs(game_df)
    ################## TEAM-LEVEL ################################
    # _Wins 
    # There should be NO ties and so only home team wins if there is a tie in the data because we're applying home team advantage
    # NOTE for H_Wins and H_Losses: test is G >= A whereas for Vis it is G > A
    ################## HOME ################################
    fieldName=MLB_dbvar.dbvar_H_Wins
    if (game_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0] >= game_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0]):
        fieldValue = 1
    else:
        fieldValue = 0
    game_df[fieldName].values[0] = float(fieldValue)  #
    # H_Losses 
    fieldName=MLB_dbvar.dbvar_H_Losses
    if (game_df[MLB_dbvar.dbvar_H_Runs_Gained].values[0] >= game_df[MLB_dbvar.dbvar_H_Runs_Allowed].values[0]):
        fieldValue = 0
    else:
        fieldValue = 1
    game_df[fieldName].values[0] = float(fieldValue)  #
    ################## VISITOR ################################
    fieldName=MLB_dbvar.dbvar_V_Wins
    if (game_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0] > game_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0]):
        fieldValue = 1
    else:
        fieldValue = 0
    game_df[fieldName].values[0] = float(fieldValue)  #
    # V_Losses 
    fieldName=MLB_dbvar.dbvar_V_Losses
    if (game_df[MLB_dbvar.dbvar_V_Runs_Gained].values[0] > game_df[MLB_dbvar.dbvar_V_Runs_Allowed].values[0]):
        fieldValue = 0
    else:
        fieldValue = 1
    game_df[fieldName].values[0] = float(fieldValue)  #
    ############### BOTH H and V #################################
    game_df = _updateTeamLines(game_df)
    
    return game_df

def updatePrimitiveTargets(game_df, dump_df, dump_row_index):
    # Only those target attributes that are directly dependent on the currently available data will be updated
    # Any attributes relying on the insample average will not be updated
    
    # Ensure cols that should have string datatypes do have str types
    # G_H_Runs
    fieldName=MLB_dbvar.dbvar_G_H_Runs
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_hom_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # G_V_Runs
    fieldName=MLB_dbvar.dbvar_G_V_Runs
    fieldValue=float(dump_df[MLB_dumpvar.dumpvar_vis_runs].iloc[dump_row_index])
    game_df[fieldName].values[0] = float(fieldValue)
    # G_Total
    fieldName=MLB_dbvar.dbvar_G_Total
    fieldValue=float(game_df[MLB_dbvar.dbvar_G_H_Runs].values[0] + game_df[MLB_dbvar.dbvar_G_V_Runs].values[0])
    game_df[fieldName].values[0] = float(fieldValue)

    return game_df

def initMasterRow(master_copy_df):
    #iterate columns, setting the value to MLB_dbvar.NO_DATA (except date, which will be initialised to today's date with expectation it will be updated later)
    for col in MLB_dbvar.MLBdb_vars:
        if col == MLB_dbvar.dbvar_G_Date:
            master_copy_df[MLB_dbvar.dbvar_G_Date].values[0] = datetime.today()
            #remove time
            master_copy_df[MLB_dbvar.dbvar_G_Date] = pd.to_datetime(master_copy_df[MLB_dbvar.dbvar_G_Date]).dt.date
        elif col in MLB_dbvar.MLBdb_str_vars:
            master_copy_df[col].values[0] = str(MLB_dbvar.NO_DATA)
        elif col in MLB_dbvar.MLBdb_float_vars:
            master_copy_df[col].values[0] = float(MLB_dbvar.NO_DATA)
        else:
            master_copy_df[col].values[0] = int(MLB_dbvar.NO_DATA)
    return master_copy_df

def updateMasterMLBAData(master_df, master_fname, dump_df):
    #all we want to do here is iteratre through the dump and for each row create a new record in the Master DB

    #NB Look ahead and look back details are NOT populated - they are simply set to MLB_dbvar.NO_DATA
    #   It is expected that either dGEN or SCION will complete these values
    try:
        # Cycle through each game in the dump creating new records and updating the master database 
        # first create a copy of the master database (as we want to use that as a template)
        game_df = master_df.copy()
        #now delete all but first row (as we will update that row!)
        num_rows= game_df.shape[0]
        if num_rows > 1:
            game_df = game_df.drop(game_df.index[:(num_rows-1)])
            game_df = game_df.reset_index(drop=True)
            num_rows= game_df.shape[0]
        #initialise all col types
        game_df = initMasterRow(game_df)
        game_df = MLB_dbvar.InitialiseMasterMLBColumnTypes(game_df)
        per_complete = 0.00    
        for i in range(0, dump_df.shape[0]):
            if dump_df.shape[0]>0:
                per_complete = (i+1)/dump_df.shape[0]*100
            
            print("\r>processing " + master_fname + " ---> " + "[game {0} of {1}".format(i+1, dump_df.shape[0]) + " : {0:.2f}% complete]".format(per_complete), end="")
            stdout.flush()
            #Update primitive features
            game_df = updatePrimitiveFeatures(game_df, dump_df, i)
            #update dependent features
            game_df = updateDependentFeatures(game_df, dump_df, i)
            #update target variables
            game_df = updatePrimitiveTargets(game_df, dump_df, i)
            #update master df
            master_df = pd.concat([master_df, game_df])
            #initialise game_df
            game_df = initMasterRow(game_df)

        print("\n")
    
    except Exception:
            print("\nupdateMasterMLBAData(): Fatal error updating the database!\n")
            _errorReport()
       
    return master_df

def loadValidateMasterData(master_df, master_fname):
    try:
        # 1) Read data into a pd frame
        master_df = pd.read_csv(master_fname, header=0)
        # 2) Check required cols exist
        mastervars_found = master_df.columns.tolist()  
        # using map() + reduce() to check if lists are equal 
        if functools.reduce(lambda i, j : i and j, map(lambda m, k: m == k, MLB_dbvar.MLBdb_vars, mastervars_found), False) :
            print("failed.")  
            print ("\nFatal Error - column headings in master CSV file do not match those expected!")
            print ("\n\nColumns EXPECTED: " + str(MLB_dbvar.MLBdb_vars))
            print ("\n\nColumns FOUND (after pre-processing): " + str(mastervars_found) + "\n")
            raise Exception
        # 3) Initialise columns types (except dates, will deal separately)
        master_df = MLB_dbvar.InitialiseMasterMLBColumnTypes(master_df)
        # 4) Convert Date to correct format
        master_df[MLB_dbvar.dbvar_G_Date] = pd.to_datetime(master_df[MLB_dbvar.dbvar_G_Date], format=MLB_dumpvar.dump_date_Format)
        master_df[MLB_dbvar.dbvar_G_Date] = master_df[MLB_dbvar.dbvar_G_Date].dt.strftime(MLB_dumpvar.dump_date_Format)
        
    except Exception:
        print("\nloadValidateMasterData(): Fatal error loading and validating " + master_fname, end="\n")
        _errorReport()
        
    return master_df

def checkForDuplicateColHeadings(dumpfname, usrDumpCommaSep):
    if usrDumpCommaSep:
        _df = pd.read_csv(dumpfname, header=None, nrows=1)
    else:  #tab separated assumed
        _df = pd.read_csv(dumpfname, header=None, sep='\t', nrows=1)
    return _df.iloc[0].is_unique

def loadValidateDumpData(dump_df, dumpfname, usrDumpCommaSep):
    try:
        _continue = True
        # 1) Read data into a pd frame
        if checkForDuplicateColHeadings(dumpfname, usrDumpCommaSep):
            if usrDumpCommaSep:
                dump_df = pd.read_csv(dumpfname, header=0, dayfirst=False)
            else:  #tab separated assumed
                dump_df = pd.read_csv(dumpfname, header=0, sep='\t', dayfirst=False)
        else:
            print ("\nColumn headings are NOT unique! Please correct column headers and try again!\n")
            _continue = False
        
        if _continue:
            # 2) Check we have data
            num_rows = dump_df.shape[0]
            if not num_rows:
                print ("\nNo update to be made - there are no games in the dump file to process.\n")
                _continue = False
            else:
                # 3) Preprocess column names (set all to lowercase and replace space between words with VAR_WORD_SEP) and only retain columns we know about
                dump_df.columns = dump_df.columns.str.strip().str.lower().str.replace(r' ', VAR_WORD_SEP, regex=True).str.replace(r'\(', r'', regex=True).str.replace(r'\)', r'', regex=True)
                dump_df = dump_df[dump_df.columns[dump_df.columns.isin(MLB_dumpvar.MLBdump_vars)]]
                # 4) Check if required cols exist
                dumpvars_found = dump_df.columns.tolist()  
                # using map() + reduce() to check if lists are equal 
                if functools.reduce(lambda i, j : i and j, map(lambda m, k: m == k, MLB_dumpvar.MLBdump_vars, dumpvars_found), False) :  
                    print ("\nFatal Error - column headings in dump file do not match those expected!")
                    print ("\n\nColumns EXPECTED: " + str(MLB_dumpvar.MLBdump_vars))
                    print ("\n\nColumns FOUND (after pre-processing): " + str(dumpvars_found) + "\n")
                    _continue = False

                # 5) Check if there are any missing values in the dump
                if _continue:
                    missing_values = dump_df.isnull().sum().sum()
                    if missing_values:
                        _continue = False
                        print ("\nFatal Error - ", missing_values, " missing value(s) were found in the dump file!")
                        print("\nThe following columns appear to be affected:\n")
                        _missingValues_df = dump_df.isnull()
                        for col in _missingValues_df.columns.values.tolist():
                            if True in _missingValues_df[col].values:
                                _keys = _missingValues_df[col].value_counts().keys().tolist() # [False, True]
                                _counts = _missingValues_df[col].value_counts().tolist() # [NumFalse, NumTrue]
                                # convert lists to dictionary
                                _colMissingValueDict = {_keys[i]: _counts[i] for i in range(len(_keys))}
                                print("\t[{0}]\t\t---> {1} missing values.".format(col, _colMissingValueDict[True]))
                        print ("\nPlease resolve the issue and try again.\n")

                    if _continue:
                        # 6) Count number of zeros in dumpvar_hom_sp_id and report
                        _zeroSP = (dump_df[MLB_dumpvar.dumpvar_hom_sp_id] == 0).sum()
                        if not num_rows:
                            _percZeroSP = 0
                        else:
                            _percZeroSP = _zeroSP / num_rows * 100
                        print("\t\tvalidating feature [" + MLB_dumpvar.dumpvar_hom_sp_id + "] ---> {0:.2f}% instances were equal to zero.".format(_percZeroSP))
                        stdout.flush()

                        # 7) Count number of zeros in dumpvar_vis_sp_id and report
                        _zeroSP = (dump_df[MLB_dumpvar.dumpvar_vis_sp_id] == 0).sum()
                        if not num_rows:
                            _percZeroSP = 0
                        else:
                            _percZeroSP = _zeroSP / num_rows * 100
                        print("\t\tvalidating feature [" + MLB_dumpvar.dumpvar_vis_sp_id + "] ---> {0:.2f}% instances were equal to zero.".format(_percZeroSP))
                        stdout.flush()
            
                        # 8) Check number of instances where opl = cll
                        _dumpCopy_df = dump_df.copy()
                        _seriesOPL = _dumpCopy_df[MLB_dumpvar.dumpvar_opening_mline]
                        _seriesCLL = _dumpCopy_df[MLB_dumpvar.dumpvar_closing_mline]
                        _seriesCLL = _seriesCLL.eq(_seriesOPL, fill_value=0)
                        _oplcllMatches = _seriesCLL.sum()
                        if not num_rows:
                            _oplcllMatchTotals = 0
                        else:
                            _oplcllMatchTotals = _oplcllMatches / num_rows * 100
                        print("\t\tvalidating features [opening_mline, closing_mline] --->" + " {0:.2f}% instances where these features have equal values.".format(_oplcllMatchTotals))
                        stdout.flush()

                        # 9) Check number of instances where opening_total_spread = closing_total_spread
                        _dumpCopy_df = dump_df.copy()
                        _seriesOPL = _dumpCopy_df[MLB_dumpvar.dumpvar_opening_total_spread]
                        _seriesCLL = _dumpCopy_df[MLB_dumpvar.dumpvar_closing_total_spread]
                        _seriesCLL = _seriesCLL.eq(_seriesOPL, fill_value=0)
                        _oplcllMatches = _seriesCLL.sum()
                        if not num_rows:
                            _oplcllMatchTotals = 0
                        else:
                            _oplcllMatchTotals = _oplcllMatches / num_rows * 100
                        print("\t\tvalidating features [opening_total_spread, closing_total_spread] --->" + " {0:.2f}% instances where these features have equal values.".format(_oplcllMatchTotals))
                        stdout.flush()
                    
                        # 10) Convert date to correct format
                        print("\t\tensuring date is in " + MLB_dumpvar.dump_date_Format + " format ---> ", end="")
                        dump_df[MLB_dumpvar.dumpvar_date] = pd.to_datetime(dump_df[MLB_dumpvar.dumpvar_date], format=MLB_dumpvar.dump_date_Format)
                        dump_df[MLB_dumpvar.dumpvar_date] = dump_df[MLB_dumpvar.dumpvar_date].dt.strftime(MLB_dumpvar.dump_date_Format)
                        print("done.")
       
    except Exception:
        print("\nloadValidateDumpData(): Fatal error validating " + dumpfname + " - see error message above\n")
        _errorReport()
        
    return dump_df, _continue


def dropMasterOverlap(master_df, dump_df):
    # We consider the DUMP to contain the latest information. Therefore any games in the master_db that occur on the same date as the dump will be removed
    try:
        # 1. Get earliest game in the dump
        dateThreshold = dump_df[MLB_dumpvar.dumpvar_date].min()
        dateThreshold_dt = datetime.strptime(dateThreshold, MLB_dumpvar.dump_date_Format)
        dateThreshold_dt = dateThreshold_dt.date()
        # 2. Drop games in the master_df that occur on or after this date
        master_df = master_df[master_df[MLB_dbvar.dbvar_G_Date] < dateThreshold]
        # 3. Add empty row if step resulted in an empty dataframe (we)
        if not master_df.shape[0]:
            master_df = pd.concat([master_df, pd.DataFrame([pd.Series()])], ignore_index=True)
        
    except Exception:
        print("\ndropMasterOverlap(): error removing overlapping games in the master database!\n")
        _errorReport()
        
    return master_df, dateThreshold_dt


if __name__ == "__main__":
    parser = argparse.ArgumentParser("\nUpdates a given MLB flat file database using a text dump of games.\n")
    parser.add_argument("usrMasterDB_Fname", help="CSV file containing current MLB flat file database")
    parser.add_argument("usrDump_Fname", help="text file or CSV file of games containing latest data dump")
    parser.add_argument("usrResults_Fname", help="CSV file containing updated MLB flat file database")
    parser.add_argument("usrDumpCommaDelim", help="True/False flag indicating whether the dump file is comma separated. If False then the assumption is that it is TAB separated")
    
    args = parser.parse_args()  # if incorrect operation entered, program will bomb here
    
    # arguments come in a str so we have to convert if required 
    usrMasterDBFname = args.usrMasterDB_Fname
    usrDumpFname = args.usrDump_Fname
    usrResultsFname = args.usrResults_Fname
    usrDumpCommaSep = args.usrDumpCommaDelim

    if usrDumpCommaSep == "True":
        usrDumpCommaSep = True
    else:
        usrDumpCommaSep = False
       
    # update user input file with full absolute path
    Full_usrMastrDBFname = os.path.join(cwd, usrMasterDBFname)
    Full_usrDumpFname = os.path.join(cwd, usrDumpFname)
    Full_usrResultsFname = os.path.join(cwd, usrResultsFname)
  
    # Read and initialise master MLB database
    try:
        #1 Load and validate  Master MLB csv file 
        print("\nLoading and validating " + usrMasterDBFname + "...", end="")
        MASTER_games_df = DUMP_games_df = pd.DataFrame
        MASTER_games_df = loadValidateMasterData(MASTER_games_df, Full_usrMastrDBFname)
        print("done.")  

        #2 Load and validate Dump txt or csv file
        _success = True
        print("Loading and validating " + usrDumpFname + ":")
        DUMP_games_df, _success = loadValidateDumpData(DUMP_games_df, Full_usrDumpFname, usrDumpCommaSep)
        print("Dump validation completed.\n")  
        
        if _success:
            #2.1 Update master database
            print("Updating the master database file with game data found in the dump file (any duplicate game data in the master file will be OVERWRITTEN!):", end="\n")
            MASTER_games_df, date_threshold = dropMasterOverlap(MASTER_games_df, DUMP_games_df)
            MASTER_games_df = updateMasterMLBAData(MASTER_games_df, usrMasterDBFname, DUMP_games_df)
            print("\n>done.\nAll games in " + usrMasterDBFname + " from " + date_threshold.strftime("%Y-%m-%d") + " onwards have been replaced by game data provided in " + usrDumpFname)  
        
            #2.2 Validate final output by removing any duplicates (based on G_Id) and sort (based on G_Date, G_Id)
            print("\nValidating and sorting updated games...", end="")
            MASTER_games_df = MASTER_games_df.drop_duplicates([MLB_dbvar.dbvar_G_Id])
            MASTER_games_df = MASTER_games_df.dropna()
            MASTER_games_df[MLB_dbvar.dbvar_G_Date] =  pd.to_datetime(MASTER_games_df[MLB_dbvar.dbvar_G_Date])
            MASTER_games_df = MASTER_games_df.sort_values(by=[MLB_dbvar.dbvar_G_Date, MLB_dbvar.dbvar_G_Id], ascending=[True, True])
            print("done.")  
        
            #2.3 Store updated database to results file
            print("\nStoring updated master database...", end="")
            MASTER_games_df.to_csv(Full_usrResultsFname, header=True, index=False, date_format=MLB_dumpvar.dump_date_Format)
            print("done.\nPlease review file "+Full_usrResultsFname+"\n")

        #3 Exit banner
        print("\n" + APP_NAME + " completed successfully.", end="\n\n")
    
    except:
        print("\nFatal Error - problem either sorting updated database or writing it to  "+Full_usrResultsFname+"\n")
        _errorReport()
    
        
