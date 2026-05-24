import math
import enum
import pandas as pd
from datetime import datetime, date, time, timedelta
# pylint: disable=c0301
#NOTE: StartingPitcher_OPP vars are no longer used!

dbvar_G_Id = "G_Id"
dbvar_G_Date = "G_Date"
dbvar_G_Year = "G_Year"
dbvar_G_Month = "G_Month"
dbvar_G_Day = "G_Day"
dbvar_G_MonthWeek = "G_MonthWeek"
dbvar_G_Opening_TotalOver = "G_Opening_TotalOver"
dbvar_G_Opening_TotalOverLine = "G_Opening_TotalOverLine"
dbvar_G_Closing_TotalOver = "G_Closing_TotalOver"
dbvar_G_Closing_TotalOverLine = "G_Closing_TotalOverLine"
dbvar_G_Bookie_TotalOver = "G_Bookie_TotalOver"
dbvar_G_Bookie_TotalOverLine = "G_Bookie_TotalOverLine"
dbvar_G_NightGame = "G_NightGame"
dbvar_G_H_Id = "G_H_Id"
dbvar_G_Bookie_H_MoneyLine = "G_Bookie_H_MoneyLine"
dbvar_G_Bookie_H_Probability = "G_Bookie_H_Probability"
dbvar_G_H_Opening_MoneyLine = "G_H_Opening_MoneyLine"
dbvar_G_H_OpeningProbabilityLine = "G_H_OpeningProbabilityLine"
dbvar_G_H_Closing_MoneyLine = "G_H_Closing_MoneyLine"
dbvar_G_H_ClosingProbabilityLine = "G_H_ClosingProbabilityLine"
dbvar_G_H_CLL_OPL_Prob_Diff = "G_H_CLL_OPL_Prob_Diff"
dbvar_G_H_ParkImpactFactor = "G_H_ParkImpactFactor"
dbvar_G_H_League = "G_H_League"
dbvar_G_H_Division = "G_H_Division"
dbvar_G_H_LeagueDiv = "G_H_LeagueDiv"
dbvar_G_H_Same_LeagueDiv = "G_H_Same_LeagueDiv"
dbvar_G_H_Same_Div = "G_H_Same_Div"
dbvar_G_H_DaysRest = "G_H_DaysRest"
dbvar_G_H_ContiguousGamesV = "G_H_ContiguousGamesV"
dbvar_G_H_ContiguousGamesH = "G_H_ContiguousGamesH"
dbvar_G_H_TotalDistanceTravelled_3G = "G_H_TotalDistanceTravelled_3G"
dbvar_G_H_Prev1_Id = "G_H_Prev1_Id"
dbvar_G_H_Prev1_LeagueDiv = "G_H_Prev1_LeagueDiv"
dbvar_G_H_Prev1_SameLeagueDiv = "G_H_Prev1_SameLeagueDiv"
dbvar_G_H_Prev1_SameDiv = "G_H_Prev1_SameDiv"
dbvar_G_H_Prev1_DistanceTravelled = "G_H_Prev1_DistanceTravelled"
dbvar_G_H_Prev1Home = "G_H_Prev1Home"
dbvar_G_H_Prev1Strength = "G_H_Prev1Strength"
dbvar_G_H_Prev1StrengthRatio = "G_H_Prev1StrengthRatio"
dbvar_G_H_Prev1Win = "G_H_Prev1Win"
dbvar_G_H_Prev1CLL = "G_H_Prev1CLL"
dbvar_G_H_Prev1_Summary = "G_H_Prev1_Summary"
dbvar_G_H_Prev2_Id = "G_H_Prev2_Id"
dbvar_G_H_Prev2_LeagueDiv = "G_H_Prev2_LeagueDiv"
dbvar_G_H_Prev2_SameLeagueDiv = "G_H_Prev2_SameLeagueDiv"
dbvar_G_H_Prev2_SameDiv = "G_H_Prev2_SameDiv"
dbvar_G_H_Prev2_DistanceTravelled = "G_H_Prev2_DistanceTravelled"
dbvar_G_H_Prev2Home = "G_H_Prev2Home"
dbvar_G_H_Prev2Strength = "G_H_Prev2Strength"
dbvar_G_H_Prev2StrengthRatio = "G_H_Prev2StrengthRatio"
dbvar_G_H_Prev2Win  = "G_H_Prev2Win"
dbvar_G_H_Prev2CLL = "G_H_Prev2CLL"
dbvar_G_H_Prev2_Summary = "G_H_Prev2_Summary"
dbvar_G_H_Prev3_Id = "G_H_Prev3_Id"
dbvar_G_H_Prev3_LeagueDiv = "G_H_Prev3_LeagueDiv"
dbvar_G_H_Prev3_SameLeagueDiv = "G_H_Prev3_SameLeagueDiv"
dbvar_G_H_Prev3_SameDiv = "G_H_Prev3_SameDiv"
dbvar_G_H_Prev3_DistanceTravelled = "G_H_Prev3_DistanceTravelled"
dbvar_G_H_Prev3Home = "G_H_Prev3Home"
dbvar_G_H_Prev3Strength = "G_H_Prev3Strength"
dbvar_G_H_Prev3StrengthRatio = "G_H_Prev3StrengthRatio"
dbvar_G_H_Prev3Win  = "G_H_Prev3Win"
dbvar_G_H_Prev3CLL = "G_H_Prev3CLL"
dbvar_G_H_Prev3_Summary = "G_H_Prev3_Summary"
dbvar_G_H_Lookback_Strength = "G_H_Lookback_Strength"
dbvar_G_H_Next1_Id = "G_H_Next1_Id"
dbvar_G_H_Next1_LeagueDiv = "G_H_Next1_LeagueDiv"
dbvar_G_H_Next1_SameLeagueDiv = "G_H_Next1_SameLeagueDiv"
dbvar_G_H_Next1_SameDiv = "G_H_Next1_SameDiv"
dbvar_G_H_Next1_DistanceTravelled = "G_H_Next1_DistanceTravelled"
dbvar_G_H_Next1Home = "G_H_Next1Home"
dbvar_G_H_Next1Strength = "G_H_Next1Strength"
dbvar_G_H_Next1StrengthRatio = "G_H_Next1StrengthRatio"
dbvar_G_H_Next1_Summary = "G_H_Next1_Summary"
dbvar_G_H_Next2_Id = "G_H_Next2_Id"
dbvar_G_H_Next2_LeagueDiv = "G_H_Next2_LeagueDiv"
dbvar_G_H_Next2_SameLeagueDiv = "G_H_Next2_SameLeagueDiv"
dbvar_G_H_Next2_SameDiv = "G_H_Next2_SameDiv"
dbvar_G_H_Next2_DistanceTravelled = "G_H_Next2_DistanceTravelled"
dbvar_G_H_Next2Home = "G_H_Next2Home"
dbvar_G_H_Next2Strength = "G_H_Next2Strength"
dbvar_G_H_Next2StrengthRatio = "G_H_Next2StrengthRatio"
dbvar_G_H_Next2_Summary = "G_H_Next2_Summary"
dbvar_G_H_Next3_Id = "G_H_Next3_Id"
dbvar_G_H_Next3_LeagueDiv = "G_H_Next3_LeagueDiv"
dbvar_G_H_Next3_SameLeagueDiv = "G_H_Next3_SameLeagueDiv"
dbvar_G_H_Next3_SameDiv = "G_H_Next3_SameDiv"
dbvar_G_H_Next3_DistanceTravelled = "G_H_Next3_DistanceTravelled"
dbvar_G_H_Next3Home = "G_H_Next3Home"
dbvar_G_H_Next3Strength = "G_H_Next3Strength"
dbvar_G_H_Next3StrengthRatio = "G_H_Next3StrengthRatio"
dbvar_G_H_Next3_Summary = "G_H_Next3_Summary"
dbvar_G_H_Lookahead_Strength = "G_H_Lookahead_Strength"
dbvar_H_ClosingProbabilityLine_HV = "H_ClosingProbabilityLine_HV"
dbvar_H_ClosingProbabilityLine_YTD_HV = "H_ClosingProbabilityLine_YTD_HV"
dbvar_H_Runs_Gained = "H_Runs_Gained"
dbvar_H_Runs_Allowed = "H_Runs_Allowed"
dbvar_H_Run_Strength = "H_Run_Strength"
dbvar_H_Run_Efficiency = "H_Run_Efficiency"
dbvar_H_Run_Pythag = "H_Run_Pythag"
dbvar_H_Runs_Gained_5G = "H_Runs_Gained_5G"
dbvar_H_Runs_Allowed_5G = "H_Runs_Allowed_5G"
dbvar_H_Run_Strength_5G = "H_Run_Strength_5G"
dbvar_H_Run_Efficiency_5G = "H_Run_Efficiency_5G"
dbvar_H_Run_Pythag_5G = "H_Run_Pythag_5G"
dbvar_H_Runs_Gained_20G = "H_Runs_Gained_20G"
dbvar_H_Runs_Allowed_20G = "H_Runs_Allowed_20G"
dbvar_H_Run_Strength_20G = "H_Run_Strength_20G"
dbvar_H_Run_Efficiency_20G = "H_Run_Efficiency_20G"
dbvar_H_Run_Pythag_20G = "H_Run_Pythag_20G"
dbvar_H_Runs_Gained_Sum = "H_Runs_Gained_Sum"
dbvar_H_Runs_Allowed_Sum = "H_Runs_Allowed_Sum"
dbvar_H_Run_Strength_Sum = "H_Run_Strength_Sum"
dbvar_H_Run_Efficiency_Sum = "H_Run_Efficiency_Sum"
dbvar_H_Run_Pythag_Sum = "H_Run_Pythag_Sum"
dbvar_H_Runs_Gained_Sum_5G = "H_Runs_Gained_Sum_5G"
dbvar_H_Runs_Allowed_Sum_5G = "H_Runs_Allowed_Sum_5G"
dbvar_H_Run_Strength_Sum_5G = "H_Run_Strength_Sum_5G"
dbvar_H_Run_Efficiency_Sum_5G = "H_Run_Efficiency_Sum_5G"
dbvar_H_Runs_Gained_Sum_20G = "H_Runs_Gained_Sum_20G"
dbvar_H_Runs_Allowed_Sum_20G = "H_Runs_Allowed_Sum_20G"
dbvar_H_Run_Strength_Sum_20G = "H_Run_Strength_Sum_20G"
dbvar_H_Run_Efficiency_Sum_20G = "H_Run_Efficiency_Sum_20G"
dbvar_H_Runs_Gained_Sum_HV = "H_Runs_Gained_Sum_HV"
dbvar_H_Runs_Allowed_Sum_HV = "H_Runs_Allowed_Sum_HV"
dbvar_H_Run_Strength_Sum_HV = "H_Run_Strength_Sum_HV"
dbvar_H_Runs_Gained_HV = "H_Runs_Gained_HV"
dbvar_H_Runs_Allowed_HV = "H_Runs_Allowed_HV"
dbvar_H_Run_Strength_HV = "H_Run_Strength_HV"
dbvar_H_Runs_Gained_YTD = "H_Runs_Gained_YTD"
dbvar_H_Runs_Allowed_YTD = "H_Runs_Allowed_YTD"
dbvar_H_Run_Strength_YTD = "H_Run_Strength_YTD"
dbvar_H_Run_Pythag_YTD = "H_Run_Pythag_YTD"
dbvar_H_Runs_Gained_YTD_HV = "H_Runs_Gained_YTD_HV"
dbvar_H_Runs_Allowed_YTD_HV = "H_Runs_Allowed_YTD_HV"
dbvar_H_Run_Strength_YTD_HV = "H_Run_Strength_YTD_HV"
dbvar_H_Runs_5InningsGained = "H_Runs_5InningsGained"
dbvar_H_Runs_5InningsAllowed = "H_Runs_5InningsAllowed"
dbvar_H_Run_5InningsStrength = "H_Run_5InningsStrength"
dbvar_H_Run_5InningsEfficiency = "H_Run_5InningsEfficiency"
dbvar_H_Runs_5InningsGained_Sum = "H_Runs_5InningsGained_Sum"
dbvar_H_Runs_5InningsAllowed_Sum = "H_Runs_5InningsAllowed_Sum"
dbvar_H_Run_5InningsStrength_Sum = "H_Run_5InningsStrength_Sum"
dbvar_H_Run_5InningsEfficiency_Sum = "H_Run_5InningsEfficiency_Sum"
dbvar_H_Runs_5InningsGained_5G = "H_Runs_5InningsGained_5G"
dbvar_H_Runs_5InningsAllowed_5G = "H_Runs_5InningsAllowed_5G"
dbvar_H_Run_5InningsStrength_5G = "H_Run_5InningsStrength_5G"
dbvar_H_Run_5InningsEfficiency_5G = "H_Run_5InningsEfficiency_5G"
dbvar_H_Runs_5InningsGained_Sum_5G = "H_Runs_5InningsGained_Sum_5G"
dbvar_H_Runs_5InningsAllowed_Sum_5G = "H_Runs_5InningsAllowed_Sum_5G"
dbvar_H_Run_5InningsStrength_Sum_5G = "H_Run_5InningsStrength_Sum_5G"
dbvar_H_Run_5InningsEfficiency_Sum_5G = "H_Run_5InningsEfficiency_Sum_5G"
dbvar_H_Runs_5InningsGained_20G = "H_Runs_5InningsGained_20G"
dbvar_H_Runs_5InningsAllowed_20G = "H_Runs_5InningsAllowed_20G"
dbvar_H_Run_5InningsStrength_20G = "H_Run_5InningsStrength_20G"
dbvar_H_Run_5InningsEfficiency_20G = "H_Run_5InningsEfficiency_20G"
dbvar_H_Runs_5InningsGained_Sum_20G = "H_Runs_5InningsGained_Sum_20G"
dbvar_H_Runs_5InningsAllowed_Sum_20G = "H_Runs_5InningsAllowed_Sum_20G"
dbvar_H_Run_5InningsStrength_Sum_20G = "H_Run_5InningsStrength_Sum_20G"
dbvar_H_Run_5InningsEfficiency_Sum_20G = "H_Run_5InningsEfficiency_Sum_20G"
dbvar_H_Runs_5InningsGained_Sum_HV = "H_Runs_5InningsGained_Sum_HV"
dbvar_H_Runs_5InningsAllowed_Sum_HV = "H_Runs_5InningsAllowed_Sum_HV"
dbvar_H_Run_5InningsStrength_Sum_HV = "H_Run_5InningsStrength_Sum_HV"
dbvar_H_Runs_5InningsGained_HV = "H_Runs_5InningsGained_HV"
dbvar_H_Runs_5InningsAllowed_HV = "H_Runs_5InningsAllowed_HV"
dbvar_H_Run_5InningsStrength_HV = "H_Run_5InningsStrength_HV"
dbvar_H_Runs_5InningsGained_YTD = "H_Runs_5InningsGained_YTD"
dbvar_H_Runs_5InningsAllowed_YTD = "H_Runs_5InningsAllowed_YTD"
dbvar_H_Run_5InningsStrength_YTD = "H_Run_5InningsStrength_YTD"
dbvar_H_Pythag_Luck_Factor = "H_Pythag_Luck_Factor"
dbvar_H_Pythag_Luck_Factor_5G = "H_Pythag_Luck_Factor_5G"
dbvar_H_Pythag_Luck_Factor_20G = "H_Pythag_Luck_Factor_20G"
dbvar_H_Pythag_Luck_Factor_YTD = "H_Pythag_Luck_Factor_YTD"
dbvar_H_Run_Differential_Per_Game = "H_Run_Differential_Per_Game"
dbvar_H_Run_Differential_Per_Game_5G = "H_Run_Differential_Per_Game_5G"
dbvar_H_Run_Differential_Per_Game_20G = "H_Run_Differential_Per_Game_20G"
dbvar_H_Run_Differential_Per_Game_YTD = "H_Run_Differential_Per_Game_YTD"
dbvar_H_Weighted_Offense_Index = "H_Weighted_Offense_Index"
dbvar_H_Weighted_Offense_Index_5G = "H_Weighted_Offense_Index_5G"
dbvar_H_Weighted_Offense_Index_20G = "H_Weighted_Offense_Index_20G"
dbvar_H_Weighted_Offense_Index_YTD = "H_Weighted_Offense_Index_YTD"
dbvar_H_At_Bat = "H_At_Bat"
dbvar_H_At_Bat_5G = "H_At_Bat_5G"
dbvar_H_At_Bat_20G = "H_At_Bat_20G"
dbvar_H_At_Bat_YTD = "H_At_Bat_YTD"
dbvar_H_At_Bat_HV = "H_At_Bat_HV"
dbvar_H_At_Bat_YTD_HV = "H_At_Bat_YTD_HV"
dbvar_H_OBP = "H_OBP"
dbvar_H_OBP_5G = "H_OBP_5G"
dbvar_H_OBP_20G = "H_OBP_20G"
dbvar_H_OBP_YTD = "H_OBP_YTD"
dbvar_H_SLG = "H_SLG"
dbvar_H_SLG_5G = "H_SLG_5G"
dbvar_H_SLG_20G = "H_SLG_20G"
dbvar_H_SLG_YTD = "H_SLG_YTD"
dbvar_H_wOBA = "H_wOBA"
dbvar_H_wOBA_5G = "H_wOBA_5G"
dbvar_H_wOBA_20G = "H_wOBA_20G"
dbvar_H_wOBA_YTD = "H_wOBA_YTD"
dbvar_H_OPS = "H_OPS"
dbvar_H_OPS_5G = "H_OPS_5G"
dbvar_H_OPS_20G = "H_OPS_20G"
dbvar_H_OPS_YTD = "H_OPS_YTD"
dbvar_H_Wins = "H_Wins"
dbvar_H_Losses = "H_Losses"
dbvar_H_WinLoss_Strength = "H_WinLoss_Strength"
dbvar_H_Wins_5G = "H_Wins_5G"
dbvar_H_Losses_5G = "H_Losses_5G"
dbvar_H_WinLoss_Strength_5G = "H_WinLoss_Strength_5G"
dbvar_H_Wins_20G = "H_Wins_20G"
dbvar_H_Losses_20G = "H_Losses_20G"
dbvar_H_WinLoss_Strength_20G = "H_WinLoss_Strength_20G"
dbvar_H_Wins_HV = "H_Wins_HV"
dbvar_H_Losses_HV = "H_Losses_HV"
dbvar_H_WinLoss_Strength_HV = "H_WinLoss_Strength_HV"
dbvar_H_Wins_YTD = "H_Wins_YTD"
dbvar_H_Losses_YTD = "H_Losses_YTD"
dbvar_H_WinLoss_Strength_YTD = "H_WinLoss_Strength_YTD"
dbvar_H_Wins_YTD_HV = "H_Wins_YTD_HV"
dbvar_H_Losses_YTD_HV = "H_Losses_YTD_HV"
dbvar_H_WinLoss_Strength_YTD_HV = "H_WinLoss_Strength_YTD_HV"
dbvar_H_OutsPitched_Sum = "H_OutsPitched_Sum"
dbvar_H_OutsPitched = "H_OutsPitched"
dbvar_H_OutsPitched_5G = "H_OutsPitched_5G"
dbvar_H_OutsPitched_20G = "H_OutsPitched_20G"
dbvar_H_OutsPitched_YTD = "H_OutsPitched_YTD"
dbvar_H_OutsPitched_YTD_HV = "H_OutsPitched_YTD_HV"
dbvar_H_StrikeoutsAllowed = "H_StrikeoutsAllowed"
dbvar_H_StrikeoutsGained = "H_StrikeoutsGained"
dbvar_H_StrikeoutAccuracy = "H_StrikeoutAccuracy"
dbvar_H_StrikeoutsAllowed_Sum = "H_StrikeoutsAllowed_Sum"
dbvar_H_StrikeoutsGained_Sum = "H_StrikeoutsGained_Sum"
dbvar_H_StrikeoutAccuracy_Sum = "H_StrikeoutAccuracy_Sum"
dbvar_H_StrikeoutsAllowed_5G = "H_StrikeoutsAllowed_5G"
dbvar_H_StrikeoutsGained_5G = "H_StrikeoutsGained_5G"
dbvar_H_StrikeoutsGained_20G = "H_StrikeoutsGained_20G"
dbvar_H_StrikeoutAccuracy_5G = "H_StrikeoutAccuracy_5G"
dbvar_H_StrikeoutsAllowed_YTD = "H_StrikeoutsAllowed_YTD"
dbvar_H_StrikeoutsGained_YTD = "H_StrikeoutsGained_YTD"
dbvar_H_StrikeoutAccuracy_YTD = "H_StrikeoutAccuracy_YTD"
dbvar_H_StrikeoutsAllowed_YTD_HV = "H_StrikeoutsAllowed_YTD_HV"
dbvar_H_StrikeoutsGained_YTD_HV = "H_StrikeoutsGained_YTD_HV"
dbvar_H_StrikeoutAccuracy_YTD_HV = "H_StrikeoutAccuracy_YTD_HV"
dbvar_H_Hits_Sum = "H_Hits_Sum"
dbvar_H_Hits = "H_Hits"
dbvar_H_Hits_Sum_5G = "H_Hits_Sum_5G"
dbvar_H_Hits_5G = "H_Hits_5G"
dbvar_H_Hits_Sum_20G = "H_Hits_Sum_20G"
dbvar_H_Hits_20G = "H_Hits_20G"
dbvar_H_Hits_YTD = "H_Hits_YTD"
dbvar_H_Hits_YTD_HV = "H_Hits_YTD_HV"
dbvar_H_HitsAllowed_Sum = "H_HitsAllowed_Sum"
dbvar_H_HitsAllowed_Sum_5G = "H_HitsAllowed_Sum_5G"
dbvar_H_HitsAllowed_Sum_20G = "H_HitsAllowed_Sum_20G"
dbvar_H_HitsAllowed = "H_HitsAllowed"
dbvar_H_HitsAllowed_5G = "H_HitsAllowed_5G"
dbvar_H_HitsAllowed_20G = "H_HitsAllowed_20G"
dbvar_H_HitsAllowed_YTD = "H_HitsAllowed_YTD"
dbvar_H_HitsAllowed_YTD_HV = "H_HitsAllowed_YTD_HV"
dbvar_H_RunsHitsRatio = "H_RunsHitsRatio"
dbvar_H_RunsHitsRatio_Sum = "H_RunsHitsRatio_Sum"
dbvar_H_RunsHitsRatio_5G = "H_RunsHitsRatio_5G"
dbvar_H_RunsHitsRatio_Sum_5G = "H_RunsHitsRatio_Sum_5G"
dbvar_H_RunsHitsRatio_20G = "H_RunsHitsRatio_20G"
dbvar_H_RunsHitsRatio_Sum_20G = "H_RunsHitsRatio_Sum_20G"
dbvar_H_RunsHitsRatio_YTD = "H_RunsHitsRatio_YTD"
dbvar_H_RunsHitsRatio_Allowed = "H_RunsHitsRatio_Allowed"
dbvar_H_RunsHitsRatio_Allowed_Sum = "H_RunsHitsRatio_Allowed_Sum"
dbvar_H_RunsHitsRatio_Allowed_5G = "H_RunsHitsRatio_Allowed_5G"
dbvar_H_RunsHitsRatio_Allowed_Sum_5G = "H_RunsHitsRatio_Allowed_Sum_5G"
dbvar_H_RunsHitsRatio_Allowed_20G = "H_RunsHitsRatio_Allowed_20G"
dbvar_H_RunsHitsRatio_Allowed_Sum_20G = "H_RunsHitsRatio_Allowed_Sum_20G"
dbvar_H_RunsHitsRatio_Allowed_YTD = "H_RunsHitsRatio_Allowed_YTD"
dbvar_H_FIP = "H_FIP"
dbvar_H_FIP_5G = "H_FIP_5G"
dbvar_H_FIP_YTD = "H_FIP_YTD"
dbvar_H_FIP_YTD_HV = "H_FIP_YTD_HV"
dbvar_H_K_Minus_BB_Pct = "H_K_Minus_BB_Pct"
dbvar_H_K_Minus_BB_Pct_5G = "H_K_Minus_BB_Pct_5G"
dbvar_H_K_Minus_BB_Pct_20G = "H_K_Minus_BB_Pct_20G"
dbvar_H_K_Minus_BB_Pct_YTD = "H_K_Minus_BB_Pct_YTD"
dbvar_H_HR_Per_9_Allowed = "H_HR_Per_9_Allowed"
dbvar_H_HR_Per_9_Allowed_5G = "H_HR_Per_9_Allowed_5G"
dbvar_H_HR_Per_9_Allowed_20G = "H_HR_Per_9_Allowed_20G"
dbvar_H_HR_Per_9_Allowed_YTD = "H_HR_Per_9_Allowed_YTD"
dbvar_H_K_Per_9 = "H_K_Per_9"
dbvar_H_K_Per_9_5G = "H_K_Per_9_5G"
dbvar_H_K_Per_9_20G = "H_K_Per_9_20G"
dbvar_H_K_Per_9_YTD = "H_K_Per_9_YTD"
dbvar_H_WalksAllowed_Sum = "H_WalksAllowed_Sum"
dbvar_H_WalksAllowed = "H_WalksAllowed"
dbvar_H_WalksAllowed_Sum_5G = "H_WalksAllowed_Sum_5G"
dbvar_H_WalksAllowed_5G = "H_WalksAllowed_5G"
dbvar_H_WalksAllowed_Sum_20G = "H_WalksAllowed_Sum_20G"
dbvar_H_WalksAllowed_20G = "H_WalksAllowed_20G"
dbvar_H_WalksAllowed_YTD = "H_WalksAllowed_YTD"
dbvar_H_WalksAllowed_YTD_HV = "H_WalksAllowed_YTD_HV"
dbvar_H_WalksGained_Sum = "H_WalksGained_Sum"
dbvar_H_WalksGained = "H_WalksGained"
dbvar_H_WalksGained_5G = "H_WalksGained_5G"
dbvar_H_WalksGained_20G = "H_WalksGained_20G"
dbvar_H_WalksGained_YTD = "H_WalksGained_YTD"
dbvar_H_WalksGained_YTD_HV = "H_WalksGained_YTD_HV"
dbvar_H_HomeRuns_Sum = "H_HomeRuns_Sum"
dbvar_H_HomeRuns = "H_HomeRuns"
dbvar_H_HomeRuns_5G = "H_HomeRuns_5G"
dbvar_H_HomeRuns_Sum_5G = "H_HomeRuns_Sum_5G"
dbvar_H_HomeRuns_20G = "H_HomeRuns_20G"
dbvar_H_HomeRuns_Sum_20G = "H_HomeRuns_Sum_20G"
dbvar_H_HomeRuns_YTD = "H_HomeRuns_YTD"
dbvar_H_HomeRuns_YTD_HV = "H_HomeRuns_YTD_HV"
dbvar_H_HomeRuns_Allowed_Sum = "H_HomeRuns_Allowed_Sum"
dbvar_H_HomeRuns_Allowed = "H_HomeRuns_Allowed"
dbvar_H_HomeRuns_Allowed_5G = "H_HomeRuns_Allowed_5G"
dbvar_H_HomeRuns_Allowed_20G = "H_HomeRuns_Allowed_20G"
dbvar_H_HomeRuns_Allowed_YTD = "H_HomeRuns_Allowed_YTD"
dbvar_H_HomeRuns_Allowed_YTD_HV = "H_HomeRuns_Allowed_YTD_HV"
dbvar_H_5thInnScore = "H_5thInnScore"
dbvar_H_Duration = "H_Duration"
dbvar_H_OverTime = "H_OverTime"
dbvar_H_NP_Sum = "H_NP_Sum"
dbvar_H_NP = "H_NP"
dbvar_H_NP_5G = "H_NP_5G"
dbvar_H_NP_YTD = "H_NP_YTD"
dbvar_H_NP_YTD_HV = "H_NP_YTD_HV"
dbvar_H_Strikes_Sum = "H_Strikes_Sum"
dbvar_H_StrikeAccuracy_Sum = "H_StrikeAccuracy_Sum"
dbvar_H_Strikes = "H_Strikes"
dbvar_H_StrikeAccuracy = "H_StrikeAccuracy"
dbvar_H_Strikes_5G = "H_Strikes_5G"
dbvar_H_StrikeAccuracy_5G = "H_StrikeAccuracy_5G"
dbvar_H_Strikes_YTD = "H_Strikes_YTD"
dbvar_H_StrikeAccuracy_YTD = "H_StrikeAccuracy_YTD"
dbvar_H_Strikes_YTD_HV = "H_Strikes_YTD_HV"
dbvar_H_StrikeAccuracy_YTD_HV = "H_StrikeAccuracy_YTD_HV"
dbvar_H_MenOnBase = "H_MenOnBase"
dbvar_H_MenOnBase_Strength = "H_MenOnBase_Strength"
dbvar_H_MenOnBase_Efficiency = "H_MenOnBase_Efficiency"
dbvar_H_MenOnBase_5G = "H_MenOnBase_5G"
dbvar_H_MenOnBase_Strength_5G = "H_MenOnBase_Strength_5G"
dbvar_H_MenOnBase_Efficiency_5G = "H_MenOnBase_Efficiency_5G"
dbvar_H_MenOnBase_20G = "H_MenOnBase_20G"
dbvar_H_MenOnBase_Strength_20G = "H_MenOnBase_Strength_20G"
dbvar_H_MenOnBase_Efficiency_20G = "H_MenOnBase_Efficiency_20G"
dbvar_H_MenOnBase_YTD = "H_MenOnBase_YTD"
dbvar_H_MenOnBase_Strength_YTD = "H_MenOnBase_Strength_YTD"
dbvar_H_MenOnBase_Efficiency_YTD = "H_MenOnBase_Efficiency_YTD"
dbvar_H_MenOnBase_Allowed = "H_MenOnBase_Allowed"
dbvar_H_MenOnBase_Allowed_Efficiency = "H_MenOnBase_Allowed_Efficiency"
dbvar_H_MenOnBase_Allowed_5G = "H_MenOnBase_Allowed_5G"
dbvar_H_MenOnBase_Allowed_Efficiency_5G = "H_MenOnBase_Allowed_Efficiency_5G"
dbvar_H_MenOnBase_Allowed_20G = "H_MenOnBase_Allowed_20G"
dbvar_H_MenOnBase_Allowed_Efficiency_20G = "H_MenOnBase_Allowed_Efficiency_20G"
dbvar_H_MenOnBase_Allowed_YTD = "H_MenOnBase_Allowed_YTD"
dbvar_H_MenOnBase_Allowed_Efficiency_YTD = "H_MenOnBase_Allowed_Efficiency_YTD"
dbvar_H_LeftOnBase_Sum = "H_LeftOnBase_Sum"
dbvar_H_LeftOnBase = "H_LeftOnBase"
dbvar_H_2BRuns_Sum = "H_2BRuns_Sum"
dbvar_H_2BRuns = "H_2BRuns"
dbvar_H_2BRuns_Sum_5G = "H_2BRuns_Sum_5G"
dbvar_H_2BRuns_5G = "H_2BRuns_5G"
dbvar_H_2BRuns_Sum_20G = "H_2BRuns_Sum_20G"
dbvar_H_2BRuns_20G = "H_2BRuns_20G"
dbvar_H_2BRuns_YTD = "H_2BRuns_YTD"
dbvar_H_2BRuns_Allowed = "H_2BRuns_Allowed"
dbvar_H_2BRuns_Allowed_5G = "H_2BRuns_Allowed_5G"
dbvar_H_2BRuns_Allowed_20G = "H_2BRuns_Allowed_20G"
dbvar_H_2BRuns_Allowed_YTD = "H_2BRuns_Allowed_YTD"
dbvar_H_2BRuns_Strength = "H_2BRuns_Strength"
dbvar_H_2BRuns_Strength_5G = "H_2BRuns_Strength_5G"
dbvar_H_2BRuns_Strength_20G = "H_2BRuns_Strength_20G"
dbvar_H_2BRuns_Strength_YTD = "H_2BRuns_Strength_YTD"
dbvar_H_3BRuns_Sum = "H_3BRuns_Sum"
dbvar_H_3BRuns = "H_3BRuns"
dbvar_H_3BRuns_5G = "H_3BRuns_5G"
dbvar_H_3BRuns_20G = "H_3BRuns_20G"
dbvar_H_3BRuns_YTD = "H_3BRuns_YTD"
dbvar_H_3BRuns_Allowed = "H_3BRuns_Allowed"
dbvar_H_3BRuns_Allowed_5G = "H_3BRuns_Allowed_5G"
dbvar_H_3BRuns_Allowed_20G = "H_3BRuns_Allowed_20G"
dbvar_H_3BRuns_Allowed_YTD = "H_3BRuns_Allowed_YTD"
dbvar_H_3BRuns_Strength = "H_3BRuns_Strength"
dbvar_H_3BRuns_Strength_5G = "H_3BRuns_Strength_5G"
dbvar_H_3BRuns_Strength_20G = "H_3BRuns_Strength_20G"
dbvar_H_3BRuns_Strength_YTD = "H_3BRuns_Strength_YTD"
dbvar_H_ErrorMade_Sum = "H_ErrorMade_Sum"
dbvar_H_ErrorMade = "H_ErrorMade"
dbvar_H_ErrorMade_Sum_5G = "H_ErrorMade_Sum_5G"
dbvar_H_ErrorMade_5G = "H_ErrorMade_5G"
dbvar_H_ErrorMade_Sum_20G = "H_ErrorMade_Sum_20G"
dbvar_H_ErrorMade_20G = "H_ErrorMade_20G"
dbvar_H_ErrorMade_YTD = "H_ErrorMade_YTD"
dbvar_H_ErrorMade_YTD_HV = "H_ErrorMade_YTD_HV"
dbvar_H_ErrorForced_Sum = "H_ErrorForced_Sum"
dbvar_H_ErrorForced_Sum_5G = "H_ErrorForced_Sum_5G"
dbvar_H_ErrorForced_Sum_20G = "H_ErrorForced_Sum_20G"
dbvar_H_ErrorForced = "H_ErrorForced"
dbvar_H_ErrorForced_5G = "H_ErrorForced_5G"
dbvar_H_ErrorForced_20G = "H_ErrorForced_20G"
dbvar_H_ErrorForced_YTD = "H_ErrorForced_YTD"
dbvar_H_HitsByPitch_Sum = "H_HitsByPitch_Sum"
dbvar_H_HitsByPitch = "H_HitsByPitch"
dbvar_H_HitsByPitch_Sum_5G = "H_HitsByPitch_Sum_5G"
dbvar_H_HitsByPitch_5G = "H_HitsByPitch_5G"
dbvar_H_HitsByPitch_Sum_20G = "H_HitsByPitch_Sum_20G"
dbvar_H_HitsByPitch_20G = "H_HitsByPitch_20G"
dbvar_H_HitsByPitch_YTD = "H_HitsByPitch_YTD"
dbvar_H_HitsByPitch_Allowed = "H_HitsByPitch_Allowed"
dbvar_H_HitsByPitch_Allowed_5G = "H_HitsByPitch_Allowed_5G"
dbvar_H_HitsByPitch_Allowed_20G = "H_HitsByPitch_Allowed_20G"
dbvar_H_HitsByPitch_Allowed_YTD = "H_HitsByPitch_Allowed_YTD"
dbvar_H_HitsByPitch_Allowed_YTD_HV = "H_HitsByPitch_Allowed_YTD_HV"
dbvar_H_DoublePlays_Gained_Sum = "H_DoublePlays_Gained_Sum"
dbvar_H_DoublePlays_Gained = "H_DoublePlays_Gained"
dbvar_H_DoublePlays_Gained_Sum_5G = "H_DoublePlays_Gained_Sum_5G"
dbvar_H_DoublePlays_Gained_5G = "H_DoublePlays_Gained_5G"
dbvar_H_DoublePlays_Gained_Sum_20G = "H_DoublePlays_Gained_Sum_20G"
dbvar_H_DoublePlays_Gained_20G = "H_DoublePlays_Gained_20G"
dbvar_H_DoublePlays_Gained_YTD = "H_DoublePlays_Gained_YTD"
dbvar_H_DoublePlays_Gained_YTD_HV = "H_DoublePlays_Gained_YTD_HV"
dbvar_H_DoublePlays_Allowed = "H_DoublePlays_Allowed"
dbvar_H_DoublePlays_Allowed_5G = "H_DoublePlays_Allowed_5G"
dbvar_H_DoublePlays_Allowed_20G = "H_DoublePlays_Allowed_20G"
dbvar_H_DoublePlays_Allowed_YTD = "H_DoublePlays_Allowed_YTD"
dbvar_H_DoublePlays_Allowed_YTD_HV = "H_DoublePlays_Allowed_YTD_HV"
dbvar_H_ReliefPitchers = "H_ReliefPitchers"
dbvar_H_TotalBases_Sum = "H_TotalBases_Sum"
dbvar_H_TotalBases = "H_TotalBases"
dbvar_H_TotalBases_5G = "H_TotalBases_5G"
dbvar_H_TotalBases_20G = "H_TotalBases_20G"
dbvar_H_TotalBases_YTD = "H_TotalBases_YTD"
dbvar_H_MenOnBaseTBRatio = "H_MenOnBaseTBRatio"
dbvar_H_MenOnBaseTBRatio_5G = "H_MenOnBaseTBRatio_5G"
dbvar_H_WalkStrikeoutRatio_Sum = "H_WalkStrikeoutRatio_Sum"
dbvar_H_WalkStrikeoutRatio = "H_WalkStrikeoutRatio"
dbvar_H_PowerHits_Sum = "H_PowerHits_Sum"
dbvar_H_PowerHits = "H_PowerHits"
dbvar_H_PowerHits_5G = "H_PowerHits_5G"
dbvar_H_Innings_OutPitched_Sum = "H_Innings_OutPitched_Sum"
dbvar_H_Innings_OutPitched = "H_Innings_OutPitched"
dbvar_H_Innings_OutPitched_Sum_5G = "H_Innings_OutPitched_Sum_5G"
dbvar_H_Innings_OutPitched_5G = "H_Innings_OutPitched_5G"
dbvar_H_Innings_OutPitched_YTD = "H_Innings_OutPitched_YTD"
dbvar_H_SP_HitsAllowed_Sum = "H_SP_HitsAllowed_Sum"
dbvar_H_SP_HitsAllowed = "H_SP_HitsAllowed"
dbvar_H_SP_HitsAllowed_5G = "H_SP_HitsAllowed_5G"
dbvar_H_SP_HitsAllowed_YTD = "H_SP_HitsAllowed_YTD"
dbvar_H_EarnedRuns_Sum = "H_EarnedRuns_Sum"
dbvar_H_EarnedRunAvg_Sum = "H_EarnedRunAvg_Sum"
dbvar_H_EarnedRuns = "H_EarnedRuns"
dbvar_H_EarnedRunAvg = "H_EarnedRunAvg"
dbvar_H_EarnedRuns_Sum_5G = "H_EarnedRuns_Sum_5G"
dbvar_H_EarnedRunAvg_Sum_5G = "H_EarnedRunAvg_Sum_5G"
dbvar_H_EarnedRuns_5G = "H_EarnedRuns_5G"
dbvar_H_EarnedRunAvg_5G = "H_EarnedRunAvg_5G"
dbvar_H_EarnedRuns_YTD = "H_EarnedRuns_YTD"
dbvar_H_EarnedRunAvg_YTD = "H_EarnedRunAvg_YTD"
dbvar_H_HitsAllowedPer9Innings_Sum = "H_HitsAllowedPer9Innings_Sum"
dbvar_H_HitsAllowedPer9Innings = "H_HitsAllowedPer9Innings"
dbvar_H_HitsAllowedPer9Innings_5G = "H_HitsAllowedPer9Innings_5G"
dbvar_H_WalksHitsAllowedPerInning = "H_WalksHitsAllowedPerInning"
dbvar_H_WalksHitsAllowedPerInning_5G = "H_WalksHitsAllowedPerInning_5G"
dbvar_H_WalksHitsAllowedPerInning_YTD = "H_WalksHitsAllowedPerInning_YTD"
dbvar_G_H_StartingPitcher_Id = "G_H_StartingPitcher_Id"
dbvar_H_StartingPitcher_DaysRest = "H_StartingPitcher_DaysRest"
dbvar_H_StartingPitcher_Score_All = "H_StartingPitcher_Score_All"
dbvar_H_StartingPitcher_Strikeouts_All = "H_StartingPitcher_Strikeouts_All"
dbvar_H_StartingPitcher_StrikeoutAccuracy_All = "H_StartingPitcher_StrikeoutAccuracy_All"
dbvar_H_StartingPitcher_BaseOnBalls_All = "H_StartingPitcher_BaseOnBalls_All"
dbvar_H_StartingPitcher_Hits_All = "H_StartingPitcher_Hits_All"
dbvar_H_StartingPitcher_NP_All = "H_StartingPitcher_NP_All"
dbvar_H_StartingPitcher_InningsPitched_All = "H_StartingPitcher_InningsPitched_All"
dbvar_H_StartingPitcher_Strikes_All = "H_StartingPitcher_Strikes_All"
dbvar_H_StartingPitcher_StrikeAccuracy_All = "H_StartingPitcher_StrikeAccuracy_All"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All = "H_StartingPitcher_WalkHitsAllowedPerInning_All"
dbvar_H_StartingPitcher_Score_YTD = "H_StartingPitcher_Score_YTD"
dbvar_H_StartingPitcher_Strikeouts_YTD = "H_StartingPitcher_Strikeouts_YTD"
dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD = "H_StartingPitcher_StrikeoutAccuracy_YTD"
dbvar_H_StartingPitcher_BaseOnBalls_YTD = "H_StartingPitcher_BaseOnBalls_YTD"
dbvar_H_StartingPitcher_Hits_YTD = "H_StartingPitcher_Hits_YTD"
dbvar_H_StartingPitcher_NP_YTD = "H_StartingPitcher_NP_YTD"
dbvar_H_StartingPitcher_InningsPitched_YTD = "H_StartingPitcher_InningsPitched_YTD"
dbvar_H_StartingPitcher_Strikes_YTD = "H_StartingPitcher_Strikes_YTD"
dbvar_H_StartingPitcher_StrikeAccuracy_YTD = "H_StartingPitcher_StrikeAccuracy_YTD"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD = "H_StartingPitcher_WalkHitsAllowedPerInning_YTD"
dbvar_H_StartingPitcher_ScoreImpact_YTD = "H_StartingPitcher_ScoreImpact_YTD"
dbvar_H_StartingPitcher_StrikeoutsImpact_YTD = "H_StartingPitcher_StrikeoutsImpact_YTD"
dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD = "H_StartingPitcher_BaseOnBallsImpact_YTD"
dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD = "H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD"
dbvar_H_StartingPitcher_HitsImpact_YTD = "H_StartingPitcher_HitsImpact_YTD"
dbvar_H_StartingPitcher_NPImpact_YTD = "H_StartingPitcher_NPImpact_YTD"
dbvar_H_StartingPitcher_InningsPitchedImpact_YTD = "H_StartingPitcher_InningsPitchedImpact_YTD"
dbvar_H_StartingPitcher_StrikeImpact_YTD = "H_StartingPitcher_StrikeImpact_YTD"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD = "H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD"
dbvar_H_StartingPitcher_Score_5G = "H_StartingPitcher_Score_5G"
dbvar_H_StartingPitcher_Strikeouts_5G = "H_StartingPitcher_Strikeouts_5G"
dbvar_H_StartingPitcher_StrikeoutAccuracy_5G = "H_StartingPitcher_StrikeoutAccuracy_5G"
dbvar_H_StartingPitcher_BaseOnBalls_5G = "H_StartingPitcher_BaseOnBalls_5G"
dbvar_H_StartingPitcher_Hits_5G = "H_StartingPitcher_Hits_5G"
dbvar_H_StartingPitcher_NP_5G = "H_StartingPitcher_NP_5G"
dbvar_H_StartingPitcher_InningsPitched_5G = "H_StartingPitcher_InningsPitched_5G"
dbvar_H_StartingPitcher_Strikes_5G = "H_StartingPitcher_Strikes_5G"
dbvar_H_StartingPitcher_StrikeAccuracy_5G = "H_StartingPitcher_StrikeAccuracy_5G"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G = "H_StartingPitcher_WalkHitsAllowedPerInning_5G"
dbvar_H_StartingPitcher_ScoreImpact_5G = "H_StartingPitcher_ScoreImpact_5G"
dbvar_H_StartingPitcher_StrikeoutsImpact_5G = "H_StartingPitcher_StrikeoutsImpact_5G"
dbvar_H_StartingPitcher_BaseOnBallsImpact_5G = "H_StartingPitcher_BaseOnBallsImpact_5G"
dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G = "H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G"
dbvar_H_StartingPitcher_HitsImpact_5G = "H_StartingPitcher_HitsImpact_5G"
dbvar_H_StartingPitcher_NPImpact_5G = "H_StartingPitcher_NPImpact_5G"
dbvar_H_StartingPitcher_InningsPitchedImpact_5G = "H_StartingPitcher_InningsPitchedImpact_5G"
dbvar_H_StartingPitcher_StrikeImpact_5G = "H_StartingPitcher_StrikeImpact_5G"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G = "H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G"
dbvar_H_StartingPitcher_Score_Ratio = "H_StartingPitcher_Score_Ratio"
dbvar_H_StartingPitcher_Strikeouts_Ratio = "H_StartingPitcher_Strikeouts_Ratio"
dbvar_H_StartingPitcher_BaseOnBalls_Ratio = "H_StartingPitcher_BaseOnBalls_Ratio"
dbvar_H_StartingPitcher_Hits_Ratio = "H_StartingPitcher_Hits_Ratio"
dbvar_H_StartingPitcher_NP_Ratio = "H_StartingPitcher_NP_Ratio"
dbvar_H_StartingPitcher_InningsPitched_Ratio = "H_StartingPitcher_InningsPitched_Ratio"
dbvar_H_StartingPitcher_Strikes_Ratio = "H_StartingPitcher_Strikes_Ratio"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio = "H_StartingPitcher_WalkHitsAllowedPerInning_Ratio"
dbvar_H_StartingPitcher_Score_Ratio_5G = "H_StartingPitcher_Score_Ratio_5G"
dbvar_H_StartingPitcher_Strikeouts_Ratio_5G = "H_StartingPitcher_Strikeouts_Ratio_5G"
dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G = "H_StartingPitcher_BaseOnBalls_Ratio_5G"
dbvar_H_StartingPitcher_Hits_Ratio_5G = "H_StartingPitcher_Hits_Ratio_5G"
dbvar_H_StartingPitcher_NP_Ratio_5G = "H_StartingPitcher_NP_Ratio_5G"
dbvar_H_StartingPitcher_InningsPitched_Ratio_5G = "H_StartingPitcher_InningsPitched_Ratio_5G"
dbvar_H_StartingPitcher_Strikes_Ratio_5G = "H_StartingPitcher_Strikes_Ratio_5G"
dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G = "H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G"
dbvar_H_BallpenOuts = "H_BallpenOuts"
dbvar_H_BallpenOuts_5G = "H_BallpenOuts_5G"
dbvar_H_BallpenOuts_YTD = "H_BallpenOuts_YTD"
dbvar_H_BallpenERA_Approx = "H_BallpenERA_Approx"
dbvar_H_BallpenERA_Approx_5G = "H_BallpenERA_Approx_5G"
dbvar_H_BallpenERA_Approx_YTD = "H_BallpenERA_Approx_YTD"
dbvar_G_V_Id = "G_V_Id"
dbvar_G_V_ParkImpactFactor = "G_V_ParkImpactFactor"
dbvar_G_Bookie_V_MoneyLine = "G_Bookie_V_MoneyLine"
dbvar_G_Bookie_V_Probability = "G_Bookie_V_Probability"
dbvar_G_V_Opening_MoneyLine = "G_V_Opening_MoneyLine"
dbvar_G_V_OpeningProbabilityLine = "G_V_OpeningProbabilityLine"
dbvar_G_V_Closing_MoneyLine = "G_V_Closing_MoneyLine"
dbvar_G_V_ClosingProbabilityLine = "G_V_ClosingProbabilityLine"
dbvar_G_V_CLL_OPL_Prob_Diff = "G_V_CLL_OPL_Prob_Diff"
dbvar_G_V_League = "G_V_League"
dbvar_G_V_Division = "G_V_Division"
dbvar_G_V_LeagueDiv = "G_V_LeagueDiv"
dbvar_G_V_Same_LeagueDiv = "G_V_Same_LeagueDiv"
dbvar_G_V_Same_Div = "G_V_Same_Div"
dbvar_G_V_DaysRest = "G_V_DaysRest"
dbvar_G_V_DistanceTravelled = "G_V_DistanceTravelled"
dbvar_G_V_ContiguousGamesV = "G_V_ContiguousGamesV"
dbvar_G_V_ContiguousGamesH = "G_V_ContiguousGamesH"
dbvar_G_V_TotalDistanceTravelled_3G = "G_V_TotalDistanceTravelled_3G"
dbvar_G_V_Prev1_Id = "G_V_Prev1_Id"
dbvar_G_V_Prev1_LeagueDiv = "G_V_Prev1_LeagueDiv"
dbvar_G_V_Prev1_SameLeagueDiv = "G_V_Prev1_SameLeagueDiv"
dbvar_G_V_Prev1_SameDiv = "G_V_Prev1_SameDiv"
dbvar_G_V_Prev1_DistanceTravelled = "G_V_Prev1_DistanceTravelled"
dbvar_G_V_Prev1Home = "G_V_Prev1Home"
dbvar_G_V_Prev1Strength = "G_V_Prev1Strength"
dbvar_G_V_Prev1StrengthRatio = "G_V_Prev1StrengthRatio"
dbvar_G_V_Prev1Win = "G_V_Prev1Win"
dbvar_G_V_Prev1CLL = "G_V_Prev1CLL"
dbvar_G_V_Prev1_Summary = "G_V_Prev1_Summary"
dbvar_G_V_Prev2_Id = "G_V_Prev2_Id"
dbvar_G_V_Prev2_LeagueDiv = "G_V_Prev2_LeagueDiv"
dbvar_G_V_Prev2_SameLeagueDiv = "G_V_Prev2_SameLeagueDiv"
dbvar_G_V_Prev2_SameDiv = "G_V_Prev2_SameDiv"
dbvar_G_V_Prev2_DistanceTravelled = "G_V_Prev2_DistanceTravelled"
dbvar_G_V_Prev2Home = "G_V_Prev2Home"
dbvar_G_V_Prev2Strength = "G_V_Prev2Strength"
dbvar_G_V_Prev2StrengthRatio = "G_V_Prev2StrengthRatio"
dbvar_G_V_Prev2Win  = "G_V_Prev2Win"
dbvar_G_V_Prev2CLL = "G_V_Prev2CLL"
dbvar_G_V_Prev2_Summary = "G_V_Prev2_Summary"
dbvar_G_V_Prev3_Id = "G_V_Prev3_Id"
dbvar_G_V_Prev3_LeagueDiv = "G_V_Prev3_LeagueDiv"
dbvar_G_V_Prev3_SameLeagueDiv = "G_V_Prev3_SameLeagueDiv"
dbvar_G_V_Prev3_SameDiv = "G_V_Prev3_SameDiv"
dbvar_G_V_Prev3_DistanceTravelled = "G_V_Prev3_DistanceTravelled"
dbvar_G_V_Prev3Home = "G_V_Prev3Home"
dbvar_G_V_Prev3Strength = "G_V_Prev3Strength"
dbvar_G_V_Prev3StrengthRatio = "G_V_Prev3StrengthRatio"
dbvar_G_V_Prev3Win  = "G_V_Prev3Win"
dbvar_G_V_Prev3CLL = "G_V_Prev3CLL"
dbvar_G_V_Prev3_Summary = "G_V_Prev3_Summary"
dbvar_G_V_Lookback_Strength = "G_V_Lookback_Strength"
dbvar_G_V_Next1_Id = "G_V_Next1_Id"
dbvar_G_V_Next1_LeagueDiv = "G_V_Next1_LeagueDiv"
dbvar_G_V_Next1_SameLeagueDiv = "G_V_Next1_SameLeagueDiv"
dbvar_G_V_Next1_SameDiv = "G_V_Next1_SameDiv"
dbvar_G_V_Next1_DistanceTravelled = "G_V_Next1_DistanceTravelled"
dbvar_G_V_Next1Home = "G_V_Next1Home"
dbvar_G_V_Next1Strength = "G_V_Next1Strength"
dbvar_G_V_Next1StrengthRatio = "G_V_Next1StrengthRatio"
dbvar_G_V_Next1_Summary = "G_V_Next1_Summary"
dbvar_G_V_Next2_Id = "G_V_Next2_Id"
dbvar_G_V_Next2_LeagueDiv = "G_V_Next2_LeagueDiv"
dbvar_G_V_Next2_SameLeagueDiv = "G_V_Next2_SameLeagueDiv"
dbvar_G_V_Next2_SameDiv = "G_V_Next2_SameDiv"
dbvar_G_V_Next2_DistanceTravelled = "G_V_Next2_DistanceTravelled"
dbvar_G_V_Next2Home = "G_V_Next2Home"
dbvar_G_V_Next2Strength = "G_V_Next2Strength"
dbvar_G_V_Next2StrengthRatio = "G_V_Next2StrengthRatio"
dbvar_G_V_Next2_Summary = "G_V_Next2_Summary"
dbvar_G_V_Next3_Id = "G_V_Next3_Id"
dbvar_G_V_Next3_LeagueDiv = "G_V_Next3_LeagueDiv"
dbvar_G_V_Next3_SameLeagueDiv = "G_V_Next3_SameLeagueDiv"
dbvar_G_V_Next3_SameDiv = "G_V_Next3_SameDiv"
dbvar_G_V_Next3_DistanceTravelled = "G_V_Next3_DistanceTravelled"
dbvar_G_V_Next3Home = "G_V_Next3Home"
dbvar_G_V_Next3Strength = "G_V_Next3Strength"
dbvar_G_V_Next3StrengthRatio = "G_V_Next3StrengthRatio"
dbvar_G_V_Next3_Summary = "G_V_Next3_Summary"
dbvar_G_V_Lookahead_Strength = "G_V_Lookahead_Strength"
dbvar_V_ClosingProbabilityLine_HV = "V_ClosingProbabilityLine_HV"
dbvar_V_ClosingProbabilityLine_YTD_HV = "V_ClosingProbabilityLine_YTD_HV"
dbvar_V_Runs_Gained = "V_Runs_Gained"
dbvar_V_Runs_Allowed = "V_Runs_Allowed"
dbvar_V_Run_Strength = "V_Run_Strength"
dbvar_V_Run_Efficiency = "V_Run_Efficiency"
dbvar_V_Run_Pythag = "V_Run_Pythag"
dbvar_V_Runs_Gained_5G = "V_Runs_Gained_5G"
dbvar_V_Runs_Allowed_5G = "V_Runs_Allowed_5G"
dbvar_V_Run_Strength_5G = "V_Run_Strength_5G"
dbvar_V_Run_Efficiency_5G = "V_Run_Efficiency_5G"
dbvar_V_Run_Pythag_5G = "V_Run_Pythag_5G"
dbvar_V_Runs_Gained_20G = "V_Runs_Gained_20G"
dbvar_V_Runs_Allowed_20G = "V_Runs_Allowed_20G"
dbvar_V_Run_Strength_20G = "V_Run_Strength_20G"
dbvar_V_Run_Efficiency_20G = "V_Run_Efficiency_20G"
dbvar_V_Run_Pythag_20G = "V_Run_Pythag_20G"
dbvar_V_Runs_Gained_Sum = "V_Runs_Gained_Sum"
dbvar_V_Runs_Allowed_Sum = "V_Runs_Allowed_Sum"
dbvar_V_Run_Strength_Sum = "V_Run_Strength_Sum"
dbvar_V_Run_Efficiency_Sum = "V_Run_Efficiency_Sum"
dbvar_V_Run_Pythag_Sum = "V_Run_Pythag_Sum"
dbvar_V_Runs_Gained_Sum_5G = "V_Runs_Gained_Sum_5G"
dbvar_V_Runs_Allowed_Sum_5G = "V_Runs_Allowed_Sum_5G"
dbvar_V_Run_Strength_Sum_5G = "V_Run_Strength_Sum_5G"
dbvar_V_Run_Efficiency_Sum_5G = "V_Run_Efficiency_Sum_5G"
dbvar_V_Runs_Gained_Sum_20G = "V_Runs_Gained_Sum_20G"
dbvar_V_Runs_Allowed_Sum_20G = "V_Runs_Allowed_Sum_20G"
dbvar_V_Run_Strength_Sum_20G = "V_Run_Strength_Sum_20G"
dbvar_V_Run_Efficiency_Sum_20G = "V_Run_Efficiency_Sum_20G"
dbvar_V_Runs_Gained_Sum_HV = "V_Runs_Gained_Sum_HV"
dbvar_V_Runs_Allowed_Sum_HV = "V_Runs_Allowed_Sum_HV"
dbvar_V_Run_Strength_Sum_HV = "V_Run_Strength_Sum_HV"
dbvar_V_Runs_Gained_HV = "V_Runs_Gained_HV"
dbvar_V_Runs_Allowed_HV = "V_Runs_Allowed_HV"
dbvar_V_Run_Strength_HV = "V_Run_Strength_HV"
dbvar_V_Runs_Gained_YTD = "V_Runs_Gained_YTD"
dbvar_V_Runs_Allowed_YTD = "V_Runs_Allowed_YTD"
dbvar_V_Run_Strength_YTD = "V_Run_Strength_YTD"
dbvar_V_Run_Pythag_YTD = "V_Run_Pythag_YTD"
dbvar_V_Runs_Gained_YTD_HV = "V_Runs_Gained_YTD_HV"
dbvar_V_Runs_Allowed_YTD_HV = "V_Runs_Allowed_YTD_HV"
dbvar_V_Run_Strength_YTD_HV = "V_Run_Strength_YTD_HV"
dbvar_V_Runs_5InningsGained = "V_Runs_5InningsGained"
dbvar_V_Runs_5InningsAllowed = "V_Runs_5InningsAllowed"
dbvar_V_Run_5InningsStrength = "V_Run_5InningsStrength"
dbvar_V_Run_5InningsEfficiency = "V_Run_5InningsEfficiency"
dbvar_V_Runs_5InningsGained_Sum = "V_Runs_5InningsGained_Sum"
dbvar_V_Runs_5InningsAllowed_Sum = "V_Runs_5InningsAllowed_Sum"
dbvar_V_Run_5InningsStrength_Sum = "V_Run_5InningsStrength_Sum"
dbvar_V_Run_5InningsEfficiency_Sum = "V_Run_5InningsEfficiency_Sum"
dbvar_V_Runs_5InningsGained_5G = "V_Runs_5InningsGained_5G"
dbvar_V_Runs_5InningsAllowed_5G = "V_Runs_5InningsAllowed_5G"
dbvar_V_Run_5InningsStrength_5G = "V_Run_5InningsStrength_5G"
dbvar_V_Run_5InningsEfficiency_5G = "V_Run_5InningsEfficiency_5G"
dbvar_V_Runs_5InningsGained_Sum_5G = "V_Runs_5InningsGained_Sum_5G"
dbvar_V_Runs_5InningsAllowed_Sum_5G = "V_Runs_5InningsAllowed_Sum_5G"
dbvar_V_Run_5InningsStrength_Sum_5G = "V_Run_5InningsStrength_Sum_5G"
dbvar_V_Run_5InningsEfficiency_Sum_5G = "V_Run_5InningsEfficiency_Sum_5G"
dbvar_V_Runs_5InningsGained_20G = "V_Runs_5InningsGained_20G"
dbvar_V_Runs_5InningsAllowed_20G = "V_Runs_5InningsAllowed_20G"
dbvar_V_Run_5InningsStrength_20G = "V_Run_5InningsStrength_20G"
dbvar_V_Run_5InningsEfficiency_20G = "V_Run_5InningsEfficiency_20G"
dbvar_V_Runs_5InningsGained_Sum_20G = "V_Runs_5InningsGained_Sum_20G"
dbvar_V_Runs_5InningsAllowed_Sum_20G = "V_Runs_5InningsAllowed_Sum_20G"
dbvar_V_Run_5InningsStrength_Sum_20G = "V_Run_5InningsStrength_Sum_20G"
dbvar_V_Run_5InningsEfficiency_Sum_20G = "V_Run_5InningsEfficiency_Sum_20G"
dbvar_V_Runs_5InningsGained_Sum_HV = "V_Runs_5InningsGained_Sum_HV"
dbvar_V_Runs_5InningsAllowed_Sum_HV = "V_Runs_5InningsAllowed_Sum_HV"
dbvar_V_Run_5InningsStrength_Sum_HV = "V_Run_5InningsStrength_Sum_HV"
dbvar_V_Runs_5InningsGained_HV = "V_Runs_5InningsGained_HV"
dbvar_V_Runs_5InningsAllowed_HV = "V_Runs_5InningsAllowed_HV"
dbvar_V_Run_5InningsStrength_HV = "V_Run_5InningsStrength_HV"
dbvar_V_Runs_5InningsGained_YTD = "V_Runs_5InningsGained_YTD"
dbvar_V_Runs_5InningsAllowed_YTD = "V_Runs_5InningsAllowed_YTD"
dbvar_V_Run_5InningsStrength_YTD = "V_Run_5InningsStrength_YTD"
dbvar_V_Pythag_Luck_Factor = "V_Pythag_Luck_Factor"
dbvar_V_Pythag_Luck_Factor_5G = "V_Pythag_Luck_Factor_5G"
dbvar_V_Pythag_Luck_Factor_20G = "V_Pythag_Luck_Factor_20G"
dbvar_V_Pythag_Luck_Factor_YTD = "V_Pythag_Luck_Factor_YTD"
dbvar_V_Run_Differential_Per_Game = "V_Run_Differential_Per_Game"
dbvar_V_Run_Differential_Per_Game_5G = "V_Run_Differential_Per_Game_5G"
dbvar_V_Run_Differential_Per_Game_20G = "V_Run_Differential_Per_Game_20G"
dbvar_V_Run_Differential_Per_Game_YTD = "V_Run_Differential_Per_Game_YTD"
dbvar_V_Weighted_Offense_Index = "V_Weighted_Offense_Index"
dbvar_V_Weighted_Offense_Index_5G = "V_Weighted_Offense_Index_5G"
dbvar_V_Weighted_Offense_Index_20G = "V_Weighted_Offense_Index_20G"
dbvar_V_Weighted_Offense_Index_YTD = "V_Weighted_Offense_Index_YTD"
dbvar_V_At_Bat = "V_At_Bat"
dbvar_V_At_Bat_5G = "V_At_Bat_5G"
dbvar_V_At_Bat_20G = "V_At_Bat_20G"
dbvar_V_At_Bat_YTD = "V_At_Bat_YTD"
dbvar_V_At_Bat_HV = "V_At_Bat_HV"
dbvar_V_At_Bat_YTD_HV = "V_At_Bat_YTD_HV"
dbvar_V_OBP = "V_OBP"
dbvar_V_OBP_5G = "V_OBP_5G"
dbvar_V_OBP_20G = "V_OBP_20G"
dbvar_V_OBP_YTD = "V_OBP_YTD"
dbvar_V_SLG = "V_SLG"
dbvar_V_SLG_5G = "V_SLG_5G"
dbvar_V_SLG_20G = "V_SLG_20G"
dbvar_V_SLG_YTD = "V_SLG_YTD"
dbvar_V_wOBA = "V_wOBA"
dbvar_V_wOBA_5G = "V_wOBA_5G"
dbvar_V_wOBA_20G = "V_wOBA_20G"
dbvar_V_wOBA_YTD = "V_wOBA_YTD"
dbvar_V_OPS = "V_OPS"
dbvar_V_OPS_5G = "V_OPS_5G"
dbvar_V_OPS_20G = "V_OPS_20G"
dbvar_V_OPS_YTD = "V_OPS_YTD"
dbvar_V_Wins = "V_Wins"
dbvar_V_Losses = "V_Losses"
dbvar_V_WinLoss_Strength = "V_WinLoss_Strength"
dbvar_V_Wins_5G = "V_Wins_5G"
dbvar_V_Losses_5G = "V_Losses_5G"
dbvar_V_WinLoss_Strength_5G = "V_WinLoss_Strength_5G"
dbvar_V_Wins_20G = "V_Wins_20G"
dbvar_V_Losses_20G = "V_Losses_20G"
dbvar_V_WinLoss_Strength_20G = "V_WinLoss_Strength_20G"
dbvar_V_Wins_HV = "V_Wins_HV"
dbvar_V_Losses_HV = "V_Losses_HV"
dbvar_V_WinLoss_Strength_HV = "V_WinLoss_Strength_HV"
dbvar_V_Wins_YTD = "V_Wins_YTD"
dbvar_V_Losses_YTD = "V_Losses_YTD"
dbvar_V_WinLoss_Strength_YTD = "V_WinLoss_Strength_YTD"
dbvar_V_Wins_YTD_HV = "V_Wins_YTD_HV"
dbvar_V_Losses_YTD_HV = "V_Losses_YTD_HV"
dbvar_V_WinLoss_Strength_YTD_HV = "V_WinLoss_Strength_YTD_HV"
dbvar_V_OutsPitched_Sum = "V_OutsPitched_Sum"
dbvar_V_OutsPitched = "V_OutsPitched"
dbvar_V_OutsPitched_5G = "V_OutsPitched_5G"
dbvar_V_OutsPitched_20G = "V_OutsPitched_20G"
dbvar_V_OutsPitched_YTD = "V_OutsPitched_YTD"
dbvar_V_OutsPitched_YTD_HV = "V_OutsPitched_YTD_HV"
dbvar_V_StrikeoutsAllowed = "V_StrikeoutsAllowed"
dbvar_V_StrikeoutsGained = "V_StrikeoutsGained"
dbvar_V_StrikeoutAccuracy = "V_StrikeoutAccuracy"
dbvar_V_StrikeoutsAllowed_Sum = "V_StrikeoutsAllowed_Sum"
dbvar_V_StrikeoutsGained_Sum = "V_StrikeoutsGained_Sum"
dbvar_V_StrikeoutAccuracy_Sum = "V_StrikeoutAccuracy_Sum"
dbvar_V_StrikeoutsAllowed_5G = "V_StrikeoutsAllowed_5G"
dbvar_V_StrikeoutsGained_5G = "V_StrikeoutsGained_5G"
dbvar_V_StrikeoutsGained_20G = "V_StrikeoutsGained_20G"
dbvar_V_StrikeoutAccuracy_5G = "V_StrikeoutAccuracy_5G"
dbvar_V_StrikeoutsAllowed_YTD = "V_StrikeoutsAllowed_YTD"
dbvar_V_StrikeoutsGained_YTD = "V_StrikeoutsGained_YTD"
dbvar_V_StrikeoutAccuracy_YTD = "V_StrikeoutAccuracy_YTD"
dbvar_V_StrikeoutsAllowed_YTD_HV = "V_StrikeoutsAllowed_YTD_HV"
dbvar_V_StrikeoutsGained_YTD_HV = "V_StrikeoutsGained_YTD_HV"
dbvar_V_StrikeoutAccuracy_YTD_HV = "V_StrikeoutAccuracy_YTD_HV"
dbvar_V_Hits_Sum = "V_Hits_Sum"
dbvar_V_Hits = "V_Hits"
dbvar_V_Hits_Sum_5G = "V_Hits_Sum_5G"
dbvar_V_Hits_5G = "V_Hits_5G"
dbvar_V_Hits_Sum_20G = "V_Hits_Sum_20G"
dbvar_V_Hits_20G = "V_Hits_20G"
dbvar_V_Hits_YTD = "V_Hits_YTD"
dbvar_V_Hits_YTD_HV = "V_Hits_YTD_HV"
dbvar_V_HitsAllowed_Sum = "V_HitsAllowed_Sum"
dbvar_V_HitsAllowed_Sum_5G = "V_HitsAllowed_Sum_5G"
dbvar_V_HitsAllowed_Sum_20G = "V_HitsAllowed_Sum_20G"
dbvar_V_HitsAllowed = "V_HitsAllowed"
dbvar_V_HitsAllowed_5G = "V_HitsAllowed_5G"
dbvar_V_HitsAllowed_20G = "V_HitsAllowed_20G"
dbvar_V_HitsAllowed_YTD = "V_HitsAllowed_YTD"
dbvar_V_HitsAllowed_YTD_HV = "V_HitsAllowed_YTD_HV"
dbvar_V_RunsHitsRatio = "V_RunsHitsRatio"
dbvar_V_RunsHitsRatio_Sum = "V_RunsHitsRatio_Sum"
dbvar_V_RunsHitsRatio_5G = "V_RunsHitsRatio_5G"
dbvar_V_RunsHitsRatio_Sum_5G = "V_RunsHitsRatio_Sum_5G"
dbvar_V_RunsHitsRatio_20G = "V_RunsHitsRatio_20G"
dbvar_V_RunsHitsRatio_Sum_20G = "V_RunsHitsRatio_Sum_20G"
dbvar_V_RunsHitsRatio_YTD = "V_RunsHitsRatio_YTD"
dbvar_V_RunsHitsRatio_Allowed = "V_RunsHitsRatio_Allowed"
dbvar_V_RunsHitsRatio_Allowed_Sum = "V_RunsHitsRatio_Allowed_Sum"
dbvar_V_RunsHitsRatio_Allowed_5G = "V_RunsHitsRatio_Allowed_5G"
dbvar_V_RunsHitsRatio_Allowed_Sum_5G = "V_RunsHitsRatio_Allowed_Sum_5G"
dbvar_V_RunsHitsRatio_Allowed_20G = "V_RunsHitsRatio_Allowed_20G"
dbvar_V_RunsHitsRatio_Allowed_Sum_20G = "V_RunsHitsRatio_Allowed_Sum_20G"
dbvar_V_RunsHitsRatio_Allowed_YTD = "V_RunsHitsRatio_Allowed_YTD"
dbvar_V_FIP = "V_FIP"
dbvar_V_FIP_5G = "V_FIP_5G"
dbvar_V_FIP_YTD = "V_FIP_YTD"
dbvar_V_FIP_YTD_HV = "V_FIP_YTD_HV"
dbvar_V_K_Minus_BB_Pct = "V_K_Minus_BB_Pct"
dbvar_V_K_Minus_BB_Pct_5G = "V_K_Minus_BB_Pct_5G"
dbvar_V_K_Minus_BB_Pct_20G = "V_K_Minus_BB_Pct_20G"
dbvar_V_K_Minus_BB_Pct_YTD = "V_K_Minus_BB_Pct_YTD"
dbvar_V_HR_Per_9_Allowed = "V_HR_Per_9_Allowed"
dbvar_V_HR_Per_9_Allowed_5G = "V_HR_Per_9_Allowed_5G"
dbvar_V_HR_Per_9_Allowed_20G = "V_HR_Per_9_Allowed_20G"
dbvar_V_HR_Per_9_Allowed_YTD = "V_HR_Per_9_Allowed_YTD"
dbvar_V_K_Per_9 = "V_K_Per_9"
dbvar_V_K_Per_9_5G = "V_K_Per_9_5G"
dbvar_V_K_Per_9_20G = "V_K_Per_9_20G"
dbvar_V_K_Per_9_YTD = "V_K_Per_9_YTD"
dbvar_V_WalksAllowed_Sum = "V_WalksAllowed_Sum"
dbvar_V_WalksAllowed = "V_WalksAllowed"
dbvar_V_WalksAllowed_Sum_5G = "V_WalksAllowed_Sum_5G"
dbvar_V_WalksAllowed_5G = "V_WalksAllowed_5G"
dbvar_V_WalksAllowed_Sum_20G = "V_WalksAllowed_Sum_20G"
dbvar_V_WalksAllowed_20G = "V_WalksAllowed_20G"
dbvar_V_WalksAllowed_YTD = "V_WalksAllowed_YTD"
dbvar_V_WalksAllowed_YTD_HV = "V_WalksAllowed_YTD_HV"
dbvar_V_WalksGained_Sum = "V_WalksGained_Sum"
dbvar_V_WalksGained = "V_WalksGained"
dbvar_V_WalksGained_5G = "V_WalksGained_5G"
dbvar_V_WalksGained_20G = "V_WalksGained_20G"
dbvar_V_WalksGained_YTD = "V_WalksGained_YTD"
dbvar_V_WalksGained_YTD_HV = "V_WalksGained_YTD_HV"
dbvar_V_HomeRuns_Sum = "V_HomeRuns_Sum"
dbvar_V_HomeRuns = "V_HomeRuns"
dbvar_V_HomeRuns_5G = "V_HomeRuns_5G"
dbvar_V_HomeRuns_Sum_5G = "V_HomeRuns_Sum_5G"
dbvar_V_HomeRuns_20G = "V_HomeRuns_20G"
dbvar_V_HomeRuns_Sum_20G = "V_HomeRuns_Sum_20G"
dbvar_V_HomeRuns_YTD = "V_HomeRuns_YTD"
dbvar_V_HomeRuns_YTD_HV = "V_HomeRuns_YTD_HV"
dbvar_V_HomeRuns_Allowed_Sum = "V_HomeRuns_Allowed_Sum"
dbvar_V_HomeRuns_Allowed = "V_HomeRuns_Allowed"
dbvar_V_HomeRuns_Allowed_5G = "V_HomeRuns_Allowed_5G"
dbvar_V_HomeRuns_Allowed_20G = "V_HomeRuns_Allowed_20G"
dbvar_V_HomeRuns_Allowed_YTD = "V_HomeRuns_Allowed_YTD"
dbvar_V_HomeRuns_Allowed_YTD_HV = "V_HomeRuns_Allowed_YTD_HV"
dbvar_V_5thInnScore = "V_5thInnScore"
dbvar_V_Duration = "V_Duration"
dbvar_V_OverTime = "V_OverTime"
dbvar_V_NP_Sum = "V_NP_Sum"
dbvar_V_NP = "V_NP"
dbvar_V_NP_5G = "V_NP_5G"
dbvar_V_NP_YTD = "V_NP_YTD"
dbvar_V_NP_YTD_HV = "V_NP_YTD_HV"
dbvar_V_Strikes_Sum = "V_Strikes_Sum"
dbvar_V_StrikeAccuracy_Sum = "V_StrikeAccuracy_Sum"
dbvar_V_Strikes = "V_Strikes"
dbvar_V_StrikeAccuracy = "V_StrikeAccuracy"
dbvar_V_Strikes_5G = "V_Strikes_5G"
dbvar_V_StrikeAccuracy_5G = "V_StrikeAccuracy_5G"
dbvar_V_Strikes_YTD = "V_Strikes_YTD"
dbvar_V_StrikeAccuracy_YTD = "V_StrikeAccuracy_YTD"
dbvar_V_Strikes_YTD_HV = "V_Strikes_YTD_HV"
dbvar_V_StrikeAccuracy_YTD_HV = "V_StrikeAccuracy_YTD_HV"
dbvar_V_MenOnBase = "V_MenOnBase"
dbvar_V_MenOnBase_Strength = "V_MenOnBase_Strength"
dbvar_V_MenOnBase_Efficiency = "V_MenOnBase_Efficiency"
dbvar_V_MenOnBase_5G = "V_MenOnBase_5G"
dbvar_V_MenOnBase_Strength_5G = "V_MenOnBase_Strength_5G"
dbvar_V_MenOnBase_Efficiency_5G = "V_MenOnBase_Efficiency_5G"
dbvar_V_MenOnBase_20G = "V_MenOnBase_20G"
dbvar_V_MenOnBase_Strength_20G = "V_MenOnBase_Strength_20G"
dbvar_V_MenOnBase_Efficiency_20G = "V_MenOnBase_Efficiency_20G"
dbvar_V_MenOnBase_YTD = "V_MenOnBase_YTD"
dbvar_V_MenOnBase_Strength_YTD = "V_MenOnBase_Strength_YTD"
dbvar_V_MenOnBase_Efficiency_YTD = "V_MenOnBase_Efficiency_YTD"
dbvar_V_MenOnBase_Allowed = "V_MenOnBase_Allowed"
dbvar_V_MenOnBase_Allowed_Efficiency = "V_MenOnBase_Allowed_Efficiency"
dbvar_V_MenOnBase_Allowed_5G = "V_MenOnBase_Allowed_5G"
dbvar_V_MenOnBase_Allowed_Efficiency_5G = "V_MenOnBase_Allowed_Efficiency_5G"
dbvar_V_MenOnBase_Allowed_20G = "V_MenOnBase_Allowed_20G"
dbvar_V_MenOnBase_Allowed_Efficiency_20G = "V_MenOnBase_Allowed_Efficiency_20G"
dbvar_V_MenOnBase_Allowed_YTD = "V_MenOnBase_Allowed_YTD"
dbvar_V_MenOnBase_Allowed_Efficiency_YTD = "V_MenOnBase_Allowed_Efficiency_YTD"
dbvar_V_LeftOnBase_Sum = "V_LeftOnBase_Sum"
dbvar_V_LeftOnBase = "V_LeftOnBase"
dbvar_V_2BRuns_Sum = "V_2BRuns_Sum"
dbvar_V_2BRuns = "V_2BRuns"
dbvar_V_2BRuns_Strength = "V_2BRuns_Strength"
dbvar_V_2BRuns_Sum_5G = "V_2BRuns_Sum_5G"
dbvar_V_2BRuns_5G = "V_2BRuns_5G"
dbvar_V_2BRuns_Strength_5G = "V_2BRuns_Strength_5G"
dbvar_V_2BRuns_Sum_20G = "V_2BRuns_Sum_20G"
dbvar_V_2BRuns_20G = "V_2BRuns_20G"
dbvar_V_2BRuns_Strength_20G = "V_2BRuns_Strength_20G"
dbvar_V_2BRuns_YTD = "V_2BRuns_YTD"
dbvar_V_2BRuns_Strength_YTD = "V_2BRuns_Strength_YTD"
dbvar_V_2BRuns_Allowed = "V_2BRuns_Allowed"
dbvar_V_2BRuns_Allowed_5G = "V_2BRuns_Allowed_5G"
dbvar_V_2BRuns_Allowed_20G = "V_2BRuns_Allowed_20G"
dbvar_V_2BRuns_Allowed_YTD = "V_2BRuns_Allowed_YTD"
dbvar_V_3BRuns_Sum = "V_3BRuns_Sum"
dbvar_V_3BRuns = "V_3BRuns"
dbvar_V_3BRuns_5G = "V_3BRuns_5G"
dbvar_V_3BRuns_20G = "V_3BRuns_20G"
dbvar_V_3BRuns_YTD = "V_3BRuns_YTD"
dbvar_V_3BRuns_Allowed = "V_3BRuns_Allowed"
dbvar_V_3BRuns_Allowed_5G = "V_3BRuns_Allowed_5G"
dbvar_V_3BRuns_Allowed_20G = "V_3BRuns_Allowed_20G"
dbvar_V_3BRuns_Allowed_YTD = "V_3BRuns_Allowed_YTD"
dbvar_V_3BRuns_Strength = "V_3BRuns_Strength"
dbvar_V_3BRuns_Strength_5G = "V_3BRuns_Strength_5G"
dbvar_V_3BRuns_Strength_20G = "V_3BRuns_Strength_20G"
dbvar_V_3BRuns_Strength_YTD = "V_3BRuns_Strength_YTD"
dbvar_V_ErrorMade_Sum = "V_ErrorMade_Sum"
dbvar_V_ErrorMade = "V_ErrorMade"
dbvar_V_ErrorMade_Sum_5G = "V_ErrorMade_Sum_5G"
dbvar_V_ErrorMade_5G = "V_ErrorMade_5G"
dbvar_V_ErrorMade_Sum_20G = "V_ErrorMade_Sum_20G"
dbvar_V_ErrorMade_20G = "V_ErrorMade_20G"
dbvar_V_ErrorMade_YTD = "V_ErrorMade_YTD"
dbvar_V_ErrorMade_YTD_HV = "V_ErrorMade_YTD_HV"
dbvar_V_ErrorForced_Sum = "V_ErrorForced_Sum"
dbvar_V_ErrorForced_Sum_5G = "V_ErrorForced_Sum_5G"
dbvar_V_ErrorForced_Sum_20G = "V_ErrorForced_Sum_20G"
dbvar_V_ErrorForced = "V_ErrorForced"
dbvar_V_ErrorForced_5G = "V_ErrorForced_5G"
dbvar_V_ErrorForced_20G = "V_ErrorForced_20G"
dbvar_V_ErrorForced_YTD = "V_ErrorForced_YTD"
dbvar_V_HitsByPitch_Sum = "V_HitsByPitch_Sum"
dbvar_V_HitsByPitch = "V_HitsByPitch"
dbvar_V_HitsByPitch_Sum_5G = "V_HitsByPitch_Sum_5G"
dbvar_V_HitsByPitch_5G = "V_HitsByPitch_5G"
dbvar_V_HitsByPitch_Sum_20G = "V_HitsByPitch_Sum_20G"
dbvar_V_HitsByPitch_20G = "V_HitsByPitch_20G"
dbvar_V_HitsByPitch_YTD = "V_HitsByPitch_YTD"
dbvar_V_HitsByPitch_Allowed = "V_HitsByPitch_Allowed"
dbvar_V_HitsByPitch_Allowed_5G = "V_HitsByPitch_Allowed_5G"
dbvar_V_HitsByPitch_Allowed_20G = "V_HitsByPitch_Allowed_20G"
dbvar_V_HitsByPitch_Allowed_YTD = "V_HitsByPitch_Allowed_YTD"
dbvar_V_HitsByPitch_Allowed_YTD_HV = "V_HitsByPitch_Allowed_YTD_HV"
dbvar_V_DoublePlays_Gained_Sum = "V_DoublePlays_Gained_Sum"
dbvar_V_DoublePlays_Gained = "V_DoublePlays_Gained"
dbvar_V_DoublePlays_Gained_Sum_5G = "V_DoublePlays_Gained_Sum_5G"
dbvar_V_DoublePlays_Gained_5G = "V_DoublePlays_Gained_5G"
dbvar_V_DoublePlays_Gained_Sum_20G = "V_DoublePlays_Gained_Sum_20G"
dbvar_V_DoublePlays_Gained_20G = "V_DoublePlays_Gained_20G"
dbvar_V_DoublePlays_Gained_YTD = "V_DoublePlays_Gained_YTD"
dbvar_V_DoublePlays_Gained_YTD_HV = "V_DoublePlays_Gained_YTD_HV"
dbvar_V_DoublePlays_Allowed = "V_DoublePlays_Allowed"
dbvar_V_DoublePlays_Allowed_5G = "V_DoublePlays_Allowed_5G"
dbvar_V_DoublePlays_Allowed_20G = "V_DoublePlays_Allowed_20G"
dbvar_V_DoublePlays_Allowed_YTD = "V_DoublePlays_Allowed_YTD"
dbvar_V_DoublePlays_Allowed_YTD_HV = "V_DoublePlays_Allowed_YTD_HV"
dbvar_V_ReliefPitchers = "V_ReliefPitchers"
dbvar_V_TotalBases_Sum = "V_TotalBases_Sum"
dbvar_V_TotalBases = "V_TotalBases"
dbvar_V_TotalBases_5G = "V_TotalBases_5G"
dbvar_V_TotalBases_20G = "V_TotalBases_20G"
dbvar_V_TotalBases_YTD = "V_TotalBases_YTD"
dbvar_V_MenOnBaseTBRatio = "V_MenOnBaseTBRatio"
dbvar_V_MenOnBaseTBRatio_5G = "V_MenOnBaseTBRatio_5G"
dbvar_V_WalkStrikeoutRatio_Sum = "V_WalkStrikeoutRatio_Sum"
dbvar_V_WalkStrikeoutRatio = "V_WalkStrikeoutRatio"
dbvar_V_PowerHits_Sum = "V_PowerHits_Sum"
dbvar_V_PowerHits = "V_PowerHits"
dbvar_V_PowerHits_5G = "V_PowerHits_5G"
dbvar_V_Innings_OutPitched_Sum = "V_Innings_OutPitched_Sum"
dbvar_V_Innings_OutPitched = "V_Innings_OutPitched"
dbvar_V_Innings_OutPitched_Sum_5G = "V_Innings_OutPitched_Sum_5G"
dbvar_V_Innings_OutPitched_5G = "V_Innings_OutPitched_5G"
dbvar_V_Innings_OutPitched_YTD = "V_Innings_OutPitched_YTD"
dbvar_V_SP_HitsAllowed_Sum = "V_SP_HitsAllowed_Sum"
dbvar_V_SP_HitsAllowed = "V_SP_HitsAllowed"
dbvar_V_SP_HitsAllowed_5G = "V_SP_HitsAllowed_5G"
dbvar_V_SP_HitsAllowed_YTD = "V_SP_HitsAllowed_YTD"
dbvar_V_EarnedRuns_Sum = "V_EarnedRuns_Sum"
dbvar_V_EarnedRunAvg_Sum = "V_EarnedRunAvg_Sum"
dbvar_V_EarnedRuns = "V_EarnedRuns"
dbvar_V_EarnedRunAvg = "V_EarnedRunAvg"
dbvar_V_EarnedRuns_Sum_5G = "V_EarnedRuns_Sum_5G"
dbvar_V_EarnedRunAvg_Sum_5G = "V_EarnedRunAvg_Sum_5G"
dbvar_V_EarnedRuns_5G = "V_EarnedRuns_5G"
dbvar_V_EarnedRunAvg_5G = "V_EarnedRunAvg_5G"
dbvar_V_EarnedRuns_YTD = "V_EarnedRuns_YTD"
dbvar_V_EarnedRunAvg_YTD = "V_EarnedRunAvg_YTD"
dbvar_V_HitsAllowedPer9Innings_Sum = "V_HitsAllowedPer9Innings_Sum"
dbvar_V_HitsAllowedPer9Innings = "V_HitsAllowedPer9Innings"
dbvar_V_HitsAllowedPer9Innings_5G = "V_HitsAllowedPer9Innings_5G"
dbvar_V_WalksHitsAllowedPerInning = "V_WalksHitsAllowedPerInning"
dbvar_V_WalksHitsAllowedPerInning_5G = "V_WalksHitsAllowedPerInning_5G"
dbvar_V_WalksHitsAllowedPerInning_YTD = "V_WalksHitsAllowedPerInning_YTD"
dbvar_G_V_StartingPitcher_Id = "G_V_StartingPitcher_Id"
dbvar_V_StartingPitcher_DaysRest = "V_StartingPitcher_DaysRest"
dbvar_V_StartingPitcher_Score_All = "V_StartingPitcher_Score_All"
dbvar_V_StartingPitcher_Strikeouts_All = "V_StartingPitcher_Strikeouts_All"
dbvar_V_StartingPitcher_StrikeoutAccuracy_All = "V_StartingPitcher_StrikeoutAccuracy_All"
dbvar_V_StartingPitcher_BaseOnBalls_All = "V_StartingPitcher_BaseOnBalls_All"
dbvar_V_StartingPitcher_Hits_All = "V_StartingPitcher_Hits_All"
dbvar_V_StartingPitcher_NP_All = "V_StartingPitcher_NP_All"
dbvar_V_StartingPitcher_InningsPitched_All = "V_StartingPitcher_InningsPitched_All"
dbvar_V_StartingPitcher_Strikes_All = "V_StartingPitcher_Strikes_All"
dbvar_V_StartingPitcher_StrikeAccuracy_All = "V_StartingPitcher_StrikeAccuracy_All"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All = "V_StartingPitcher_WalkHitsAllowedPerInning_All"
dbvar_V_StartingPitcher_Score_YTD = "V_StartingPitcher_Score_YTD"
dbvar_V_StartingPitcher_Strikeouts_YTD = "V_StartingPitcher_Strikeouts_YTD"
dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD = "V_StartingPitcher_StrikeoutAccuracy_YTD"
dbvar_V_StartingPitcher_BaseOnBalls_YTD = "V_StartingPitcher_BaseOnBalls_YTD"
dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD = "V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD"
dbvar_V_StartingPitcher_Hits_YTD = "V_StartingPitcher_Hits_YTD"
dbvar_V_StartingPitcher_NP_YTD = "V_StartingPitcher_NP_YTD"
dbvar_V_StartingPitcher_InningsPitched_YTD = "V_StartingPitcher_InningsPitched_YTD"
dbvar_V_StartingPitcher_Strikes_YTD = "V_StartingPitcher_Strikes_YTD"
dbvar_V_StartingPitcher_StrikeAccuracy_YTD = "V_StartingPitcher_StrikeAccuracy_YTD"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD = "V_StartingPitcher_WalkHitsAllowedPerInning_YTD"
dbvar_V_StartingPitcher_ScoreImpact_YTD = "V_StartingPitcher_ScoreImpact_YTD"
dbvar_V_StartingPitcher_StrikeoutsImpact_YTD = "V_StartingPitcher_StrikeoutsImpact_YTD"
dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD = "V_StartingPitcher_BaseOnBallsImpact_YTD"
dbvar_V_StartingPitcher_HitsImpact_YTD = "V_StartingPitcher_HitsImpact_YTD"
dbvar_V_StartingPitcher_NPImpact_YTD = "V_StartingPitcher_NPImpact_YTD"
dbvar_V_StartingPitcher_InningsPitchedImpact_YTD = "V_StartingPitcher_InningsPitchedImpact_YTD"
dbvar_V_StartingPitcher_StrikeImpact_YTD = "V_StartingPitcher_StrikeImpact_YTD"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD = "V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD"
dbvar_V_StartingPitcher_Score_5G = "V_StartingPitcher_Score_5G"
dbvar_V_StartingPitcher_Strikeouts_5G = "V_StartingPitcher_Strikeouts_5G"
dbvar_V_StartingPitcher_StrikeoutAccuracy_5G = "V_StartingPitcher_StrikeoutAccuracy_5G"
dbvar_V_StartingPitcher_BaseOnBalls_5G = "V_StartingPitcher_BaseOnBalls_5G"
dbvar_V_StartingPitcher_Hits_5G = "V_StartingPitcher_Hits_5G"
dbvar_V_StartingPitcher_NP_5G = "V_StartingPitcher_NP_5G"
dbvar_V_StartingPitcher_InningsPitched_5G = "V_StartingPitcher_InningsPitched_5G"
dbvar_V_StartingPitcher_Strikes_5G = "V_StartingPitcher_Strikes_5G"
dbvar_V_StartingPitcher_StrikeAccuracy_5G = "V_StartingPitcher_StrikeAccuracy_5G"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G = "V_StartingPitcher_WalkHitsAllowedPerInning_5G"
dbvar_V_StartingPitcher_ScoreImpact_5G = "V_StartingPitcher_ScoreImpact_5G"
dbvar_V_StartingPitcher_StrikeoutsImpact_5G = "V_StartingPitcher_StrikeoutsImpact_5G"
dbvar_V_StartingPitcher_BaseOnBallsImpact_5G = "V_StartingPitcher_BaseOnBallsImpact_5G"
dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G = "V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G"
dbvar_V_StartingPitcher_HitsImpact_5G = "V_StartingPitcher_HitsImpact_5G"
dbvar_V_StartingPitcher_NPImpact_5G = "V_StartingPitcher_NPImpact_5G"
dbvar_V_StartingPitcher_InningsPitchedImpact_5G = "V_StartingPitcher_InningsPitchedImpact_5G"
dbvar_V_StartingPitcher_StrikeImpact_5G = "V_StartingPitcher_StrikeImpact_5G"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G = "V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G"
dbvar_V_StartingPitcher_Score_Ratio = "V_StartingPitcher_Score_Ratio"
dbvar_V_StartingPitcher_Strikeouts_Ratio = "V_StartingPitcher_Strikeouts_Ratio"
dbvar_V_StartingPitcher_BaseOnBalls_Ratio = "V_StartingPitcher_BaseOnBalls_Ratio"
dbvar_V_StartingPitcher_Hits_Ratio = "V_StartingPitcher_Hits_Ratio"
dbvar_V_StartingPitcher_NP_Ratio = "V_StartingPitcher_NP_Ratio"
dbvar_V_StartingPitcher_InningsPitched_Ratio = "V_StartingPitcher_InningsPitched_Ratio"
dbvar_V_StartingPitcher_Strikes_Ratio = "V_StartingPitcher_Strikes_Ratio"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio = "V_StartingPitcher_WalkHitsAllowedPerInning_Ratio"
dbvar_V_StartingPitcher_Score_Ratio_5G = "V_StartingPitcher_Score_Ratio_5G"
dbvar_V_StartingPitcher_Strikeouts_Ratio_5G = "V_StartingPitcher_Strikeouts_Ratio_5G"
dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G = "V_StartingPitcher_BaseOnBalls_Ratio_5G"
dbvar_V_StartingPitcher_Hits_Ratio_5G = "V_StartingPitcher_Hits_Ratio_5G"
dbvar_V_StartingPitcher_NP_Ratio_5G = "V_StartingPitcher_NP_Ratio_5G"
dbvar_V_StartingPitcher_InningsPitched_Ratio_5G = "V_StartingPitcher_InningsPitched_Ratio_5G"
dbvar_V_StartingPitcher_Strikes_Ratio_5G = "V_StartingPitcher_Strikes_Ratio_5G"
dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G = "V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G"
dbvar_V_BallpenOuts = "V_BallpenOuts"
dbvar_V_BallpenOuts_5G = "V_BallpenOuts_5G"
dbvar_V_BallpenOuts_YTD = "V_BallpenOuts_YTD"
dbvar_V_BallpenERA_Approx = "V_BallpenERA_Approx"
dbvar_V_BallpenERA_Approx_5G = "V_BallpenERA_Approx_5G"
dbvar_V_BallpenERA_Approx_YTD = "V_BallpenERA_Approx_YTD"
dbvar_G_VHRatio_DaysRest = "G_VHRatio_DaysRest"
dbvar_G_VHRatio_SP_DaysRest = "G_VHRatio_SP_DaysRest"
dbvar_G_VHRatio_ParkImpactFactor = "G_VHRatio_ParkImpactFactor"
dbvar_G_VHRatio_ContiguousGamesV = "G_VHRatio_ContiguousGamesV"
dbvar_G_VHRatio_ContiguousGamesH = "G_VHRatio_ContiguousGamesH"
dbvar_G_VHRatio_TotalDistanceTravelled_3G = "G_VHRatio_TotalDistanceTravelled_3G"
dbvar_G_VHRatio_ClosingProbabilityLine_HV = "G_VHRatio_ClosingProbabilityLine_HV"
dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV = "G_VHRatio_ClosingProbabilityLine_YTD_HV"
dbvar_G_VHRatio_Runs_Gained = "G_VHRatio_Runs_Gained"
dbvar_G_VHRatio_Runs_Allowed = "G_VHRatio_Runs_Allowed"
dbvar_G_VHRatio_Run_Strength = "G_VHRatio_Run_Strength"
dbvar_G_VHRatio_Run_Efficiency = "G_VHRatio_Run_Efficiency"
dbvar_G_VHRatio_Runs_Gained_Sum = "G_VHRatio_Runs_Gained_Sum"
dbvar_G_VHRatio_Runs_Allowed_Sum = "G_VHRatio_Runs_Allowed_Sum"
dbvar_G_VHRatio_Run_Strength_Sum = "G_VHRatio_Run_Strength_Sum"
dbvar_G_VHRatio_Run_Efficiency_Sum = "G_VHRatio_Run_Efficiency_Sum"
dbvar_G_VHRatio_Run_Pythag = "G_VHRatio_Run_Pythag"
dbvar_G_VHRatio_Runs_Gained_5G = "G_VHRatio_Runs_Gained_5G"
dbvar_G_VHRatio_Runs_Allowed_5G = "G_VHRatio_Runs_Allowed_5G"
dbvar_G_VHRatio_Run_Strength_5G = "G_VHRatio_Run_Strength_5G"
dbvar_G_VHRatio_Run_Efficiency_5G = "G_VHRatio_Run_Efficiency_5G"
dbvar_G_VHRatio_Run_Pythag_5G = "G_VHRatio_Run_Pythag_5G"
dbvar_G_VHRatio_Runs_Gained_Sum_5G = "G_VHRatio_Runs_Gained_Sum_5G"
dbvar_G_VHRatio_Runs_Allowed_Sum_5G = "G_VHRatio_Runs_Allowed_Sum_5G"
dbvar_G_VHRatio_Run_Strength_Sum_5G = "G_VHRatio_Run_Strength_Sum_5G"
dbvar_G_VHRatio_Run_Efficiency_Sum_5G = "G_VHRatio_Run_Efficiency_Sum_5G"
dbvar_G_VHRatio_Runs_Gained_20G = "G_VHRatio_Runs_Gained_20G"
dbvar_G_VHRatio_Runs_Allowed_20G = "G_VHRatio_Runs_Allowed_20G"
dbvar_G_VHRatio_Run_Strength_20G = "G_VHRatio_Run_Strength_20G"
dbvar_G_VHRatio_Run_Efficiency_20G = "G_VHRatio_Run_Efficiency_20G"
dbvar_G_VHRatio_Run_Pythag_20G = "G_VHRatio_Run_Pythag_20G"
dbvar_G_VHRatio_Runs_Gained_Sum_20G = "G_VHRatio_Runs_Gained_Sum_20G"
dbvar_G_VHRatio_Runs_Allowed_Sum_20G = "G_VHRatio_Runs_Allowed_Sum_20G"
dbvar_G_VHRatio_Run_Strength_Sum_20G = "G_VHRatio_Run_Strength_Sum_20G"
dbvar_G_VHRatio_Run_Efficiency_Sum_20G = "G_VHRatio_Run_Efficiency_Sum_20G"
dbvar_G_VHRatio_Runs_5InningsGained = "G_VHRatio_Runs_5InningsGained"
dbvar_G_VHRatio_Runs_5InningsAllowed = "G_VHRatio_Runs_5InningsAllowed"
dbvar_G_VHRatio_Run_5InningsStrength = "G_VHRatio_Run_5InningsStrength"
dbvar_G_VHRatio_Run_5InningsEfficiency = "G_VHRatio_Run_5InningsEfficiency"
dbvar_G_VHRatio_Runs_5InningsGained_Sum = "G_VHRatio_Runs_5InningsGained_Sum"
dbvar_G_VHRatio_Runs_5InningsAllowed_Sum = "G_VHRatio_Runs_5InningsAllowed_Sum"
dbvar_G_VHRatio_Run_5InningsStrength_Sum = "G_VHRatio_Run_5InningsStrength_Sum"
dbvar_G_VHRatio_Run_5InningsEfficiency_Sum = "G_VHRatio_Run_5InningsEfficiency_Sum"
dbvar_G_VHRatio_Runs_5InningsGained_5G = "G_VHRatio_Runs_5InningsGained_5G"
dbvar_G_VHRatio_Runs_5InningsAllowed_5G = "G_VHRatio_Runs_5InningsAllowed_5G"
dbvar_G_VHRatio_Run_5InningsStrength_5G = "G_VHRatio_Run_5InningsStrength_5G"
dbvar_G_VHRatio_Run_5InningsEfficiency_5G = "G_VHRatio_Run_5InningsEfficiency_5G"
dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G = "G_VHRatio_Runs_5InningsGained_Sum_5G"
dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G = "G_VHRatio_Runs_5InningsAllowed_Sum_5G"
dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G = "G_VHRatio_Run_5InningsStrength_Sum_5G"
dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G = "G_VHRatio_Run_5InningsEfficiency_Sum_5G"
dbvar_G_VHRatio_Runs_5InningsGained_20G = "G_VHRatio_Runs_5InningsGained_20G"
dbvar_G_VHRatio_Runs_5InningsAllowed_20G = "G_VHRatio_Runs_5InningsAllowed_20G"
dbvar_G_VHRatio_Run_5InningsStrength_20G = "G_VHRatio_Run_5InningsStrength_20G"
dbvar_G_VHRatio_Run_5InningsEfficiency_20G = "G_VHRatio_Run_5InningsEfficiency_20G"
dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G = "G_VHRatio_Runs_5InningsGained_Sum_20G"
dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G = "G_VHRatio_Runs_5InningsAllowed_Sum_20G"
dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G = "G_VHRatio_Run_5InningsStrength_Sum_20G"
dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G = "G_VHRatio_Run_5InningsEfficiency_Sum_20G"
dbvar_G_VHRatio_Runs_5InningsGained_HV = "G_VHRatio_Runs_5InningsGained_HV"
dbvar_G_VHRatio_Runs_5InningsAllowed_HV = "G_VHRatio_Runs_5InningsAllowed_HV"
dbvar_G_VHRatio_Runs_5InningsGained_YTD = "G_VHRatio_Runs_5InningsGained_YTD"
dbvar_G_VHRatio_Runs_5InningsAllowed_YTD = "G_VHRatio_Runs_5InningsAllowed_YTD"
dbvar_G_VHRatio_Pythag_Luck_Factor = "G_VHRatio_Pythag_Luck_Factor"
dbvar_G_VHRatio_Pythag_Luck_Factor_5G = "G_VHRatio_Pythag_Luck_Factor_5G"
dbvar_G_VHRatio_Pythag_Luck_Factor_20G = "G_VHRatio_Pythag_Luck_Factor_20G"
dbvar_G_VHRatio_Pythag_Luck_Factor_YTD = "G_VHRatio_Pythag_Luck_Factor_YTD"
dbvar_G_VHRatio_Run_Differential_Per_Game = "G_VHRatio_Run_Differential_Per_Game"
dbvar_G_VHRatio_Run_Differential_Per_Game_5G = "G_VHRatio_Run_Differential_Per_Game_5G"
dbvar_G_VHRatio_Run_Differential_Per_Game_20G = "G_VHRatio_Run_Differential_Per_Game_20G"
dbvar_G_VHRatio_Run_Differential_Per_Game_YTD = "G_VHRatio_Run_Differential_Per_Game_YTD"
dbvar_G_VHRatio_Weighted_Offense_Index = "G_VHRatio_Weighted_Offense_Index"
dbvar_G_VHRatio_Weighted_Offense_Index_5G = "G_VHRatio_Weighted_Offense_Index_5G"
dbvar_G_VHRatio_Weighted_Offense_Index_20G = "G_VHRatio_Weighted_Offense_Index_20G"
dbvar_G_VHRatio_Weighted_Offense_Index_YTD = "G_VHRatio_Weighted_Offense_Index_YTD"
dbvar_G_VHRatio_At_Bat = "G_VHRatio_At_Bat"
dbvar_G_VHRatio_At_Bat_5G = "G_VHRatio_At_Bat_5G"
dbvar_G_VHRatio_At_Bat_20G = "G_VHRatio_At_Bat_20G"
dbvar_G_VHRatio_At_Bat_YTD = "G_VHRatio_At_Bat_YTD"
dbvar_G_VHRatio_At_Bat_HV = "G_VHRatio_At_Bat_HV"
dbvar_G_VHRatio_At_Bat_YTD_HV = "G_VHRatio_At_Bat_YTD_HV"
dbvar_G_VHRatio_OBP = "G_VHRatio_OBP"
dbvar_G_VHRatio_OBP_5G = "G_VHRatio_OBP_5G"
dbvar_G_VHRatio_OBP_20G = "G_VHRatio_OBP_20G"
dbvar_G_VHRatio_OBP_YTD = "G_VHRatio_OBP_YTD"
dbvar_G_VHRatio_SLG = "G_VHRatio_SLG"
dbvar_G_VHRatio_SLG_5G = "G_VHRatio_SLG_5G"
dbvar_G_VHRatio_SLG_20G = "G_VHRatio_SLG_20G"
dbvar_G_VHRatio_SLG_YTD = "G_VHRatio_SLG_YTD"
dbvar_G_VHRatio_wOBA = "G_VHRatio_wOBA"
dbvar_G_VHRatio_wOBA_5G = "G_VHRatio_wOBA_5G"
dbvar_G_VHRatio_wOBA_20G = "G_VHRatio_wOBA_20G"
dbvar_G_VHRatio_wOBA_YTD = "G_VHRatio_wOBA_YTD"
dbvar_G_VHRatio_OPS = "G_VHRatio_OPS"
dbvar_G_VHRatio_OPS_5G = "G_VHRatio_OPS_5G"
dbvar_G_VHRatio_OPS_20G = "G_VHRatio_OPS_20G"
dbvar_G_VHRatio_OPS_YTD = "G_VHRatio_OPS_YTD"
dbvar_G_VHRatio_Wins = "G_VHRatio_Wins"
dbvar_G_VHRatio_Losses = "G_VHRatio_Losses"
dbvar_G_VHRatio_WinLoss_Strength = "G_VHRatio_WinLoss_Strength"
dbvar_G_VHRatio_Wins_5G = "G_VHRatio_Wins_5G"
dbvar_G_VHRatio_Losses_5G = "G_VHRatio_Losses_5G"
dbvar_G_VHRatio_WinLoss_Strength_5G = "G_VHRatio_WinLoss_Strength_5G"
dbvar_G_VHRatio_Wins_20G = "G_VHRatio_Wins_20G"
dbvar_G_VHRatio_Losses_20G = "G_VHRatio_Losses_20G"
dbvar_G_VHRatio_WinLoss_Strength_20G = "G_VHRatio_WinLoss_Strength_20G"
dbvar_G_VHRatio_OutsPitched = "G_VHRatio_OutsPitched"
dbvar_G_VHRatio_OutsPitched_5G = "G_VHRatio_OutsPitched_5G"
dbvar_G_VHRatio_OutsPitched_20G = "G_VHRatio_OutsPitched_20G"
dbvar_G_VHRatio_OutsPitched_YTD = "G_VHRatio_OutsPitched_YTD"
dbvar_G_VHRatio_OutsPitched_YTD_HV = "G_VHRatio_OutsPitched_YTD_HV"
dbvar_G_VHRatio_StrikeAccuracy = "G_VHRatio_StrikeAccuracy"
dbvar_G_VHRatio_StrikeAccuracy_5G = "G_VHRatio_StrikeAccuracy_5G"
dbvar_G_VHRatio_StrikeoutsGained = "G_VHRatio_StrikeoutsGained"
dbvar_G_VHRatio_StrikeoutsAllowed = "G_VHRatio_StrikeoutsAllowed"
dbvar_G_VHRatio_StrikeoutsAccuracy = "G_VHRatio_StrikeoutsAccuracy"
dbvar_G_VHRatio_StrikeoutsGained_5G = "G_VHRatio_StrikeoutsGained_5G"
dbvar_G_VHRatio_StrikeoutsAllowed_5G = "G_VHRatio_StrikeoutsAllowed_5G"
dbvar_G_VHRatio_StrikeoutsAccuracy_5G = "G_VHRatio_StrikeoutsAccuracy_5G"
dbvar_G_VHRatio_StrikeoutsGained_20G = "G_VHRatio_StrikeoutsGained_20G"
dbvar_G_VHRatio_EarnedRuns = "G_VHRatio_EarnedRuns"
dbvar_G_VHRatio_EarnedRunAvg = "G_VHRatio_EarnedRunAvg"
dbvar_G_VHRatio_EarnedRuns_5G = "G_VHRatio_EarnedRuns_5G"
dbvar_G_VHRatio_EarnedRuns_Avg_5G = "G_VHRatio_EarnedRuns_Avg_5G"
dbvar_G_VHRatio_EarnedRuns_Sum_5G = "G_VHRatio_EarnedRuns_Sum_5G"
dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G = "G_VHRatio_EarnedRuns_Avg_Sum_5G"
dbvar_G_VHRatio_EarnedRuns_YTD = "G_VHRatio_EarnedRuns_YTD"
dbvar_G_VHRatio_EarnedRunAvg_YTD = "G_VHRatio_EarnedRunAvg_YTD"
dbvar_G_VHRatio_RunsHitsRatio = "G_VHRatio_RunsHitsRatio"
dbvar_G_VHRatio_RunsHitsRatio_Sum = "G_VHRatio_RunsHitsRatio_Sum"
dbvar_G_VHRatio_RunsHitsRatio_5G = "G_VHRatio_RunsHitsRatio_5G"
dbvar_G_VHRatio_RunsHitsRatio_Sum_5G = "G_VHRatio_RunsHitsRatio_Sum_5G"
dbvar_G_VHRatio_RunsHitsRatio_Allowed = "G_VHRatio_RunsHitsRatio_Allowed"
dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G = "G_VHRatio_RunsHitsRatio_Allowed_5G"
dbvar_G_VHRatio_FIP = "G_VHRatio_FIP"
dbvar_G_VHRatio_FIP_5G = "G_VHRatio_FIP_5G"
dbvar_G_VHRatio_FIP_YTD = "G_VHRatio_FIP_YTD"
dbvar_G_VHRatio_FIP_YTD_HV = "G_VHRatio_FIP_YTD_HV"
dbvar_G_VHRatio_K_Minus_BB_Pct = "G_VHRatio_K_Minus_BB_Pct"
dbvar_G_VHRatio_K_Minus_BB_Pct_5G = "G_VHRatio_K_Minus_BB_Pct_5G"
dbvar_G_VHRatio_K_Minus_BB_Pct_20G = "G_VHRatio_K_Minus_BB_Pct_20G"
dbvar_G_VHRatio_K_Minus_BB_Pct_YTD = "G_VHRatio_K_Minus_BB_Pct_YTD"
dbvar_G_VHRatio_HR_Per_9_Allowed = "G_VHRatio_HR_Per_9_Allowed"
dbvar_G_VHRatio_HR_Per_9_Allowed_5G = "G_VHRatio_HR_Per_9_Allowed_5G"
dbvar_G_VHRatio_HR_Per_9_Allowed_20G = "G_VHRatio_HR_Per_9_Allowed_20G"
dbvar_G_VHRatio_HR_Per_9_Allowed_YTD = "G_VHRatio_HR_Per_9_Allowed_YTD"
dbvar_G_VHRatio_K_Per_9 = "G_VHRatio_K_Per_9"
dbvar_G_VHRatio_K_Per_9_5G = "G_VHRatio_K_Per_9_5G"
dbvar_G_VHRatio_K_Per_9_20G = "G_VHRatio_K_Per_9_20G"
dbvar_G_VHRatio_K_Per_9_YTD = "G_VHRatio_K_Per_9_YTD"
dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV = "G_VHRatio_HitsByPitch_Allowed_YTD_HV"
dbvar_G_VHRatio_WalksAllowed = "G_VHRatio_WalksAllowed"
dbvar_G_VHRatio_WalksAllowed_5G = "G_VHRatio_WalksAllowed_5G"
dbvar_G_VHRatio_WalksAllowed_20G = "G_VHRatio_WalksAllowed_20G"
dbvar_G_VHRatio_WalksAllowed_Sum = "G_VHRatio_WalksAllowed_Sum"
dbvar_G_VHRatio_WalksAllowed_Sum_5G = "G_VHRatio_WalksAllowed_Sum_5G"
dbvar_G_VHRatio_WalksAllowed_Sum_20G = "G_VHRatio_WalksAllowed_Sum_20G"
dbvar_G_VHRatio_PowerHits = "G_VHRatio_PowerHits"
dbvar_G_VHRatio_PowerHits_5G = "G_VHRatio_PowerHits_5G"
dbvar_G_VHRatio_HitsAllowed_5G = "G_VHRatio_HitsAllowed_5G"
dbvar_G_VHRatio_HitsAllowed_20G = "G_VHRatio_HitsAllowed_20G"
dbvar_G_VHRatio_HitsAllowedPer9Innings = "G_VHRatio_HitsAllowedPer9Innings"
dbvar_G_VHRatio_HitsAllowedPer9Innings_5G = "G_VHRatio_HitsAllowedPer9Innings_5G"
dbvar_G_VHRatio_HitsByPitch_5G = "G_VHRatio_HitsByPitch_5G"
dbvar_G_VHRatio_HitsByPitch_20G = "G_VHRatio_HitsByPitch_20G"
dbvar_G_VHRatio_2BRuns = "G_VHRatio_2BRuns"
dbvar_G_VHRatio_2BRuns_5G = "G_VHRatio_2BRuns_5G"
dbvar_G_VHRatio_2BRuns_20G = "G_VHRatio_2BRuns_20G"
dbvar_G_VHRatio_2BRuns_YTD = "G_VHRatio_2BRuns_YTD"
dbvar_G_VHRatio_2BRuns_Strength = "G_VHRatio_2BRuns_Strength"
dbvar_G_VHRatio_2BRuns_Strength_5G = "G_VHRatio_2BRuns_Strength_5G"
dbvar_G_VHRatio_2BRuns_Strength_20G = "G_VHRatio_2BRuns_Strength_20G"
dbvar_G_VHRatio_2BRuns_Strength_YTD = "G_VHRatio_2BRuns_Strength_YTD"
dbvar_G_VHRatio_3BRuns = "G_VHRatio_3BRuns"
dbvar_G_VHRatio_3BRuns_5G = "G_VHRatio_3BRuns_5G"
dbvar_G_VHRatio_3BRuns_20G = "G_VHRatio_3BRuns_20G"
dbvar_G_VHRatio_3BRuns_YTD = "G_VHRatio_3BRuns_YTD"
dbvar_G_VHRatio_3BRuns_Strength = "G_VHRatio_3BRuns_Strength"
dbvar_G_VHRatio_3BRuns_Strength_5G = "G_VHRatio_3BRuns_Strength_5G"
dbvar_G_VHRatio_3BRuns_Strength_20G = "G_VHRatio_3BRuns_Strength_20G"
dbvar_G_VHRatio_3BRuns_Strength_YTD = "G_VHRatio_3BRuns_Strength_YTD"
dbvar_G_VHRatio_HomeRuns_5G = "G_VHRatio_HomeRuns_5G"
dbvar_G_VHRatio_HomeRuns_20G = "G_VHRatio_HomeRuns_20G"
dbvar_G_VHRatio_DoublePlays_Gained_5G = "G_VHRatio_DoublePlays_Gained_5G"
dbvar_G_VHRatio_DoublePlays_Gained_20G = "G_VHRatio_DoublePlays_Gained_20G"
dbvar_G_VHRatio_DoublePlays_Gained_YTD = "G_VHRatio_DoublePlays_Gained_YTD"
dbvar_G_VHRatio_DoublePlays_Allowed_5G = "G_VHRatio_DoublePlays_Allowed_5G"
dbvar_G_VHRatio_DoublePlays_Allowed_20G = "G_VHRatio_DoublePlays_Allowed_20G"
dbvar_G_VHRatio_DoublePlays_Allowed_YTD = "G_VHRatio_DoublePlays_Allowed_YTD"
dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV = "G_VHRatio_DoublePlays_Allowed_YTD_HV"
dbvar_G_VHRatio_TotalBases = "G_VHRatio_TotalBases"
dbvar_G_VHRatio_TotalBases_5G = "G_VHRatio_TotalBases_5G"
dbvar_G_VHRatio_TotalBases_20G = "G_VHRatio_TotalBases_20G"
dbvar_G_VHRatio_TotalBases_YTD = "G_VHRatio_TotalBases_YTD"
dbvar_G_VHRatio_MenOnBaseTBRatio = "G_VHRatio_MenOnBaseTBRatio"
dbvar_G_VHRatio_MenOnBaseTBRatio_5G = "G_VHRatio_MenOnBaseTBRatio_5G"
dbvar_G_VHRatio_MenOnBase = "G_VHRatio_MenOnBase"
dbvar_G_VHRatio_MenOnBase_Strength = "G_VHRatio_MenOnBase_Strength"
dbvar_G_VHRatio_MenOnBase_Efficiency = "G_VHRatio_MenOnBase_Efficiency"
dbvar_G_VHRatio_MenOnBase_5G = "G_VHRatio_MenOnBase_5G"
dbvar_G_VHRatio_MenOnBase_Strength_5G = "G_VHRatio_MenOnBase_Strength_5G"
dbvar_G_VHRatio_MenOnBase_Efficiency_5G = "G_VHRatio_MenOnBase_Efficiency_5G"
dbvar_G_VHRatio_MenOnBase_20G = "G_VHRatio_MenOnBase_20G"
dbvar_G_VHRatio_MenOnBase_Strength_20G = "G_VHRatio_MenOnBase_Strength_20G"
dbvar_G_VHRatio_MenOnBase_Efficiency_20G = "G_VHRatio_MenOnBase_Efficiency_20G"
dbvar_G_VHRatio_MenOnBase_Strength_YTD = "G_VHRatio_MenOnBase_Strength_YTD"
dbvar_G_VHRatio_MenOnBase_Allowed = "G_VHRatio_MenOnBase_Allowed"
dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency = "G_VHRatio_MenOnBase_Allowed_Efficiency"
dbvar_G_VHRatio_MenOnBase_Allowed_5G = "G_VHRatio_MenOnBase_Allowed_5G"
dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G = "G_VHRatio_MenOnBase_Allowed_Efficiency_5G"
dbvar_G_VHRatio_MenOnBase_Allowed_20G = "G_VHRatio_MenOnBase_Allowed_20G"
dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G = "G_VHRatio_MenOnBase_Allowed_Efficiency_20G"
dbvar_G_VHRatio_MenOnBase_Allowed_YTD = "G_VHRatio_MenOnBase_Allowed_YTD"
dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD = "G_VHRatio_MenOnBase_Allowed_Efficiency_YTD"
dbvar_G_VHRatio_StartingPitcher_Score_Ratio = "G_VHRatio_StartingPitcher_Score_Ratio"
dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio = "G_VHRatio_StartingPitcher_Strikeouts_Ratio"
dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio = "G_VHRatio_StartingPitcher_BaseOnBalls_Ratio"
dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio = "G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio"
dbvar_G_VHRatio_StartingPitcher_Hits_Ratio = "G_VHRatio_StartingPitcher_Hits_Ratio"
dbvar_G_VHRatio_StartingPitcher_NP_Ratio = "G_VHRatio_StartingPitcher_NP_Ratio"
dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio = "G_VHRatio_StartingPitcher_InningsPitched_Ratio"
dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio = "G_VHRatio_StartingPitcher_Strikes_Ratio"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio"
dbvar_G_VHRatio_StartingPitcher_Score_YTD = "G_VHRatio_StartingPitcher_Score_YTD"
dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD = "G_VHRatio_StartingPitcher_Strikeouts_YTD"
dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD = "G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD"
dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD = "G_VHRatio_StartingPitcher_BaseOnBalls_YTD"
dbvar_G_VHRatio_StartingPitcher_Hits_YTD = "G_VHRatio_StartingPitcher_Hits_YTD"
dbvar_G_VHRatio_StartingPitcher_NP_YTD = "G_VHRatio_StartingPitcher_NP_YTD"
dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD = "G_VHRatio_StartingPitcher_InningsPitched_YTD"
dbvar_G_VHRatio_StartingPitcher_Strikes_YTD = "G_VHRatio_StartingPitcher_Strikes_YTD"
dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD = "G_VHRatio_StartingPitcher_StrikeAccuracy_YTD"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD"
dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD = "G_VHRatio_StartingPitcher_ScoreImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD = "G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD = "G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD = "G_VHRatio_StartingPitcher_HitsImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD = "G_VHRatio_StartingPitcher_NPImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD = "G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD = "G_VHRatio_StartingPitcher_StrikesImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD"
dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G = "G_VHRatio_StartingPitcher_Score_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G = "G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G = "G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G = "G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G = "G_VHRatio_StartingPitcher_Hits_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G = "G_VHRatio_StartingPitcher_NP_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G = "G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G = "G_VHRatio_StartingPitcher_Strikes_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G"
dbvar_G_VHRatio_StartingPitcher_Score_5G = "G_VHRatio_StartingPitcher_Score_5G"
dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G = "G_VHRatio_StartingPitcher_Strikeouts_5G"
dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G = "G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G"
dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G = "G_VHRatio_StartingPitcher_BaseOnBalls_5G"
dbvar_G_VHRatio_StartingPitcher_Hits_5G = "G_VHRatio_StartingPitcher_Hits_5G"
dbvar_G_VHRatio_StartingPitcher_NP_5G = "G_VHRatio_StartingPitcher_NP_5G"
dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G = "G_VHRatio_StartingPitcher_InningsPitched_5G"
dbvar_G_VHRatio_StartingPitcher_Strikes_5G = "G_VHRatio_StartingPitcher_Strikes_5G"
dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G = "G_VHRatio_StartingPitcher_StrikeAccuracy_5G"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G"
dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G = "G_VHRatio_StartingPitcher_ScoreImpact_5G"
dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G = "G_VHRatio_StartingPitcher_StrikeoutsImpact_5G"
dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G = "G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G"
dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G = "G_VHRatio_StartingPitcher_HitsImpact_5G"
dbvar_G_VHRatio_StartingPitcher_NPImpact_5G = "G_VHRatio_StartingPitcher_NPImpact_5G"
dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G = "G_VHRatio_StartingPitcher_InningsPitchedImpact_5G"
dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G = "G_VHRatio_StartingPitcher_StrikesImpact_5G"
dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G = "G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G"
dbvar_G_VHRatio_BallpenOuts = "G_VHRatio_BallpenOuts"
dbvar_G_VHRatio_BallpenOuts_5G = "G_VHRatio_BallpenOuts_5G"
dbvar_G_VHRatio_BallpenOuts_YTD = "G_VHRatio_BallpenOuts_YTD"
dbvar_G_VHRatio_BallpenERA_Approx = "G_VHRatio_BallpenERA_Approx"
dbvar_G_VHRatio_BallpenERA_Approx_5G = "G_VHRatio_BallpenERA_Approx_5G"
dbvar_G_VHRatio_BallpenERA_Approx_YTD = "G_VHRatio_BallpenERA_Approx_YTD"
dbvar_G_Ivan_BP_DefenseProbability = "G_Ivan_BP_DefenseProbability"
dbvar_G_Ivan_BP_OffenseProbability = "G_Ivan_BP_OffenseProbability"
dbvar_G_Ivan_BP_NullProbability = "G_Ivan_BP_NullProbability"
dbvar_G_Ivan_BP_NoLineProbability = "G_Ivan_BP_NoLineProbability"
dbvar_G_H_AdjBookieProbabilityLine = "G_H_AdjBookieProbabilityLine"
dbvar_G_PH_Win = "G_PH_Win"
dbvar_G_PV_Win = "G_PV_Win"
dbvar_G_H_Runs = "G_H_Runs"
dbvar_G_H_Run_Prediction = "G_H_Run_Prediction"
dbvar_G_V_Runs = "G_V_Runs"
dbvar_G_V_Run_Prediction = "G_V_Run_Prediction"
dbvar_G_Actual_Runs_Diff = "G_Actual_Runs_Diff"
dbvar_G_ABSActual_Runs_Diff = "G_ABSActual_Runs_Diff"
dbvar_G_ABSActual_Runs_DiffCategory = "G_ABSActual_Runs_DiffCategory"
dbvar_G_Total = "G_Total"
dbvar_G_BookieAdjustedTotal = "G_BookieAdjustedTotal"
dbvar_G_Total_IsOver = "G_Total_IsOver"
dbvar_G_Bookie_Prob_Bet = "G_Bookie_Prob_Bet"
dbvar_G_Bookie_FaveWin = "G_Bookie_FaveWin"
dbvar_G_Bookie_DogWin = "G_Bookie_DogWin"

dbvar_MLB_Date_Format = '%Y%m%d'
## Variables need to be read into a data struct from a JSON file with various bits set eg is_Primitive, is_SP etc
MLBdb_vars =    [  
                    dbvar_G_Id,
                    dbvar_G_Date,
                    dbvar_G_Year,
                    dbvar_G_Month,
                    dbvar_G_Day,
                    dbvar_G_MonthWeek,
                    dbvar_G_Opening_TotalOver,
                    dbvar_G_Opening_TotalOverLine,
                    dbvar_G_Closing_TotalOver,
                    dbvar_G_Closing_TotalOverLine,
                    dbvar_G_Bookie_TotalOver,
                    dbvar_G_Bookie_TotalOverLine,
                    dbvar_G_NightGame,
                    dbvar_G_H_Id,
                    dbvar_G_Bookie_H_MoneyLine,
                    dbvar_G_Bookie_H_Probability,
                    dbvar_G_H_Opening_MoneyLine,
                    dbvar_G_H_OpeningProbabilityLine,
                    dbvar_G_H_Closing_MoneyLine,
                    dbvar_G_H_ClosingProbabilityLine,
                    dbvar_G_H_CLL_OPL_Prob_Diff,
                    dbvar_G_H_ParkImpactFactor,
                    dbvar_G_H_League,
                    dbvar_G_H_Division,
                    dbvar_G_H_LeagueDiv,
                    dbvar_G_H_Same_LeagueDiv,
                    dbvar_G_H_Same_Div,
                    dbvar_G_H_DaysRest,
                    dbvar_G_H_ContiguousGamesV,
                    dbvar_G_H_ContiguousGamesH,
                    dbvar_G_H_TotalDistanceTravelled_3G,
                    dbvar_G_H_Prev1_Id,
                    dbvar_G_H_Prev1_LeagueDiv,
                    dbvar_G_H_Prev1_SameLeagueDiv,
                    dbvar_G_H_Prev1_SameDiv,
                    dbvar_G_H_Prev1_DistanceTravelled,
                    dbvar_G_H_Prev1Home,
                    dbvar_G_H_Prev1Strength,
                    dbvar_G_H_Prev1StrengthRatio,
                    dbvar_G_H_Prev1Win,
                    dbvar_G_H_Prev1CLL,
                    dbvar_G_H_Prev1_Summary,
                    dbvar_G_H_Prev2_Id,
                    dbvar_G_H_Prev2_LeagueDiv,
                    dbvar_G_H_Prev2_SameLeagueDiv,
                    dbvar_G_H_Prev2_SameDiv,
                    dbvar_G_H_Prev2_DistanceTravelled,
                    dbvar_G_H_Prev2Home,
                    dbvar_G_H_Prev2Strength,
                    dbvar_G_H_Prev2StrengthRatio,
                    dbvar_G_H_Prev2Win,
                    dbvar_G_H_Prev2CLL,
                    dbvar_G_H_Prev2_Summary,
                    dbvar_G_H_Prev3_Id,
                    dbvar_G_H_Prev3_LeagueDiv,
                    dbvar_G_H_Prev3_SameLeagueDiv,
                    dbvar_G_H_Prev3_SameDiv,
                    dbvar_G_H_Prev3_DistanceTravelled,
                    dbvar_G_H_Prev3Home,
                    dbvar_G_H_Prev3Strength,
                    dbvar_G_H_Prev3StrengthRatio,
                    dbvar_G_H_Prev3Win,
                    dbvar_G_H_Prev3CLL,
                    dbvar_G_H_Prev3_Summary,
                    dbvar_G_H_Lookback_Strength,
                    dbvar_G_H_Next1_Id,
                    dbvar_G_H_Next1_LeagueDiv,
                    dbvar_G_H_Next1_SameLeagueDiv,
                    dbvar_G_H_Next1_SameDiv,
                    dbvar_G_H_Next1_DistanceTravelled,
                    dbvar_G_H_Next1Home,
                    dbvar_G_H_Next1Strength,
                    dbvar_G_H_Next1StrengthRatio,
                    dbvar_G_H_Next1_Summary,
                    dbvar_G_H_Next2_Id,
                    dbvar_G_H_Next2_LeagueDiv,
                    dbvar_G_H_Next2_SameLeagueDiv,
                    dbvar_G_H_Next2_SameDiv,
                    dbvar_G_H_Next2_DistanceTravelled,
                    dbvar_G_H_Next2Home,
                    dbvar_G_H_Next2Strength,
                    dbvar_G_H_Next2StrengthRatio,
                    dbvar_G_H_Next2_Summary,
                    dbvar_G_H_Next3_Id,
                    dbvar_G_H_Next3_LeagueDiv,
                    dbvar_G_H_Next3_SameLeagueDiv,
                    dbvar_G_H_Next3_SameDiv,
                    dbvar_G_H_Next3_DistanceTravelled,
                    dbvar_G_H_Next3Home,
                    dbvar_G_H_Next3Strength,
                    dbvar_G_H_Next3StrengthRatio,
                    dbvar_G_H_Next3_Summary,
                    dbvar_G_H_Lookahead_Strength,
                    dbvar_H_ClosingProbabilityLine_HV,
                    dbvar_H_ClosingProbabilityLine_YTD_HV,
                    dbvar_H_Runs_Gained,
                    dbvar_H_Runs_Allowed,
                    dbvar_H_Run_Strength,
                    dbvar_H_Run_Efficiency,
                    dbvar_H_Run_Pythag,
                    dbvar_H_Runs_Gained_5G,
                    dbvar_H_Runs_Allowed_5G,
                    dbvar_H_Run_Strength_5G,
                    dbvar_H_Run_Efficiency_5G,
                    dbvar_H_Run_Pythag_5G,
                    dbvar_H_Runs_Gained_20G,
                    dbvar_H_Runs_Allowed_20G,
                    dbvar_H_Run_Strength_20G,
                    dbvar_H_Run_Efficiency_20G,
                    dbvar_H_Run_Pythag_20G,
                    dbvar_H_Runs_Gained_Sum,
                    dbvar_H_Runs_Allowed_Sum,
                    dbvar_H_Run_Strength_Sum,
                    dbvar_H_Run_Efficiency_Sum,
                    dbvar_H_Run_Pythag_Sum,
                    dbvar_H_Runs_Gained_Sum_5G,
                    dbvar_H_Runs_Allowed_Sum_5G,
                    dbvar_H_Run_Strength_Sum_5G,
                    dbvar_H_Run_Efficiency_Sum_5G,
                    dbvar_H_Runs_Gained_Sum_20G,
                    dbvar_H_Runs_Allowed_Sum_20G,
                    dbvar_H_Run_Strength_Sum_20G,
                    dbvar_H_Run_Efficiency_Sum_20G,
                    dbvar_H_Runs_Gained_Sum_HV,
                    dbvar_H_Runs_Allowed_Sum_HV,
                    dbvar_H_Run_Strength_Sum_HV,
                    dbvar_H_Runs_Gained_HV,
                    dbvar_H_Runs_Allowed_HV,
                    dbvar_H_Run_Strength_HV,
                    dbvar_H_Runs_Gained_YTD,
                    dbvar_H_Runs_Allowed_YTD,
                    dbvar_H_Run_Strength_YTD,
                    dbvar_H_Run_Pythag_YTD,
                    dbvar_H_Runs_Gained_YTD_HV,
                    dbvar_H_Runs_Allowed_YTD_HV,
                    dbvar_H_Run_Strength_YTD_HV,
                    dbvar_H_Runs_5InningsGained,
                    dbvar_H_Runs_5InningsAllowed,
                    dbvar_H_Run_5InningsStrength,
                    dbvar_H_Run_5InningsEfficiency,
                    dbvar_H_Runs_5InningsGained_Sum,
                    dbvar_H_Runs_5InningsAllowed_Sum,
                    dbvar_H_Run_5InningsStrength_Sum,
                    dbvar_H_Run_5InningsEfficiency_Sum,
                    dbvar_H_Runs_5InningsGained_5G,
                    dbvar_H_Runs_5InningsAllowed_5G,
                    dbvar_H_Run_5InningsStrength_5G,
                    dbvar_H_Run_5InningsEfficiency_5G,
                    dbvar_H_Runs_5InningsGained_Sum_5G,
                    dbvar_H_Runs_5InningsAllowed_Sum_5G,
                    dbvar_H_Run_5InningsStrength_Sum_5G,
                    dbvar_H_Run_5InningsEfficiency_Sum_5G,
                    dbvar_H_Runs_5InningsGained_20G,
                    dbvar_H_Runs_5InningsAllowed_20G,
                    dbvar_H_Run_5InningsStrength_20G,
                    dbvar_H_Run_5InningsEfficiency_20G,
                    dbvar_H_Runs_5InningsGained_Sum_20G,
                    dbvar_H_Runs_5InningsAllowed_Sum_20G,
                    dbvar_H_Run_5InningsStrength_Sum_20G,
                    dbvar_H_Run_5InningsEfficiency_Sum_20G,
                    dbvar_H_Runs_5InningsGained_Sum_HV,
                    dbvar_H_Runs_5InningsAllowed_Sum_HV,
                    dbvar_H_Run_5InningsStrength_Sum_HV,
                    dbvar_H_Runs_5InningsGained_HV,
                    dbvar_H_Runs_5InningsAllowed_HV,
                    dbvar_H_Run_5InningsStrength_HV,
                    dbvar_H_Runs_5InningsGained_YTD,
                    dbvar_H_Runs_5InningsAllowed_YTD,
                    dbvar_H_Run_5InningsStrength_YTD,
                    dbvar_H_Pythag_Luck_Factor,
                    dbvar_H_Pythag_Luck_Factor_5G,
                    dbvar_H_Pythag_Luck_Factor_20G,
                    dbvar_H_Pythag_Luck_Factor_YTD,
                    dbvar_H_Run_Differential_Per_Game,
                    dbvar_H_Run_Differential_Per_Game_5G,
                    dbvar_H_Run_Differential_Per_Game_20G,
                    dbvar_H_Run_Differential_Per_Game_YTD,
                    dbvar_H_Weighted_Offense_Index,
                    dbvar_H_Weighted_Offense_Index_5G,
                    dbvar_H_Weighted_Offense_Index_20G,
                    dbvar_H_Weighted_Offense_Index_YTD,
                    dbvar_H_At_Bat,
                    dbvar_H_At_Bat_5G,
                    dbvar_H_At_Bat_20G,
                    dbvar_H_At_Bat_YTD,
                    dbvar_H_At_Bat_HV,
                    dbvar_H_At_Bat_YTD_HV,
                    dbvar_H_OBP,
                    dbvar_H_OBP_5G,
                    dbvar_H_OBP_20G,
                    dbvar_H_OBP_YTD,
                    dbvar_H_SLG,
                    dbvar_H_SLG_5G,
                    dbvar_H_SLG_20G,
                    dbvar_H_SLG_YTD,
                    dbvar_H_wOBA,
                    dbvar_H_wOBA_5G,
                    dbvar_H_wOBA_20G,
                    dbvar_H_wOBA_YTD,
                    dbvar_H_OPS,
                    dbvar_H_OPS_5G,
                    dbvar_H_OPS_20G,
                    dbvar_H_OPS_YTD,
                    dbvar_H_Wins,
                    dbvar_H_Losses,
                    dbvar_H_WinLoss_Strength,
                    dbvar_H_Wins_5G,
                    dbvar_H_Losses_5G,
                    dbvar_H_WinLoss_Strength_5G,
                    dbvar_H_Wins_20G,
                    dbvar_H_Losses_20G,
                    dbvar_H_WinLoss_Strength_20G,
                    dbvar_H_Wins_HV,
                    dbvar_H_Losses_HV,
                    dbvar_H_WinLoss_Strength_HV,
                    dbvar_H_Wins_YTD,
                    dbvar_H_Losses_YTD,
                    dbvar_H_WinLoss_Strength_YTD,
                    dbvar_H_Wins_YTD_HV,
                    dbvar_H_Losses_YTD_HV,
                    dbvar_H_WinLoss_Strength_YTD_HV,
                    dbvar_H_OutsPitched_Sum,
                    dbvar_H_OutsPitched,
                    dbvar_H_OutsPitched_5G,
                    dbvar_H_OutsPitched_20G,
                    dbvar_H_OutsPitched_YTD,
                    dbvar_H_OutsPitched_YTD_HV,
                    dbvar_H_StrikeoutsAllowed,
                    dbvar_H_StrikeoutsGained,
                    dbvar_H_StrikeoutAccuracy,
                    dbvar_H_StrikeoutsAllowed_Sum,
                    dbvar_H_StrikeoutsGained_Sum,
                    dbvar_H_StrikeoutAccuracy_Sum,
                    dbvar_H_StrikeoutsAllowed_5G,
                    dbvar_H_StrikeoutsGained_5G,
                    dbvar_H_StrikeoutAccuracy_5G,
                    dbvar_H_StrikeoutsGained_20G,
                    dbvar_H_StrikeoutsAllowed_YTD,
                    dbvar_H_StrikeoutsGained_YTD,
                    dbvar_H_StrikeoutAccuracy_YTD,
                    dbvar_H_StrikeoutsAllowed_YTD_HV,
                    dbvar_H_StrikeoutsGained_YTD_HV,
                    dbvar_H_StrikeoutAccuracy_YTD_HV,
                    dbvar_H_Hits_Sum,
                    dbvar_H_Hits,
                    dbvar_H_Hits_Sum_5G,
                    dbvar_H_Hits_5G,
                    dbvar_H_Hits_Sum_20G,
                    dbvar_H_Hits_20G,
                    dbvar_H_Hits_YTD,
                    dbvar_H_Hits_YTD_HV,
                    dbvar_H_HitsAllowed_Sum,
                    dbvar_H_HitsAllowed_Sum_5G,
                    dbvar_H_HitsAllowed_Sum_20G,
                    dbvar_H_HitsAllowed,
                    dbvar_H_HitsAllowed_5G,
                    dbvar_H_HitsAllowed_20G,
                    dbvar_H_HitsAllowed_YTD,
                    dbvar_H_HitsAllowed_YTD_HV,
                    dbvar_H_RunsHitsRatio,
                    dbvar_H_RunsHitsRatio_Sum,
                    dbvar_H_RunsHitsRatio_5G,
                    dbvar_H_RunsHitsRatio_Sum_5G,
                    dbvar_H_RunsHitsRatio_20G,
                    dbvar_H_RunsHitsRatio_Sum_20G,
                    dbvar_H_RunsHitsRatio_YTD,
                    dbvar_H_RunsHitsRatio_Allowed,
                    dbvar_H_RunsHitsRatio_Allowed_Sum,
                    dbvar_H_RunsHitsRatio_Allowed_5G,
                    dbvar_H_RunsHitsRatio_Allowed_Sum_5G,
                    dbvar_H_RunsHitsRatio_Allowed_20G,
                    dbvar_H_RunsHitsRatio_Allowed_Sum_20G,
                    dbvar_H_RunsHitsRatio_Allowed_YTD,
                    dbvar_H_FIP,
                    dbvar_H_FIP_5G,
                    dbvar_H_FIP_YTD,
                    dbvar_H_FIP_YTD_HV,
                    dbvar_H_K_Minus_BB_Pct,
                    dbvar_H_K_Minus_BB_Pct_5G,
                    dbvar_H_K_Minus_BB_Pct_20G,
                    dbvar_H_K_Minus_BB_Pct_YTD,
                    dbvar_H_HR_Per_9_Allowed,
                    dbvar_H_HR_Per_9_Allowed_5G,
                    dbvar_H_HR_Per_9_Allowed_20G,
                    dbvar_H_HR_Per_9_Allowed_YTD,
                    dbvar_H_K_Per_9,
                    dbvar_H_K_Per_9_5G,
                    dbvar_H_K_Per_9_20G,
                    dbvar_H_K_Per_9_YTD,
                    dbvar_H_WalksAllowed_Sum,
                    dbvar_H_WalksAllowed,
                    dbvar_H_WalksAllowed_Sum_5G,
                    dbvar_H_WalksAllowed_5G,
                    dbvar_H_WalksAllowed_Sum_20G,
                    dbvar_H_WalksAllowed_20G,
                    dbvar_H_WalksAllowed_YTD,
                    dbvar_H_WalksAllowed_YTD_HV,
                    dbvar_H_WalksGained_Sum,
                    dbvar_H_WalksGained,
                    dbvar_H_WalksGained_5G,
                    dbvar_H_WalksGained_20G,
                    dbvar_H_WalksGained_YTD,
                    dbvar_H_WalksGained_YTD_HV,
                    dbvar_H_HomeRuns_Sum,
                    dbvar_H_HomeRuns,
                    dbvar_H_HomeRuns_5G,
                    dbvar_H_HomeRuns_Sum_5G,
                    dbvar_H_HomeRuns_20G,
                    dbvar_H_HomeRuns_Sum_20G,
                    dbvar_H_HomeRuns_YTD,
                    dbvar_H_HomeRuns_YTD_HV,
                    dbvar_H_HomeRuns_Allowed_Sum,
                    dbvar_H_HomeRuns_Allowed,
                    dbvar_H_HomeRuns_Allowed_5G,
                    dbvar_H_HomeRuns_Allowed_20G,
                    dbvar_H_HomeRuns_Allowed_YTD,
                    dbvar_H_HomeRuns_Allowed_YTD_HV,
                    dbvar_H_5thInnScore,
                    dbvar_H_Duration,
                    dbvar_H_OverTime,
                    dbvar_H_NP_Sum,
                    dbvar_H_NP,
                    dbvar_H_NP_5G,
                    dbvar_H_NP_YTD,
                    dbvar_H_NP_YTD_HV,
                    dbvar_H_Strikes_Sum,
                    dbvar_H_StrikeAccuracy_Sum,
                    dbvar_H_Strikes,
                    dbvar_H_StrikeAccuracy,
                    dbvar_H_Strikes_5G,
                    dbvar_H_StrikeAccuracy_5G,
                    dbvar_H_Strikes_YTD,
                    dbvar_H_StrikeAccuracy_YTD,
                    dbvar_H_Strikes_YTD_HV,
                    dbvar_H_StrikeAccuracy_YTD_HV,
                    dbvar_H_MenOnBase,
                    dbvar_H_MenOnBase_Strength,
                    dbvar_H_MenOnBase_Efficiency,
                    dbvar_H_MenOnBase_5G,
                    dbvar_H_MenOnBase_Strength_5G,
                    dbvar_H_MenOnBase_Efficiency_5G,
                    dbvar_H_MenOnBase_20G,
                    dbvar_H_MenOnBase_Strength_20G,
                    dbvar_H_MenOnBase_Efficiency_20G,
                    dbvar_H_MenOnBase_YTD,
                    dbvar_H_MenOnBase_Strength_YTD,
                    dbvar_H_MenOnBase_Efficiency_YTD,
                    dbvar_H_MenOnBase_Allowed,
                    dbvar_H_MenOnBase_Allowed_Efficiency,
                    dbvar_H_MenOnBase_Allowed_5G,
                    dbvar_H_MenOnBase_Allowed_Efficiency_5G,
                    dbvar_H_MenOnBase_Allowed_20G,
                    dbvar_H_MenOnBase_Allowed_Efficiency_20G,
                    dbvar_H_MenOnBase_Allowed_YTD,
                    dbvar_H_MenOnBase_Allowed_Efficiency_YTD,
                    dbvar_H_LeftOnBase_Sum,
                    dbvar_H_LeftOnBase,
                    dbvar_H_2BRuns_Sum,
                    dbvar_H_2BRuns,
                    dbvar_H_2BRuns_Sum_5G,
                    dbvar_H_2BRuns_5G,
                    dbvar_H_2BRuns_Sum_20G,
                    dbvar_H_2BRuns_20G,
                    dbvar_H_2BRuns_YTD,
                    dbvar_H_2BRuns_Allowed,
                    dbvar_H_2BRuns_Allowed_5G,
                    dbvar_H_2BRuns_Allowed_20G,
                    dbvar_H_2BRuns_Allowed_YTD,
                    dbvar_H_2BRuns_Strength,
                    dbvar_H_2BRuns_Strength_5G,
                    dbvar_H_2BRuns_Strength_20G,
                    dbvar_H_2BRuns_Strength_YTD,
                    dbvar_H_3BRuns_Sum,
                    dbvar_H_3BRuns,
                    dbvar_H_3BRuns_5G,
                    dbvar_H_3BRuns_20G,
                    dbvar_H_3BRuns_YTD,
                    dbvar_H_3BRuns_Allowed,
                    dbvar_H_3BRuns_Allowed_5G,
                    dbvar_H_3BRuns_Allowed_20G,
                    dbvar_H_3BRuns_Allowed_YTD,
                    dbvar_H_3BRuns_Strength,
                    dbvar_H_3BRuns_Strength_5G,
                    dbvar_H_3BRuns_Strength_20G,
                    dbvar_H_3BRuns_Strength_YTD,
                    dbvar_H_ErrorMade_Sum,
                    dbvar_H_ErrorMade,
                    dbvar_H_ErrorMade_Sum_5G,
                    dbvar_H_ErrorMade_5G,
                    dbvar_H_ErrorMade_Sum_20G,
                    dbvar_H_ErrorMade_20G,
                    dbvar_H_ErrorMade_YTD,
                    dbvar_H_ErrorMade_YTD_HV,
                    dbvar_H_ErrorForced_Sum,
                    dbvar_H_ErrorForced,
                    dbvar_H_ErrorForced_Sum_5G,
                    dbvar_H_ErrorForced_5G,
                    dbvar_H_ErrorForced_Sum_20G,
                    dbvar_H_ErrorForced_20G,
                    dbvar_H_ErrorForced_YTD,
                    dbvar_H_HitsByPitch_Sum,
                    dbvar_H_HitsByPitch,
                    dbvar_H_HitsByPitch_Sum_5G,
                    dbvar_H_HitsByPitch_5G,
                    dbvar_H_HitsByPitch_Sum_20G,
                    dbvar_H_HitsByPitch_20G,
                    dbvar_H_HitsByPitch_YTD,
                    dbvar_H_HitsByPitch_Allowed,
                    dbvar_H_HitsByPitch_Allowed_5G,
                    dbvar_H_HitsByPitch_Allowed_20G,
                    dbvar_H_HitsByPitch_Allowed_YTD,
                    dbvar_H_DoublePlays_Gained_Sum,
                    dbvar_H_DoublePlays_Gained,
                    dbvar_H_DoublePlays_Gained_Sum_5G,
                    dbvar_H_DoublePlays_Gained_5G,
                    dbvar_H_DoublePlays_Gained_Sum_20G,
                    dbvar_H_DoublePlays_Gained_20G,
                    dbvar_H_DoublePlays_Gained_YTD,
                    dbvar_H_DoublePlays_Gained_YTD_HV,
                    dbvar_H_DoublePlays_Allowed,
                    dbvar_H_DoublePlays_Allowed_5G,
                    dbvar_H_DoublePlays_Allowed_20G,
                    dbvar_H_DoublePlays_Allowed_YTD,
                    dbvar_H_DoublePlays_Allowed_YTD_HV,
                    dbvar_H_ReliefPitchers,
                    dbvar_H_TotalBases_Sum,
                    dbvar_H_TotalBases,
                    dbvar_H_TotalBases_5G,
                    dbvar_H_TotalBases_20G,
                    dbvar_H_TotalBases_YTD,
                    dbvar_H_MenOnBaseTBRatio,
                    dbvar_H_MenOnBaseTBRatio_5G,
                    dbvar_H_WalkStrikeoutRatio_Sum,
                    dbvar_H_WalkStrikeoutRatio,
                    dbvar_H_PowerHits_Sum,
                    dbvar_H_PowerHits,
                    dbvar_H_PowerHits_5G,
                    dbvar_H_Innings_OutPitched_Sum,
                    dbvar_H_Innings_OutPitched,
                    dbvar_H_Innings_OutPitched_Sum_5G,
                    dbvar_H_Innings_OutPitched_5G,
                    dbvar_H_Innings_OutPitched_YTD,
                    dbvar_H_SP_HitsAllowed_Sum,
                    dbvar_H_SP_HitsAllowed,
                    dbvar_H_SP_HitsAllowed_5G,
                    dbvar_H_SP_HitsAllowed_YTD,
                    dbvar_H_EarnedRuns_Sum,
                    dbvar_H_EarnedRunAvg_Sum,
                    dbvar_H_EarnedRuns,
                    dbvar_H_EarnedRunAvg,
                    dbvar_H_EarnedRuns_Sum_5G,
                    dbvar_H_EarnedRunAvg_Sum_5G,
                    dbvar_H_EarnedRuns_5G,
                    dbvar_H_EarnedRunAvg_5G,
                    dbvar_H_EarnedRuns_YTD,
                    dbvar_H_EarnedRunAvg_YTD,
                    dbvar_H_HitsAllowedPer9Innings_Sum,
                    dbvar_H_HitsAllowedPer9Innings,
                    dbvar_H_HitsAllowedPer9Innings_5G,
                    dbvar_H_WalksHitsAllowedPerInning,
                    dbvar_H_WalksHitsAllowedPerInning_5G,
                    dbvar_H_WalksHitsAllowedPerInning_YTD,
                    dbvar_G_H_StartingPitcher_Id,
                    dbvar_H_StartingPitcher_DaysRest,
                    dbvar_H_StartingPitcher_Score_All,
                    dbvar_H_StartingPitcher_Strikeouts_All,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_All,
                    dbvar_H_StartingPitcher_BaseOnBalls_All,
                    dbvar_H_StartingPitcher_Hits_All,
                    dbvar_H_StartingPitcher_NP_All,
                    dbvar_H_StartingPitcher_InningsPitched_All,
                    dbvar_H_StartingPitcher_Strikes_All,
                    dbvar_H_StartingPitcher_StrikeAccuracy_All,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All,
                    dbvar_H_StartingPitcher_Score_YTD,
                    dbvar_H_StartingPitcher_Strikeouts_YTD,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD,
                    dbvar_H_StartingPitcher_BaseOnBalls_YTD,
                    dbvar_H_StartingPitcher_Hits_YTD,
                    dbvar_H_StartingPitcher_NP_YTD,
                    dbvar_H_StartingPitcher_InningsPitched_YTD,
                    dbvar_H_StartingPitcher_Strikes_YTD,
                    dbvar_H_StartingPitcher_StrikeAccuracy_YTD,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                    dbvar_H_StartingPitcher_ScoreImpact_YTD,
                    dbvar_H_StartingPitcher_StrikeoutsImpact_YTD,
                    dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD,
                    dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                    dbvar_H_StartingPitcher_HitsImpact_YTD,
                    dbvar_H_StartingPitcher_NPImpact_YTD,
                    dbvar_H_StartingPitcher_InningsPitchedImpact_YTD,
                    dbvar_H_StartingPitcher_StrikeImpact_YTD,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                    dbvar_H_StartingPitcher_Score_5G,
                    dbvar_H_StartingPitcher_Strikeouts_5G,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_5G,
                    dbvar_H_StartingPitcher_BaseOnBalls_5G,
                    dbvar_H_StartingPitcher_Hits_5G,
                    dbvar_H_StartingPitcher_NP_5G,
                    dbvar_H_StartingPitcher_InningsPitched_5G,
                    dbvar_H_StartingPitcher_Strikes_5G,
                    dbvar_H_StartingPitcher_StrikeAccuracy_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G,
                    dbvar_H_StartingPitcher_ScoreImpact_5G,
                    dbvar_H_StartingPitcher_StrikeoutsImpact_5G,
                    dbvar_H_StartingPitcher_BaseOnBallsImpact_5G,
                    dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                    dbvar_H_StartingPitcher_HitsImpact_5G,
                    dbvar_H_StartingPitcher_NPImpact_5G,
                    dbvar_H_StartingPitcher_InningsPitchedImpact_5G,
                    dbvar_H_StartingPitcher_StrikeImpact_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                    dbvar_H_StartingPitcher_Score_Ratio,
                    dbvar_H_StartingPitcher_Strikeouts_Ratio,
                    dbvar_H_StartingPitcher_BaseOnBalls_Ratio,
                    dbvar_H_StartingPitcher_Hits_Ratio,
                    dbvar_H_StartingPitcher_NP_Ratio,
                    dbvar_H_StartingPitcher_InningsPitched_Ratio,
                    dbvar_H_StartingPitcher_Strikes_Ratio,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                    dbvar_H_StartingPitcher_Score_Ratio_5G,
                    dbvar_H_StartingPitcher_Strikeouts_Ratio_5G,
                    dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G,
                    dbvar_H_StartingPitcher_Hits_Ratio_5G,
                    dbvar_H_StartingPitcher_NP_Ratio_5G,
                    dbvar_H_StartingPitcher_InningsPitched_Ratio_5G,
                    dbvar_H_StartingPitcher_Strikes_Ratio_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                    dbvar_H_BallpenOuts,
                    dbvar_H_BallpenOuts_5G,
                    dbvar_H_BallpenOuts_YTD,
                    dbvar_H_BallpenERA_Approx,
                    dbvar_H_BallpenERA_Approx_5G,
                    dbvar_H_BallpenERA_Approx_YTD,
                    dbvar_G_V_Id,
                    dbvar_G_V_ParkImpactFactor,
                    dbvar_G_Bookie_V_MoneyLine,
                    dbvar_G_Bookie_V_Probability,
                    dbvar_G_V_Opening_MoneyLine,
                    dbvar_G_V_OpeningProbabilityLine,
                    dbvar_G_V_Closing_MoneyLine,
                    dbvar_G_V_ClosingProbabilityLine,
                    dbvar_G_V_CLL_OPL_Prob_Diff,
                    dbvar_G_V_League,
                    dbvar_G_V_Division,
                    dbvar_G_V_LeagueDiv,
                    dbvar_G_V_Same_LeagueDiv,
                    dbvar_G_V_Same_Div,
                    dbvar_G_V_DaysRest,
                    dbvar_G_V_DistanceTravelled,
                    dbvar_G_V_ContiguousGamesV,
                    dbvar_G_V_ContiguousGamesH,
                    dbvar_G_V_TotalDistanceTravelled_3G,
                    dbvar_G_V_Prev1_Id,
                    dbvar_G_V_Prev1_LeagueDiv,
                    dbvar_G_V_Prev1_SameLeagueDiv,
                    dbvar_G_V_Prev1_SameDiv,
                    dbvar_G_V_Prev1_DistanceTravelled,
                    dbvar_G_V_Prev1Home,
                    dbvar_G_V_Prev1Strength,
                    dbvar_G_V_Prev1StrengthRatio,
                    dbvar_G_V_Prev1Win,
                    dbvar_G_V_Prev1CLL,
                    dbvar_G_V_Prev1_Summary,
                    dbvar_G_V_Prev2_Id,
                    dbvar_G_V_Prev2_LeagueDiv,
                    dbvar_G_V_Prev2_SameLeagueDiv,
                    dbvar_G_V_Prev2_SameDiv,
                    dbvar_G_V_Prev2_DistanceTravelled,
                    dbvar_G_V_Prev2Home,
                    dbvar_G_V_Prev2Strength,
                    dbvar_G_V_Prev2StrengthRatio,
                    dbvar_G_V_Prev2Win,
                    dbvar_G_V_Prev2CLL,
                    dbvar_G_V_Prev2_Summary,
                    dbvar_G_V_Prev3_Id,
                    dbvar_G_V_Prev3_LeagueDiv,
                    dbvar_G_V_Prev3_SameLeagueDiv,
                    dbvar_G_V_Prev3_SameDiv,
                    dbvar_G_V_Prev3_DistanceTravelled,
                    dbvar_G_V_Prev3Home,
                    dbvar_G_V_Prev3Strength,
                    dbvar_G_V_Prev3StrengthRatio,
                    dbvar_G_V_Prev3Win,
                    dbvar_G_V_Prev3CLL,
                    dbvar_G_V_Prev3_Summary,
                    dbvar_G_V_Lookback_Strength,
                    dbvar_G_V_Next1_Id,
                    dbvar_G_V_Next1_LeagueDiv,
                    dbvar_G_V_Next1_SameLeagueDiv,
                    dbvar_G_V_Next1_SameDiv,
                    dbvar_G_V_Next1_DistanceTravelled,
                    dbvar_G_V_Next1Home,
                    dbvar_G_V_Next1Strength,
                    dbvar_G_V_Next1StrengthRatio,
                    dbvar_G_V_Next1_Summary,
                    dbvar_G_V_Next2_Id,
                    dbvar_G_V_Next2_LeagueDiv,
                    dbvar_G_V_Next2_SameLeagueDiv,
                    dbvar_G_V_Next2_SameDiv,
                    dbvar_G_V_Next2_DistanceTravelled,
                    dbvar_G_V_Next2Home,
                    dbvar_G_V_Next2Strength,
                    dbvar_G_V_Next2StrengthRatio,
                    dbvar_G_V_Next2_Summary,
                    dbvar_G_V_Next3_Id,
                    dbvar_G_V_Next3_LeagueDiv,
                    dbvar_G_V_Next3_SameLeagueDiv,
                    dbvar_G_V_Next3_SameDiv,
                    dbvar_G_V_Next3_DistanceTravelled,
                    dbvar_G_V_Next3Home,
                    dbvar_G_V_Next3Strength,
                    dbvar_G_V_Next3StrengthRatio,
                    dbvar_G_V_Next3_Summary,
                    dbvar_G_V_Lookahead_Strength,
                    dbvar_V_ClosingProbabilityLine_HV,
                    dbvar_V_ClosingProbabilityLine_YTD_HV,
                    dbvar_V_Runs_Gained,
                    dbvar_V_Runs_Allowed,
                    dbvar_V_Run_Strength,
                    dbvar_V_Run_Efficiency,
                    dbvar_V_Run_Pythag,
                    dbvar_V_Runs_Gained_5G,
                    dbvar_V_Runs_Allowed_5G,
                    dbvar_V_Run_Strength_5G,
                    dbvar_V_Run_Efficiency_5G,
                    dbvar_V_Run_Pythag_5G,
                    dbvar_V_Runs_Gained_20G,
                    dbvar_V_Runs_Allowed_20G,
                    dbvar_V_Run_Strength_20G,
                    dbvar_V_Run_Efficiency_20G,
                    dbvar_V_Run_Pythag_20G,
                    dbvar_V_Runs_Gained_Sum,
                    dbvar_V_Runs_Allowed_Sum,
                    dbvar_V_Run_Strength_Sum,
                    dbvar_V_Run_Efficiency_Sum,
                    dbvar_V_Run_Pythag_Sum,
                    dbvar_V_Runs_Gained_Sum_5G,
                    dbvar_V_Runs_Allowed_Sum_5G,
                    dbvar_V_Run_Strength_Sum_5G,
                    dbvar_V_Run_Efficiency_Sum_5G,
                    dbvar_V_Runs_Gained_Sum_20G,
                    dbvar_V_Runs_Allowed_Sum_20G,
                    dbvar_V_Run_Strength_Sum_20G,
                    dbvar_V_Run_Efficiency_Sum_20G,
                    dbvar_V_Runs_Gained_Sum_HV,
                    dbvar_V_Runs_Allowed_Sum_HV,
                    dbvar_V_Run_Strength_Sum_HV,
                    dbvar_V_Runs_Gained_HV,
                    dbvar_V_Runs_Allowed_HV,
                    dbvar_V_Run_Strength_HV,
                    dbvar_V_Runs_Gained_YTD,
                    dbvar_V_Runs_Allowed_YTD,
                    dbvar_V_Run_Strength_YTD,
                    dbvar_V_Run_Pythag_YTD,
                    dbvar_V_Runs_Gained_YTD_HV,
                    dbvar_V_Runs_Allowed_YTD_HV,
                    dbvar_V_Run_Strength_YTD_HV,
                    dbvar_V_Runs_5InningsGained,
                    dbvar_V_Runs_5InningsAllowed,
                    dbvar_V_Run_5InningsStrength,
                    dbvar_V_Run_5InningsEfficiency,
                    dbvar_V_Runs_5InningsGained_Sum,
                    dbvar_V_Runs_5InningsAllowed_Sum,
                    dbvar_V_Run_5InningsStrength_Sum,
                    dbvar_V_Run_5InningsEfficiency_Sum,
                    dbvar_V_Runs_5InningsGained_5G,
                    dbvar_V_Runs_5InningsAllowed_5G,
                    dbvar_V_Run_5InningsStrength_5G,
                    dbvar_V_Run_5InningsEfficiency_5G,
                    dbvar_V_Runs_5InningsGained_Sum_5G,
                    dbvar_V_Runs_5InningsAllowed_Sum_5G,
                    dbvar_V_Run_5InningsStrength_Sum_5G,
                    dbvar_V_Run_5InningsEfficiency_Sum_5G,
                    dbvar_V_Runs_5InningsGained_20G,
                    dbvar_V_Runs_5InningsAllowed_20G,
                    dbvar_V_Run_5InningsStrength_20G,
                    dbvar_V_Run_5InningsEfficiency_20G,
                    dbvar_V_Runs_5InningsGained_Sum_20G,
                    dbvar_V_Runs_5InningsAllowed_Sum_20G,
                    dbvar_V_Run_5InningsStrength_Sum_20G,
                    dbvar_V_Run_5InningsEfficiency_Sum_20G,
                    dbvar_V_Runs_5InningsGained_Sum_HV,
                    dbvar_V_Runs_5InningsAllowed_Sum_HV,
                    dbvar_V_Run_5InningsStrength_Sum_HV,
                    dbvar_V_Runs_5InningsGained_HV,
                    dbvar_V_Runs_5InningsAllowed_HV,
                    dbvar_V_Run_5InningsStrength_HV,
                    dbvar_V_Runs_5InningsGained_YTD,
                    dbvar_V_Runs_5InningsAllowed_YTD,
                    dbvar_V_Run_5InningsStrength_YTD,
                    dbvar_V_Pythag_Luck_Factor,
                    dbvar_V_Pythag_Luck_Factor_5G,
                    dbvar_V_Pythag_Luck_Factor_20G,
                    dbvar_V_Pythag_Luck_Factor_YTD,
                    dbvar_V_Run_Differential_Per_Game,
                    dbvar_V_Run_Differential_Per_Game_5G,
                    dbvar_V_Run_Differential_Per_Game_20G,
                    dbvar_V_Run_Differential_Per_Game_YTD,
                    dbvar_V_Weighted_Offense_Index,
                    dbvar_V_Weighted_Offense_Index_5G,
                    dbvar_V_Weighted_Offense_Index_20G,
                    dbvar_V_Weighted_Offense_Index_YTD,
                    dbvar_V_At_Bat,
                    dbvar_V_At_Bat_5G,
                    dbvar_V_At_Bat_20G,
                    dbvar_V_At_Bat_YTD,
                    dbvar_V_At_Bat_HV,
                    dbvar_V_At_Bat_YTD_HV,
                    dbvar_V_OBP,
                    dbvar_V_OBP_5G,
                    dbvar_V_OBP_20G,
                    dbvar_V_OBP_YTD,
                    dbvar_V_SLG,
                    dbvar_V_SLG_5G,
                    dbvar_V_SLG_20G,
                    dbvar_V_SLG_YTD,
                    dbvar_V_wOBA,
                    dbvar_V_wOBA_5G,
                    dbvar_V_wOBA_20G,
                    dbvar_V_wOBA_YTD,
                    dbvar_V_OPS,
                    dbvar_V_OPS_5G,
                    dbvar_V_OPS_20G,
                    dbvar_V_OPS_YTD,
                    dbvar_V_Wins,
                    dbvar_V_Losses,
                    dbvar_V_WinLoss_Strength,
                    dbvar_V_Wins_5G,
                    dbvar_V_Losses_5G,
                    dbvar_V_WinLoss_Strength_5G,
                    dbvar_V_Wins_20G,
                    dbvar_V_Losses_20G,
                    dbvar_V_WinLoss_Strength_20G,
                    dbvar_V_Wins_HV,
                    dbvar_V_Losses_HV,
                    dbvar_V_WinLoss_Strength_HV,
                    dbvar_V_Wins_YTD,
                    dbvar_V_Losses_YTD,
                    dbvar_V_WinLoss_Strength_YTD,
                    dbvar_V_Wins_YTD_HV,
                    dbvar_V_Losses_YTD_HV,
                    dbvar_V_WinLoss_Strength_YTD_HV,
                    dbvar_V_OutsPitched_Sum,
                    dbvar_V_OutsPitched,
                    dbvar_V_OutsPitched_5G,
                    dbvar_V_OutsPitched_20G,
                    dbvar_V_OutsPitched_YTD,
                    dbvar_V_OutsPitched_YTD_HV,
                    dbvar_V_StrikeoutsAllowed,
                    dbvar_V_StrikeoutsGained,
                    dbvar_V_StrikeoutAccuracy,
                    dbvar_V_StrikeoutsAllowed_Sum,
                    dbvar_V_StrikeoutsGained_Sum,
                    dbvar_V_StrikeoutAccuracy_Sum,
                    dbvar_V_StrikeoutsAllowed_5G,
                    dbvar_V_StrikeoutsGained_5G,
                    dbvar_V_StrikeoutAccuracy_5G,
                    dbvar_V_StrikeoutsGained_20G,
                    dbvar_V_StrikeoutsAllowed_YTD,
                    dbvar_V_StrikeoutsGained_YTD,
                    dbvar_V_StrikeoutAccuracy_YTD,
                    dbvar_V_StrikeoutsAllowed_YTD_HV,
                    dbvar_V_StrikeoutsGained_YTD_HV,
                    dbvar_V_StrikeoutAccuracy_YTD_HV,
                    dbvar_V_Hits_Sum,
                    dbvar_V_Hits,
                    dbvar_V_Hits_Sum_5G,
                    dbvar_V_Hits_5G,
                    dbvar_V_Hits_Sum_20G,
                    dbvar_V_Hits_20G,
                    dbvar_V_Hits_YTD,
                    dbvar_V_Hits_YTD_HV,
                    dbvar_V_HitsAllowed_Sum,
                    dbvar_V_HitsAllowed_Sum_5G,
                    dbvar_V_HitsAllowed_Sum_20G,
                    dbvar_V_HitsAllowed,
                    dbvar_V_HitsAllowed_5G,
                    dbvar_V_HitsAllowed_20G,
                    dbvar_V_HitsAllowed_YTD,
                    dbvar_V_HitsAllowed_YTD_HV,
                    dbvar_V_RunsHitsRatio,
                    dbvar_V_RunsHitsRatio_Sum,
                    dbvar_V_RunsHitsRatio_5G,
                    dbvar_V_RunsHitsRatio_Sum_5G,
                    dbvar_V_RunsHitsRatio_20G,
                    dbvar_V_RunsHitsRatio_Sum_20G,
                    dbvar_V_RunsHitsRatio_YTD,
                    dbvar_V_RunsHitsRatio_Allowed,
                    dbvar_V_RunsHitsRatio_Allowed_Sum,
                    dbvar_V_RunsHitsRatio_Allowed_5G,
                    dbvar_V_RunsHitsRatio_Allowed_Sum_5G,
                    dbvar_V_RunsHitsRatio_Allowed_20G,
                    dbvar_V_RunsHitsRatio_Allowed_Sum_20G,
                    dbvar_V_RunsHitsRatio_Allowed_YTD,
                    dbvar_V_FIP,
                    dbvar_V_FIP_5G,
                    dbvar_V_FIP_YTD,
                    dbvar_V_FIP_YTD_HV,
                    dbvar_V_K_Minus_BB_Pct,
                    dbvar_V_K_Minus_BB_Pct_5G,
                    dbvar_V_K_Minus_BB_Pct_20G,
                    dbvar_V_K_Minus_BB_Pct_YTD,
                    dbvar_V_HR_Per_9_Allowed,
                    dbvar_V_HR_Per_9_Allowed_5G,
                    dbvar_V_HR_Per_9_Allowed_20G,
                    dbvar_V_HR_Per_9_Allowed_YTD,
                    dbvar_V_K_Per_9,
                    dbvar_V_K_Per_9_5G,
                    dbvar_V_K_Per_9_20G,
                    dbvar_V_K_Per_9_YTD,
                    dbvar_V_WalksAllowed_Sum,
                    dbvar_V_WalksAllowed,
                    dbvar_V_WalksAllowed_Sum_5G,
                    dbvar_V_WalksAllowed_5G,
                    dbvar_V_WalksAllowed_Sum_20G,
                    dbvar_V_WalksAllowed_20G,
                    dbvar_V_WalksAllowed_YTD,
                    dbvar_V_WalksAllowed_YTD_HV,
                    dbvar_V_WalksGained_Sum,
                    dbvar_V_WalksGained,
                    dbvar_V_WalksGained_5G,
                    dbvar_V_WalksGained_20G,
                    dbvar_V_WalksGained_YTD,
                    dbvar_V_WalksGained_YTD_HV,
                    dbvar_V_HomeRuns_Sum,
                    dbvar_V_HomeRuns,
                    dbvar_V_HomeRuns_5G,
                    dbvar_V_HomeRuns_Sum_5G,
                    dbvar_V_HomeRuns_20G,
                    dbvar_V_HomeRuns_Sum_20G,
                    dbvar_V_HomeRuns_YTD,
                    dbvar_V_HomeRuns_YTD_HV,
                    dbvar_V_HomeRuns_Allowed_Sum,
                    dbvar_V_HomeRuns_Allowed,
                    dbvar_V_HomeRuns_Allowed_5G,
                    dbvar_V_HomeRuns_Allowed_20G,
                    dbvar_V_HomeRuns_Allowed_YTD,
                    dbvar_V_HomeRuns_Allowed_YTD_HV,
                    dbvar_V_5thInnScore,
                    dbvar_V_Duration,
                    dbvar_V_OverTime,
                    dbvar_V_NP_Sum,
                    dbvar_V_NP,
                    dbvar_V_NP_5G,
                    dbvar_V_NP_YTD,
                    dbvar_V_NP_YTD_HV,
                    dbvar_V_Strikes_Sum,
                    dbvar_V_StrikeAccuracy_Sum,
                    dbvar_V_Strikes,
                    dbvar_V_StrikeAccuracy,
                    dbvar_V_Strikes_5G,
                    dbvar_V_StrikeAccuracy_5G,
                    dbvar_V_Strikes_YTD,
                    dbvar_V_StrikeAccuracy_YTD,
                    dbvar_V_Strikes_YTD_HV,
                    dbvar_V_StrikeAccuracy_YTD_HV,
                    dbvar_V_MenOnBase,
                    dbvar_V_MenOnBase_Strength,
                    dbvar_V_MenOnBase_Efficiency,
                    dbvar_V_MenOnBase_5G,
                    dbvar_V_MenOnBase_Strength_5G,
                    dbvar_V_MenOnBase_Efficiency_5G,
                    dbvar_V_MenOnBase_20G,
                    dbvar_V_MenOnBase_Strength_20G,
                    dbvar_V_MenOnBase_Efficiency_20G,
                    dbvar_V_MenOnBase_YTD,
                    dbvar_V_MenOnBase_Strength_YTD,
                    dbvar_V_MenOnBase_Efficiency_YTD,
                    dbvar_V_MenOnBase_Allowed,
                    dbvar_V_MenOnBase_Allowed_Efficiency,
                    dbvar_V_MenOnBase_Allowed_5G,
                    dbvar_V_MenOnBase_Allowed_Efficiency_5G,
                    dbvar_V_MenOnBase_Allowed_20G,
                    dbvar_V_MenOnBase_Allowed_Efficiency_20G,
                    dbvar_V_MenOnBase_Allowed_YTD,
                    dbvar_V_MenOnBase_Allowed_Efficiency_YTD,
                    dbvar_V_LeftOnBase_Sum,
                    dbvar_V_LeftOnBase,
                    dbvar_V_2BRuns_Sum,
                    dbvar_V_2BRuns,
                    dbvar_V_2BRuns_Strength,
                    dbvar_V_2BRuns_Sum_5G,
                    dbvar_V_2BRuns_5G,
                    dbvar_V_2BRuns_Strength_5G,
                    dbvar_V_2BRuns_Sum_20G,
                    dbvar_V_2BRuns_20G,
                    dbvar_V_2BRuns_Strength_20G,
                    dbvar_V_2BRuns_YTD,
                    dbvar_V_2BRuns_Strength_YTD,
                    dbvar_V_2BRuns_Allowed,
                    dbvar_V_2BRuns_Allowed_5G,
                    dbvar_V_2BRuns_Allowed_20G,
                    dbvar_V_2BRuns_Allowed_YTD,
                    dbvar_V_3BRuns_Sum,
                    dbvar_V_3BRuns,
                    dbvar_V_3BRuns_5G,
                    dbvar_V_3BRuns_20G,
                    dbvar_V_3BRuns_YTD,
                    dbvar_V_3BRuns_Allowed,
                    dbvar_V_3BRuns_Allowed_5G,
                    dbvar_V_3BRuns_Allowed_20G,
                    dbvar_V_3BRuns_Allowed_YTD,
                    dbvar_V_3BRuns_Strength,
                    dbvar_V_3BRuns_Strength_5G,
                    dbvar_V_3BRuns_Strength_20G,
                    dbvar_V_3BRuns_Strength_YTD,
                    dbvar_V_ErrorMade_Sum,
                    dbvar_V_ErrorMade,
                    dbvar_V_ErrorMade_Sum_5G,
                    dbvar_V_ErrorMade_5G,
                    dbvar_V_ErrorMade_Sum_20G,
                    dbvar_V_ErrorMade_20G,
                    dbvar_V_ErrorMade_YTD,
                    dbvar_V_ErrorMade_YTD_HV,
                    dbvar_V_ErrorForced_Sum,
                    dbvar_V_ErrorForced,
                    dbvar_V_ErrorForced_Sum_5G,
                    dbvar_V_ErrorForced_5G,
                    dbvar_V_ErrorForced_Sum_20G,
                    dbvar_V_ErrorForced_20G,
                    dbvar_V_ErrorForced_YTD,
                    dbvar_V_HitsByPitch_Sum,
                    dbvar_V_HitsByPitch,
                    dbvar_V_HitsByPitch_Sum_5G,
                    dbvar_V_HitsByPitch_5G,
                    dbvar_V_HitsByPitch_Sum_20G,
                    dbvar_V_HitsByPitch_20G,
                    dbvar_V_HitsByPitch_YTD,
                    dbvar_V_HitsByPitch_Allowed,
                    dbvar_V_HitsByPitch_Allowed_5G,
                    dbvar_V_HitsByPitch_Allowed_20G,
                    dbvar_V_HitsByPitch_Allowed_YTD,
                    dbvar_V_DoublePlays_Gained_Sum,
                    dbvar_V_DoublePlays_Gained,
                    dbvar_V_DoublePlays_Gained_Sum_5G,
                    dbvar_V_DoublePlays_Gained_5G,
                    dbvar_V_DoublePlays_Gained_Sum_20G,
                    dbvar_V_DoublePlays_Gained_20G,
                    dbvar_V_DoublePlays_Gained_YTD,
                    dbvar_V_DoublePlays_Gained_YTD_HV,
                    dbvar_V_DoublePlays_Allowed,
                    dbvar_V_DoublePlays_Allowed_5G,
                    dbvar_V_DoublePlays_Allowed_20G,
                    dbvar_V_DoublePlays_Allowed_YTD,
                    dbvar_V_DoublePlays_Allowed_YTD_HV,
                    dbvar_V_ReliefPitchers,
                    dbvar_V_TotalBases_Sum,
                    dbvar_V_TotalBases,
                    dbvar_V_TotalBases_5G,
                    dbvar_V_TotalBases_20G,
                    dbvar_V_TotalBases_YTD, 
                    dbvar_V_MenOnBaseTBRatio,
                    dbvar_V_MenOnBaseTBRatio_5G,
                    dbvar_V_WalkStrikeoutRatio_Sum,
                    dbvar_V_WalkStrikeoutRatio,
                    dbvar_V_PowerHits_Sum,
                    dbvar_V_PowerHits,
                    dbvar_V_PowerHits_5G,
                    dbvar_V_Innings_OutPitched_Sum,
                    dbvar_V_Innings_OutPitched,
                    dbvar_V_Innings_OutPitched_Sum_5G,
                    dbvar_V_Innings_OutPitched_5G,
                    dbvar_V_Innings_OutPitched_YTD,
                    dbvar_V_SP_HitsAllowed_Sum,
                    dbvar_V_SP_HitsAllowed,
                    dbvar_V_SP_HitsAllowed_5G,
                    dbvar_V_SP_HitsAllowed_YTD,
                    dbvar_V_EarnedRuns_Sum,
                    dbvar_V_EarnedRunAvg_Sum,
                    dbvar_V_EarnedRuns,
                    dbvar_V_EarnedRunAvg,
                    dbvar_V_EarnedRuns_Sum_5G,
                    dbvar_V_EarnedRunAvg_Sum_5G,
                    dbvar_V_EarnedRuns_5G,
                    dbvar_V_EarnedRunAvg_5G,
                    dbvar_V_EarnedRuns_YTD,
                    dbvar_V_EarnedRunAvg_YTD,
                    dbvar_V_HitsAllowedPer9Innings_Sum,
                    dbvar_V_HitsAllowedPer9Innings,
                    dbvar_V_HitsAllowedPer9Innings_5G,
                    dbvar_V_WalksHitsAllowedPerInning,
                    dbvar_V_WalksHitsAllowedPerInning_5G,
                    dbvar_V_WalksHitsAllowedPerInning_YTD,
                    dbvar_G_V_StartingPitcher_Id,
                    dbvar_V_StartingPitcher_DaysRest,
                    dbvar_V_StartingPitcher_Score_All,
                    dbvar_V_StartingPitcher_Strikeouts_All,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_All,
                    dbvar_V_StartingPitcher_BaseOnBalls_All,
                    dbvar_V_StartingPitcher_Hits_All,
                    dbvar_V_StartingPitcher_NP_All,
                    dbvar_V_StartingPitcher_InningsPitched_All,
                    dbvar_V_StartingPitcher_Strikes_All,
                    dbvar_V_StartingPitcher_StrikeAccuracy_All,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All,
                    dbvar_V_StartingPitcher_Score_YTD,
                    dbvar_V_StartingPitcher_Strikeouts_YTD,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD,
                    dbvar_V_StartingPitcher_BaseOnBalls_YTD,
                    dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                    dbvar_V_StartingPitcher_Hits_YTD,
                    dbvar_V_StartingPitcher_NP_YTD,
                    dbvar_V_StartingPitcher_InningsPitched_YTD,
                    dbvar_V_StartingPitcher_Strikes_YTD,
                    dbvar_V_StartingPitcher_StrikeAccuracy_YTD,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                    dbvar_V_StartingPitcher_ScoreImpact_YTD,
                    dbvar_V_StartingPitcher_StrikeoutsImpact_YTD,
                    dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD,
                    dbvar_V_StartingPitcher_HitsImpact_YTD,
                    dbvar_V_StartingPitcher_NPImpact_YTD,
                    dbvar_V_StartingPitcher_InningsPitchedImpact_YTD,
                    dbvar_V_StartingPitcher_StrikeImpact_YTD,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                    dbvar_V_StartingPitcher_Score_5G,
                    dbvar_V_StartingPitcher_Strikeouts_5G,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_5G,
                    dbvar_V_StartingPitcher_BaseOnBalls_5G,
                    dbvar_V_StartingPitcher_Hits_5G,
                    dbvar_V_StartingPitcher_NP_5G,
                    dbvar_V_StartingPitcher_InningsPitched_5G,
                    dbvar_V_StartingPitcher_Strikes_5G,
                    dbvar_V_StartingPitcher_StrikeAccuracy_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G,
                    dbvar_V_StartingPitcher_ScoreImpact_5G,
                    dbvar_V_StartingPitcher_StrikeoutsImpact_5G,
                    dbvar_V_StartingPitcher_BaseOnBallsImpact_5G,
                    dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                    dbvar_V_StartingPitcher_HitsImpact_5G,
                    dbvar_V_StartingPitcher_NPImpact_5G,
                    dbvar_V_StartingPitcher_InningsPitchedImpact_5G,
                    dbvar_V_StartingPitcher_StrikeImpact_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                    dbvar_V_StartingPitcher_Score_Ratio,
                    dbvar_V_StartingPitcher_Strikeouts_Ratio,
                    dbvar_V_StartingPitcher_BaseOnBalls_Ratio,
                    dbvar_V_StartingPitcher_Hits_Ratio,
                    dbvar_V_StartingPitcher_NP_Ratio,
                    dbvar_V_StartingPitcher_InningsPitched_Ratio,
                    dbvar_V_StartingPitcher_Strikes_Ratio,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                    dbvar_V_StartingPitcher_Score_Ratio_5G,
                    dbvar_V_StartingPitcher_Strikeouts_Ratio_5G,
                    dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G,
                    dbvar_V_StartingPitcher_Hits_Ratio_5G,
                    dbvar_V_StartingPitcher_NP_Ratio_5G,
                    dbvar_V_StartingPitcher_InningsPitched_Ratio_5G,
                    dbvar_V_StartingPitcher_Strikes_Ratio_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                    dbvar_V_BallpenOuts,
                    dbvar_V_BallpenOuts_5G,
                    dbvar_V_BallpenOuts_YTD,
                    dbvar_V_BallpenERA_Approx,
                    dbvar_V_BallpenERA_Approx_5G,
                    dbvar_V_BallpenERA_Approx_YTD,
                    dbvar_G_VHRatio_DaysRest,
                    dbvar_G_VHRatio_SP_DaysRest,
                    dbvar_G_VHRatio_ParkImpactFactor,
                    dbvar_G_VHRatio_ContiguousGamesV,
                    dbvar_G_VHRatio_ContiguousGamesH,
                    dbvar_G_VHRatio_TotalDistanceTravelled_3G,
                    dbvar_G_VHRatio_ClosingProbabilityLine_HV,
                    dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV,
                    dbvar_G_VHRatio_Runs_Gained,
                    dbvar_G_VHRatio_Runs_Allowed,
                    dbvar_G_VHRatio_Run_Strength,
                    dbvar_G_VHRatio_Run_Efficiency,
                    dbvar_G_VHRatio_Runs_Gained_Sum,
                    dbvar_G_VHRatio_Runs_Allowed_Sum,
                    dbvar_G_VHRatio_Run_Strength_Sum,
                    dbvar_G_VHRatio_Run_Efficiency_Sum,
                    dbvar_G_VHRatio_Run_Pythag,
                    dbvar_G_VHRatio_Runs_Gained_5G,
                    dbvar_G_VHRatio_Runs_Allowed_5G,
                    dbvar_G_VHRatio_Run_Strength_5G,
                    dbvar_G_VHRatio_Run_Efficiency_5G,
                    dbvar_G_VHRatio_Run_Pythag_5G,
                    dbvar_G_VHRatio_Runs_Gained_Sum_5G,
                    dbvar_G_VHRatio_Runs_Allowed_Sum_5G,
                    dbvar_G_VHRatio_Run_Strength_Sum_5G,
                    dbvar_G_VHRatio_Run_Efficiency_Sum_5G,
                    dbvar_G_VHRatio_Runs_Gained_20G,
                    dbvar_G_VHRatio_Runs_Allowed_20G,
                    dbvar_G_VHRatio_Run_Strength_20G,
                    dbvar_G_VHRatio_Run_Efficiency_20G,
                    dbvar_G_VHRatio_Run_Pythag_20G,
                    dbvar_G_VHRatio_Runs_Gained_Sum_20G,
                    dbvar_G_VHRatio_Runs_Allowed_Sum_20G,
                    dbvar_G_VHRatio_Run_Strength_Sum_20G,
                    dbvar_G_VHRatio_Run_Efficiency_Sum_20G,
                    dbvar_G_VHRatio_Runs_5InningsGained,
                    dbvar_G_VHRatio_Runs_5InningsAllowed,
                    dbvar_G_VHRatio_Run_5InningsStrength,
                    dbvar_G_VHRatio_Run_5InningsEfficiency,
                    dbvar_G_VHRatio_Runs_5InningsGained_Sum,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_Sum,
                    dbvar_G_VHRatio_Run_5InningsStrength_Sum,
                    dbvar_G_VHRatio_Run_5InningsEfficiency_Sum,
                    dbvar_G_VHRatio_Runs_5InningsGained_5G,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_5G,
                    dbvar_G_VHRatio_Run_5InningsStrength_5G,
                    dbvar_G_VHRatio_Run_5InningsEfficiency_5G,
                    dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G,
                    dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G,
                    dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G,
                    dbvar_G_VHRatio_Runs_5InningsGained_20G,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_20G,
                    dbvar_G_VHRatio_Run_5InningsStrength_20G,
                    dbvar_G_VHRatio_Run_5InningsEfficiency_20G,
                    dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G,
                    dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G,
                    dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G,
                    dbvar_G_VHRatio_Runs_5InningsGained_HV,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_HV,
                    dbvar_G_VHRatio_Runs_5InningsGained_YTD,
                    dbvar_G_VHRatio_Runs_5InningsAllowed_YTD,
                    dbvar_G_VHRatio_Pythag_Luck_Factor,
                    dbvar_G_VHRatio_Pythag_Luck_Factor_5G,
                    dbvar_G_VHRatio_Pythag_Luck_Factor_20G,
                    dbvar_G_VHRatio_Pythag_Luck_Factor_YTD,
                    dbvar_G_VHRatio_Run_Differential_Per_Game,
                    dbvar_G_VHRatio_Run_Differential_Per_Game_5G,
                    dbvar_G_VHRatio_Run_Differential_Per_Game_20G,
                    dbvar_G_VHRatio_Run_Differential_Per_Game_YTD,
                    dbvar_G_VHRatio_Weighted_Offense_Index,
                    dbvar_G_VHRatio_Weighted_Offense_Index_5G,
                    dbvar_G_VHRatio_Weighted_Offense_Index_20G,
                    dbvar_G_VHRatio_Weighted_Offense_Index_YTD,
                    dbvar_G_VHRatio_At_Bat,
                    dbvar_G_VHRatio_At_Bat_5G,
                    dbvar_G_VHRatio_At_Bat_20G,
                    dbvar_G_VHRatio_At_Bat_YTD,
                    dbvar_G_VHRatio_At_Bat_HV,
                    dbvar_G_VHRatio_At_Bat_YTD_HV,
                    dbvar_G_VHRatio_OBP,
                    dbvar_G_VHRatio_OBP_5G,
                    dbvar_G_VHRatio_OBP_20G,
                    dbvar_G_VHRatio_OBP_YTD,
                    dbvar_G_VHRatio_SLG,
                    dbvar_G_VHRatio_SLG_5G,
                    dbvar_G_VHRatio_SLG_20G,
                    dbvar_G_VHRatio_SLG_YTD,
                    dbvar_G_VHRatio_wOBA,
                    dbvar_G_VHRatio_wOBA_5G,
                    dbvar_G_VHRatio_wOBA_20G,
                    dbvar_G_VHRatio_wOBA_YTD,
                    dbvar_G_VHRatio_OPS,
                    dbvar_G_VHRatio_OPS_5G,
                    dbvar_G_VHRatio_OPS_20G,
                    dbvar_G_VHRatio_OPS_YTD,
                    dbvar_G_VHRatio_Wins,
                    dbvar_G_VHRatio_Losses,
                    dbvar_G_VHRatio_WinLoss_Strength,
                    dbvar_G_VHRatio_Wins_5G,
                    dbvar_G_VHRatio_Losses_5G,
                    dbvar_G_VHRatio_WinLoss_Strength_5G,
                    dbvar_G_VHRatio_Wins_20G,
                    dbvar_G_VHRatio_Losses_20G,
                    dbvar_G_VHRatio_WinLoss_Strength_20G,
                    dbvar_G_VHRatio_OutsPitched,
                    dbvar_G_VHRatio_OutsPitched_5G,
                    dbvar_G_VHRatio_OutsPitched_20G,
                    dbvar_G_VHRatio_OutsPitched_YTD,
                    dbvar_G_VHRatio_OutsPitched_YTD_HV,
                    dbvar_G_VHRatio_StrikeAccuracy,
                    dbvar_G_VHRatio_StrikeAccuracy_5G,
                    dbvar_G_VHRatio_StrikeoutsGained,
                    dbvar_G_VHRatio_StrikeoutsAllowed,
                    dbvar_G_VHRatio_StrikeoutsAccuracy,
                    dbvar_G_VHRatio_StrikeoutsGained_5G,
                    dbvar_G_VHRatio_StrikeoutsAllowed_5G,
                    dbvar_G_VHRatio_StrikeoutsAccuracy_5G,
                    dbvar_G_VHRatio_StrikeoutsGained_20G,
                    dbvar_G_VHRatio_EarnedRuns,
                    dbvar_G_VHRatio_EarnedRunAvg,
                    dbvar_G_VHRatio_EarnedRuns_5G,
                    dbvar_G_VHRatio_EarnedRuns_Avg_5G,
                    dbvar_G_VHRatio_EarnedRuns_Sum_5G,
                    dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G,
                    dbvar_G_VHRatio_EarnedRuns_YTD,
                    dbvar_G_VHRatio_EarnedRunAvg_YTD,
                    dbvar_G_VHRatio_RunsHitsRatio,
                    dbvar_G_VHRatio_RunsHitsRatio_Sum,
                    dbvar_G_VHRatio_RunsHitsRatio_5G,
                    dbvar_G_VHRatio_RunsHitsRatio_Sum_5G,
                    dbvar_G_VHRatio_RunsHitsRatio_Allowed,
                    dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G,
                    dbvar_G_VHRatio_FIP,
                    dbvar_G_VHRatio_FIP_5G,
                    dbvar_G_VHRatio_FIP_YTD,
                    dbvar_G_VHRatio_FIP_YTD_HV,
                    dbvar_G_VHRatio_K_Minus_BB_Pct,
                    dbvar_G_VHRatio_K_Minus_BB_Pct_5G,
                    dbvar_G_VHRatio_K_Minus_BB_Pct_20G,
                    dbvar_G_VHRatio_K_Minus_BB_Pct_YTD,
                    dbvar_G_VHRatio_HR_Per_9_Allowed,
                    dbvar_G_VHRatio_HR_Per_9_Allowed_5G,
                    dbvar_G_VHRatio_HR_Per_9_Allowed_20G,
                    dbvar_G_VHRatio_HR_Per_9_Allowed_YTD,
                    dbvar_G_VHRatio_K_Per_9,
                    dbvar_G_VHRatio_K_Per_9_5G,
                    dbvar_G_VHRatio_K_Per_9_20G,
                    dbvar_G_VHRatio_K_Per_9_YTD,
                    dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV,
                    dbvar_G_VHRatio_WalksAllowed,
                    dbvar_G_VHRatio_WalksAllowed_5G,
                    dbvar_G_VHRatio_WalksAllowed_20G,
                    dbvar_G_VHRatio_WalksAllowed_Sum,
                    dbvar_G_VHRatio_WalksAllowed_Sum_5G,
                    dbvar_G_VHRatio_WalksAllowed_Sum_20G,
                    dbvar_G_VHRatio_PowerHits,
                    dbvar_G_VHRatio_PowerHits_5G,
                    dbvar_G_VHRatio_HitsAllowed_5G,
                    dbvar_G_VHRatio_HitsAllowed_20G,
                    dbvar_G_VHRatio_HitsAllowedPer9Innings,
                    dbvar_G_VHRatio_HitsAllowedPer9Innings_5G,
                    dbvar_G_VHRatio_HitsByPitch_5G,
                    dbvar_G_VHRatio_HitsByPitch_20G,
                    dbvar_G_VHRatio_2BRuns,
                    dbvar_G_VHRatio_2BRuns_5G,
                    dbvar_G_VHRatio_2BRuns_20G,
                    dbvar_G_VHRatio_2BRuns_YTD,
                    dbvar_G_VHRatio_2BRuns_Strength,
                    dbvar_G_VHRatio_2BRuns_Strength_5G,
                    dbvar_G_VHRatio_2BRuns_Strength_20G,
                    dbvar_G_VHRatio_2BRuns_Strength_YTD,
                    dbvar_G_VHRatio_3BRuns,
                    dbvar_G_VHRatio_3BRuns_5G,
                    dbvar_G_VHRatio_3BRuns_20G,
                    dbvar_G_VHRatio_3BRuns_YTD,
                    dbvar_G_VHRatio_3BRuns_Strength,
                    dbvar_G_VHRatio_3BRuns_Strength_5G,
                    dbvar_G_VHRatio_3BRuns_Strength_20G,
                    dbvar_G_VHRatio_3BRuns_Strength_YTD,
                    dbvar_G_VHRatio_HomeRuns_5G,
                    dbvar_G_VHRatio_HomeRuns_20G,
                    dbvar_G_VHRatio_DoublePlays_Gained_5G,
                    dbvar_G_VHRatio_DoublePlays_Gained_20G,
                    dbvar_G_VHRatio_DoublePlays_Gained_YTD,
                    dbvar_G_VHRatio_DoublePlays_Allowed_5G,
                    dbvar_G_VHRatio_DoublePlays_Allowed_20G,
                    dbvar_G_VHRatio_DoublePlays_Allowed_YTD,
                    dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV,
                    dbvar_G_VHRatio_TotalBases,
                    dbvar_G_VHRatio_TotalBases_5G,
                    dbvar_G_VHRatio_TotalBases_20G,
                    dbvar_G_VHRatio_TotalBases_YTD, 
                    dbvar_G_VHRatio_MenOnBaseTBRatio,
                    dbvar_G_VHRatio_MenOnBaseTBRatio_5G,
                    dbvar_G_VHRatio_MenOnBase,
                    dbvar_G_VHRatio_MenOnBase_Strength,
                    dbvar_G_VHRatio_MenOnBase_Efficiency,
                    dbvar_G_VHRatio_MenOnBase_5G,
                    dbvar_G_VHRatio_MenOnBase_Strength_5G,
                    dbvar_G_VHRatio_MenOnBase_Efficiency_5G,
                    dbvar_G_VHRatio_MenOnBase_20G,
                    dbvar_G_VHRatio_MenOnBase_Strength_20G,
                    dbvar_G_VHRatio_MenOnBase_Efficiency_20G,
                    dbvar_G_VHRatio_MenOnBase_Strength_YTD,
                    dbvar_G_VHRatio_MenOnBase_Allowed,
                    dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency,
                    dbvar_G_VHRatio_MenOnBase_Allowed_5G,
                    dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G,
                    dbvar_G_VHRatio_MenOnBase_Allowed_20G,
                    dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G,
                    dbvar_G_VHRatio_MenOnBase_Allowed_YTD,
                    dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD,
                    dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                    dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                    dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                    dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                    dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                    dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                    dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                    dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                    dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                    dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                    dbvar_G_VHRatio_StartingPitcher_Score_5G,
                    dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                    dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                    dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                    dbvar_G_VHRatio_StartingPitcher_NP_5G,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                    dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                    dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                    dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                    dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                    dbvar_G_VHRatio_BallpenOuts,
                    dbvar_G_VHRatio_BallpenOuts_5G,
                    dbvar_G_VHRatio_BallpenOuts_YTD,
                    dbvar_G_VHRatio_BallpenERA_Approx,
                    dbvar_G_VHRatio_BallpenERA_Approx_5G,
                    dbvar_G_VHRatio_BallpenERA_Approx_YTD,
                    dbvar_G_Ivan_BP_DefenseProbability,
                    dbvar_G_Ivan_BP_OffenseProbability,
                    dbvar_G_Ivan_BP_NullProbability,
                    dbvar_G_Ivan_BP_NoLineProbability,
                    dbvar_G_H_AdjBookieProbabilityLine,
                    dbvar_G_PH_Win,
                    dbvar_G_PV_Win,
                    dbvar_G_H_Runs,
                    dbvar_G_H_Run_Prediction,
                    dbvar_G_V_Runs,
                    dbvar_G_V_Run_Prediction,
                    dbvar_G_Actual_Runs_Diff,
                    dbvar_G_ABSActual_Runs_Diff,
                    dbvar_G_ABSActual_Runs_DiffCategory,
                    dbvar_G_Total,
                    dbvar_G_BookieAdjustedTotal,
                    dbvar_G_Total_IsOver,
                    dbvar_G_Bookie_Prob_Bet,
                    dbvar_G_Bookie_FaveWin,
                    dbvar_G_Bookie_DogWin
                ]

MLBdb_int_vars =    [ 
                        dbvar_G_Id, 
                        dbvar_G_Year, 
                        dbvar_G_Month, 
                        dbvar_G_Day, 
                        dbvar_G_H_Id, 
                        dbvar_G_H_League, 
                        dbvar_G_H_Division, 
                        dbvar_G_H_Same_LeagueDiv, 
                        dbvar_G_H_Same_Div, 
                        dbvar_G_H_Prev1_Id, 
                        dbvar_G_H_Prev1_SameLeagueDiv, 
                        dbvar_G_H_Prev1_SameDiv, 
                        dbvar_G_H_Prev1Home, 
                        dbvar_G_H_Prev1Win, 
                        dbvar_G_H_Prev2_Id, 
                        dbvar_G_H_Prev2_SameLeagueDiv, 
                        dbvar_G_H_Prev2_SameDiv, 
                        dbvar_G_H_Prev2Home, 
                        dbvar_G_H_Prev2Win , 
                        dbvar_G_H_Prev3_Id, 
                        dbvar_G_H_Prev3_SameLeagueDiv, 
                        dbvar_G_H_Prev3_SameDiv, 
                        dbvar_G_H_Prev3Home, 
                        dbvar_G_H_Prev3Win , 
                        dbvar_G_H_Next1_Id, 
                        dbvar_G_H_Next1_SameLeagueDiv, 
                        dbvar_G_H_Next1_SameDiv, 
                        dbvar_G_H_Next1Home, 
                        dbvar_G_H_Next2_Id, 
                        dbvar_G_H_Next2_SameLeagueDiv, 
                        dbvar_G_H_Next2_SameDiv, 
                        dbvar_G_H_Next2Home, 
                        dbvar_G_H_Next3_Id, 
                        dbvar_G_H_Next3_SameLeagueDiv, 
                        dbvar_G_H_Next3_SameDiv, 
                        dbvar_G_H_Next3Home, 
                        dbvar_H_OverTime, 
                        dbvar_G_H_StartingPitcher_Id, 
                        dbvar_G_V_Id, 
                        dbvar_G_V_League, 
                        dbvar_G_V_Division, 
                        dbvar_G_V_Same_LeagueDiv, 
                        dbvar_G_V_Same_Div, 
                        dbvar_G_V_Prev1_Id, 
                        dbvar_G_V_Prev1_SameLeagueDiv, 
                        dbvar_G_V_Prev1_SameDiv, 
                        dbvar_G_V_Prev1Home, 
                        dbvar_G_V_Prev1Win, 
                        dbvar_G_V_Prev2_Id, 
                        dbvar_G_V_Prev2_SameLeagueDiv, 
                        dbvar_G_V_Prev2_SameDiv, 
                        dbvar_G_V_Prev2Home, 
                        dbvar_G_V_Prev2Win , 
                        dbvar_G_V_Prev3_Id, 
                        dbvar_G_V_Prev3_SameLeagueDiv, 
                        dbvar_G_V_Prev3_SameDiv, 
                        dbvar_G_V_Prev3Home, 
                        dbvar_G_V_Prev3Win , 
                        dbvar_G_V_Next1_Id, 
                        dbvar_G_V_Next1_SameLeagueDiv, 
                        dbvar_G_V_Next1_SameDiv, 
                        dbvar_G_V_Next1Home, 
                        dbvar_G_V_Next2_Id, 
                        dbvar_G_V_Next2_SameLeagueDiv, 
                        dbvar_G_V_Next2_SameDiv, 
                        dbvar_G_V_Next2Home, 
                        dbvar_G_V_Next3_Id, 
                        dbvar_G_V_Next3_SameLeagueDiv, 
                        dbvar_G_V_Next3_SameDiv, 
                        dbvar_G_V_Next3Home, 
                        dbvar_V_OverTime, 
                        dbvar_G_V_StartingPitcher_Id, 
                        dbvar_G_PH_Win, 
                        dbvar_G_PV_Win, 
                        dbvar_G_Total_IsOver, 
                        dbvar_G_Bookie_FaveWin, 
                        dbvar_G_Bookie_DogWin
                    ]

MLBdb_float_vars =  [  
                        dbvar_G_MonthWeek,
                        dbvar_G_Opening_TotalOver,
                        dbvar_G_Opening_TotalOverLine,
                        dbvar_G_Closing_TotalOver,
                        dbvar_G_Closing_TotalOverLine,
                        dbvar_G_Bookie_TotalOver,
                        dbvar_G_Bookie_TotalOverLine,
                        dbvar_G_Bookie_H_MoneyLine,
                        dbvar_G_Bookie_H_Probability,
                        dbvar_G_H_Opening_MoneyLine,
                        dbvar_G_H_OpeningProbabilityLine,
                        dbvar_G_H_Closing_MoneyLine,
                        dbvar_G_H_ClosingProbabilityLine,
                        dbvar_G_H_CLL_OPL_Prob_Diff,
                        dbvar_G_H_ParkImpactFactor,
                        dbvar_G_H_DaysRest,
                        dbvar_G_H_ContiguousGamesV,
                        dbvar_G_H_ContiguousGamesH,
                        dbvar_G_H_TotalDistanceTravelled_3G,
                        dbvar_G_H_Prev1_DistanceTravelled,
                        dbvar_G_H_Prev1Strength,
                        dbvar_G_H_Prev1StrengthRatio,
                        dbvar_G_H_Prev1CLL,
                        dbvar_G_H_Prev2_DistanceTravelled,
                        dbvar_G_H_Prev2Strength,
                        dbvar_G_H_Prev2StrengthRatio,
                        dbvar_G_H_Prev2CLL,
                        dbvar_G_H_Prev3_DistanceTravelled,
                        dbvar_G_H_Prev3Strength,
                        dbvar_G_H_Prev3StrengthRatio,
                        dbvar_G_H_Prev3CLL,
                        dbvar_G_H_Lookback_Strength,
                        dbvar_G_H_Next1_DistanceTravelled,
                        dbvar_G_H_Next1Strength,
                        dbvar_G_H_Next1StrengthRatio,
                        dbvar_G_H_Next2_DistanceTravelled,
                        dbvar_G_H_Next2Strength,
                        dbvar_G_H_Next2StrengthRatio,
                        dbvar_G_H_Next3_DistanceTravelled,
                        dbvar_G_H_Next3Strength,
                        dbvar_G_H_Next3StrengthRatio,
                        dbvar_G_H_Lookahead_Strength,
                        dbvar_H_ClosingProbabilityLine_HV,
                        dbvar_H_ClosingProbabilityLine_YTD_HV,
                        dbvar_H_Runs_Gained,
                        dbvar_H_Runs_Allowed,
                        dbvar_H_Run_Strength,
                        dbvar_H_Run_Efficiency,
                        dbvar_H_Run_Pythag,
                        dbvar_H_Runs_Gained_5G,
                        dbvar_H_Runs_Allowed_5G,
                        dbvar_H_Run_Strength_5G,
                        dbvar_H_Run_Efficiency_5G,
                        dbvar_H_Run_Pythag_5G,
                        dbvar_H_Runs_Gained_20G,
                        dbvar_H_Runs_Allowed_20G,
                        dbvar_H_Run_Strength_20G,
                        dbvar_H_Run_Efficiency_20G,
                        dbvar_H_Run_Pythag_20G,
                        dbvar_H_Runs_Gained_Sum,
                        dbvar_H_Runs_Allowed_Sum,
                        dbvar_H_Run_Strength_Sum,
                        dbvar_H_Run_Efficiency_Sum,
                        dbvar_H_Run_Pythag_Sum,
                        dbvar_H_Runs_Gained_Sum_5G,
                        dbvar_H_Runs_Allowed_Sum_5G,
                        dbvar_H_Run_Strength_Sum_5G,
                        dbvar_H_Run_Efficiency_Sum_5G,
                        dbvar_H_Runs_Gained_Sum_20G,
                        dbvar_H_Runs_Allowed_Sum_20G,
                        dbvar_H_Run_Strength_Sum_20G,
                        dbvar_H_Run_Efficiency_Sum_20G,
                        dbvar_H_Runs_Gained_Sum_HV,
                        dbvar_H_Runs_Allowed_Sum_HV,
                        dbvar_H_Run_Strength_Sum_HV,
                        dbvar_H_Runs_Gained_HV,
                        dbvar_H_Runs_Allowed_HV,
                        dbvar_H_Run_Strength_HV,
                        dbvar_H_Runs_Gained_YTD,
                        dbvar_H_Runs_Allowed_YTD,
                        dbvar_H_Run_Strength_YTD,
                        dbvar_H_Run_Pythag_YTD,
                        dbvar_H_Runs_Gained_YTD_HV,
                        dbvar_H_Runs_Allowed_YTD_HV,
                        dbvar_H_Run_Strength_YTD_HV,
                        dbvar_H_Runs_5InningsGained,
                        dbvar_H_Runs_5InningsAllowed,
                        dbvar_H_Run_5InningsStrength,
                        dbvar_H_Run_5InningsEfficiency,
                        dbvar_H_Runs_5InningsGained_Sum,
                        dbvar_H_Runs_5InningsAllowed_Sum,
                        dbvar_H_Run_5InningsStrength_Sum,
                        dbvar_H_Run_5InningsEfficiency_Sum,
                        dbvar_H_Runs_5InningsGained_5G,
                        dbvar_H_Runs_5InningsAllowed_5G,
                        dbvar_H_Run_5InningsStrength_5G,
                        dbvar_H_Run_5InningsEfficiency_5G,
                        dbvar_H_Runs_5InningsGained_Sum_5G,
                        dbvar_H_Runs_5InningsAllowed_Sum_5G,
                        dbvar_H_Run_5InningsStrength_Sum_5G,
                        dbvar_H_Run_5InningsEfficiency_Sum_5G,
                        dbvar_H_Runs_5InningsGained_20G,
                        dbvar_H_Runs_5InningsAllowed_20G,
                        dbvar_H_Run_5InningsStrength_20G,
                        dbvar_H_Run_5InningsEfficiency_20G,
                        dbvar_H_Runs_5InningsGained_Sum_20G,
                        dbvar_H_Runs_5InningsAllowed_Sum_20G,
                        dbvar_H_Run_5InningsStrength_Sum_20G,
                        dbvar_H_Run_5InningsEfficiency_Sum_20G,
                        dbvar_H_Runs_5InningsGained_Sum_HV,
                        dbvar_H_Runs_5InningsAllowed_Sum_HV,
                        dbvar_H_Run_5InningsStrength_Sum_HV,
                        dbvar_H_Runs_5InningsGained_HV,
                        dbvar_H_Runs_5InningsAllowed_HV,
                        dbvar_H_Run_5InningsStrength_HV,
                        dbvar_H_Runs_5InningsGained_YTD,
                        dbvar_H_Runs_5InningsAllowed_YTD,
                        dbvar_H_Run_5InningsStrength_YTD,
                        dbvar_H_Pythag_Luck_Factor,
                        dbvar_H_Pythag_Luck_Factor_5G,
                        dbvar_H_Pythag_Luck_Factor_20G,
                        dbvar_H_Pythag_Luck_Factor_YTD,
                        dbvar_H_Run_Differential_Per_Game,
                        dbvar_H_Run_Differential_Per_Game_5G,
                        dbvar_H_Run_Differential_Per_Game_20G,
                        dbvar_H_Run_Differential_Per_Game_YTD,
                        dbvar_H_Weighted_Offense_Index,
                        dbvar_H_Weighted_Offense_Index_5G,
                        dbvar_H_Weighted_Offense_Index_20G,
                        dbvar_H_Weighted_Offense_Index_YTD,
                        dbvar_H_At_Bat,
                        dbvar_H_At_Bat_5G,
                        dbvar_H_At_Bat_20G,
                        dbvar_H_At_Bat_YTD,
                        dbvar_H_At_Bat_HV,
                        dbvar_H_At_Bat_YTD_HV,
                        dbvar_H_OBP,
                        dbvar_H_OBP_5G,
                        dbvar_H_OBP_20G,
                        dbvar_H_OBP_YTD,
                        dbvar_H_SLG,
                        dbvar_H_SLG_5G,
                        dbvar_H_SLG_20G,
                        dbvar_H_SLG_YTD,
                        dbvar_H_wOBA,
                        dbvar_H_wOBA_5G,
                        dbvar_H_wOBA_20G,
                        dbvar_H_wOBA_YTD,
                        dbvar_H_OPS,
                        dbvar_H_OPS_5G,
                        dbvar_H_OPS_20G,
                        dbvar_H_OPS_YTD,
                        dbvar_H_Wins,
                        dbvar_H_Losses,
                        dbvar_H_WinLoss_Strength,
                        dbvar_H_Wins_5G,
                        dbvar_H_Losses_5G,
                        dbvar_H_WinLoss_Strength_5G,
                        dbvar_H_Wins_20G,
                        dbvar_H_Losses_20G,
                        dbvar_H_WinLoss_Strength_20G,
                        dbvar_H_Wins_HV,
                        dbvar_H_Losses_HV,
                        dbvar_H_WinLoss_Strength_HV,
                        dbvar_H_Wins_YTD,
                        dbvar_H_Losses_YTD,
                        dbvar_H_WinLoss_Strength_YTD,
                        dbvar_H_Wins_YTD_HV,
                        dbvar_H_Losses_YTD_HV,
                        dbvar_H_WinLoss_Strength_YTD_HV,
                        dbvar_H_OutsPitched_Sum,
                        dbvar_H_OutsPitched,
                        dbvar_H_OutsPitched_5G,
                        dbvar_H_OutsPitched_20G,
                        dbvar_H_OutsPitched_YTD,
                        dbvar_H_OutsPitched_YTD_HV,
                        dbvar_H_StrikeoutsAllowed,
                        dbvar_H_StrikeoutsGained,
                        dbvar_H_StrikeoutAccuracy,
                        dbvar_H_StrikeoutsAllowed_Sum,
                        dbvar_H_StrikeoutsGained_Sum,
                        dbvar_H_StrikeoutAccuracy_Sum,
                        dbvar_H_StrikeoutsAllowed_5G,
                        dbvar_H_StrikeoutsGained_5G,
                        dbvar_H_StrikeoutAccuracy_5G,
                        dbvar_H_StrikeoutsGained_20G,
                        dbvar_H_StrikeoutsAllowed_YTD,
                        dbvar_H_StrikeoutsGained_YTD,
                        dbvar_H_StrikeoutAccuracy_YTD,
                        dbvar_H_StrikeoutsAllowed_YTD_HV,
                        dbvar_H_StrikeoutsGained_YTD_HV,
                        dbvar_H_StrikeoutAccuracy_YTD_HV,
                        dbvar_H_Hits_Sum,
                        dbvar_H_Hits,
                        dbvar_H_Hits_Sum_5G,
                        dbvar_H_Hits_5G,
                        dbvar_H_Hits_Sum_20G,
                        dbvar_H_Hits_20G,
                        dbvar_H_Hits_YTD,
                        dbvar_H_Hits_YTD_HV,
                        dbvar_H_HitsAllowed_Sum,
                        dbvar_H_HitsAllowed_Sum_5G,
                        dbvar_H_HitsAllowed_Sum_20G,
                        dbvar_H_HitsAllowed,
                        dbvar_H_HitsAllowed_5G,
                        dbvar_H_HitsAllowed_20G,
                        dbvar_H_HitsAllowed_YTD,
                        dbvar_H_HitsAllowed_YTD_HV,
                        dbvar_H_RunsHitsRatio,
                        dbvar_H_RunsHitsRatio_Sum,
                        dbvar_H_RunsHitsRatio_5G,
                        dbvar_H_RunsHitsRatio_Sum_5G,
                        dbvar_H_RunsHitsRatio_20G,
                        dbvar_H_RunsHitsRatio_Sum_20G,
                        dbvar_H_RunsHitsRatio_YTD,
                        dbvar_H_RunsHitsRatio_Allowed,
                        dbvar_H_RunsHitsRatio_Allowed_Sum,
                        dbvar_H_RunsHitsRatio_Allowed_5G,
                        dbvar_H_RunsHitsRatio_Allowed_Sum_5G,
                        dbvar_H_RunsHitsRatio_Allowed_20G,
                        dbvar_H_RunsHitsRatio_Allowed_Sum_20G,
                        dbvar_H_RunsHitsRatio_Allowed_YTD,
                        dbvar_H_FIP,
                        dbvar_H_FIP_5G,
                        dbvar_H_FIP_YTD,
                        dbvar_H_FIP_YTD_HV,
                        dbvar_H_K_Minus_BB_Pct,
                        dbvar_H_K_Minus_BB_Pct_5G,
                        dbvar_H_K_Minus_BB_Pct_20G,
                        dbvar_H_K_Minus_BB_Pct_YTD,
                        dbvar_H_HR_Per_9_Allowed,
                        dbvar_H_HR_Per_9_Allowed_5G,
                        dbvar_H_HR_Per_9_Allowed_20G,
                        dbvar_H_HR_Per_9_Allowed_YTD,
                        dbvar_H_K_Per_9,
                        dbvar_H_K_Per_9_5G,
                        dbvar_H_K_Per_9_20G,
                        dbvar_H_K_Per_9_YTD,
                        dbvar_H_WalksAllowed_Sum,
                        dbvar_H_WalksAllowed,
                        dbvar_H_WalksAllowed_Sum_5G,
                        dbvar_H_WalksAllowed_5G,
                        dbvar_H_WalksAllowed_Sum_20G,
                        dbvar_H_WalksAllowed_20G,
                        dbvar_H_WalksAllowed_YTD,
                        dbvar_H_WalksAllowed_YTD_HV,
                        dbvar_H_WalksGained_Sum,
                        dbvar_H_WalksGained,
                        dbvar_H_WalksGained_5G,
                        dbvar_H_WalksGained_20G,
                        dbvar_H_WalksGained_YTD,
                        dbvar_H_WalksGained_YTD_HV,
                        dbvar_H_HomeRuns_Sum,
                        dbvar_H_HomeRuns,
                        dbvar_H_HomeRuns_5G,
                        dbvar_H_HomeRuns_Sum_5G,
                        dbvar_H_HomeRuns_20G,
                        dbvar_H_HomeRuns_Sum_20G,
                        dbvar_H_HomeRuns_YTD,
                        dbvar_H_HomeRuns_YTD_HV,
                        dbvar_H_HomeRuns_Allowed_Sum,
                        dbvar_H_HomeRuns_Allowed,
                        dbvar_H_HomeRuns_Allowed_5G,
                        dbvar_H_HomeRuns_Allowed_20G,
                        dbvar_H_HomeRuns_Allowed_YTD,
                        dbvar_H_HomeRuns_Allowed_YTD_HV,
                        dbvar_H_5thInnScore,
                        dbvar_H_Duration,
                        dbvar_H_NP_Sum,
                        dbvar_H_NP,
                        dbvar_H_NP_5G,
                        dbvar_H_NP_YTD,
                        dbvar_H_NP_YTD_HV,
                        dbvar_H_Strikes_Sum,
                        dbvar_H_StrikeAccuracy_Sum,
                        dbvar_H_Strikes,
                        dbvar_H_StrikeAccuracy,
                        dbvar_H_Strikes_5G,
                        dbvar_H_StrikeAccuracy_5G,
                        dbvar_H_Strikes_YTD,
                        dbvar_H_StrikeAccuracy_YTD,
                        dbvar_H_Strikes_YTD_HV,
                        dbvar_H_StrikeAccuracy_YTD_HV,
                        dbvar_H_MenOnBase,
                        dbvar_H_MenOnBase_Strength,
                        dbvar_H_MenOnBase_Efficiency,
                        dbvar_H_MenOnBase_5G,
                        dbvar_H_MenOnBase_Strength_5G,
                        dbvar_H_MenOnBase_Efficiency_5G,
                        dbvar_H_MenOnBase_20G,
                        dbvar_H_MenOnBase_Strength_20G,
                        dbvar_H_MenOnBase_Efficiency_20G,
                        dbvar_H_MenOnBase_YTD,
                        dbvar_H_MenOnBase_Strength_YTD,
                        dbvar_H_MenOnBase_Efficiency_YTD,
                        dbvar_H_MenOnBase_Allowed,
                        dbvar_H_MenOnBase_Allowed_Efficiency,
                        dbvar_H_MenOnBase_Allowed_5G,
                        dbvar_H_MenOnBase_Allowed_Efficiency_5G,
                        dbvar_H_MenOnBase_Allowed_20G,
                        dbvar_H_MenOnBase_Allowed_Efficiency_20G,
                        dbvar_H_MenOnBase_Allowed_YTD,
                        dbvar_H_MenOnBase_Allowed_Efficiency_YTD,
                        dbvar_H_LeftOnBase_Sum,
                        dbvar_H_LeftOnBase,
                        dbvar_H_2BRuns_Sum,
                        dbvar_H_2BRuns,
                        dbvar_H_2BRuns_Sum_5G,
                        dbvar_H_2BRuns_5G,
                        dbvar_H_2BRuns_Sum_20G,
                        dbvar_H_2BRuns_20G,
                        dbvar_H_2BRuns_YTD,
                        dbvar_H_2BRuns_Allowed,
                        dbvar_H_2BRuns_Allowed_5G,
                        dbvar_H_2BRuns_Allowed_20G,
                        dbvar_H_2BRuns_Allowed_YTD,
                        dbvar_H_2BRuns_Strength,
                        dbvar_H_2BRuns_Strength_5G,
                        dbvar_H_2BRuns_Strength_20G,
                        dbvar_H_2BRuns_Strength_YTD,
                        dbvar_H_3BRuns_Sum,
                        dbvar_H_3BRuns,
                        dbvar_H_3BRuns_5G,
                        dbvar_H_3BRuns_20G,
                        dbvar_H_3BRuns_YTD,
                        dbvar_H_3BRuns_Allowed,
                        dbvar_H_3BRuns_Allowed_5G,
                        dbvar_H_3BRuns_Allowed_20G,
                        dbvar_H_3BRuns_Allowed_YTD,
                        dbvar_H_3BRuns_Strength,
                        dbvar_H_3BRuns_Strength_5G,
                        dbvar_H_3BRuns_Strength_20G,
                        dbvar_H_3BRuns_Strength_YTD,
                        dbvar_H_ErrorMade_Sum,
                        dbvar_H_ErrorMade,
                        dbvar_H_ErrorMade_Sum_5G,
                        dbvar_H_ErrorMade_5G,
                        dbvar_H_ErrorMade_Sum_20G,
                        dbvar_H_ErrorMade_20G,
                        dbvar_H_ErrorMade_YTD,
                        dbvar_H_ErrorMade_YTD_HV,
                        dbvar_H_ErrorForced_Sum,
                        dbvar_H_ErrorForced_Sum_5G,
                        dbvar_H_ErrorForced_Sum_20G,
                        dbvar_H_ErrorForced,
                        dbvar_H_ErrorForced_5G,
                        dbvar_H_ErrorForced_20G,
                        dbvar_H_ErrorForced_YTD,
                        dbvar_H_HitsByPitch_Sum,
                        dbvar_H_HitsByPitch,
                        dbvar_H_HitsByPitch_Sum_5G,
                        dbvar_H_HitsByPitch_5G,
                        dbvar_H_HitsByPitch_Sum_20G,
                        dbvar_H_HitsByPitch_20G,
                        dbvar_H_HitsByPitch_YTD,
                        dbvar_H_HitsByPitch_Allowed,
                        dbvar_H_HitsByPitch_Allowed_5G,
                        dbvar_H_HitsByPitch_Allowed_20G,
                        dbvar_H_HitsByPitch_Allowed_YTD,
                        dbvar_H_DoublePlays_Gained_Sum,
                        dbvar_H_DoublePlays_Gained,
                        dbvar_H_DoublePlays_Gained_Sum_5G,
                        dbvar_H_DoublePlays_Gained_5G,
                        dbvar_H_DoublePlays_Gained_Sum_20G,
                        dbvar_H_DoublePlays_Gained_20G,
                        dbvar_H_DoublePlays_Gained_YTD,
                        dbvar_H_DoublePlays_Gained_YTD_HV,
                        dbvar_H_DoublePlays_Allowed,
                        dbvar_H_DoublePlays_Allowed_5G,
                        dbvar_H_DoublePlays_Allowed_20G,
                        dbvar_H_DoublePlays_Allowed_YTD,
                        dbvar_H_DoublePlays_Allowed_YTD_HV,
                        dbvar_H_ReliefPitchers,
                        dbvar_H_TotalBases_Sum,
                        dbvar_H_TotalBases,
                        dbvar_H_TotalBases_5G,
                        dbvar_H_TotalBases_20G,
                        dbvar_H_TotalBases_YTD,     
                        dbvar_H_MenOnBaseTBRatio,
                        dbvar_H_MenOnBaseTBRatio_5G,
                        dbvar_H_WalkStrikeoutRatio_Sum,
                        dbvar_H_WalkStrikeoutRatio,
                        dbvar_H_PowerHits_Sum,
                        dbvar_H_PowerHits,
                        dbvar_H_PowerHits_5G,
                        dbvar_H_Innings_OutPitched_Sum,
                        dbvar_H_Innings_OutPitched,
                        dbvar_H_Innings_OutPitched_Sum_5G,
                        dbvar_H_Innings_OutPitched_5G,
                        dbvar_H_Innings_OutPitched_YTD,  
                        dbvar_H_SP_HitsAllowed_Sum,
                        dbvar_H_SP_HitsAllowed,
                        dbvar_H_SP_HitsAllowed_5G,
                        dbvar_H_SP_HitsAllowed_YTD,
                        dbvar_H_EarnedRuns_Sum,
                        dbvar_H_EarnedRunAvg_Sum,
                        dbvar_H_EarnedRuns,
                        dbvar_H_EarnedRunAvg,
                        dbvar_H_EarnedRuns_Sum_5G,
                        dbvar_H_EarnedRunAvg_Sum_5G,
                        dbvar_H_EarnedRuns_5G,
                        dbvar_H_EarnedRunAvg_5G,
                        dbvar_H_EarnedRuns_YTD,
                        dbvar_H_EarnedRunAvg_YTD,
                        dbvar_H_HitsAllowedPer9Innings_Sum,
                        dbvar_H_HitsAllowedPer9Innings,
                        dbvar_H_HitsAllowedPer9Innings_5G,
                        dbvar_H_WalksHitsAllowedPerInning,
                        dbvar_H_WalksHitsAllowedPerInning_5G,
                        dbvar_H_WalksHitsAllowedPerInning_YTD,
                        dbvar_H_StartingPitcher_DaysRest,
                        dbvar_H_StartingPitcher_Score_All,
                        dbvar_H_StartingPitcher_Strikeouts_All,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_All,
                        dbvar_H_StartingPitcher_BaseOnBalls_All,
                        dbvar_H_StartingPitcher_Hits_All,
                        dbvar_H_StartingPitcher_NP_All,
                        dbvar_H_StartingPitcher_InningsPitched_All,
                        dbvar_H_StartingPitcher_Strikes_All,
                        dbvar_H_StartingPitcher_StrikeAccuracy_All,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All,
                        dbvar_H_StartingPitcher_Score_YTD,
                        dbvar_H_StartingPitcher_Strikeouts_YTD,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_H_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_H_StartingPitcher_Hits_YTD,
                        dbvar_H_StartingPitcher_NP_YTD,
                        dbvar_H_StartingPitcher_InningsPitched_YTD,
                        dbvar_H_StartingPitcher_Strikes_YTD,
                        dbvar_H_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_H_StartingPitcher_ScoreImpact_YTD,
                        dbvar_H_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                        dbvar_H_StartingPitcher_HitsImpact_YTD,
                        dbvar_H_StartingPitcher_NPImpact_YTD,
                        dbvar_H_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_H_StartingPitcher_StrikeImpact_YTD,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_H_StartingPitcher_Score_5G,
                        dbvar_H_StartingPitcher_Strikeouts_5G,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_H_StartingPitcher_BaseOnBalls_5G,
                        dbvar_H_StartingPitcher_Hits_5G,
                        dbvar_H_StartingPitcher_NP_5G,
                        dbvar_H_StartingPitcher_InningsPitched_5G,
                        dbvar_H_StartingPitcher_Strikes_5G,
                        dbvar_H_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_H_StartingPitcher_ScoreImpact_5G,
                        dbvar_H_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_H_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_H_StartingPitcher_HitsImpact_5G,
                        dbvar_H_StartingPitcher_NPImpact_5G,
                        dbvar_H_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_H_StartingPitcher_StrikeImpact_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_H_StartingPitcher_Score_Ratio,
                        dbvar_H_StartingPitcher_Strikeouts_Ratio,
                        dbvar_H_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_H_StartingPitcher_Hits_Ratio,
                        dbvar_H_StartingPitcher_NP_Ratio,
                        dbvar_H_StartingPitcher_InningsPitched_Ratio,
                        dbvar_H_StartingPitcher_Strikes_Ratio,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_H_StartingPitcher_Score_Ratio_5G,
                        dbvar_H_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_H_StartingPitcher_Hits_Ratio_5G,
                        dbvar_H_StartingPitcher_NP_Ratio_5G,
                        dbvar_H_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_H_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_H_BallpenOuts,
                        dbvar_H_BallpenOuts_5G,
                        dbvar_H_BallpenOuts_YTD,
                        dbvar_H_BallpenERA_Approx,
                        dbvar_H_BallpenERA_Approx_5G,
                        dbvar_H_BallpenERA_Approx_YTD,
                        dbvar_G_V_ParkImpactFactor,
                        dbvar_G_Bookie_V_MoneyLine,
                        dbvar_G_Bookie_V_Probability,
                        dbvar_G_V_Opening_MoneyLine,
                        dbvar_G_V_OpeningProbabilityLine,
                        dbvar_G_V_Closing_MoneyLine,
                        dbvar_G_V_ClosingProbabilityLine,
                        dbvar_G_V_CLL_OPL_Prob_Diff,
                        dbvar_G_V_DaysRest,
                        dbvar_G_V_DistanceTravelled,
                        dbvar_G_V_ContiguousGamesV,
                        dbvar_G_V_ContiguousGamesH,
                        dbvar_G_V_TotalDistanceTravelled_3G,
                        dbvar_G_V_Prev1_DistanceTravelled,
                        dbvar_G_V_Prev1Strength,
                        dbvar_G_V_Prev1StrengthRatio,
                        dbvar_G_V_Prev1CLL,
                        dbvar_G_V_Prev2_DistanceTravelled,
                        dbvar_G_V_Prev2Strength,
                        dbvar_G_V_Prev2StrengthRatio,
                        dbvar_G_V_Prev2CLL,
                        dbvar_G_V_Prev3_DistanceTravelled,
                        dbvar_G_V_Prev3Strength,
                        dbvar_G_V_Prev3StrengthRatio,
                        dbvar_G_V_Prev3CLL,
                        dbvar_G_V_Lookback_Strength,
                        dbvar_G_V_Next1_DistanceTravelled,
                        dbvar_G_V_Next1Strength,
                        dbvar_G_V_Next1StrengthRatio,
                        dbvar_G_V_Next2_DistanceTravelled,
                        dbvar_G_V_Next2Strength,
                        dbvar_G_V_Next2StrengthRatio,
                        dbvar_G_V_Next3_DistanceTravelled,
                        dbvar_G_V_Next3Strength,
                        dbvar_G_V_Next3StrengthRatio,
                        dbvar_G_V_Lookahead_Strength,
                        dbvar_V_ClosingProbabilityLine_HV,
                        dbvar_V_ClosingProbabilityLine_YTD_HV,
                        dbvar_V_Runs_Gained,
                        dbvar_V_Runs_Allowed,
                        dbvar_V_Run_Strength,
                        dbvar_V_Run_Efficiency,
                        dbvar_V_Run_Pythag,
                        dbvar_V_Runs_Gained_5G,
                        dbvar_V_Runs_Allowed_5G,
                        dbvar_V_Run_Strength_5G,
                        dbvar_V_Run_Efficiency_5G,
                        dbvar_V_Run_Pythag_5G,
                        dbvar_V_Runs_Gained_20G,
                        dbvar_V_Runs_Allowed_20G,
                        dbvar_V_Run_Strength_20G,
                        dbvar_V_Run_Efficiency_20G,
                        dbvar_V_Run_Pythag_20G,
                        dbvar_V_Runs_Gained_Sum,
                        dbvar_V_Runs_Allowed_Sum,
                        dbvar_V_Run_Strength_Sum,
                        dbvar_V_Run_Efficiency_Sum,
                        dbvar_V_Run_Pythag_Sum,
                        dbvar_V_Runs_Gained_Sum_5G,
                        dbvar_V_Runs_Allowed_Sum_5G,
                        dbvar_V_Run_Strength_Sum_5G,
                        dbvar_V_Run_Efficiency_Sum_5G,
                        dbvar_V_Runs_Gained_Sum_20G,
                        dbvar_V_Runs_Allowed_Sum_20G,
                        dbvar_V_Run_Strength_Sum_20G,
                        dbvar_V_Run_Efficiency_Sum_20G,
                        dbvar_V_Runs_Gained_Sum_HV,
                        dbvar_V_Runs_Allowed_Sum_HV,
                        dbvar_V_Run_Strength_Sum_HV,
                        dbvar_V_Runs_Gained_HV,
                        dbvar_V_Runs_Allowed_HV,
                        dbvar_V_Run_Strength_HV,
                        dbvar_V_Runs_Gained_YTD,
                        dbvar_V_Runs_Allowed_YTD,
                        dbvar_V_Run_Strength_YTD,
                        dbvar_V_Run_Pythag_YTD,
                        dbvar_V_Runs_Gained_YTD_HV,
                        dbvar_V_Runs_Allowed_YTD_HV,
                        dbvar_V_Run_Strength_YTD_HV,
                        dbvar_V_Runs_5InningsGained,
                        dbvar_V_Runs_5InningsAllowed,
                        dbvar_V_Run_5InningsStrength,
                        dbvar_V_Run_5InningsEfficiency,
                        dbvar_V_Runs_5InningsGained_Sum,
                        dbvar_V_Runs_5InningsAllowed_Sum,
                        dbvar_V_Run_5InningsStrength_Sum,
                        dbvar_V_Run_5InningsEfficiency_Sum,
                        dbvar_V_Runs_5InningsGained_5G,
                        dbvar_V_Runs_5InningsAllowed_5G,
                        dbvar_V_Run_5InningsStrength_5G,
                        dbvar_V_Run_5InningsEfficiency_5G,
                        dbvar_V_Runs_5InningsGained_Sum_5G,
                        dbvar_V_Runs_5InningsAllowed_Sum_5G,
                        dbvar_V_Run_5InningsStrength_Sum_5G,
                        dbvar_V_Run_5InningsEfficiency_Sum_5G,
                        dbvar_V_Runs_5InningsGained_20G,
                        dbvar_V_Runs_5InningsAllowed_20G,
                        dbvar_V_Run_5InningsStrength_20G,
                        dbvar_V_Run_5InningsEfficiency_20G,
                        dbvar_V_Runs_5InningsGained_Sum_20G,
                        dbvar_V_Runs_5InningsAllowed_Sum_20G,
                        dbvar_V_Run_5InningsStrength_Sum_20G,
                        dbvar_V_Run_5InningsEfficiency_Sum_20G,
                        dbvar_V_Runs_5InningsGained_Sum_HV,
                        dbvar_V_Runs_5InningsAllowed_Sum_HV,
                        dbvar_V_Run_5InningsStrength_Sum_HV,
                        dbvar_V_Runs_5InningsGained_HV,
                        dbvar_V_Runs_5InningsAllowed_HV,
                        dbvar_V_Run_5InningsStrength_HV,
                        dbvar_V_Runs_5InningsGained_YTD,
                        dbvar_V_Runs_5InningsAllowed_YTD,
                        dbvar_V_Run_5InningsStrength_YTD,
                        dbvar_V_Pythag_Luck_Factor,
                        dbvar_V_Pythag_Luck_Factor_5G,
                        dbvar_V_Pythag_Luck_Factor_20G,
                        dbvar_V_Pythag_Luck_Factor_YTD,
                        dbvar_V_Run_Differential_Per_Game,
                        dbvar_V_Run_Differential_Per_Game_5G,
                        dbvar_V_Run_Differential_Per_Game_20G,
                        dbvar_V_Run_Differential_Per_Game_YTD,
                        dbvar_V_Weighted_Offense_Index,
                        dbvar_V_Weighted_Offense_Index_5G,
                        dbvar_V_Weighted_Offense_Index_20G,
                        dbvar_V_Weighted_Offense_Index_YTD,
                        dbvar_V_At_Bat,
                        dbvar_V_At_Bat_5G,
                        dbvar_V_At_Bat_20G,
                        dbvar_V_At_Bat_YTD,
                        dbvar_V_At_Bat_HV,
                        dbvar_V_At_Bat_YTD_HV,
                        dbvar_V_OBP,
                        dbvar_V_OBP_5G,
                        dbvar_V_OBP_20G,
                        dbvar_V_OBP_YTD,
                        dbvar_V_SLG,
                        dbvar_V_SLG_5G,
                        dbvar_V_SLG_20G,
                        dbvar_V_SLG_YTD,
                        dbvar_V_wOBA,
                        dbvar_V_wOBA_5G,
                        dbvar_V_wOBA_20G,
                        dbvar_V_wOBA_YTD,
                        dbvar_V_OPS,
                        dbvar_V_OPS_5G,
                        dbvar_V_OPS_20G,
                        dbvar_V_OPS_YTD,
                        dbvar_V_Wins,
                        dbvar_V_Losses,
                        dbvar_V_WinLoss_Strength,
                        dbvar_V_Wins_5G,
                        dbvar_V_Losses_5G,
                        dbvar_V_WinLoss_Strength_5G,
                        dbvar_V_Wins_20G,
                        dbvar_V_Losses_20G,
                        dbvar_V_WinLoss_Strength_20G,
                        dbvar_V_Wins_HV,
                        dbvar_V_Losses_HV,
                        dbvar_V_WinLoss_Strength_HV,
                        dbvar_V_Wins_YTD,
                        dbvar_V_Losses_YTD,
                        dbvar_V_WinLoss_Strength_YTD,
                        dbvar_V_Wins_YTD_HV,
                        dbvar_V_Losses_YTD_HV,
                        dbvar_V_WinLoss_Strength_YTD_HV,
                        dbvar_V_OutsPitched_Sum,
                        dbvar_V_OutsPitched,
                        dbvar_V_OutsPitched_5G,
                        dbvar_V_OutsPitched_20G,
                        dbvar_V_OutsPitched_YTD,
                        dbvar_V_OutsPitched_YTD_HV,
                        dbvar_V_StrikeoutsAllowed,
                        dbvar_V_StrikeoutsGained,
                        dbvar_V_StrikeoutAccuracy,
                        dbvar_V_StrikeoutsAllowed_Sum,
                        dbvar_V_StrikeoutsGained_Sum,
                        dbvar_V_StrikeoutAccuracy_Sum,
                        dbvar_V_StrikeoutsAllowed_5G,
                        dbvar_V_StrikeoutsGained_5G,
                        dbvar_V_StrikeoutAccuracy_5G,
                        dbvar_V_StrikeoutsGained_20G,
                        dbvar_V_StrikeoutsAllowed_YTD,
                        dbvar_V_StrikeoutsGained_YTD,
                        dbvar_V_StrikeoutAccuracy_YTD,
                        dbvar_V_StrikeoutsAllowed_YTD_HV,
                        dbvar_V_StrikeoutsGained_YTD_HV,
                        dbvar_V_StrikeoutAccuracy_YTD_HV,
                        dbvar_V_Hits_Sum,
                        dbvar_V_Hits,
                        dbvar_V_Hits_Sum_5G,
                        dbvar_V_Hits_5G,
                        dbvar_V_Hits_Sum_20G,
                        dbvar_V_Hits_20G,
                        dbvar_V_Hits_YTD,
                        dbvar_V_Hits_YTD_HV,
                        dbvar_V_HitsAllowed_Sum,
                        dbvar_V_HitsAllowed_Sum_5G,
                        dbvar_V_HitsAllowed_Sum_20G,
                        dbvar_V_HitsAllowed,
                        dbvar_V_HitsAllowed_5G,
                        dbvar_V_HitsAllowed_20G,
                        dbvar_V_HitsAllowed_YTD,
                        dbvar_V_HitsAllowed_YTD_HV,
                        dbvar_V_RunsHitsRatio,
                        dbvar_V_RunsHitsRatio_Sum,
                        dbvar_V_RunsHitsRatio_5G,
                        dbvar_V_RunsHitsRatio_Sum_5G,
                        dbvar_V_RunsHitsRatio_20G,
                        dbvar_V_RunsHitsRatio_Sum_20G,
                        dbvar_V_RunsHitsRatio_YTD,
                        dbvar_V_RunsHitsRatio_Allowed,
                        dbvar_V_RunsHitsRatio_Allowed_Sum,
                        dbvar_V_RunsHitsRatio_Allowed_5G,
                        dbvar_V_RunsHitsRatio_Allowed_Sum_5G,
                        dbvar_V_RunsHitsRatio_Allowed_20G,
                        dbvar_V_RunsHitsRatio_Allowed_Sum_20G,
                        dbvar_V_RunsHitsRatio_Allowed_YTD,
                        dbvar_V_FIP,
                        dbvar_V_FIP_5G,
                        dbvar_V_FIP_YTD,
                        dbvar_V_FIP_YTD_HV,
                        dbvar_V_K_Minus_BB_Pct,
                        dbvar_V_K_Minus_BB_Pct_5G,
                        dbvar_V_K_Minus_BB_Pct_20G,
                        dbvar_V_K_Minus_BB_Pct_YTD,
                        dbvar_V_HR_Per_9_Allowed,
                        dbvar_V_HR_Per_9_Allowed_5G,
                        dbvar_V_HR_Per_9_Allowed_20G,
                        dbvar_V_HR_Per_9_Allowed_YTD,
                        dbvar_V_K_Per_9,
                        dbvar_V_K_Per_9_5G,
                        dbvar_V_K_Per_9_20G,
                        dbvar_V_K_Per_9_YTD,
                        dbvar_V_WalksAllowed_Sum,
                        dbvar_V_WalksAllowed,
                        dbvar_V_WalksAllowed_Sum_5G,
                        dbvar_V_WalksAllowed_5G,
                        dbvar_V_WalksAllowed_Sum_20G,
                        dbvar_V_WalksAllowed_20G,
                        dbvar_V_WalksAllowed_YTD,
                        dbvar_V_WalksAllowed_YTD_HV,
                        dbvar_V_WalksGained_Sum,
                        dbvar_V_WalksGained,
                        dbvar_V_WalksGained_5G,
                        dbvar_V_WalksGained_20G,
                        dbvar_V_WalksGained_YTD,
                        dbvar_V_WalksGained_YTD_HV,
                        dbvar_V_HomeRuns_Sum,
                        dbvar_V_HomeRuns,
                        dbvar_V_HomeRuns_5G,
                        dbvar_V_HomeRuns_Sum_5G,
                        dbvar_V_HomeRuns_20G,
                        dbvar_V_HomeRuns_Sum_20G,
                        dbvar_V_HomeRuns_YTD,
                        dbvar_V_HomeRuns_YTD_HV,
                        dbvar_V_HomeRuns_Allowed_Sum,
                        dbvar_V_HomeRuns_Allowed,
                        dbvar_V_HomeRuns_Allowed_5G,
                        dbvar_V_HomeRuns_Allowed_20G,
                        dbvar_V_HomeRuns_Allowed_YTD,
                        dbvar_V_HomeRuns_Allowed_YTD_HV,
                        dbvar_V_5thInnScore,
                        dbvar_V_Duration,
                        dbvar_V_NP_Sum,
                        dbvar_V_NP,
                        dbvar_V_NP_5G,
                        dbvar_V_NP_YTD,
                        dbvar_V_NP_YTD_HV,
                        dbvar_V_Strikes_Sum,
                        dbvar_V_StrikeAccuracy_Sum,
                        dbvar_V_Strikes,
                        dbvar_V_StrikeAccuracy,
                        dbvar_V_Strikes_5G,
                        dbvar_V_StrikeAccuracy_5G,
                        dbvar_V_Strikes_YTD,
                        dbvar_V_StrikeAccuracy_YTD,
                        dbvar_V_Strikes_YTD_HV,
                        dbvar_V_StrikeAccuracy_YTD_HV,
                        dbvar_V_MenOnBase,
                        dbvar_V_MenOnBase_Strength,
                        dbvar_V_MenOnBase_Efficiency,
                        dbvar_V_MenOnBase_5G,
                        dbvar_V_MenOnBase_Strength_5G,
                        dbvar_V_MenOnBase_Efficiency_5G,
                        dbvar_V_MenOnBase_20G,
                        dbvar_V_MenOnBase_Strength_20G,
                        dbvar_V_MenOnBase_Efficiency_20G,
                        dbvar_V_MenOnBase_YTD,
                        dbvar_V_MenOnBase_Strength_YTD,
                        dbvar_V_MenOnBase_Efficiency_YTD,
                        dbvar_V_MenOnBase_Allowed,
                        dbvar_V_MenOnBase_Allowed_Efficiency,
                        dbvar_V_MenOnBase_Allowed_5G,
                        dbvar_V_MenOnBase_Allowed_Efficiency_5G,
                        dbvar_V_MenOnBase_Allowed_20G,
                        dbvar_V_MenOnBase_Allowed_Efficiency_20G,
                        dbvar_V_MenOnBase_Allowed_YTD,
                        dbvar_V_MenOnBase_Allowed_Efficiency_YTD,
                        dbvar_V_LeftOnBase_Sum,
                        dbvar_V_LeftOnBase,
                        dbvar_V_2BRuns_Sum,
                        dbvar_V_2BRuns,
                        dbvar_V_2BRuns_Strength,
                        dbvar_V_2BRuns_Sum_5G,
                        dbvar_V_2BRuns_5G,
                        dbvar_V_2BRuns_Strength_5G,
                        dbvar_V_2BRuns_Sum_20G,
                        dbvar_V_2BRuns_20G,
                        dbvar_V_2BRuns_Strength_20G,
                        dbvar_V_2BRuns_YTD,
                        dbvar_V_2BRuns_Strength_YTD,
                        dbvar_V_2BRuns_Allowed,
                        dbvar_V_2BRuns_Allowed_5G,
                        dbvar_V_2BRuns_Allowed_20G,
                        dbvar_V_2BRuns_Allowed_YTD,
                        dbvar_V_3BRuns_Sum,
                        dbvar_V_3BRuns,
                        dbvar_V_3BRuns_5G,
                        dbvar_V_3BRuns_20G,
                        dbvar_V_3BRuns_YTD,
                        dbvar_V_3BRuns_Allowed,
                        dbvar_V_3BRuns_Allowed_5G,
                        dbvar_V_3BRuns_Allowed_20G,
                        dbvar_V_3BRuns_Allowed_YTD,
                        dbvar_V_3BRuns_Strength,
                        dbvar_V_3BRuns_Strength_5G,
                        dbvar_V_3BRuns_Strength_20G,
                        dbvar_V_3BRuns_Strength_YTD,
                        dbvar_V_ErrorMade_Sum,
                        dbvar_V_ErrorMade,
                        dbvar_V_ErrorMade_Sum_5G,
                        dbvar_V_ErrorMade_5G,
                        dbvar_V_ErrorMade_Sum_20G,
                        dbvar_V_ErrorMade_20G,
                        dbvar_V_ErrorMade_YTD,
                        dbvar_V_ErrorMade_YTD_HV,
                        dbvar_V_ErrorForced_Sum,
                        dbvar_V_ErrorForced_Sum_5G,
                        dbvar_V_ErrorForced_Sum_20G,
                        dbvar_V_ErrorForced,
                        dbvar_V_ErrorForced_5G,
                        dbvar_V_ErrorForced_20G,
                        dbvar_V_ErrorForced_YTD,
                        dbvar_V_HitsByPitch_Sum,
                        dbvar_V_HitsByPitch,
                        dbvar_V_HitsByPitch_Sum_5G,
                        dbvar_V_HitsByPitch_5G,
                        dbvar_V_HitsByPitch_Sum_20G,
                        dbvar_V_HitsByPitch_20G,
                        dbvar_V_HitsByPitch_YTD,
                        dbvar_V_HitsByPitch_Allowed,
                        dbvar_V_HitsByPitch_Allowed_5G,
                        dbvar_V_HitsByPitch_Allowed_20G,
                        dbvar_V_HitsByPitch_Allowed_YTD,
                        dbvar_V_DoublePlays_Gained_Sum,
                        dbvar_V_DoublePlays_Gained,
                        dbvar_V_DoublePlays_Gained_Sum_5G,
                        dbvar_V_DoublePlays_Gained_5G,
                        dbvar_V_DoublePlays_Gained_Sum_20G,
                        dbvar_V_DoublePlays_Gained_20G,
                        dbvar_V_DoublePlays_Gained_YTD,
                        dbvar_V_DoublePlays_Gained_YTD_HV,
                        dbvar_V_DoublePlays_Allowed,
                        dbvar_V_DoublePlays_Allowed_5G,
                        dbvar_V_DoublePlays_Allowed_20G,
                        dbvar_V_DoublePlays_Allowed_YTD,
                        dbvar_V_DoublePlays_Allowed_YTD_HV,
                        dbvar_V_ReliefPitchers,
                        dbvar_V_TotalBases_Sum,
                        dbvar_V_TotalBases,
                        dbvar_V_TotalBases_5G,  
                        dbvar_V_TotalBases_20G,
                        dbvar_V_TotalBases_YTD, 
                        dbvar_V_MenOnBaseTBRatio,
                        dbvar_V_MenOnBaseTBRatio_5G,
                        dbvar_V_WalkStrikeoutRatio_Sum,
                        dbvar_V_WalkStrikeoutRatio,
                        dbvar_V_PowerHits_Sum,
                        dbvar_V_PowerHits,
                        dbvar_V_PowerHits_5G,
                        dbvar_V_Innings_OutPitched_Sum,
                        dbvar_V_Innings_OutPitched,
                        dbvar_V_Innings_OutPitched_Sum_5G,
                        dbvar_V_Innings_OutPitched_5G,
                        dbvar_V_Innings_OutPitched_YTD,
                        dbvar_V_SP_HitsAllowed_Sum,
                        dbvar_V_SP_HitsAllowed,
                        dbvar_V_SP_HitsAllowed_5G,
                        dbvar_V_SP_HitsAllowed_YTD,
                        dbvar_V_EarnedRuns_Sum,
                        dbvar_V_EarnedRunAvg_Sum,
                        dbvar_V_EarnedRuns,
                        dbvar_V_EarnedRunAvg,
                        dbvar_V_EarnedRuns_Sum_5G,
                        dbvar_V_EarnedRunAvg_Sum_5G,
                        dbvar_V_EarnedRuns_5G,
                        dbvar_V_EarnedRunAvg_5G,
                        dbvar_V_EarnedRuns_YTD,
                        dbvar_V_EarnedRunAvg_YTD,
                        dbvar_V_HitsAllowedPer9Innings_Sum,
                        dbvar_V_HitsAllowedPer9Innings,
                        dbvar_V_HitsAllowedPer9Innings_5G,
                        dbvar_V_WalksHitsAllowedPerInning,
                        dbvar_V_WalksHitsAllowedPerInning_5G,
                        dbvar_V_WalksHitsAllowedPerInning_YTD,
                        dbvar_V_StartingPitcher_DaysRest,
                        dbvar_V_StartingPitcher_Score_All,
                        dbvar_V_StartingPitcher_Strikeouts_All,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_All,
                        dbvar_V_StartingPitcher_BaseOnBalls_All,
                        dbvar_V_StartingPitcher_Hits_All,
                        dbvar_V_StartingPitcher_NP_All,
                        dbvar_V_StartingPitcher_InningsPitched_All,
                        dbvar_V_StartingPitcher_Strikes_All,
                        dbvar_V_StartingPitcher_StrikeAccuracy_All,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All,
                        dbvar_V_StartingPitcher_Score_YTD,
                        dbvar_V_StartingPitcher_Strikeouts_YTD,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_V_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                        dbvar_V_StartingPitcher_Hits_YTD,
                        dbvar_V_StartingPitcher_NP_YTD,
                        dbvar_V_StartingPitcher_InningsPitched_YTD,
                        dbvar_V_StartingPitcher_Strikes_YTD,
                        dbvar_V_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_V_StartingPitcher_ScoreImpact_YTD,
                        dbvar_V_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_V_StartingPitcher_HitsImpact_YTD,
                        dbvar_V_StartingPitcher_NPImpact_YTD,
                        dbvar_V_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_V_StartingPitcher_StrikeImpact_YTD,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_V_StartingPitcher_Score_5G,
                        dbvar_V_StartingPitcher_Strikeouts_5G,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_V_StartingPitcher_BaseOnBalls_5G,
                        dbvar_V_StartingPitcher_Hits_5G,
                        dbvar_V_StartingPitcher_NP_5G,
                        dbvar_V_StartingPitcher_InningsPitched_5G,
                        dbvar_V_StartingPitcher_Strikes_5G,
                        dbvar_V_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_V_StartingPitcher_ScoreImpact_5G,
                        dbvar_V_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_V_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_V_StartingPitcher_HitsImpact_5G,
                        dbvar_V_StartingPitcher_NPImpact_5G,
                        dbvar_V_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_V_StartingPitcher_StrikeImpact_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_V_StartingPitcher_Score_Ratio,
                        dbvar_V_StartingPitcher_Strikeouts_Ratio,
                        dbvar_V_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_V_StartingPitcher_Hits_Ratio,
                        dbvar_V_StartingPitcher_NP_Ratio,
                        dbvar_V_StartingPitcher_InningsPitched_Ratio,
                        dbvar_V_StartingPitcher_Strikes_Ratio,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_V_StartingPitcher_Score_Ratio_5G,
                        dbvar_V_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_V_StartingPitcher_Hits_Ratio_5G,
                        dbvar_V_StartingPitcher_NP_Ratio_5G,
                        dbvar_V_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_V_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_V_BallpenOuts,
                        dbvar_V_BallpenOuts_5G,
                        dbvar_V_BallpenOuts_YTD,
                        dbvar_V_BallpenERA_Approx,
                        dbvar_V_BallpenERA_Approx_5G,
                        dbvar_V_BallpenERA_Approx_YTD,
                        dbvar_G_VHRatio_DaysRest,
                        dbvar_G_VHRatio_SP_DaysRest,
                        dbvar_G_VHRatio_ParkImpactFactor,
                        dbvar_G_VHRatio_ContiguousGamesV,
                        dbvar_G_VHRatio_ContiguousGamesH,
                        dbvar_G_VHRatio_TotalDistanceTravelled_3G,
                        dbvar_G_VHRatio_ClosingProbabilityLine_HV,
                        dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV,
                        dbvar_G_VHRatio_Runs_Gained,
                        dbvar_G_VHRatio_Runs_Allowed,
                        dbvar_G_VHRatio_Run_Strength,
                        dbvar_G_VHRatio_Run_Efficiency,
                        dbvar_G_VHRatio_Runs_Gained_Sum,
                        dbvar_G_VHRatio_Runs_Allowed_Sum,
                        dbvar_G_VHRatio_Run_Strength_Sum,
                        dbvar_G_VHRatio_Run_Efficiency_Sum,
                        dbvar_G_VHRatio_Run_Pythag,
                        dbvar_G_VHRatio_Runs_Gained_5G,
                        dbvar_G_VHRatio_Runs_Allowed_5G,
                        dbvar_G_VHRatio_Run_Strength_5G,
                        dbvar_G_VHRatio_Run_Efficiency_5G,
                        dbvar_G_VHRatio_Run_Pythag_5G,
                        dbvar_G_VHRatio_Runs_Gained_Sum_5G,
                        dbvar_G_VHRatio_Runs_Allowed_Sum_5G,
                        dbvar_G_VHRatio_Run_Strength_Sum_5G,
                        dbvar_G_VHRatio_Run_Efficiency_Sum_5G,
                        dbvar_G_VHRatio_Runs_Gained_20G,
                        dbvar_G_VHRatio_Runs_Allowed_20G,
                        dbvar_G_VHRatio_Run_Strength_20G,
                        dbvar_G_VHRatio_Run_Efficiency_20G,
                        dbvar_G_VHRatio_Run_Pythag_20G,
                        dbvar_G_VHRatio_Runs_Gained_Sum_20G,
                        dbvar_G_VHRatio_Runs_Allowed_Sum_20G,
                        dbvar_G_VHRatio_Run_Strength_Sum_20G,
                        dbvar_G_VHRatio_Run_Efficiency_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained,
                        dbvar_G_VHRatio_Runs_5InningsAllowed,
                        dbvar_G_VHRatio_Run_5InningsStrength,
                        dbvar_G_VHRatio_Run_5InningsEfficiency,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum,
                        dbvar_G_VHRatio_Runs_5InningsGained_5G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_5G,
                        dbvar_G_VHRatio_Run_5InningsStrength_5G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_5G,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G,
                        dbvar_G_VHRatio_Runs_5InningsGained_20G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_20G,
                        dbvar_G_VHRatio_Run_5InningsStrength_20G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained_HV,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_HV,
                        dbvar_G_VHRatio_Runs_5InningsGained_YTD,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_YTD,
                        dbvar_G_VHRatio_Pythag_Luck_Factor,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_5G,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_20G,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_YTD,
                        dbvar_G_VHRatio_Run_Differential_Per_Game,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_5G,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_20G,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_YTD,
                        dbvar_G_VHRatio_Weighted_Offense_Index,
                        dbvar_G_VHRatio_Weighted_Offense_Index_5G,
                        dbvar_G_VHRatio_Weighted_Offense_Index_20G,
                        dbvar_G_VHRatio_Weighted_Offense_Index_YTD,
                        dbvar_G_VHRatio_At_Bat,
                        dbvar_G_VHRatio_At_Bat_5G,
                        dbvar_G_VHRatio_At_Bat_20G,
                        dbvar_G_VHRatio_At_Bat_YTD,
                        dbvar_G_VHRatio_At_Bat_HV,
                        dbvar_G_VHRatio_At_Bat_YTD_HV,
                        dbvar_G_VHRatio_OBP,
                        dbvar_G_VHRatio_OBP_5G,
                        dbvar_G_VHRatio_OBP_20G,
                        dbvar_G_VHRatio_OBP_YTD,
                        dbvar_G_VHRatio_SLG,
                        dbvar_G_VHRatio_SLG_5G,
                        dbvar_G_VHRatio_SLG_20G,
                        dbvar_G_VHRatio_SLG_YTD,
                        dbvar_G_VHRatio_wOBA,
                        dbvar_G_VHRatio_wOBA_5G,
                        dbvar_G_VHRatio_wOBA_20G,
                        dbvar_G_VHRatio_wOBA_YTD,
                        dbvar_G_VHRatio_OPS,
                        dbvar_G_VHRatio_OPS_5G,
                        dbvar_G_VHRatio_OPS_20G,
                        dbvar_G_VHRatio_OPS_YTD,
                        dbvar_G_VHRatio_Wins,
                        dbvar_G_VHRatio_Losses,
                        dbvar_G_VHRatio_WinLoss_Strength,
                        dbvar_G_VHRatio_Wins_5G,
                        dbvar_G_VHRatio_Losses_5G,
                        dbvar_G_VHRatio_WinLoss_Strength_5G,
                        dbvar_G_VHRatio_Wins_20G,
                        dbvar_G_VHRatio_Losses_20G,
                        dbvar_G_VHRatio_WinLoss_Strength_20G,
                        dbvar_G_VHRatio_OutsPitched,
                        dbvar_G_VHRatio_OutsPitched_5G,
                        dbvar_G_VHRatio_OutsPitched_20G,
                        dbvar_G_VHRatio_OutsPitched_YTD,
                        dbvar_G_VHRatio_OutsPitched_YTD_HV,
                        dbvar_G_VHRatio_StrikeAccuracy,
                        dbvar_G_VHRatio_StrikeAccuracy_5G,
                        dbvar_G_VHRatio_StrikeoutsGained,
                        dbvar_G_VHRatio_StrikeoutsAllowed,
                        dbvar_G_VHRatio_StrikeoutsAccuracy,
                        dbvar_G_VHRatio_StrikeoutsGained_5G,
                        dbvar_G_VHRatio_StrikeoutsAllowed_5G,
                        dbvar_G_VHRatio_StrikeoutsAccuracy_5G,
                        dbvar_G_VHRatio_StrikeoutsGained_20G,
                        dbvar_G_VHRatio_EarnedRuns,
                        dbvar_G_VHRatio_EarnedRunAvg,
                        dbvar_G_VHRatio_EarnedRuns_5G,
                        dbvar_G_VHRatio_EarnedRuns_Avg_5G,
                        dbvar_G_VHRatio_EarnedRuns_Sum_5G,
                        dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G,
                        dbvar_G_VHRatio_EarnedRuns_YTD,
                        dbvar_G_VHRatio_EarnedRunAvg_YTD,
                        dbvar_G_VHRatio_RunsHitsRatio,
                        dbvar_G_VHRatio_RunsHitsRatio_Sum,
                        dbvar_G_VHRatio_RunsHitsRatio_5G,
                        dbvar_G_VHRatio_RunsHitsRatio_Sum_5G,
                        dbvar_G_VHRatio_RunsHitsRatio_Allowed,
                        dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G,
                        dbvar_G_VHRatio_FIP,
                        dbvar_G_VHRatio_FIP_5G,
                        dbvar_G_VHRatio_FIP_YTD,
                        dbvar_G_VHRatio_FIP_YTD_HV,
                        dbvar_G_VHRatio_K_Minus_BB_Pct,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_5G,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_20G,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_YTD,
                        dbvar_G_VHRatio_HR_Per_9_Allowed,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_5G,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_20G,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_YTD,
                        dbvar_G_VHRatio_K_Per_9,
                        dbvar_G_VHRatio_K_Per_9_5G,
                        dbvar_G_VHRatio_K_Per_9_20G,
                        dbvar_G_VHRatio_K_Per_9_YTD,
                        dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV,
                        dbvar_G_VHRatio_WalksAllowed,
                        dbvar_G_VHRatio_WalksAllowed_5G,
                        dbvar_G_VHRatio_WalksAllowed_20G,
                        dbvar_G_VHRatio_WalksAllowed_Sum,
                        dbvar_G_VHRatio_WalksAllowed_Sum_5G,
                        dbvar_G_VHRatio_WalksAllowed_Sum_20G,
                        dbvar_G_VHRatio_PowerHits,
                        dbvar_G_VHRatio_PowerHits_5G,
                        dbvar_G_VHRatio_HitsAllowed_5G,
                        dbvar_G_VHRatio_HitsAllowed_20G,
                        dbvar_G_VHRatio_HitsAllowedPer9Innings,
                        dbvar_G_VHRatio_HitsAllowedPer9Innings_5G,
                        dbvar_G_VHRatio_HitsByPitch_5G,
                        dbvar_G_VHRatio_HitsByPitch_20G,
                        dbvar_G_VHRatio_2BRuns,
                        dbvar_G_VHRatio_2BRuns_5G,
                        dbvar_G_VHRatio_2BRuns_20G,
                        dbvar_G_VHRatio_2BRuns_YTD,
                        dbvar_G_VHRatio_2BRuns_Strength,
                        dbvar_G_VHRatio_2BRuns_Strength_5G,
                        dbvar_G_VHRatio_2BRuns_Strength_20G,
                        dbvar_G_VHRatio_2BRuns_Strength_YTD,
                        dbvar_G_VHRatio_3BRuns,
                        dbvar_G_VHRatio_3BRuns_5G,
                        dbvar_G_VHRatio_3BRuns_20G,
                        dbvar_G_VHRatio_3BRuns_YTD,
                        dbvar_G_VHRatio_3BRuns_Strength,
                        dbvar_G_VHRatio_3BRuns_Strength_5G,
                        dbvar_G_VHRatio_3BRuns_Strength_20G,
                        dbvar_G_VHRatio_3BRuns_Strength_YTD,
                        dbvar_G_VHRatio_HomeRuns_5G,
                        dbvar_G_VHRatio_HomeRuns_20G,
                        dbvar_G_VHRatio_DoublePlays_Gained_5G,
                        dbvar_G_VHRatio_DoublePlays_Gained_20G,
                        dbvar_G_VHRatio_DoublePlays_Gained_YTD,
                        dbvar_G_VHRatio_DoublePlays_Allowed_5G,
                        dbvar_G_VHRatio_DoublePlays_Allowed_20G,
                        dbvar_G_VHRatio_DoublePlays_Allowed_YTD,
                        dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV,
                        dbvar_G_VHRatio_TotalBases,
                        dbvar_G_VHRatio_TotalBases_5G,
                        dbvar_G_VHRatio_TotalBases_20G,
                        dbvar_G_VHRatio_TotalBases_YTD,     
                        dbvar_G_VHRatio_MenOnBaseTBRatio,
                        dbvar_G_VHRatio_MenOnBaseTBRatio_5G,
                        dbvar_G_VHRatio_MenOnBase,
                        dbvar_G_VHRatio_MenOnBase_Strength,
                        dbvar_G_VHRatio_MenOnBase_Efficiency,
                        dbvar_G_VHRatio_MenOnBase_5G,
                        dbvar_G_VHRatio_MenOnBase_Strength_5G,
                        dbvar_G_VHRatio_MenOnBase_Efficiency_5G,
                        dbvar_G_VHRatio_MenOnBase_20G,
                        dbvar_G_VHRatio_MenOnBase_Strength_20G,
                        dbvar_G_VHRatio_MenOnBase_Efficiency_20G,
                        dbvar_G_VHRatio_MenOnBase_Strength_YTD,
                        dbvar_G_VHRatio_MenOnBase_Allowed,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency,
                        dbvar_G_VHRatio_MenOnBase_Allowed_5G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_20G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_YTD,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Score_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_G_VHRatio_BallpenOuts,
                        dbvar_G_VHRatio_BallpenOuts_5G,
                        dbvar_G_VHRatio_BallpenOuts_YTD,
                        dbvar_G_VHRatio_BallpenERA_Approx,
                        dbvar_G_VHRatio_BallpenERA_Approx_5G,
                        dbvar_G_VHRatio_BallpenERA_Approx_YTD,
                        dbvar_G_Ivan_BP_DefenseProbability,
                        dbvar_G_Ivan_BP_OffenseProbability,
                        dbvar_G_Ivan_BP_NullProbability,
                        dbvar_G_Ivan_BP_NoLineProbability,
                        dbvar_G_H_AdjBookieProbabilityLine,
                        dbvar_G_H_Runs,
                        dbvar_G_V_Runs,
                        dbvar_G_Actual_Runs_Diff,
                        dbvar_G_ABSActual_Runs_Diff,
                        dbvar_G_Total,
                        dbvar_G_BookieAdjustedTotal
                    ]

MLBdb_str_vars =    [                         
                        dbvar_G_H_LeagueDiv, 
                        dbvar_G_H_Prev1_LeagueDiv, 
                        dbvar_G_H_Prev1_Summary, 
                        dbvar_G_H_Prev2_LeagueDiv, 
                        dbvar_G_H_Prev2_Summary, 
                        dbvar_G_H_Prev3_LeagueDiv, 
                        dbvar_G_H_Prev3_Summary, 
                        dbvar_G_H_Next1_LeagueDiv, 
                        dbvar_G_H_Next1_Summary, 
                        dbvar_G_H_Next2_LeagueDiv, 
                        dbvar_G_H_Next2_Summary, 
                        dbvar_G_H_Next3_LeagueDiv, 
                        dbvar_G_H_Next3_Summary, 
                        dbvar_G_V_LeagueDiv, 
                        dbvar_G_V_Prev1_LeagueDiv, 
                        dbvar_G_V_Prev1_Summary, 
                        dbvar_G_V_Prev2_LeagueDiv, 
                        dbvar_G_V_Prev2_Summary, 
                        dbvar_G_V_Prev3_LeagueDiv, 
                        dbvar_G_V_Prev3_Summary, 
                        dbvar_G_V_Next1_LeagueDiv, 
                        dbvar_G_V_Next1_Summary, 
                        dbvar_G_V_Next2_LeagueDiv, 
                        dbvar_G_V_Next2_Summary, 
                        dbvar_G_V_Next3_LeagueDiv, 
                        dbvar_G_V_Next3_Summary, 
                        dbvar_G_H_Run_Prediction, 
                        dbvar_G_V_Run_Prediction,
                        dbvar_G_ABSActual_Runs_DiffCategory, 	 
                        dbvar_G_Bookie_Prob_Bet
                    ]

MLBdb_feature_vars =    [ 
                            dbvar_G_Year,
                            dbvar_G_Month,
                            dbvar_G_Day,
                            dbvar_G_MonthWeek,
                            dbvar_G_Opening_TotalOver,
                            dbvar_G_Opening_TotalOverLine,
                            dbvar_G_Closing_TotalOver,
                            dbvar_G_Closing_TotalOverLine,
                            dbvar_G_Bookie_TotalOver,
                            dbvar_G_Bookie_TotalOverLine,
                            dbvar_G_NightGame,
                            dbvar_G_H_Id,
                            dbvar_G_Bookie_H_MoneyLine,
                            dbvar_G_Bookie_H_Probability,
                            dbvar_G_H_Opening_MoneyLine,
                            dbvar_G_H_OpeningProbabilityLine,
                            dbvar_G_H_Closing_MoneyLine,
                            dbvar_G_H_ClosingProbabilityLine,
                            dbvar_G_H_CLL_OPL_Prob_Diff,
                            dbvar_G_H_ParkImpactFactor,
                            dbvar_G_H_League,
                            dbvar_G_H_Division,
                            dbvar_G_H_LeagueDiv,
                            dbvar_G_H_Same_LeagueDiv,
                            dbvar_G_H_Same_Div,
                            dbvar_G_H_DaysRest,
                            dbvar_G_H_ContiguousGamesV,
                            dbvar_G_H_ContiguousGamesH,
                            dbvar_G_H_TotalDistanceTravelled_3G,
                            dbvar_G_H_Prev1_Id,
                            dbvar_G_H_Prev1_LeagueDiv,
                            dbvar_G_H_Prev1_SameLeagueDiv,
                            dbvar_G_H_Prev1_SameDiv,
                            dbvar_G_H_Prev1_DistanceTravelled,
                            dbvar_G_H_Prev1Home,
                            dbvar_G_H_Prev1Strength,
                            dbvar_G_H_Prev1StrengthRatio,
                            dbvar_G_H_Prev1Win,
                            dbvar_G_H_Prev1CLL,
                            dbvar_G_H_Prev1_Summary,
                            dbvar_G_H_Prev2_Id,
                            dbvar_G_H_Prev2_LeagueDiv,
                            dbvar_G_H_Prev2_SameLeagueDiv,
                            dbvar_G_H_Prev2_SameDiv,
                            dbvar_G_H_Prev2_DistanceTravelled,
                            dbvar_G_H_Prev2Home,
                            dbvar_G_H_Prev2Strength,
                            dbvar_G_H_Prev2StrengthRatio,
                            dbvar_G_H_Prev2Win,
                            dbvar_G_H_Prev2CLL,
                            dbvar_G_H_Prev2_Summary,
                            dbvar_G_H_Prev3_Id,
                            dbvar_G_H_Prev3_LeagueDiv,
                            dbvar_G_H_Prev3_SameLeagueDiv,
                            dbvar_G_H_Prev3_SameDiv,
                            dbvar_G_H_Prev3_DistanceTravelled,
                            dbvar_G_H_Prev3Home,
                            dbvar_G_H_Prev3Strength,
                            dbvar_G_H_Prev3StrengthRatio,
                            dbvar_G_H_Prev3Win,
                            dbvar_G_H_Prev3CLL,
                            dbvar_G_H_Prev3_Summary,
                            dbvar_G_H_Lookback_Strength,
                            dbvar_G_H_Next1_Id,
                            dbvar_G_H_Next1_LeagueDiv,
                            dbvar_G_H_Next1_SameLeagueDiv,
                            dbvar_G_H_Next1_SameDiv,
                            dbvar_G_H_Next1_DistanceTravelled,
                            dbvar_G_H_Next1Home,
                            dbvar_G_H_Next1Strength,
                            dbvar_G_H_Next1StrengthRatio,
                            dbvar_G_H_Next1_Summary,
                            dbvar_G_H_Next2_Id,
                            dbvar_G_H_Next2_LeagueDiv,
                            dbvar_G_H_Next2_SameLeagueDiv,
                            dbvar_G_H_Next2_SameDiv,
                            dbvar_G_H_Next2_DistanceTravelled,
                            dbvar_G_H_Next2Home,
                            dbvar_G_H_Next2Strength,
                            dbvar_G_H_Next2StrengthRatio,
                            dbvar_G_H_Next2_Summary,
                            dbvar_G_H_Next3_Id,
                            dbvar_G_H_Next3_LeagueDiv,
                            dbvar_G_H_Next3_SameLeagueDiv,
                            dbvar_G_H_Next3_SameDiv,
                            dbvar_G_H_Next3_DistanceTravelled,
                            dbvar_G_H_Next3Home,
                            dbvar_G_H_Next3Strength,
                            dbvar_G_H_Next3StrengthRatio,
                            dbvar_G_H_Next3_Summary,
                            dbvar_G_H_Lookahead_Strength,
                            dbvar_H_ClosingProbabilityLine_HV,
                            dbvar_H_ClosingProbabilityLine_YTD_HV,
                            dbvar_H_Runs_Gained,
                            dbvar_H_Runs_Allowed,
                            dbvar_H_Run_Strength,
                            dbvar_H_Run_Efficiency,
                            dbvar_H_Run_Pythag,
                            dbvar_H_Runs_Gained_5G,
                            dbvar_H_Runs_Allowed_5G,
                            dbvar_H_Run_Strength_5G,
                            dbvar_H_Run_Efficiency_5G,
                            dbvar_H_Run_Pythag_5G,
                            dbvar_H_Runs_Gained_20G,
                            dbvar_H_Runs_Allowed_20G,
                            dbvar_H_Run_Strength_20G,
                            dbvar_H_Run_Efficiency_20G,
                            dbvar_H_Run_Pythag_20G,
                            dbvar_H_Runs_Gained_Sum,
                            dbvar_H_Runs_Allowed_Sum,
                            dbvar_H_Run_Strength_Sum,
                            dbvar_H_Run_Efficiency_Sum,
                            dbvar_H_Run_Pythag_Sum,
                            dbvar_H_Runs_Gained_Sum_5G,
                            dbvar_H_Runs_Allowed_Sum_5G,
                            dbvar_H_Run_Strength_Sum_5G,
                            dbvar_H_Run_Efficiency_Sum_5G,
                            dbvar_H_Runs_Gained_Sum_20G,
                            dbvar_H_Runs_Allowed_Sum_20G,
                            dbvar_H_Run_Strength_Sum_20G,
                            dbvar_H_Run_Efficiency_Sum_20G,
                            dbvar_H_Runs_Gained_Sum_HV,
                            dbvar_H_Runs_Allowed_Sum_HV,
                            dbvar_H_Run_Strength_Sum_HV,
                            dbvar_H_Runs_Gained_HV,
                            dbvar_H_Runs_Allowed_HV,
                            dbvar_H_Run_Strength_HV,
                            dbvar_H_Runs_Gained_YTD,
                            dbvar_H_Runs_Allowed_YTD,
                            dbvar_H_Run_Strength_YTD,
                            dbvar_H_Run_Pythag_YTD,
                            dbvar_H_Runs_Gained_YTD_HV,
                            dbvar_H_Runs_Allowed_YTD_HV,
                            dbvar_H_Run_Strength_YTD_HV,
                            dbvar_H_Runs_5InningsGained,
                            dbvar_H_Runs_5InningsAllowed,
                            dbvar_H_Run_5InningsStrength,
                            dbvar_H_Run_5InningsEfficiency,
                            dbvar_H_Runs_5InningsGained_Sum,
                            dbvar_H_Runs_5InningsAllowed_Sum,
                            dbvar_H_Run_5InningsStrength_Sum,
                            dbvar_H_Run_5InningsEfficiency_Sum,
                            dbvar_H_Runs_5InningsGained_5G,
                            dbvar_H_Runs_5InningsAllowed_5G,
                            dbvar_H_Run_5InningsStrength_5G,
                            dbvar_H_Run_5InningsEfficiency_5G,
                            dbvar_H_Runs_5InningsGained_Sum_5G,
                            dbvar_H_Runs_5InningsAllowed_Sum_5G,
                            dbvar_H_Run_5InningsStrength_Sum_5G,
                            dbvar_H_Run_5InningsEfficiency_Sum_5G,
                            dbvar_H_Runs_5InningsGained_20G,
                            dbvar_H_Runs_5InningsAllowed_20G,
                            dbvar_H_Run_5InningsStrength_20G,
                            dbvar_H_Run_5InningsEfficiency_20G,
                            dbvar_H_Runs_5InningsGained_Sum_20G,
                            dbvar_H_Runs_5InningsAllowed_Sum_20G,
                            dbvar_H_Run_5InningsStrength_Sum_20G,
                            dbvar_H_Run_5InningsEfficiency_Sum_20G,
                            dbvar_H_Runs_5InningsGained_Sum_HV,
                            dbvar_H_Runs_5InningsAllowed_Sum_HV,
                            dbvar_H_Run_5InningsStrength_Sum_HV,
                            dbvar_H_Runs_5InningsGained_HV,
                            dbvar_H_Runs_5InningsAllowed_HV,
                            dbvar_H_Run_5InningsStrength_HV,
                            dbvar_H_Runs_5InningsGained_YTD,
                            dbvar_H_Runs_5InningsAllowed_YTD,
                            dbvar_H_Run_5InningsStrength_YTD,
                            dbvar_H_Pythag_Luck_Factor,
                            dbvar_H_Pythag_Luck_Factor_5G,
                            dbvar_H_Pythag_Luck_Factor_20G,
                            dbvar_H_Pythag_Luck_Factor_YTD,
                            dbvar_H_Run_Differential_Per_Game,
                            dbvar_H_Run_Differential_Per_Game_5G,
                            dbvar_H_Run_Differential_Per_Game_20G,
                            dbvar_H_Run_Differential_Per_Game_YTD,
                            dbvar_H_Weighted_Offense_Index,
                            dbvar_H_Weighted_Offense_Index_5G,
                            dbvar_H_Weighted_Offense_Index_20G,
                            dbvar_H_Weighted_Offense_Index_YTD,
                            dbvar_H_At_Bat,
                            dbvar_H_At_Bat_5G,
                            dbvar_H_At_Bat_20G,
                            dbvar_H_At_Bat_YTD,
                            dbvar_H_At_Bat_HV,
                            dbvar_H_At_Bat_YTD_HV,
                            dbvar_H_OBP,
                            dbvar_H_OBP_5G,
                            dbvar_H_OBP_20G,
                            dbvar_H_OBP_YTD,
                            dbvar_H_SLG,
                            dbvar_H_SLG_5G,
                            dbvar_H_SLG_20G,
                            dbvar_H_SLG_YTD,
                            dbvar_H_wOBA,
                            dbvar_H_wOBA_5G,
                            dbvar_H_wOBA_20G,
                            dbvar_H_wOBA_YTD,
                            dbvar_H_OPS,
                            dbvar_H_OPS_5G,
                            dbvar_H_OPS_20G,
                            dbvar_H_OPS_YTD,
                            dbvar_H_Wins,
                            dbvar_H_Losses,
                            dbvar_H_WinLoss_Strength,
                            dbvar_H_Wins_5G,
                            dbvar_H_Losses_5G,
                            dbvar_H_WinLoss_Strength_5G,
                            dbvar_H_Wins_20G,
                            dbvar_H_Losses_20G,
                            dbvar_H_WinLoss_Strength_20G,
                            dbvar_H_Wins_HV,
                            dbvar_H_Losses_HV,
                            dbvar_H_WinLoss_Strength_HV,
                            dbvar_H_Wins_YTD,
                            dbvar_H_Losses_YTD,
                            dbvar_H_WinLoss_Strength_YTD,
                            dbvar_H_Wins_YTD_HV,
                            dbvar_H_Losses_YTD_HV,
                            dbvar_H_WinLoss_Strength_YTD_HV,
                            dbvar_H_OutsPitched_Sum,
                            dbvar_H_OutsPitched,
                            dbvar_H_OutsPitched_5G,
                            dbvar_H_OutsPitched_20G,
                            dbvar_H_OutsPitched_YTD,
                            dbvar_H_OutsPitched_YTD_HV,
                            dbvar_H_StrikeoutsAllowed,
                            dbvar_H_StrikeoutsGained,
                            dbvar_H_StrikeoutAccuracy,
                            dbvar_H_StrikeoutsAllowed_Sum,
                            dbvar_H_StrikeoutsGained_Sum,
                            dbvar_H_StrikeoutAccuracy_Sum,
                            dbvar_H_StrikeoutsAllowed_5G,
                            dbvar_H_StrikeoutsGained_5G,
                            dbvar_H_StrikeoutAccuracy_5G,
                            dbvar_H_StrikeoutsGained_20G,
                            dbvar_H_StrikeoutsAllowed_YTD,
                            dbvar_H_StrikeoutsGained_YTD,
                            dbvar_H_StrikeoutAccuracy_YTD,
                            dbvar_H_StrikeoutsAllowed_YTD_HV,
                            dbvar_H_StrikeoutsGained_YTD_HV,
                            dbvar_H_StrikeoutAccuracy_YTD_HV,
                            dbvar_H_Hits_Sum,
                            dbvar_H_Hits,
                            dbvar_H_Hits_Sum_5G,
                            dbvar_H_Hits_5G,
                            dbvar_H_Hits_Sum_20G,
                            dbvar_H_Hits_20G,
                            dbvar_H_Hits_YTD,
                            dbvar_H_Hits_YTD_HV,
                            dbvar_H_HitsAllowed_Sum,
                            dbvar_H_HitsAllowed_Sum_5G,
                            dbvar_H_HitsAllowed_Sum_20G,
                            dbvar_H_HitsAllowed,
                            dbvar_H_HitsAllowed_5G,
                            dbvar_H_HitsAllowed_20G,
                            dbvar_H_HitsAllowed_YTD,
                            dbvar_H_HitsAllowed_YTD_HV,
                            dbvar_H_RunsHitsRatio,
                            dbvar_H_RunsHitsRatio_Sum,
                            dbvar_H_RunsHitsRatio_5G,
                            dbvar_H_RunsHitsRatio_Sum_5G,
                            dbvar_H_RunsHitsRatio_20G,
                            dbvar_H_RunsHitsRatio_Sum_20G,
                            dbvar_H_RunsHitsRatio_YTD,
                            dbvar_H_RunsHitsRatio_Allowed,
                            dbvar_H_RunsHitsRatio_Allowed_Sum,
                            dbvar_H_RunsHitsRatio_Allowed_5G,
                            dbvar_H_RunsHitsRatio_Allowed_Sum_5G,
                            dbvar_H_RunsHitsRatio_Allowed_20G,
                            dbvar_H_RunsHitsRatio_Allowed_Sum_20G,
                            dbvar_H_RunsHitsRatio_Allowed_YTD,
                            dbvar_H_FIP,
                            dbvar_H_FIP_5G,
                            dbvar_H_FIP_YTD,
                            dbvar_H_FIP_YTD_HV,
                            dbvar_H_K_Minus_BB_Pct,
                            dbvar_H_K_Minus_BB_Pct_5G,
                            dbvar_H_K_Minus_BB_Pct_20G,
                            dbvar_H_K_Minus_BB_Pct_YTD,
                            dbvar_H_HR_Per_9_Allowed,
                            dbvar_H_HR_Per_9_Allowed_5G,
                            dbvar_H_HR_Per_9_Allowed_20G,
                            dbvar_H_HR_Per_9_Allowed_YTD,
                            dbvar_H_K_Per_9,
                            dbvar_H_K_Per_9_5G,
                            dbvar_H_K_Per_9_20G,
                            dbvar_H_K_Per_9_YTD,
                            dbvar_H_WalksAllowed_Sum,
                            dbvar_H_WalksAllowed,
                            dbvar_H_WalksAllowed_Sum_5G,
                            dbvar_H_WalksAllowed_5G,
                            dbvar_H_WalksAllowed_Sum_20G,
                            dbvar_H_WalksAllowed_20G,
                            dbvar_H_WalksAllowed_YTD,
                            dbvar_H_WalksAllowed_YTD_HV,
                            dbvar_H_WalksGained_Sum,
                            dbvar_H_WalksGained,
                            dbvar_H_WalksGained_5G,
                            dbvar_H_WalksGained_20G,
                            dbvar_H_WalksGained_YTD,
                            dbvar_H_WalksGained_YTD_HV,
                            dbvar_H_HomeRuns_Sum,
                            dbvar_H_HomeRuns,
                            dbvar_H_HomeRuns_5G,
                            dbvar_H_HomeRuns_Sum_5G,
                            dbvar_H_HomeRuns_20G,
                            dbvar_H_HomeRuns_Sum_20G,
                            dbvar_H_HomeRuns_YTD,
                            dbvar_H_HomeRuns_YTD_HV,
                            dbvar_H_HomeRuns_Allowed_Sum,
                            dbvar_H_HomeRuns_Allowed,
                            dbvar_H_HomeRuns_Allowed_5G,
                            dbvar_H_HomeRuns_Allowed_20G,
                            dbvar_H_HomeRuns_Allowed_YTD,
                            dbvar_H_HomeRuns_Allowed_YTD_HV,
                            dbvar_H_5thInnScore,
                            dbvar_H_Duration,
                            dbvar_H_OverTime,
                            dbvar_H_NP_Sum,
                            dbvar_H_NP,
                            dbvar_H_NP_5G,
                            dbvar_H_NP_YTD,
                            dbvar_H_NP_YTD_HV,
                            dbvar_H_Strikes_Sum,
                            dbvar_H_StrikeAccuracy_Sum,
                            dbvar_H_Strikes,
                            dbvar_H_StrikeAccuracy,
                            dbvar_H_Strikes_5G,
                            dbvar_H_StrikeAccuracy_5G,
                            dbvar_H_Strikes_YTD,
                            dbvar_H_StrikeAccuracy_YTD,
                            dbvar_H_Strikes_YTD_HV,
                            dbvar_H_StrikeAccuracy_YTD_HV,
                            dbvar_H_MenOnBase,
                            dbvar_H_MenOnBase_Strength,
                            dbvar_H_MenOnBase_Efficiency,
                            dbvar_H_MenOnBase_5G,
                            dbvar_H_MenOnBase_Strength_5G,
                            dbvar_H_MenOnBase_Efficiency_5G,
                            dbvar_H_MenOnBase_20G,
                            dbvar_H_MenOnBase_Strength_20G,
                            dbvar_H_MenOnBase_Efficiency_20G,
                            dbvar_H_MenOnBase_YTD,
                            dbvar_H_MenOnBase_Strength_YTD,
                            dbvar_H_MenOnBase_Efficiency_YTD,
                            dbvar_H_MenOnBase_Allowed,
                            dbvar_H_MenOnBase_Allowed_Efficiency,
                            dbvar_H_MenOnBase_Allowed_5G,
                            dbvar_H_MenOnBase_Allowed_Efficiency_5G,
                            dbvar_H_MenOnBase_Allowed_20G,
                            dbvar_H_MenOnBase_Allowed_Efficiency_20G,
                            dbvar_H_MenOnBase_Allowed_YTD,
                            dbvar_H_MenOnBase_Allowed_Efficiency_YTD,
                            dbvar_H_LeftOnBase_Sum,
                            dbvar_H_LeftOnBase,
                            dbvar_H_2BRuns_Sum,
                            dbvar_H_2BRuns,
                            dbvar_H_2BRuns_Sum_5G,
                            dbvar_H_2BRuns_5G,
                            dbvar_H_2BRuns_Sum_20G,
                            dbvar_H_2BRuns_20G,
                            dbvar_H_2BRuns_YTD,
                            dbvar_H_2BRuns_Allowed,
                            dbvar_H_2BRuns_Allowed_5G,
                            dbvar_H_2BRuns_Allowed_20G,
                            dbvar_H_2BRuns_Allowed_YTD,
                            dbvar_H_2BRuns_Strength,
                            dbvar_H_2BRuns_Strength_5G,
                            dbvar_H_2BRuns_Strength_20G,
                            dbvar_H_2BRuns_Strength_YTD,
                            dbvar_H_3BRuns_Sum,
                            dbvar_H_3BRuns,
                            dbvar_H_3BRuns_5G,
                            dbvar_H_3BRuns_20G,
                            dbvar_H_3BRuns_YTD,
                            dbvar_H_3BRuns_Allowed,
                            dbvar_H_3BRuns_Allowed_5G,
                            dbvar_H_3BRuns_Allowed_20G,
                            dbvar_H_3BRuns_Allowed_YTD,
                            dbvar_H_3BRuns_Strength,
                            dbvar_H_3BRuns_Strength_5G,
                            dbvar_H_3BRuns_Strength_20G,
                            dbvar_H_3BRuns_Strength_YTD,
                            dbvar_H_ErrorMade_Sum,
                            dbvar_H_ErrorMade,
                            dbvar_H_ErrorMade_Sum_5G,
                            dbvar_H_ErrorMade_5G,
                            dbvar_H_ErrorMade_Sum_20G,
                            dbvar_H_ErrorMade_20G,
                            dbvar_H_ErrorMade_YTD,
                            dbvar_H_ErrorMade_YTD_HV,
                            dbvar_H_ErrorForced_Sum,
                            dbvar_H_ErrorForced_Sum_5G,
                            dbvar_H_ErrorForced_Sum_20G,
                            dbvar_H_ErrorForced,
                            dbvar_H_ErrorForced_5G,
                            dbvar_H_ErrorForced_20G,
                            dbvar_H_ErrorForced_YTD,
                            dbvar_H_HitsByPitch_Sum,
                            dbvar_H_HitsByPitch,
                            dbvar_H_HitsByPitch_Sum_5G,
                            dbvar_H_HitsByPitch_5G,
                            dbvar_H_HitsByPitch_Sum_20G,
                            dbvar_H_HitsByPitch_20G,
                            dbvar_H_HitsByPitch_YTD,
                            dbvar_H_HitsByPitch_Allowed,
                            dbvar_H_HitsByPitch_Allowed_5G,
                            dbvar_H_HitsByPitch_Allowed_20G,
                            dbvar_H_HitsByPitch_Allowed_YTD,
                            dbvar_H_DoublePlays_Gained_Sum,
                            dbvar_H_DoublePlays_Gained,
                            dbvar_H_DoublePlays_Gained_Sum_5G,
                            dbvar_H_DoublePlays_Gained_5G,
                            dbvar_H_DoublePlays_Gained_Sum_20G,
                            dbvar_H_DoublePlays_Gained_20G,
                            dbvar_H_DoublePlays_Gained_YTD,
                            dbvar_H_DoublePlays_Gained_YTD_HV,
                            dbvar_H_DoublePlays_Allowed,
                            dbvar_H_DoublePlays_Allowed_5G,
                            dbvar_H_DoublePlays_Allowed_20G,
                            dbvar_H_DoublePlays_Allowed_YTD,
                            dbvar_H_DoublePlays_Allowed_YTD_HV,
                            dbvar_H_ReliefPitchers,
                            dbvar_H_TotalBases_Sum,
                            dbvar_H_TotalBases,
                            dbvar_H_TotalBases_5G,          
                            dbvar_H_TotalBases_20G,
                            dbvar_H_TotalBases_YTD,     
                            dbvar_H_MenOnBaseTBRatio,
                            dbvar_H_MenOnBaseTBRatio_5G,
                            dbvar_H_WalkStrikeoutRatio_Sum,
                            dbvar_H_WalkStrikeoutRatio,
                            dbvar_H_PowerHits_Sum,
                            dbvar_H_PowerHits,
                            dbvar_H_PowerHits_5G,
                            dbvar_H_Innings_OutPitched_Sum,
                            dbvar_H_Innings_OutPitched,
                            dbvar_H_Innings_OutPitched_Sum_5G,
                            dbvar_H_Innings_OutPitched_5G, 
                            dbvar_H_Innings_OutPitched_YTD, 
                            dbvar_H_SP_HitsAllowed_Sum,
                            dbvar_H_SP_HitsAllowed,
                            dbvar_H_SP_HitsAllowed_5G,
                            dbvar_H_SP_HitsAllowed_YTD,
                            dbvar_H_EarnedRuns_Sum,
                            dbvar_H_EarnedRunAvg_Sum,
                            dbvar_H_EarnedRuns,
                            dbvar_H_EarnedRunAvg,
                            dbvar_H_EarnedRuns_Sum_5G,
                            dbvar_H_EarnedRunAvg_Sum_5G,
                            dbvar_H_EarnedRuns_5G,
                            dbvar_H_EarnedRunAvg_5G,
                            dbvar_H_EarnedRuns_YTD,
                            dbvar_H_EarnedRunAvg_YTD,
                            dbvar_H_HitsAllowedPer9Innings_Sum,
                            dbvar_H_HitsAllowedPer9Innings,
                            dbvar_H_HitsAllowedPer9Innings_5G,
                            dbvar_H_WalksHitsAllowedPerInning,
                            dbvar_H_WalksHitsAllowedPerInning_5G,
                            dbvar_H_WalksHitsAllowedPerInning_YTD,
                            dbvar_G_H_StartingPitcher_Id,
                            dbvar_H_StartingPitcher_DaysRest,
                            dbvar_H_StartingPitcher_Score_All,
                            dbvar_H_StartingPitcher_Strikeouts_All,
                            dbvar_H_StartingPitcher_StrikeoutAccuracy_All,
                            dbvar_H_StartingPitcher_BaseOnBalls_All,
                            dbvar_H_StartingPitcher_Hits_All,
                            dbvar_H_StartingPitcher_NP_All,
                            dbvar_H_StartingPitcher_InningsPitched_All,
                            dbvar_H_StartingPitcher_Strikes_All,
                            dbvar_H_StartingPitcher_StrikeAccuracy_All,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All,
                            dbvar_H_StartingPitcher_Score_YTD,
                            dbvar_H_StartingPitcher_Strikeouts_YTD,
                            dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD,
                            dbvar_H_StartingPitcher_BaseOnBalls_YTD,
                            dbvar_H_StartingPitcher_Hits_YTD,
                            dbvar_H_StartingPitcher_NP_YTD,
                            dbvar_H_StartingPitcher_InningsPitched_YTD,
                            dbvar_H_StartingPitcher_Strikes_YTD,
                            dbvar_H_StartingPitcher_StrikeAccuracy_YTD,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                            dbvar_H_StartingPitcher_ScoreImpact_YTD,
                            dbvar_H_StartingPitcher_StrikeoutsImpact_YTD,
                            dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD,
                            dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                            dbvar_H_StartingPitcher_HitsImpact_YTD,
                            dbvar_H_StartingPitcher_NPImpact_YTD,
                            dbvar_H_StartingPitcher_InningsPitchedImpact_YTD,
                            dbvar_H_StartingPitcher_StrikeImpact_YTD,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                            dbvar_H_StartingPitcher_Score_5G,
                            dbvar_H_StartingPitcher_Strikeouts_5G,
                            dbvar_H_StartingPitcher_StrikeoutAccuracy_5G,
                            dbvar_H_StartingPitcher_BaseOnBalls_5G,
                            dbvar_H_StartingPitcher_Hits_5G,
                            dbvar_H_StartingPitcher_NP_5G,
                            dbvar_H_StartingPitcher_InningsPitched_5G,
                            dbvar_H_StartingPitcher_Strikes_5G,
                            dbvar_H_StartingPitcher_StrikeAccuracy_5G,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G,
                            dbvar_H_StartingPitcher_ScoreImpact_5G,
                            dbvar_H_StartingPitcher_StrikeoutsImpact_5G,
                            dbvar_H_StartingPitcher_BaseOnBallsImpact_5G,
                            dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                            dbvar_H_StartingPitcher_HitsImpact_5G,
                            dbvar_H_StartingPitcher_NPImpact_5G,
                            dbvar_H_StartingPitcher_InningsPitchedImpact_5G,
                            dbvar_H_StartingPitcher_StrikeImpact_5G,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                            dbvar_H_StartingPitcher_Score_Ratio,
                            dbvar_H_StartingPitcher_Strikeouts_Ratio,
                            dbvar_H_StartingPitcher_BaseOnBalls_Ratio,
                            dbvar_H_StartingPitcher_Hits_Ratio,
                            dbvar_H_StartingPitcher_NP_Ratio,
                            dbvar_H_StartingPitcher_InningsPitched_Ratio,
                            dbvar_H_StartingPitcher_Strikes_Ratio,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                            dbvar_H_StartingPitcher_Score_Ratio_5G,
                            dbvar_H_StartingPitcher_Strikeouts_Ratio_5G,
                            dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G,
                            dbvar_H_StartingPitcher_Hits_Ratio_5G,
                            dbvar_H_StartingPitcher_NP_Ratio_5G,
                            dbvar_H_StartingPitcher_InningsPitched_Ratio_5G,
                            dbvar_H_StartingPitcher_Strikes_Ratio_5G,
                            dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                            dbvar_H_BallpenOuts,
                            dbvar_H_BallpenOuts_5G,
                            dbvar_H_BallpenOuts_YTD,
                            dbvar_H_BallpenERA_Approx,
                            dbvar_H_BallpenERA_Approx_5G,
                            dbvar_H_BallpenERA_Approx_YTD,
                            dbvar_G_V_Id,
                            dbvar_G_V_ParkImpactFactor,
                            dbvar_G_Bookie_V_MoneyLine,
                            dbvar_G_Bookie_V_Probability,
                            dbvar_G_V_Opening_MoneyLine,
                            dbvar_G_V_OpeningProbabilityLine,
                            dbvar_G_V_Closing_MoneyLine,
                            dbvar_G_V_ClosingProbabilityLine,
                            dbvar_G_V_CLL_OPL_Prob_Diff,
                            dbvar_G_V_League,
                            dbvar_G_V_Division,
                            dbvar_G_V_LeagueDiv,
                            dbvar_G_V_Same_LeagueDiv,
                            dbvar_G_V_Same_Div,
                            dbvar_G_V_DaysRest,
                            dbvar_G_V_DistanceTravelled,
                            dbvar_G_V_ContiguousGamesV,
                            dbvar_G_V_ContiguousGamesH,
                            dbvar_G_V_TotalDistanceTravelled_3G,
                            dbvar_G_V_Prev1_Id,
                            dbvar_G_V_Prev1_LeagueDiv,
                            dbvar_G_V_Prev1_SameLeagueDiv,
                            dbvar_G_V_Prev1_SameDiv,
                            dbvar_G_V_Prev1_DistanceTravelled,
                            dbvar_G_V_Prev1Home,
                            dbvar_G_V_Prev1Strength,
                            dbvar_G_V_Prev1StrengthRatio,
                            dbvar_G_V_Prev1Win,
                            dbvar_G_V_Prev1CLL,
                            dbvar_G_V_Prev1_Summary,
                            dbvar_G_V_Prev2_Id,
                            dbvar_G_V_Prev2_LeagueDiv,
                            dbvar_G_V_Prev2_SameLeagueDiv,
                            dbvar_G_V_Prev2_SameDiv,
                            dbvar_G_V_Prev2_DistanceTravelled,
                            dbvar_G_V_Prev2Home,
                            dbvar_G_V_Prev2Strength,
                            dbvar_G_V_Prev2StrengthRatio,
                            dbvar_G_V_Prev2Win,
                            dbvar_G_V_Prev2CLL,
                            dbvar_G_V_Prev2_Summary,
                            dbvar_G_V_Prev3_Id,
                            dbvar_G_V_Prev3_LeagueDiv,
                            dbvar_G_V_Prev3_SameLeagueDiv,
                            dbvar_G_V_Prev3_SameDiv,
                            dbvar_G_V_Prev3_DistanceTravelled,
                            dbvar_G_V_Prev3Home,
                            dbvar_G_V_Prev3Strength,
                            dbvar_G_V_Prev3StrengthRatio,
                            dbvar_G_V_Prev3Win,
                            dbvar_G_V_Prev3CLL,
                            dbvar_G_V_Prev3_Summary,
                            dbvar_G_V_Lookback_Strength,
                            dbvar_G_V_Next1_Id,
                            dbvar_G_V_Next1_LeagueDiv,
                            dbvar_G_V_Next1_SameLeagueDiv,
                            dbvar_G_V_Next1_SameDiv,
                            dbvar_G_V_Next1_DistanceTravelled,
                            dbvar_G_V_Next1Home,
                            dbvar_G_V_Next1Strength,
                            dbvar_G_V_Next1StrengthRatio,
                            dbvar_G_V_Next1_Summary,
                            dbvar_G_V_Next2_Id,
                            dbvar_G_V_Next2_LeagueDiv,
                            dbvar_G_V_Next2_SameLeagueDiv,
                            dbvar_G_V_Next2_SameDiv,
                            dbvar_G_V_Next2_DistanceTravelled,
                            dbvar_G_V_Next2Home,
                            dbvar_G_V_Next2Strength,
                            dbvar_G_V_Next2StrengthRatio,
                            dbvar_G_V_Next2_Summary,
                            dbvar_G_V_Next3_Id,
                            dbvar_G_V_Next3_LeagueDiv,
                            dbvar_G_V_Next3_SameLeagueDiv,
                            dbvar_G_V_Next3_SameDiv,
                            dbvar_G_V_Next3_DistanceTravelled,
                            dbvar_G_V_Next3Home,
                            dbvar_G_V_Next3Strength,
                            dbvar_G_V_Next3StrengthRatio,
                            dbvar_G_V_Next3_Summary,
                            dbvar_G_V_Lookahead_Strength,
                            dbvar_V_ClosingProbabilityLine_HV,
                            dbvar_V_ClosingProbabilityLine_YTD_HV,
                            dbvar_V_Runs_Gained,
                            dbvar_V_Runs_Allowed,
                            dbvar_V_Run_Strength,
                            dbvar_V_Run_Efficiency,
                            dbvar_V_Run_Pythag,
                            dbvar_V_Runs_Gained_5G,
                            dbvar_V_Runs_Allowed_5G,
                            dbvar_V_Run_Strength_5G,
                            dbvar_V_Run_Efficiency_5G,
                            dbvar_V_Run_Pythag_5G,
                            dbvar_V_Runs_Gained_20G,
                            dbvar_V_Runs_Allowed_20G,
                            dbvar_V_Run_Strength_20G,
                            dbvar_V_Run_Efficiency_20G,
                            dbvar_V_Run_Pythag_20G,
                            dbvar_V_Runs_Gained_Sum,
                            dbvar_V_Runs_Allowed_Sum,
                            dbvar_V_Run_Strength_Sum,
                            dbvar_V_Run_Efficiency_Sum,
                            dbvar_V_Run_Pythag_Sum,
                            dbvar_V_Runs_Gained_Sum_5G,
                            dbvar_V_Runs_Allowed_Sum_5G,
                            dbvar_V_Run_Strength_Sum_5G,
                            dbvar_V_Run_Efficiency_Sum_5G,
                            dbvar_V_Runs_Gained_Sum_20G,
                            dbvar_V_Runs_Allowed_Sum_20G,
                            dbvar_V_Run_Strength_Sum_20G,
                            dbvar_V_Run_Efficiency_Sum_20G,
                            dbvar_V_Runs_Gained_Sum_HV,
                            dbvar_V_Runs_Allowed_Sum_HV,
                            dbvar_V_Run_Strength_Sum_HV,
                            dbvar_V_Runs_Gained_HV,
                            dbvar_V_Runs_Allowed_HV,
                            dbvar_V_Run_Strength_HV,
                            dbvar_V_Runs_Gained_YTD,
                            dbvar_V_Runs_Allowed_YTD,
                            dbvar_V_Run_Strength_YTD,
                            dbvar_V_Run_Pythag_YTD,
                            dbvar_V_Runs_Gained_YTD_HV,
                            dbvar_V_Runs_Allowed_YTD_HV,
                            dbvar_V_Run_Strength_YTD_HV,
                            dbvar_V_Runs_5InningsGained,
                            dbvar_V_Runs_5InningsAllowed,
                            dbvar_V_Run_5InningsStrength,
                            dbvar_V_Run_5InningsEfficiency,
                            dbvar_V_Runs_5InningsGained_Sum,
                            dbvar_V_Runs_5InningsAllowed_Sum,
                            dbvar_V_Run_5InningsStrength_Sum,
                            dbvar_V_Run_5InningsEfficiency_Sum,
                            dbvar_V_Runs_5InningsGained_5G,
                            dbvar_V_Runs_5InningsAllowed_5G,
                            dbvar_V_Run_5InningsStrength_5G,
                            dbvar_V_Run_5InningsEfficiency_5G,
                            dbvar_V_Runs_5InningsGained_Sum_5G,
                            dbvar_V_Runs_5InningsAllowed_Sum_5G,
                            dbvar_V_Run_5InningsStrength_Sum_5G,
                            dbvar_V_Run_5InningsEfficiency_Sum_5G,
                            dbvar_V_Runs_5InningsGained_20G,
                            dbvar_V_Runs_5InningsAllowed_20G,
                            dbvar_V_Run_5InningsStrength_20G,
                            dbvar_V_Run_5InningsEfficiency_20G,
                            dbvar_V_Runs_5InningsGained_Sum_20G,
                            dbvar_V_Runs_5InningsAllowed_Sum_20G,
                            dbvar_V_Run_5InningsStrength_Sum_20G,
                            dbvar_V_Run_5InningsEfficiency_Sum_20G,
                            dbvar_V_Runs_5InningsGained_Sum_HV,
                            dbvar_V_Runs_5InningsAllowed_Sum_HV,
                            dbvar_V_Run_5InningsStrength_Sum_HV,
                            dbvar_V_Runs_5InningsGained_HV,
                            dbvar_V_Runs_5InningsAllowed_HV,
                            dbvar_V_Run_5InningsStrength_HV,
                            dbvar_V_Runs_5InningsGained_YTD,
                            dbvar_V_Runs_5InningsAllowed_YTD,
                            dbvar_V_Run_5InningsStrength_YTD,
                            dbvar_V_Pythag_Luck_Factor,
                            dbvar_V_Pythag_Luck_Factor_5G,
                            dbvar_V_Pythag_Luck_Factor_20G,
                            dbvar_V_Pythag_Luck_Factor_YTD,
                            dbvar_V_Run_Differential_Per_Game,
                            dbvar_V_Run_Differential_Per_Game_5G,
                            dbvar_V_Run_Differential_Per_Game_20G,
                            dbvar_V_Run_Differential_Per_Game_YTD,
                            dbvar_V_Weighted_Offense_Index,
                            dbvar_V_Weighted_Offense_Index_5G,
                            dbvar_V_Weighted_Offense_Index_20G,
                            dbvar_V_Weighted_Offense_Index_YTD,
                            dbvar_V_At_Bat,
                            dbvar_V_At_Bat_5G,
                            dbvar_V_At_Bat_20G,
                            dbvar_V_At_Bat_YTD,
                            dbvar_V_At_Bat_HV,
                            dbvar_V_At_Bat_YTD_HV,
                            dbvar_V_OBP,
                            dbvar_V_OBP_5G,
                            dbvar_V_OBP_20G,
                            dbvar_V_OBP_YTD,
                            dbvar_V_SLG,
                            dbvar_V_SLG_5G,
                            dbvar_V_SLG_20G,
                            dbvar_V_SLG_YTD,
                            dbvar_V_wOBA,
                            dbvar_V_wOBA_5G,
                            dbvar_V_wOBA_20G,
                            dbvar_V_wOBA_YTD,
                            dbvar_V_OPS,
                            dbvar_V_OPS_5G,
                            dbvar_V_OPS_20G,
                            dbvar_V_OPS_YTD,
                            dbvar_V_Wins,
                            dbvar_V_Losses,
                            dbvar_V_WinLoss_Strength,
                            dbvar_V_Wins_5G,
                            dbvar_V_Losses_5G,
                            dbvar_V_WinLoss_Strength_5G,
                            dbvar_V_Wins_20G,
                            dbvar_V_Losses_20G,
                            dbvar_V_WinLoss_Strength_20G,
                            dbvar_V_Wins_HV,
                            dbvar_V_Losses_HV,
                            dbvar_V_WinLoss_Strength_HV,
                            dbvar_V_Wins_YTD,
                            dbvar_V_Losses_YTD,
                            dbvar_V_WinLoss_Strength_YTD,
                            dbvar_V_Wins_YTD_HV,
                            dbvar_V_Losses_YTD_HV,
                            dbvar_V_WinLoss_Strength_YTD_HV,
                            dbvar_V_OutsPitched_Sum,
                            dbvar_V_OutsPitched,
                            dbvar_V_OutsPitched_5G,
                            dbvar_V_OutsPitched_20G,
                            dbvar_V_OutsPitched_YTD,
                            dbvar_V_OutsPitched_YTD_HV,
                            dbvar_V_StrikeoutsAllowed,
                            dbvar_V_StrikeoutsGained,
                            dbvar_V_StrikeoutAccuracy,
                            dbvar_V_StrikeoutsAllowed_Sum,
                            dbvar_V_StrikeoutsGained_Sum,
                            dbvar_V_StrikeoutAccuracy_Sum,
                            dbvar_V_StrikeoutsAllowed_5G,
                            dbvar_V_StrikeoutsGained_5G,
                            dbvar_V_StrikeoutAccuracy_5G,
                            dbvar_V_StrikeoutsGained_20G,
                            dbvar_V_StrikeoutsAllowed_YTD,
                            dbvar_V_StrikeoutsGained_YTD,
                            dbvar_V_StrikeoutAccuracy_YTD,
                            dbvar_V_StrikeoutsAllowed_YTD_HV,
                            dbvar_V_StrikeoutsGained_YTD_HV,
                            dbvar_V_StrikeoutAccuracy_YTD_HV,
                            dbvar_V_Hits_Sum,
                            dbvar_V_Hits,
                            dbvar_V_Hits_Sum_5G,
                            dbvar_V_Hits_5G,
                            dbvar_V_Hits_Sum_20G,
                            dbvar_V_Hits_20G,
                            dbvar_V_Hits_YTD,
                            dbvar_V_Hits_YTD_HV,
                            dbvar_V_HitsAllowed_Sum,
                            dbvar_V_HitsAllowed_Sum_5G,
                            dbvar_V_HitsAllowed_Sum_20G,
                            dbvar_V_HitsAllowed,
                            dbvar_V_HitsAllowed_5G,
                            dbvar_V_HitsAllowed_20G,
                            dbvar_V_HitsAllowed_YTD,
                            dbvar_V_HitsAllowed_YTD_HV,
                            dbvar_V_RunsHitsRatio,
                            dbvar_V_RunsHitsRatio_Sum,
                            dbvar_V_RunsHitsRatio_5G,
                            dbvar_V_RunsHitsRatio_Sum_5G,
                            dbvar_V_RunsHitsRatio_20G,
                            dbvar_V_RunsHitsRatio_Sum_20G,
                            dbvar_V_RunsHitsRatio_YTD,
                            dbvar_V_RunsHitsRatio_Allowed,
                            dbvar_V_RunsHitsRatio_Allowed_Sum,
                            dbvar_V_RunsHitsRatio_Allowed_5G,
                            dbvar_V_RunsHitsRatio_Allowed_Sum_5G,
                            dbvar_V_RunsHitsRatio_Allowed_20G,
                            dbvar_V_RunsHitsRatio_Allowed_Sum_20G,
                            dbvar_V_RunsHitsRatio_Allowed_YTD,
                            dbvar_V_FIP,
                            dbvar_V_FIP_5G,
                            dbvar_V_FIP_YTD,
                            dbvar_V_FIP_YTD_HV,
                            dbvar_V_K_Minus_BB_Pct,
                            dbvar_V_K_Minus_BB_Pct_5G,
                            dbvar_V_K_Minus_BB_Pct_20G,
                            dbvar_V_K_Minus_BB_Pct_YTD,
                            dbvar_V_HR_Per_9_Allowed,
                            dbvar_V_HR_Per_9_Allowed_5G,
                            dbvar_V_HR_Per_9_Allowed_20G,
                            dbvar_V_HR_Per_9_Allowed_YTD,
                            dbvar_V_K_Per_9,
                            dbvar_V_K_Per_9_5G,
                            dbvar_V_K_Per_9_20G,
                            dbvar_V_K_Per_9_YTD,
                            dbvar_V_WalksAllowed_Sum,
                            dbvar_V_WalksAllowed,
                            dbvar_V_WalksAllowed_Sum_5G,
                            dbvar_V_WalksAllowed_5G,
                            dbvar_V_WalksAllowed_Sum_20G,
                            dbvar_V_WalksAllowed_20G,
                            dbvar_V_WalksAllowed_YTD,
                            dbvar_V_WalksAllowed_YTD_HV,
                            dbvar_V_WalksGained_Sum,
                            dbvar_V_WalksGained,
                            dbvar_V_WalksGained_5G,
                            dbvar_V_WalksGained_20G,
                            dbvar_V_WalksGained_YTD,
                            dbvar_V_WalksGained_YTD_HV,
                            dbvar_V_HomeRuns_Sum,
                            dbvar_V_HomeRuns,
                            dbvar_V_HomeRuns_5G,
                            dbvar_V_HomeRuns_Sum_5G,
                            dbvar_V_HomeRuns_20G,
                            dbvar_V_HomeRuns_Sum_20G,
                            dbvar_V_HomeRuns_YTD,
                            dbvar_V_HomeRuns_YTD_HV,
                            dbvar_V_HomeRuns_Allowed_Sum,
                            dbvar_V_HomeRuns_Allowed,
                            dbvar_V_HomeRuns_Allowed_5G,
                            dbvar_V_HomeRuns_Allowed_20G,
                            dbvar_V_HomeRuns_Allowed_YTD,
                            dbvar_V_HomeRuns_Allowed_YTD_HV,
                            dbvar_V_5thInnScore,
                            dbvar_V_Duration,
                            dbvar_V_OverTime,
                            dbvar_V_NP_Sum,
                            dbvar_V_NP,
                            dbvar_V_NP_5G,
                            dbvar_V_NP_YTD,
                            dbvar_V_NP_YTD_HV,
                            dbvar_V_Strikes_Sum,
                            dbvar_V_StrikeAccuracy_Sum,
                            dbvar_V_Strikes,
                            dbvar_V_StrikeAccuracy,
                            dbvar_V_Strikes_5G,
                            dbvar_V_StrikeAccuracy_5G,
                            dbvar_V_Strikes_YTD,
                            dbvar_V_StrikeAccuracy_YTD,
                            dbvar_V_Strikes_YTD_HV,
                            dbvar_V_StrikeAccuracy_YTD_HV,
                            dbvar_V_MenOnBase,
                            dbvar_V_MenOnBase_Strength,
                            dbvar_V_MenOnBase_Efficiency,
                            dbvar_V_MenOnBase_5G,
                            dbvar_V_MenOnBase_Strength_5G,
                            dbvar_V_MenOnBase_Efficiency_5G,
                            dbvar_V_MenOnBase_20G,
                            dbvar_V_MenOnBase_Strength_20G,
                            dbvar_V_MenOnBase_Efficiency_20G,
                            dbvar_V_MenOnBase_YTD,
                            dbvar_V_MenOnBase_Strength_YTD,
                            dbvar_V_MenOnBase_Efficiency_YTD,
                            dbvar_V_MenOnBase_Allowed,
                            dbvar_V_MenOnBase_Allowed_Efficiency,
                            dbvar_V_MenOnBase_Allowed_5G,
                            dbvar_V_MenOnBase_Allowed_Efficiency_5G,
                            dbvar_V_MenOnBase_Allowed_20G,
                            dbvar_V_MenOnBase_Allowed_Efficiency_20G,
                            dbvar_V_MenOnBase_Allowed_YTD,
                            dbvar_V_MenOnBase_Allowed_Efficiency_YTD,
                            dbvar_V_LeftOnBase_Sum,
                            dbvar_V_LeftOnBase,
                            dbvar_V_2BRuns_Sum,
                            dbvar_V_2BRuns,
                            dbvar_V_2BRuns_Strength,
                            dbvar_V_2BRuns_Sum_5G,
                            dbvar_V_2BRuns_5G,
                            dbvar_V_2BRuns_Strength_5G,
                            dbvar_V_2BRuns_Sum_20G,
                            dbvar_V_2BRuns_20G,
                            dbvar_V_2BRuns_Strength_20G,
                            dbvar_V_2BRuns_YTD,
                            dbvar_V_2BRuns_Strength_YTD,
                            dbvar_V_2BRuns_Allowed,
                            dbvar_V_2BRuns_Allowed_5G,
                            dbvar_V_2BRuns_Allowed_20G,
                            dbvar_V_2BRuns_Allowed_YTD,
                            dbvar_V_3BRuns_Sum,
                            dbvar_V_3BRuns,
                            dbvar_V_3BRuns_5G,
                            dbvar_V_3BRuns_20G,
                            dbvar_V_3BRuns_YTD,
                            dbvar_V_3BRuns_Allowed,
                            dbvar_V_3BRuns_Allowed_5G,
                            dbvar_V_3BRuns_Allowed_20G,
                            dbvar_V_3BRuns_Allowed_YTD,
                            dbvar_V_3BRuns_Strength,
                            dbvar_V_3BRuns_Strength_5G,
                            dbvar_V_3BRuns_Strength_20G,
                            dbvar_V_3BRuns_Strength_YTD,
                            dbvar_V_ErrorMade_Sum,
                            dbvar_V_ErrorMade,
                            dbvar_V_ErrorMade_Sum_5G,
                            dbvar_V_ErrorMade_5G,
                            dbvar_V_ErrorMade_Sum_20G,
                            dbvar_V_ErrorMade_20G,
                            dbvar_V_ErrorMade_YTD,
                            dbvar_V_ErrorMade_YTD_HV,
                            dbvar_V_ErrorForced_Sum,
                            dbvar_V_ErrorForced_Sum_5G,
                            dbvar_V_ErrorForced_Sum_20G,
                            dbvar_V_ErrorForced,
                            dbvar_V_ErrorForced_5G,
                            dbvar_V_ErrorForced_20G,
                            dbvar_V_ErrorForced_YTD,
                            dbvar_V_HitsByPitch_Sum,
                            dbvar_V_HitsByPitch,
                            dbvar_V_HitsByPitch_Sum_5G,
                            dbvar_V_HitsByPitch_5G,
                            dbvar_V_HitsByPitch_Sum_20G,
                            dbvar_V_HitsByPitch_20G,
                            dbvar_V_HitsByPitch_YTD,
                            dbvar_V_HitsByPitch_Allowed,
                            dbvar_V_HitsByPitch_Allowed_5G,
                            dbvar_V_HitsByPitch_Allowed_20G,
                            dbvar_V_HitsByPitch_Allowed_YTD,
                            dbvar_V_DoublePlays_Gained_Sum,
                            dbvar_V_DoublePlays_Gained,
                            dbvar_V_DoublePlays_Gained_Sum_5G,
                            dbvar_V_DoublePlays_Gained_5G,
                            dbvar_V_DoublePlays_Gained_Sum_20G,
                            dbvar_V_DoublePlays_Gained_20G,
                            dbvar_V_DoublePlays_Gained_YTD,
                            dbvar_V_DoublePlays_Gained_YTD_HV,
                            dbvar_V_DoublePlays_Allowed,
                            dbvar_V_DoublePlays_Allowed_5G,
                            dbvar_V_DoublePlays_Allowed_20G,
                            dbvar_V_DoublePlays_Allowed_YTD,
                            dbvar_V_DoublePlays_Allowed_YTD_HV,
                            dbvar_V_ReliefPitchers,
                            dbvar_V_TotalBases_Sum,
                            dbvar_V_TotalBases,
                            dbvar_V_TotalBases_5G,
                            dbvar_V_TotalBases_20G,
                            dbvar_V_TotalBases_YTD,         
                            dbvar_V_MenOnBaseTBRatio,
                            dbvar_V_MenOnBaseTBRatio_5G,
                            dbvar_V_WalkStrikeoutRatio_Sum,
                            dbvar_V_WalkStrikeoutRatio,
                            dbvar_V_PowerHits_Sum,
                            dbvar_V_PowerHits,
                            dbvar_V_PowerHits_5G,
                            dbvar_V_Innings_OutPitched_Sum,
                            dbvar_V_Innings_OutPitched,
                            dbvar_V_Innings_OutPitched_Sum_5G,
                            dbvar_V_Innings_OutPitched_5G,
                            dbvar_V_Innings_OutPitched_YTD,
                            dbvar_V_SP_HitsAllowed_Sum,
                            dbvar_V_SP_HitsAllowed,
                            dbvar_V_SP_HitsAllowed_5G,
                            dbvar_V_SP_HitsAllowed_YTD,
                            dbvar_V_EarnedRuns_Sum,
                            dbvar_V_EarnedRunAvg_Sum,
                            dbvar_V_EarnedRuns,
                            dbvar_V_EarnedRunAvg,
                            dbvar_V_EarnedRuns_Sum_5G,
                            dbvar_V_EarnedRunAvg_Sum_5G,
                            dbvar_V_EarnedRuns_5G,
                            dbvar_V_EarnedRunAvg_5G,
                            dbvar_V_EarnedRuns_YTD,
                            dbvar_V_EarnedRunAvg_YTD,
                            dbvar_V_HitsAllowedPer9Innings_Sum,
                            dbvar_V_HitsAllowedPer9Innings,
                            dbvar_V_HitsAllowedPer9Innings_5G,
                            dbvar_V_WalksHitsAllowedPerInning,
                            dbvar_V_WalksHitsAllowedPerInning_5G,
                            dbvar_V_WalksHitsAllowedPerInning_YTD,
                            dbvar_G_V_StartingPitcher_Id,
                            dbvar_V_StartingPitcher_DaysRest,
                            dbvar_V_StartingPitcher_Score_All,
                            dbvar_V_StartingPitcher_Strikeouts_All,
                            dbvar_V_StartingPitcher_StrikeoutAccuracy_All,
                            dbvar_V_StartingPitcher_BaseOnBalls_All,
                            dbvar_V_StartingPitcher_Hits_All,
                            dbvar_V_StartingPitcher_NP_All,
                            dbvar_V_StartingPitcher_InningsPitched_All,
                            dbvar_V_StartingPitcher_Strikes_All,
                            dbvar_V_StartingPitcher_StrikeAccuracy_All,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All,
                            dbvar_V_StartingPitcher_Score_YTD,
                            dbvar_V_StartingPitcher_Strikeouts_YTD,
                            dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD,
                            dbvar_V_StartingPitcher_BaseOnBalls_YTD,
                            dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                            dbvar_V_StartingPitcher_Hits_YTD,
                            dbvar_V_StartingPitcher_NP_YTD,
                            dbvar_V_StartingPitcher_InningsPitched_YTD,
                            dbvar_V_StartingPitcher_Strikes_YTD,
                            dbvar_V_StartingPitcher_StrikeAccuracy_YTD,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                            dbvar_V_StartingPitcher_ScoreImpact_YTD,
                            dbvar_V_StartingPitcher_StrikeoutsImpact_YTD,
                            dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD,
                            dbvar_V_StartingPitcher_HitsImpact_YTD,
                            dbvar_V_StartingPitcher_NPImpact_YTD,
                            dbvar_V_StartingPitcher_InningsPitchedImpact_YTD,
                            dbvar_V_StartingPitcher_StrikeImpact_YTD,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                            dbvar_V_StartingPitcher_Score_5G,
                            dbvar_V_StartingPitcher_Strikeouts_5G,
                            dbvar_V_StartingPitcher_StrikeoutAccuracy_5G,
                            dbvar_V_StartingPitcher_BaseOnBalls_5G,
                            dbvar_V_StartingPitcher_Hits_5G,
                            dbvar_V_StartingPitcher_NP_5G,
                            dbvar_V_StartingPitcher_InningsPitched_5G,
                            dbvar_V_StartingPitcher_Strikes_5G,
                            dbvar_V_StartingPitcher_StrikeAccuracy_5G,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G,
                            dbvar_V_StartingPitcher_ScoreImpact_5G,
                            dbvar_V_StartingPitcher_StrikeoutsImpact_5G,
                            dbvar_V_StartingPitcher_BaseOnBallsImpact_5G,
                            dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                            dbvar_V_StartingPitcher_HitsImpact_5G,
                            dbvar_V_StartingPitcher_NPImpact_5G,
                            dbvar_V_StartingPitcher_InningsPitchedImpact_5G,
                            dbvar_V_StartingPitcher_StrikeImpact_5G,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                            dbvar_V_StartingPitcher_Score_Ratio,
                            dbvar_V_StartingPitcher_Strikeouts_Ratio,
                            dbvar_V_StartingPitcher_BaseOnBalls_Ratio,
                            dbvar_V_StartingPitcher_Hits_Ratio,
                            dbvar_V_StartingPitcher_NP_Ratio,
                            dbvar_V_StartingPitcher_InningsPitched_Ratio,
                            dbvar_V_StartingPitcher_Strikes_Ratio,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                            dbvar_V_StartingPitcher_Score_Ratio_5G,
                            dbvar_V_StartingPitcher_Strikeouts_Ratio_5G,
                            dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G,
                            dbvar_V_StartingPitcher_Hits_Ratio_5G,
                            dbvar_V_StartingPitcher_NP_Ratio_5G,
                            dbvar_V_StartingPitcher_InningsPitched_Ratio_5G,
                            dbvar_V_StartingPitcher_Strikes_Ratio_5G,
                            dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                            dbvar_V_BallpenOuts,
                            dbvar_V_BallpenOuts_5G,
                            dbvar_V_BallpenOuts_YTD,
                            dbvar_V_BallpenERA_Approx,
                            dbvar_V_BallpenERA_Approx_5G,
                            dbvar_V_BallpenERA_Approx_YTD,
                            dbvar_G_VHRatio_DaysRest,
                            dbvar_G_VHRatio_SP_DaysRest,
                            dbvar_G_VHRatio_ParkImpactFactor,
                            dbvar_G_VHRatio_ContiguousGamesV,
                            dbvar_G_VHRatio_ContiguousGamesH,
                            dbvar_G_VHRatio_TotalDistanceTravelled_3G,
                            dbvar_G_VHRatio_ClosingProbabilityLine_HV,
                            dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV,
                            dbvar_G_VHRatio_Runs_Gained,
                            dbvar_G_VHRatio_Runs_Allowed,
                            dbvar_G_VHRatio_Run_Strength,
                            dbvar_G_VHRatio_Run_Efficiency,
                            dbvar_G_VHRatio_Runs_Gained_Sum,
                            dbvar_G_VHRatio_Runs_Allowed_Sum,
                            dbvar_G_VHRatio_Run_Strength_Sum,
                            dbvar_G_VHRatio_Run_Efficiency_Sum,
                            dbvar_G_VHRatio_Run_Pythag,
                            dbvar_G_VHRatio_Runs_Gained_5G,
                            dbvar_G_VHRatio_Runs_Allowed_5G,
                            dbvar_G_VHRatio_Run_Strength_5G,
                            dbvar_G_VHRatio_Run_Efficiency_5G,
                            dbvar_G_VHRatio_Run_Pythag_5G,
                            dbvar_G_VHRatio_Runs_Gained_Sum_5G,
                            dbvar_G_VHRatio_Runs_Allowed_Sum_5G,
                            dbvar_G_VHRatio_Run_Strength_Sum_5G,
                            dbvar_G_VHRatio_Run_Efficiency_Sum_5G,
                            dbvar_G_VHRatio_Runs_Gained_20G,
                            dbvar_G_VHRatio_Runs_Allowed_20G,
                            dbvar_G_VHRatio_Run_Strength_20G,
                            dbvar_G_VHRatio_Run_Efficiency_20G,
                            dbvar_G_VHRatio_Run_Pythag_20G,
                            dbvar_G_VHRatio_Runs_Gained_Sum_20G,
                            dbvar_G_VHRatio_Runs_Allowed_Sum_20G,
                            dbvar_G_VHRatio_Run_Strength_Sum_20G,
                            dbvar_G_VHRatio_Run_Efficiency_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained,
                            dbvar_G_VHRatio_Runs_5InningsAllowed,
                            dbvar_G_VHRatio_Run_5InningsStrength,
                            dbvar_G_VHRatio_Run_5InningsEfficiency,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum,
                            dbvar_G_VHRatio_Runs_5InningsGained_5G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_5G,
                            dbvar_G_VHRatio_Run_5InningsStrength_5G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_5G,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G,
                            dbvar_G_VHRatio_Runs_5InningsGained_20G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_20G,
                            dbvar_G_VHRatio_Run_5InningsStrength_20G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained_HV,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_HV,
                            dbvar_G_VHRatio_Runs_5InningsGained_YTD,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_YTD,
                            dbvar_G_VHRatio_Pythag_Luck_Factor,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_5G,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_20G,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_YTD,
                            dbvar_G_VHRatio_Run_Differential_Per_Game,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_5G,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_20G,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_YTD,
                            dbvar_G_VHRatio_Weighted_Offense_Index,
                            dbvar_G_VHRatio_Weighted_Offense_Index_5G,
                            dbvar_G_VHRatio_Weighted_Offense_Index_20G,
                            dbvar_G_VHRatio_Weighted_Offense_Index_YTD,
                            dbvar_G_VHRatio_At_Bat,
                            dbvar_G_VHRatio_At_Bat_5G,
                            dbvar_G_VHRatio_At_Bat_20G,
                            dbvar_G_VHRatio_At_Bat_YTD,
                            dbvar_G_VHRatio_At_Bat_HV,
                            dbvar_G_VHRatio_At_Bat_YTD_HV,
                            dbvar_G_VHRatio_OBP,
                            dbvar_G_VHRatio_OBP_5G,
                            dbvar_G_VHRatio_OBP_20G,
                            dbvar_G_VHRatio_OBP_YTD,
                            dbvar_G_VHRatio_SLG,
                            dbvar_G_VHRatio_SLG_5G,
                            dbvar_G_VHRatio_SLG_20G,
                            dbvar_G_VHRatio_SLG_YTD,
                            dbvar_G_VHRatio_wOBA,
                            dbvar_G_VHRatio_wOBA_5G,
                            dbvar_G_VHRatio_wOBA_20G,
                            dbvar_G_VHRatio_wOBA_YTD,
                            dbvar_G_VHRatio_OPS,
                            dbvar_G_VHRatio_OPS_5G,
                            dbvar_G_VHRatio_OPS_20G,
                            dbvar_G_VHRatio_OPS_YTD,
                            dbvar_G_VHRatio_Wins,
                            dbvar_G_VHRatio_Losses,
                            dbvar_G_VHRatio_WinLoss_Strength,
                            dbvar_G_VHRatio_Wins_5G,
                            dbvar_G_VHRatio_Losses_5G,
                            dbvar_G_VHRatio_WinLoss_Strength_5G,
                            dbvar_G_VHRatio_Wins_20G,
                            dbvar_G_VHRatio_Losses_20G,
                            dbvar_G_VHRatio_WinLoss_Strength_20G,
                            dbvar_G_VHRatio_OutsPitched,
                            dbvar_G_VHRatio_OutsPitched_5G,
                            dbvar_G_VHRatio_OutsPitched_20G,
                            dbvar_G_VHRatio_OutsPitched_YTD,
                            dbvar_G_VHRatio_OutsPitched_YTD_HV,
                            dbvar_G_VHRatio_StrikeAccuracy,
                            dbvar_G_VHRatio_StrikeAccuracy_5G,
                            dbvar_G_VHRatio_StrikeoutsGained,
                            dbvar_G_VHRatio_StrikeoutsAllowed,
                            dbvar_G_VHRatio_StrikeoutsAccuracy,
                            dbvar_G_VHRatio_StrikeoutsGained_5G,
                            dbvar_G_VHRatio_StrikeoutsAllowed_5G,
                            dbvar_G_VHRatio_StrikeoutsAccuracy_5G,
                            dbvar_G_VHRatio_StrikeoutsGained_20G,
                            dbvar_G_VHRatio_EarnedRuns,
                            dbvar_G_VHRatio_EarnedRunAvg,
                            dbvar_G_VHRatio_EarnedRuns_5G,
                            dbvar_G_VHRatio_EarnedRuns_Avg_5G,
                            dbvar_G_VHRatio_EarnedRuns_Sum_5G,
                            dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G,
                            dbvar_G_VHRatio_EarnedRuns_YTD,
                            dbvar_G_VHRatio_EarnedRunAvg_YTD,
                            dbvar_G_VHRatio_RunsHitsRatio,
                            dbvar_G_VHRatio_RunsHitsRatio_Sum,
                            dbvar_G_VHRatio_RunsHitsRatio_5G,
                            dbvar_G_VHRatio_RunsHitsRatio_Sum_5G,
                            dbvar_G_VHRatio_RunsHitsRatio_Allowed,
                            dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G,
                            dbvar_G_VHRatio_FIP,
                            dbvar_G_VHRatio_FIP_5G,
                            dbvar_G_VHRatio_FIP_YTD,
                            dbvar_G_VHRatio_FIP_YTD_HV,
                            dbvar_G_VHRatio_K_Minus_BB_Pct,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_5G,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_20G,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_YTD,
                            dbvar_G_VHRatio_HR_Per_9_Allowed,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_5G,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_20G,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_YTD,
                            dbvar_G_VHRatio_K_Per_9,
                            dbvar_G_VHRatio_K_Per_9_5G,
                            dbvar_G_VHRatio_K_Per_9_20G,
                            dbvar_G_VHRatio_K_Per_9_YTD,
                            dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV,
                            dbvar_G_VHRatio_WalksAllowed,
                            dbvar_G_VHRatio_WalksAllowed_5G,
                            dbvar_G_VHRatio_WalksAllowed_20G,
                            dbvar_G_VHRatio_WalksAllowed_Sum,
                            dbvar_G_VHRatio_WalksAllowed_Sum_5G,
                            dbvar_G_VHRatio_WalksAllowed_Sum_20G,
                            dbvar_G_VHRatio_PowerHits,
                            dbvar_G_VHRatio_PowerHits_5G,
                            dbvar_G_VHRatio_HitsAllowed_5G,
                            dbvar_G_VHRatio_HitsAllowed_20G,
                            dbvar_G_VHRatio_HitsAllowedPer9Innings,
                            dbvar_G_VHRatio_HitsAllowedPer9Innings_5G,
                            dbvar_G_VHRatio_HitsByPitch_5G,
                            dbvar_G_VHRatio_HitsByPitch_20G,
                            dbvar_G_VHRatio_2BRuns,
                            dbvar_G_VHRatio_2BRuns_5G,
                            dbvar_G_VHRatio_2BRuns_20G,
                            dbvar_G_VHRatio_2BRuns_YTD,
                            dbvar_G_VHRatio_2BRuns_Strength,
                            dbvar_G_VHRatio_2BRuns_Strength_5G,
                            dbvar_G_VHRatio_2BRuns_Strength_20G,
                            dbvar_G_VHRatio_2BRuns_Strength_YTD,
                            dbvar_G_VHRatio_3BRuns,
                            dbvar_G_VHRatio_3BRuns_5G,
                            dbvar_G_VHRatio_3BRuns_20G,
                            dbvar_G_VHRatio_3BRuns_YTD,
                            dbvar_G_VHRatio_3BRuns_Strength,
                            dbvar_G_VHRatio_3BRuns_Strength_5G,
                            dbvar_G_VHRatio_3BRuns_Strength_20G,
                            dbvar_G_VHRatio_3BRuns_Strength_YTD,
                            dbvar_G_VHRatio_HomeRuns_5G,
                            dbvar_G_VHRatio_HomeRuns_20G,
                            dbvar_G_VHRatio_DoublePlays_Gained_5G,
                            dbvar_G_VHRatio_DoublePlays_Gained_20G,
                            dbvar_G_VHRatio_DoublePlays_Gained_YTD,
                            dbvar_G_VHRatio_DoublePlays_Allowed_5G,
                            dbvar_G_VHRatio_DoublePlays_Allowed_20G,
                            dbvar_G_VHRatio_DoublePlays_Allowed_YTD,
                            dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV,
                            dbvar_G_VHRatio_TotalBases,
                            dbvar_G_VHRatio_TotalBases_5G,
                            dbvar_G_VHRatio_TotalBases_20G,     
                            dbvar_G_VHRatio_TotalBases_YTD,                    
                            dbvar_G_VHRatio_MenOnBaseTBRatio,
                            dbvar_G_VHRatio_MenOnBaseTBRatio_5G,
                            dbvar_G_VHRatio_MenOnBase,
                            dbvar_G_VHRatio_MenOnBase_Strength,
                            dbvar_G_VHRatio_MenOnBase_Efficiency,
                            dbvar_G_VHRatio_MenOnBase_5G,
                            dbvar_G_VHRatio_MenOnBase_Strength_5G,
                            dbvar_G_VHRatio_MenOnBase_Efficiency_5G,
                            dbvar_G_VHRatio_MenOnBase_20G,
                            dbvar_G_VHRatio_MenOnBase_Strength_20G,
                            dbvar_G_VHRatio_MenOnBase_Efficiency_20G,
                            dbvar_G_VHRatio_MenOnBase_Strength_YTD,
                            dbvar_G_VHRatio_MenOnBase_Allowed,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency,
                            dbvar_G_VHRatio_MenOnBase_Allowed_5G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_20G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_YTD,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                            dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                            dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Score_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                            dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                            dbvar_G_VHRatio_StartingPitcher_NP_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                            dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                            dbvar_G_VHRatio_BallpenOuts,
                            dbvar_G_VHRatio_BallpenOuts_5G,
                            dbvar_G_VHRatio_BallpenOuts_YTD,
                            dbvar_G_VHRatio_BallpenERA_Approx,
                            dbvar_G_VHRatio_BallpenERA_Approx_5G,
                            dbvar_G_VHRatio_BallpenERA_Approx_YTD,
                            dbvar_G_Ivan_BP_DefenseProbability,
                            dbvar_G_Ivan_BP_OffenseProbability,
                            dbvar_G_Ivan_BP_NullProbability,
                            dbvar_G_Ivan_BP_NoLineProbability,
                            dbvar_G_H_AdjBookieProbabilityLine,
                            dbvar_G_PH_Win,
                            dbvar_G_PV_Win,
                            dbvar_G_H_Runs,
                            dbvar_G_H_Run_Prediction,
                            dbvar_G_V_Runs,
                            dbvar_G_V_Run_Prediction,
                            dbvar_G_Actual_Runs_Diff,
                            dbvar_G_ABSActual_Runs_Diff,
                            dbvar_G_ABSActual_Runs_DiffCategory,
                            dbvar_G_Total,
                            dbvar_G_BookieAdjustedTotal,
                            dbvar_G_Total_IsOver,
                            dbvar_G_Bookie_Prob_Bet,
                            dbvar_G_Bookie_FaveWin,
                            dbvar_G_Bookie_DogWin
                        ]																

MLBdb_target_vars = [   
                        dbvar_G_H_AdjBookieProbabilityLine, 	
                        dbvar_G_PH_Win, 	
                        dbvar_G_PV_Win, 	
                        dbvar_G_H_Runs, 	
                        dbvar_G_H_Run_Prediction, 	
                        dbvar_G_V_Runs, 	
                        dbvar_G_V_Run_Prediction, 	
                        dbvar_G_Actual_Runs_Diff, 	
                        dbvar_G_ABSActual_Runs_Diff, 	
                        dbvar_G_ABSActual_Runs_DiffCategory, 	
                        dbvar_G_Total, 	
                        dbvar_G_BookieAdjustedTotal, 	
                        dbvar_G_Total_IsOver, 	
                        dbvar_G_Bookie_Prob_Bet, 	
                        dbvar_G_Bookie_FaveWin, 	
                        dbvar_G_Bookie_DogWin
                    ]

MLBdb_pitcher_vars = [ 
                        dbvar_H_ReliefPitchers,
                        dbvar_H_Innings_OutPitched_Sum,
                        dbvar_H_Innings_OutPitched,
                        dbvar_H_Innings_OutPitched_Sum_5G,
                        dbvar_H_Innings_OutPitched_5G,
                        dbvar_H_Innings_OutPitched_YTD,
                        dbvar_H_SP_HitsAllowed_Sum,
                        dbvar_H_SP_HitsAllowed,
                        dbvar_H_SP_HitsAllowed_5G,
                        dbvar_H_SP_HitsAllowed_YTD,
                        dbvar_G_H_StartingPitcher_Id,
                        dbvar_H_StartingPitcher_DaysRest,
                        dbvar_H_StartingPitcher_Score_All,
                        dbvar_H_StartingPitcher_Strikeouts_All,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_All,
                        dbvar_H_StartingPitcher_BaseOnBalls_All,
                        dbvar_H_StartingPitcher_Hits_All,
                        dbvar_H_StartingPitcher_NP_All,
                        dbvar_H_StartingPitcher_InningsPitched_All,
                        dbvar_H_StartingPitcher_Strikes_All,
                        dbvar_H_StartingPitcher_StrikeAccuracy_All,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All,
                        dbvar_H_StartingPitcher_Score_YTD,
                        dbvar_H_StartingPitcher_Strikeouts_YTD,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_H_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_H_StartingPitcher_Hits_YTD,
                        dbvar_H_StartingPitcher_NP_YTD,
                        dbvar_H_StartingPitcher_InningsPitched_YTD,
                        dbvar_H_StartingPitcher_Strikes_YTD,
                        dbvar_H_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_H_StartingPitcher_ScoreImpact_YTD,
                        dbvar_H_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                        dbvar_H_StartingPitcher_HitsImpact_YTD,
                        dbvar_H_StartingPitcher_NPImpact_YTD,
                        dbvar_H_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_H_StartingPitcher_StrikeImpact_YTD,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_H_StartingPitcher_Score_5G,
                        dbvar_H_StartingPitcher_Strikeouts_5G,
                        dbvar_H_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_H_StartingPitcher_BaseOnBalls_5G,
                        dbvar_H_StartingPitcher_Hits_5G,
                        dbvar_H_StartingPitcher_NP_5G,
                        dbvar_H_StartingPitcher_InningsPitched_5G,
                        dbvar_H_StartingPitcher_Strikes_5G,
                        dbvar_H_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_H_StartingPitcher_ScoreImpact_5G,
                        dbvar_H_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_H_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_H_StartingPitcher_HitsImpact_5G,
                        dbvar_H_StartingPitcher_NPImpact_5G,
                        dbvar_H_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_H_StartingPitcher_StrikeImpact_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_H_StartingPitcher_Score_Ratio,
                        dbvar_H_StartingPitcher_Strikeouts_Ratio,
                        dbvar_H_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_H_StartingPitcher_Hits_Ratio,
                        dbvar_H_StartingPitcher_NP_Ratio,
                        dbvar_H_StartingPitcher_InningsPitched_Ratio,
                        dbvar_H_StartingPitcher_Strikes_Ratio,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_H_StartingPitcher_Score_Ratio_5G,
                        dbvar_H_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_H_StartingPitcher_Hits_Ratio_5G,
                        dbvar_H_StartingPitcher_NP_Ratio_5G,
                        dbvar_H_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_H_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_V_ReliefPitchers,
                        dbvar_V_Innings_OutPitched_Sum,
                        dbvar_V_Innings_OutPitched,
                        dbvar_V_Innings_OutPitched_Sum_5G,
                        dbvar_V_Innings_OutPitched_5G,
                        dbvar_V_Innings_OutPitched_YTD,
                        dbvar_V_SP_HitsAllowed_Sum,
                        dbvar_V_SP_HitsAllowed,
                        dbvar_V_SP_HitsAllowed_5G,
                        dbvar_V_SP_HitsAllowed_YTD,
                        dbvar_G_V_StartingPitcher_Id,
                        dbvar_V_StartingPitcher_DaysRest,
                        dbvar_V_StartingPitcher_Score_All,
                        dbvar_V_StartingPitcher_Strikeouts_All,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_All,
                        dbvar_V_StartingPitcher_BaseOnBalls_All,
                        dbvar_V_StartingPitcher_Hits_All,
                        dbvar_V_StartingPitcher_NP_All,
                        dbvar_V_StartingPitcher_InningsPitched_All,
                        dbvar_V_StartingPitcher_Strikes_All,
                        dbvar_V_StartingPitcher_StrikeAccuracy_All,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All,
                        dbvar_V_StartingPitcher_Score_YTD,
                        dbvar_V_StartingPitcher_Strikeouts_YTD,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_V_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                        dbvar_V_StartingPitcher_Hits_YTD,
                        dbvar_V_StartingPitcher_NP_YTD,
                        dbvar_V_StartingPitcher_InningsPitched_YTD,
                        dbvar_V_StartingPitcher_Strikes_YTD,
                        dbvar_V_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_V_StartingPitcher_ScoreImpact_YTD,
                        dbvar_V_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_V_StartingPitcher_HitsImpact_YTD,
                        dbvar_V_StartingPitcher_NPImpact_YTD,
                        dbvar_V_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_V_StartingPitcher_StrikeImpact_YTD,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_V_StartingPitcher_Score_5G,
                        dbvar_V_StartingPitcher_Strikeouts_5G,
                        dbvar_V_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_V_StartingPitcher_BaseOnBalls_5G,
                        dbvar_V_StartingPitcher_Hits_5G,
                        dbvar_V_StartingPitcher_NP_5G,
                        dbvar_V_StartingPitcher_InningsPitched_5G,
                        dbvar_V_StartingPitcher_Strikes_5G,
                        dbvar_V_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_V_StartingPitcher_ScoreImpact_5G,
                        dbvar_V_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_V_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_V_StartingPitcher_HitsImpact_5G,
                        dbvar_V_StartingPitcher_NPImpact_5G,
                        dbvar_V_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_V_StartingPitcher_StrikeImpact_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_V_StartingPitcher_Score_Ratio,
                        dbvar_V_StartingPitcher_Strikeouts_Ratio,
                        dbvar_V_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_V_StartingPitcher_Hits_Ratio,
                        dbvar_V_StartingPitcher_NP_Ratio,
                        dbvar_V_StartingPitcher_InningsPitched_Ratio,
                        dbvar_V_StartingPitcher_Strikes_Ratio,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_V_StartingPitcher_Score_Ratio_5G,
                        dbvar_V_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_V_StartingPitcher_Hits_Ratio_5G,
                        dbvar_V_StartingPitcher_NP_Ratio_5G,
                        dbvar_V_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_V_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Score_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G
                    ]

MLBdb_pitcherprimitive_vars = [
                                dbvar_H_StartingPitcher_Score_All, 	
                                dbvar_H_StartingPitcher_Strikeouts_All, 	
                                dbvar_H_StartingPitcher_BaseOnBalls_All, 	
                                dbvar_H_StartingPitcher_Hits_All, 	
                                dbvar_H_StartingPitcher_NP_All, 	
                                dbvar_H_StartingPitcher_InningsPitched_All, 	
                                dbvar_H_StartingPitcher_Strikes_All, 	
                                dbvar_H_StartingPitcher_Score_YTD, 	
                                dbvar_H_StartingPitcher_Strikeouts_YTD, 	
                                dbvar_H_StartingPitcher_BaseOnBalls_YTD, 	
                                dbvar_H_StartingPitcher_Hits_YTD, 	
                                dbvar_H_StartingPitcher_NP_YTD, 	
                                dbvar_H_StartingPitcher_InningsPitched_YTD, 	
                                dbvar_H_StartingPitcher_Strikes_YTD, 	
                                dbvar_H_StartingPitcher_Score_5G, 	
                                dbvar_H_StartingPitcher_Strikeouts_5G, 	
                                dbvar_H_StartingPitcher_BaseOnBalls_5G, 	
                                dbvar_H_StartingPitcher_Hits_5G, 	
                                dbvar_H_StartingPitcher_NP_5G, 	
                                dbvar_H_StartingPitcher_InningsPitched_5G, 	
                                dbvar_H_StartingPitcher_Strikes_5G,
                                dbvar_V_StartingPitcher_Score_All, 	
                                dbvar_V_StartingPitcher_Strikeouts_All, 	
                                dbvar_V_StartingPitcher_BaseOnBalls_All, 	
                                dbvar_V_StartingPitcher_Hits_All, 	
                                dbvar_V_StartingPitcher_NP_All, 	
                                dbvar_V_StartingPitcher_InningsPitched_All, 	
                                dbvar_V_StartingPitcher_Strikes_All, 	
                                dbvar_V_StartingPitcher_Score_YTD, 	
                                dbvar_V_StartingPitcher_Strikeouts_YTD, 	
                                dbvar_V_StartingPitcher_BaseOnBalls_YTD, 	
                                dbvar_V_StartingPitcher_Hits_YTD, 	
                                dbvar_V_StartingPitcher_NP_YTD, 	
                                dbvar_V_StartingPitcher_InningsPitched_YTD, 	
                                dbvar_V_StartingPitcher_Strikes_YTD, 	
                                dbvar_V_StartingPitcher_Score_5G, 	
                                dbvar_V_StartingPitcher_Strikeouts_5G, 	
                                dbvar_V_StartingPitcher_BaseOnBalls_5G, 	
                                dbvar_V_StartingPitcher_Hits_5G, 	
                                dbvar_V_StartingPitcher_NP_5G, 	
                                dbvar_V_StartingPitcher_InningsPitched_5G, 	
                                dbvar_V_StartingPitcher_Strikes_5G
                            ]

MLBdb_H_pitcherprimitive_vars = [
                                    dbvar_H_StartingPitcher_Score_All, 	
                                    dbvar_H_StartingPitcher_Strikeouts_All, 	
                                    dbvar_H_StartingPitcher_BaseOnBalls_All, 	
                                    dbvar_H_StartingPitcher_Hits_All, 	
                                    dbvar_H_StartingPitcher_NP_All, 	
                                    dbvar_H_StartingPitcher_InningsPitched_All, 	
                                    dbvar_H_StartingPitcher_Strikes_All, 	
                                    dbvar_H_StartingPitcher_Score_YTD, 	
                                    dbvar_H_StartingPitcher_Strikeouts_YTD, 	
                                    dbvar_H_StartingPitcher_BaseOnBalls_YTD, 	
                                    dbvar_H_StartingPitcher_Hits_YTD, 	
                                    dbvar_H_StartingPitcher_NP_YTD, 	
                                    dbvar_H_StartingPitcher_InningsPitched_YTD, 	
                                    dbvar_H_StartingPitcher_Strikes_YTD, 	
                                    dbvar_H_StartingPitcher_Score_5G, 	
                                    dbvar_H_StartingPitcher_Strikeouts_5G, 	
                                    dbvar_H_StartingPitcher_BaseOnBalls_5G, 	
                                    dbvar_H_StartingPitcher_Hits_5G, 	
                                    dbvar_H_StartingPitcher_NP_5G, 	
                                    dbvar_H_StartingPitcher_InningsPitched_5G, 	
                                    dbvar_H_StartingPitcher_Strikes_5G
                                ]

MLBdb_V_pitcherprimitive_vars = [
                                    dbvar_V_StartingPitcher_Score_All, 	
                                    dbvar_V_StartingPitcher_Strikeouts_All, 	
                                    dbvar_V_StartingPitcher_BaseOnBalls_All, 	
                                    dbvar_V_StartingPitcher_Hits_All, 	
                                    dbvar_V_StartingPitcher_NP_All, 	
                                    dbvar_V_StartingPitcher_InningsPitched_All, 	
                                    dbvar_V_StartingPitcher_Strikes_All, 	
                                    dbvar_V_StartingPitcher_Score_YTD, 	
                                    dbvar_V_StartingPitcher_Strikeouts_YTD, 	
                                    dbvar_V_StartingPitcher_BaseOnBalls_YTD, 	
                                    dbvar_V_StartingPitcher_Hits_YTD, 	
                                    dbvar_V_StartingPitcher_NP_YTD, 	
                                    dbvar_V_StartingPitcher_InningsPitched_YTD, 	
                                    dbvar_V_StartingPitcher_Strikes_YTD, 	
                                    dbvar_V_StartingPitcher_Score_5G, 	
                                    dbvar_V_StartingPitcher_Strikeouts_5G, 	
                                    dbvar_V_StartingPitcher_BaseOnBalls_5G, 	
                                    dbvar_V_StartingPitcher_Hits_5G, 	
                                    dbvar_V_StartingPitcher_NP_5G, 	
                                    dbvar_V_StartingPitcher_InningsPitched_5G, 	
                                    dbvar_V_StartingPitcher_Strikes_5G
                            ]

MLBdb_VHRatio_vars =    [ 
                            dbvar_G_VHRatio_DaysRest,
                            dbvar_G_VHRatio_SP_DaysRest,
                            dbvar_G_VHRatio_ParkImpactFactor,
                            dbvar_G_VHRatio_ContiguousGamesV,
                            dbvar_G_VHRatio_ContiguousGamesH,
                            dbvar_G_VHRatio_TotalDistanceTravelled_3G,
                            dbvar_G_VHRatio_ClosingProbabilityLine_HV,
                            dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV,
                            dbvar_G_VHRatio_Runs_Gained,
                            dbvar_G_VHRatio_Runs_Allowed,
                            dbvar_G_VHRatio_Run_Strength,
                            dbvar_G_VHRatio_Run_Efficiency,
                            dbvar_G_VHRatio_Runs_Gained_Sum,
                            dbvar_G_VHRatio_Runs_Allowed_Sum,
                            dbvar_G_VHRatio_Run_Strength_Sum,
                            dbvar_G_VHRatio_Run_Efficiency_Sum,
                            dbvar_G_VHRatio_Run_Pythag,
                            dbvar_G_VHRatio_Runs_Gained_5G,
                            dbvar_G_VHRatio_Runs_Allowed_5G,
                            dbvar_G_VHRatio_Run_Strength_5G,
                            dbvar_G_VHRatio_Run_Efficiency_5G,
                            dbvar_G_VHRatio_Run_Pythag_5G,
                            dbvar_G_VHRatio_Runs_Gained_Sum_5G,
                            dbvar_G_VHRatio_Runs_Allowed_Sum_5G,
                            dbvar_G_VHRatio_Run_Strength_Sum_5G,
                            dbvar_G_VHRatio_Run_Efficiency_Sum_5G,
                            dbvar_G_VHRatio_Runs_Gained_20G,
                            dbvar_G_VHRatio_Runs_Allowed_20G,
                            dbvar_G_VHRatio_Run_Strength_20G,
                            dbvar_G_VHRatio_Run_Efficiency_20G,
                            dbvar_G_VHRatio_Run_Pythag_20G,
                            dbvar_G_VHRatio_Runs_Gained_Sum_20G,
                            dbvar_G_VHRatio_Runs_Allowed_Sum_20G,
                            dbvar_G_VHRatio_Run_Strength_Sum_20G,
                            dbvar_G_VHRatio_Run_Efficiency_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained,
                            dbvar_G_VHRatio_Runs_5InningsAllowed,
                            dbvar_G_VHRatio_Run_5InningsStrength,
                            dbvar_G_VHRatio_Run_5InningsEfficiency,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum,
                            dbvar_G_VHRatio_Runs_5InningsGained_5G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_5G,
                            dbvar_G_VHRatio_Run_5InningsStrength_5G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_5G,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G,
                            dbvar_G_VHRatio_Runs_5InningsGained_20G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_20G,
                            dbvar_G_VHRatio_Run_5InningsStrength_20G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G,
                            dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G,
                            dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G,
                            dbvar_G_VHRatio_Runs_5InningsGained_HV,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_HV,
                            dbvar_G_VHRatio_Runs_5InningsGained_YTD,
                            dbvar_G_VHRatio_Runs_5InningsAllowed_YTD,
                            dbvar_G_VHRatio_Pythag_Luck_Factor,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_5G,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_20G,
                            dbvar_G_VHRatio_Pythag_Luck_Factor_YTD,
                            dbvar_G_VHRatio_Run_Differential_Per_Game,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_5G,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_20G,
                            dbvar_G_VHRatio_Run_Differential_Per_Game_YTD,
                            dbvar_G_VHRatio_Weighted_Offense_Index,
                            dbvar_G_VHRatio_Weighted_Offense_Index_5G,
                            dbvar_G_VHRatio_Weighted_Offense_Index_20G,
                            dbvar_G_VHRatio_Weighted_Offense_Index_YTD,
                            dbvar_G_VHRatio_At_Bat,
                            dbvar_G_VHRatio_At_Bat_5G,
                            dbvar_G_VHRatio_At_Bat_20G,
                            dbvar_G_VHRatio_At_Bat_YTD,
                            dbvar_G_VHRatio_At_Bat_HV,
                            dbvar_G_VHRatio_At_Bat_YTD_HV,
                            dbvar_G_VHRatio_OBP,
                            dbvar_G_VHRatio_OBP_5G,
                            dbvar_G_VHRatio_OBP_20G,
                            dbvar_G_VHRatio_OBP_YTD,
                            dbvar_G_VHRatio_SLG,
                            dbvar_G_VHRatio_SLG_5G,
                            dbvar_G_VHRatio_SLG_20G,
                            dbvar_G_VHRatio_SLG_YTD,
                            dbvar_G_VHRatio_wOBA,
                            dbvar_G_VHRatio_wOBA_5G,
                            dbvar_G_VHRatio_wOBA_20G,
                            dbvar_G_VHRatio_wOBA_YTD,
                            dbvar_G_VHRatio_OPS,
                            dbvar_G_VHRatio_OPS_5G,
                            dbvar_G_VHRatio_OPS_20G,
                            dbvar_G_VHRatio_OPS_YTD,
                            dbvar_G_VHRatio_Wins,
                            dbvar_G_VHRatio_Losses,
                            dbvar_G_VHRatio_WinLoss_Strength,
                            dbvar_G_VHRatio_Wins_5G,
                            dbvar_G_VHRatio_Losses_5G,
                            dbvar_G_VHRatio_WinLoss_Strength_5G,
                            dbvar_G_VHRatio_Wins_20G,
                            dbvar_G_VHRatio_Losses_20G,
                            dbvar_G_VHRatio_WinLoss_Strength_20G,
                            dbvar_G_VHRatio_OutsPitched,
                            dbvar_G_VHRatio_OutsPitched_5G,
                            dbvar_G_VHRatio_OutsPitched_20G,
                            dbvar_G_VHRatio_OutsPitched_YTD,
                            dbvar_G_VHRatio_OutsPitched_YTD_HV,
                            dbvar_G_VHRatio_StrikeAccuracy,
                            dbvar_G_VHRatio_StrikeAccuracy_5G,
                            dbvar_G_VHRatio_StrikeoutsGained,
                            dbvar_G_VHRatio_StrikeoutsAllowed,
                            dbvar_G_VHRatio_StrikeoutsAccuracy,
                            dbvar_G_VHRatio_StrikeoutsGained_5G,
                            dbvar_G_VHRatio_StrikeoutsAllowed_5G,
                            dbvar_G_VHRatio_StrikeoutsAccuracy_5G,
                            dbvar_G_VHRatio_StrikeoutsGained_20G,
                            dbvar_G_VHRatio_EarnedRuns,
                            dbvar_G_VHRatio_EarnedRunAvg,
                            dbvar_G_VHRatio_EarnedRuns_5G,
                            dbvar_G_VHRatio_EarnedRuns_Avg_5G,
                            dbvar_G_VHRatio_EarnedRuns_Sum_5G,
                            dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G,
                            dbvar_G_VHRatio_EarnedRuns_YTD,
                            dbvar_G_VHRatio_EarnedRunAvg_YTD,
                            dbvar_G_VHRatio_RunsHitsRatio,
                            dbvar_G_VHRatio_RunsHitsRatio_Sum,
                            dbvar_G_VHRatio_RunsHitsRatio_5G,
                            dbvar_G_VHRatio_RunsHitsRatio_Sum_5G,
                            dbvar_G_VHRatio_RunsHitsRatio_Allowed,
                            dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G,
                            dbvar_G_VHRatio_FIP,
                            dbvar_G_VHRatio_FIP_5G,
                            dbvar_G_VHRatio_FIP_YTD,
                            dbvar_G_VHRatio_FIP_YTD_HV,
                            dbvar_G_VHRatio_K_Minus_BB_Pct,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_5G,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_20G,
                            dbvar_G_VHRatio_K_Minus_BB_Pct_YTD,
                            dbvar_G_VHRatio_HR_Per_9_Allowed,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_5G,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_20G,
                            dbvar_G_VHRatio_HR_Per_9_Allowed_YTD,
                            dbvar_G_VHRatio_K_Per_9,
                            dbvar_G_VHRatio_K_Per_9_5G,
                            dbvar_G_VHRatio_K_Per_9_20G,
                            dbvar_G_VHRatio_K_Per_9_YTD,
                            dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV,
                            dbvar_G_VHRatio_WalksAllowed,
                            dbvar_G_VHRatio_WalksAllowed_5G,
                            dbvar_G_VHRatio_WalksAllowed_20G,
                            dbvar_G_VHRatio_WalksAllowed_Sum,
                            dbvar_G_VHRatio_WalksAllowed_Sum_5G,
                            dbvar_G_VHRatio_WalksAllowed_Sum_20G,
                            dbvar_G_VHRatio_PowerHits,
                            dbvar_G_VHRatio_PowerHits_5G,
                            dbvar_G_VHRatio_HitsAllowed_5G,
                            dbvar_G_VHRatio_HitsAllowed_20G,
                            dbvar_G_VHRatio_HitsAllowedPer9Innings,
                            dbvar_G_VHRatio_HitsAllowedPer9Innings_5G,
                            dbvar_G_VHRatio_HitsByPitch_5G,
                            dbvar_G_VHRatio_HitsByPitch_20G,
                            dbvar_G_VHRatio_2BRuns,
                            dbvar_G_VHRatio_2BRuns_5G,
                            dbvar_G_VHRatio_2BRuns_20G,
                            dbvar_G_VHRatio_2BRuns_YTD,
                            dbvar_G_VHRatio_2BRuns_Strength,
                            dbvar_G_VHRatio_2BRuns_Strength_5G,
                            dbvar_G_VHRatio_2BRuns_Strength_20G,
                            dbvar_G_VHRatio_2BRuns_Strength_YTD,
                            dbvar_G_VHRatio_3BRuns,
                            dbvar_G_VHRatio_3BRuns_5G,
                            dbvar_G_VHRatio_3BRuns_20G,
                            dbvar_G_VHRatio_3BRuns_YTD,
                            dbvar_G_VHRatio_3BRuns_Strength,
                            dbvar_G_VHRatio_3BRuns_Strength_5G,
                            dbvar_G_VHRatio_3BRuns_Strength_20G,
                            dbvar_G_VHRatio_3BRuns_Strength_YTD,
                            dbvar_G_VHRatio_HomeRuns_5G,
                            dbvar_G_VHRatio_HomeRuns_20G,
                            dbvar_G_VHRatio_DoublePlays_Gained_5G,
                            dbvar_G_VHRatio_DoublePlays_Gained_20G,
                            dbvar_G_VHRatio_DoublePlays_Gained_YTD,
                            dbvar_G_VHRatio_DoublePlays_Allowed_5G,
                            dbvar_G_VHRatio_DoublePlays_Allowed_20G,
                            dbvar_G_VHRatio_DoublePlays_Allowed_YTD,
                            dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV,
                            dbvar_G_VHRatio_TotalBases,
                            dbvar_G_VHRatio_TotalBases_5G,
                            dbvar_G_VHRatio_TotalBases_20G,     
                            dbvar_G_VHRatio_TotalBases_YTD,       
                            dbvar_G_VHRatio_MenOnBaseTBRatio,
                            dbvar_G_VHRatio_MenOnBaseTBRatio_5G,
                            dbvar_G_VHRatio_MenOnBase,
                            dbvar_G_VHRatio_MenOnBase_Strength,
                            dbvar_G_VHRatio_MenOnBase_Efficiency,
                            dbvar_G_VHRatio_MenOnBase_5G,
                            dbvar_G_VHRatio_MenOnBase_Strength_5G,
                            dbvar_G_VHRatio_MenOnBase_Efficiency_5G,
                            dbvar_G_VHRatio_MenOnBase_20G,
                            dbvar_G_VHRatio_MenOnBase_Strength_20G,
                            dbvar_G_VHRatio_MenOnBase_Efficiency_20G,
                            dbvar_G_VHRatio_MenOnBase_Strength_YTD,
                            dbvar_G_VHRatio_MenOnBase_Allowed,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency,
                            dbvar_G_VHRatio_MenOnBase_Allowed_5G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_20G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G,
                            dbvar_G_VHRatio_MenOnBase_Allowed_YTD,
                            dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                            dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                            dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                            dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                            dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                            dbvar_G_VHRatio_StartingPitcher_Score_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                            dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                            dbvar_G_VHRatio_StartingPitcher_NP_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                            dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                            dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                            dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                            dbvar_G_VHRatio_BallpenOuts,
                            dbvar_G_VHRatio_BallpenOuts_5G,
                            dbvar_G_VHRatio_BallpenOuts_YTD,
                            dbvar_G_VHRatio_BallpenERA_Approx,
                            dbvar_G_VHRatio_BallpenERA_Approx_5G,
                            dbvar_G_VHRatio_BallpenERA_Approx_YTD
                        ]

MLBdb_G_vars =    [  
                        dbvar_G_Year,
                        dbvar_G_Month,
                        dbvar_G_Day,
                        dbvar_G_MonthWeek,
                        dbvar_G_Opening_TotalOver,
                        dbvar_G_Opening_TotalOverLine,
                        dbvar_G_Closing_TotalOver,
                        dbvar_G_Closing_TotalOverLine,
                        dbvar_G_Bookie_TotalOver,
                        dbvar_G_Bookie_TotalOverLine,
                        dbvar_G_NightGame,
                        dbvar_G_H_Id,
                        dbvar_G_Bookie_H_MoneyLine,
                        dbvar_G_Bookie_H_Probability,
                        dbvar_G_H_Opening_MoneyLine,
                        dbvar_G_H_OpeningProbabilityLine,
                        dbvar_G_H_Closing_MoneyLine,
                        dbvar_G_H_ClosingProbabilityLine,
                        dbvar_G_H_CLL_OPL_Prob_Diff,
                        dbvar_G_H_ParkImpactFactor,
                        dbvar_G_H_League,
                        dbvar_G_H_Division,
                        dbvar_G_H_LeagueDiv,
                        dbvar_G_H_Same_LeagueDiv,
                        dbvar_G_H_Same_Div,
                        dbvar_G_H_DaysRest,
                        dbvar_G_H_ContiguousGamesV,
                        dbvar_G_H_ContiguousGamesH,
                        dbvar_G_H_TotalDistanceTravelled_3G,
                        dbvar_G_H_Prev1_Id,
                        dbvar_G_H_Prev1_LeagueDiv,
                        dbvar_G_H_Prev1_SameLeagueDiv,
                        dbvar_G_H_Prev1_SameDiv,
                        dbvar_G_H_Prev1_DistanceTravelled,
                        dbvar_G_H_Prev1Home,
                        dbvar_G_H_Prev1Strength,
                        dbvar_G_H_Prev1StrengthRatio,
                        dbvar_G_H_Prev1Win,
                        dbvar_G_H_Prev1CLL,
                        dbvar_G_H_Prev1_Summary,
                        dbvar_G_H_Prev2_Id,
                        dbvar_G_H_Prev2_LeagueDiv,
                        dbvar_G_H_Prev2_SameLeagueDiv,
                        dbvar_G_H_Prev2_SameDiv,
                        dbvar_G_H_Prev2_DistanceTravelled,
                        dbvar_G_H_Prev2Home,
                        dbvar_G_H_Prev2Strength,
                        dbvar_G_H_Prev2StrengthRatio,
                        dbvar_G_H_Prev2Win,
                        dbvar_G_H_Prev2CLL,
                        dbvar_G_H_Prev2_Summary,
                        dbvar_G_H_Prev3_Id,
                        dbvar_G_H_Prev3_LeagueDiv,
                        dbvar_G_H_Prev3_SameLeagueDiv,
                        dbvar_G_H_Prev3_SameDiv,
                        dbvar_G_H_Prev3_DistanceTravelled,
                        dbvar_G_H_Prev3Home,
                        dbvar_G_H_Prev3Strength,
                        dbvar_G_H_Prev3StrengthRatio,
                        dbvar_G_H_Prev3Win,
                        dbvar_G_H_Prev3CLL,
                        dbvar_G_H_Prev3_Summary,
                        dbvar_G_H_Lookback_Strength,
                        dbvar_G_H_Next1_Id,
                        dbvar_G_H_Next1_LeagueDiv,
                        dbvar_G_H_Next1_SameLeagueDiv,
                        dbvar_G_H_Next1_SameDiv,
                        dbvar_G_H_Next1_DistanceTravelled,
                        dbvar_G_H_Next1Home,
                        dbvar_G_H_Next1Strength,
                        dbvar_G_H_Next1StrengthRatio,
                        dbvar_G_H_Next1_Summary,
                        dbvar_G_H_Next2_Id,
                        dbvar_G_H_Next2_LeagueDiv,
                        dbvar_G_H_Next2_SameLeagueDiv,
                        dbvar_G_H_Next2_SameDiv,
                        dbvar_G_H_Next2_DistanceTravelled,
                        dbvar_G_H_Next2Home,
                        dbvar_G_H_Next2Strength,
                        dbvar_G_H_Next2StrengthRatio,
                        dbvar_G_H_Next2_Summary,
                        dbvar_G_H_Next3_Id,
                        dbvar_G_H_Next3_LeagueDiv,
                        dbvar_G_H_Next3_SameLeagueDiv,
                        dbvar_G_H_Next3_SameDiv,
                        dbvar_G_H_Next3_DistanceTravelled,
                        dbvar_G_H_Next3Home,
                        dbvar_G_H_Next3Strength,
                        dbvar_G_H_Next3StrengthRatio,
                        dbvar_G_H_Next3_Summary,
                        dbvar_G_H_Lookahead_Strength,
                        dbvar_G_V_Id,
                        dbvar_G_V_ParkImpactFactor,
                        dbvar_G_Bookie_V_MoneyLine,
                        dbvar_G_Bookie_V_Probability,
                        dbvar_G_V_Opening_MoneyLine,
                        dbvar_G_V_OpeningProbabilityLine,
                        dbvar_G_V_Closing_MoneyLine,
                        dbvar_G_V_ClosingProbabilityLine,
                        dbvar_G_V_CLL_OPL_Prob_Diff,
                        dbvar_G_V_League,
                        dbvar_G_V_Division,
                        dbvar_G_V_LeagueDiv,
                        dbvar_G_V_Same_LeagueDiv,
                        dbvar_G_V_Same_Div,
                        dbvar_G_V_DaysRest,
                        dbvar_G_V_DistanceTravelled,
                        dbvar_G_V_ContiguousGamesV,
                        dbvar_G_V_ContiguousGamesH,
                        dbvar_G_V_TotalDistanceTravelled_3G,
                        dbvar_G_V_Prev1_Id,
                        dbvar_G_V_Prev1_LeagueDiv,
                        dbvar_G_V_Prev1_SameLeagueDiv,
                        dbvar_G_V_Prev1_SameDiv,
                        dbvar_G_V_Prev1_DistanceTravelled,
                        dbvar_G_V_Prev1Home,
                        dbvar_G_V_Prev1Strength,
                        dbvar_G_V_Prev1StrengthRatio,
                        dbvar_G_V_Prev1Win,
                        dbvar_G_V_Prev1CLL,
                        dbvar_G_V_Prev1_Summary,
                        dbvar_G_V_Prev2_Id,
                        dbvar_G_V_Prev2_LeagueDiv,
                        dbvar_G_V_Prev2_SameLeagueDiv,
                        dbvar_G_V_Prev2_SameDiv,
                        dbvar_G_V_Prev2_DistanceTravelled,
                        dbvar_G_V_Prev2Home,
                        dbvar_G_V_Prev2Strength,
                        dbvar_G_V_Prev2StrengthRatio,
                        dbvar_G_V_Prev2Win,
                        dbvar_G_V_Prev2CLL,
                        dbvar_G_V_Prev2_Summary,
                        dbvar_G_V_Prev3_Id,
                        dbvar_G_V_Prev3_LeagueDiv,
                        dbvar_G_V_Prev3_SameLeagueDiv,
                        dbvar_G_V_Prev3_SameDiv,
                        dbvar_G_V_Prev3_DistanceTravelled,
                        dbvar_G_V_Prev3Home,
                        dbvar_G_V_Prev3Strength,
                        dbvar_G_V_Prev3StrengthRatio,
                        dbvar_G_V_Prev3Win,
                        dbvar_G_V_Prev3CLL,
                        dbvar_G_V_Prev3_Summary,
                        dbvar_G_V_Lookback_Strength,
                        dbvar_G_V_Next1_Id,
                        dbvar_G_V_Next1_LeagueDiv,
                        dbvar_G_V_Next1_SameLeagueDiv,
                        dbvar_G_V_Next1_SameDiv,
                        dbvar_G_V_Next1_DistanceTravelled,
                        dbvar_G_V_Next1Home,
                        dbvar_G_V_Next1Strength,
                        dbvar_G_V_Next1StrengthRatio,
                        dbvar_G_V_Next1_Summary,
                        dbvar_G_V_Next2_Id,
                        dbvar_G_V_Next2_LeagueDiv,
                        dbvar_G_V_Next2_SameLeagueDiv,
                        dbvar_G_V_Next2_SameDiv,
                        dbvar_G_V_Next2_DistanceTravelled,
                        dbvar_G_V_Next2Home,
                        dbvar_G_V_Next2Strength,
                        dbvar_G_V_Next2StrengthRatio,
                        dbvar_G_V_Next2_Summary,
                        dbvar_G_V_Next3_Id,
                        dbvar_G_V_Next3_LeagueDiv,
                        dbvar_G_V_Next3_SameLeagueDiv,
                        dbvar_G_V_Next3_SameDiv,
                        dbvar_G_V_Next3_DistanceTravelled,
                        dbvar_G_V_Next3Home,
                        dbvar_G_V_Next3Strength,
                        dbvar_G_V_Next3StrengthRatio,
                        dbvar_G_V_Next3_Summary,
                        dbvar_G_V_Lookahead_Strength,
                        dbvar_G_VHRatio_DaysRest,
                        dbvar_G_VHRatio_SP_DaysRest,
                        dbvar_G_VHRatio_ParkImpactFactor,
                        dbvar_G_VHRatio_ContiguousGamesV,
                        dbvar_G_VHRatio_ContiguousGamesH,
                        dbvar_G_VHRatio_TotalDistanceTravelled_3G,
                        dbvar_G_VHRatio_ClosingProbabilityLine_HV,
                        dbvar_G_VHRatio_ClosingProbabilityLine_YTD_HV,
                        dbvar_G_VHRatio_Runs_Gained,
                        dbvar_G_VHRatio_Runs_Allowed,
                        dbvar_G_VHRatio_Run_Strength,
                        dbvar_G_VHRatio_Run_Efficiency,
                        dbvar_G_VHRatio_Runs_Gained_Sum,
                        dbvar_G_VHRatio_Runs_Allowed_Sum,
                        dbvar_G_VHRatio_Run_Strength_Sum,
                        dbvar_G_VHRatio_Run_Efficiency_Sum,
                        dbvar_G_VHRatio_Run_Pythag,
                        dbvar_G_VHRatio_Runs_Gained_5G,
                        dbvar_G_VHRatio_Runs_Allowed_5G,
                        dbvar_G_VHRatio_Run_Strength_5G,
                        dbvar_G_VHRatio_Run_Efficiency_5G,
                        dbvar_G_VHRatio_Run_Pythag_5G,
                        dbvar_G_VHRatio_Runs_Gained_Sum_5G,
                        dbvar_G_VHRatio_Runs_Allowed_Sum_5G,
                        dbvar_G_VHRatio_Run_Strength_Sum_5G,
                        dbvar_G_VHRatio_Run_Efficiency_Sum_5G,
                        dbvar_G_VHRatio_Runs_Gained_20G,
                        dbvar_G_VHRatio_Runs_Allowed_20G,
                        dbvar_G_VHRatio_Run_Strength_20G,
                        dbvar_G_VHRatio_Run_Efficiency_20G,
                        dbvar_G_VHRatio_Run_Pythag_20G,
                        dbvar_G_VHRatio_Runs_Gained_Sum_20G,
                        dbvar_G_VHRatio_Runs_Allowed_Sum_20G,
                        dbvar_G_VHRatio_Run_Strength_Sum_20G,
                        dbvar_G_VHRatio_Run_Efficiency_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained,
                        dbvar_G_VHRatio_Runs_5InningsAllowed,
                        dbvar_G_VHRatio_Run_5InningsStrength,
                        dbvar_G_VHRatio_Run_5InningsEfficiency,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum,
                        dbvar_G_VHRatio_Runs_5InningsGained_5G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_5G,
                        dbvar_G_VHRatio_Run_5InningsStrength_5G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_5G,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum_5G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_5G,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum_5G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_5G,
                        dbvar_G_VHRatio_Runs_5InningsGained_20G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_20G,
                        dbvar_G_VHRatio_Run_5InningsStrength_20G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_Sum_20G,
                        dbvar_G_VHRatio_Run_5InningsStrength_Sum_20G,
                        dbvar_G_VHRatio_Run_5InningsEfficiency_Sum_20G,
                        dbvar_G_VHRatio_Runs_5InningsGained_HV,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_HV,
                        dbvar_G_VHRatio_Runs_5InningsGained_YTD,
                        dbvar_G_VHRatio_Runs_5InningsAllowed_YTD,
                        dbvar_G_VHRatio_Pythag_Luck_Factor,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_5G,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_20G,
                        dbvar_G_VHRatio_Pythag_Luck_Factor_YTD,
                        dbvar_G_VHRatio_Run_Differential_Per_Game,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_5G,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_20G,
                        dbvar_G_VHRatio_Run_Differential_Per_Game_YTD,
                        dbvar_G_VHRatio_Weighted_Offense_Index,
                        dbvar_G_VHRatio_Weighted_Offense_Index_5G,
                        dbvar_G_VHRatio_Weighted_Offense_Index_20G,
                        dbvar_G_VHRatio_Weighted_Offense_Index_YTD,
                        dbvar_G_VHRatio_At_Bat,
                        dbvar_G_VHRatio_At_Bat_5G,
                        dbvar_G_VHRatio_At_Bat_20G,
                        dbvar_G_VHRatio_At_Bat_YTD,
                        dbvar_G_VHRatio_At_Bat_HV,
                        dbvar_G_VHRatio_At_Bat_YTD_HV,
                        dbvar_G_VHRatio_OBP,
                        dbvar_G_VHRatio_OBP_5G,
                        dbvar_G_VHRatio_OBP_20G,
                        dbvar_G_VHRatio_OBP_YTD,
                        dbvar_G_VHRatio_SLG,
                        dbvar_G_VHRatio_SLG_5G,
                        dbvar_G_VHRatio_SLG_20G,
                        dbvar_G_VHRatio_SLG_YTD,
                        dbvar_G_VHRatio_wOBA,
                        dbvar_G_VHRatio_wOBA_5G,
                        dbvar_G_VHRatio_wOBA_20G,
                        dbvar_G_VHRatio_wOBA_YTD,
                        dbvar_G_VHRatio_OPS,
                        dbvar_G_VHRatio_OPS_5G,
                        dbvar_G_VHRatio_OPS_20G,
                        dbvar_G_VHRatio_OPS_YTD,
                        dbvar_G_VHRatio_Wins,
                        dbvar_G_VHRatio_Losses,
                        dbvar_G_VHRatio_WinLoss_Strength,
                        dbvar_G_VHRatio_Wins_5G,
                        dbvar_G_VHRatio_Losses_5G,
                        dbvar_G_VHRatio_WinLoss_Strength_5G,
                        dbvar_G_VHRatio_Wins_20G,
                        dbvar_G_VHRatio_Losses_20G,
                        dbvar_G_VHRatio_WinLoss_Strength_20G,
                        dbvar_G_VHRatio_OutsPitched,
                        dbvar_G_VHRatio_OutsPitched_5G,
                        dbvar_G_VHRatio_OutsPitched_20G,
                        dbvar_G_VHRatio_OutsPitched_YTD,
                        dbvar_G_VHRatio_OutsPitched_YTD_HV,
                        dbvar_G_VHRatio_StrikeAccuracy,
                        dbvar_G_VHRatio_StrikeAccuracy_5G,
                        dbvar_G_VHRatio_StrikeoutsGained,
                        dbvar_G_VHRatio_StrikeoutsAllowed,
                        dbvar_G_VHRatio_StrikeoutsAccuracy,
                        dbvar_G_VHRatio_StrikeoutsGained_5G,
                        dbvar_G_VHRatio_StrikeoutsAllowed_5G,
                        dbvar_G_VHRatio_StrikeoutsAccuracy_5G,
                        dbvar_G_VHRatio_StrikeoutsGained_20G,
                        dbvar_G_VHRatio_EarnedRuns,
                        dbvar_G_VHRatio_EarnedRunAvg,
                        dbvar_G_VHRatio_EarnedRuns_5G,
                        dbvar_G_VHRatio_EarnedRuns_Avg_5G,
                        dbvar_G_VHRatio_EarnedRuns_Sum_5G,
                        dbvar_G_VHRatio_EarnedRuns_Avg_Sum_5G,
                        dbvar_G_VHRatio_EarnedRuns_YTD,
                        dbvar_G_VHRatio_EarnedRunAvg_YTD,
                        dbvar_G_VHRatio_RunsHitsRatio,
                        dbvar_G_VHRatio_RunsHitsRatio_Sum,
                        dbvar_G_VHRatio_RunsHitsRatio_5G,
                        dbvar_G_VHRatio_RunsHitsRatio_Sum_5G,
                        dbvar_G_VHRatio_RunsHitsRatio_Allowed,
                        dbvar_G_VHRatio_RunsHitsRatio_Allowed_5G,
                        dbvar_G_VHRatio_FIP,
                        dbvar_G_VHRatio_FIP_5G,
                        dbvar_G_VHRatio_FIP_YTD,
                        dbvar_G_VHRatio_FIP_YTD_HV,
                        dbvar_G_VHRatio_K_Minus_BB_Pct,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_5G,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_20G,
                        dbvar_G_VHRatio_K_Minus_BB_Pct_YTD,
                        dbvar_G_VHRatio_HR_Per_9_Allowed,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_5G,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_20G,
                        dbvar_G_VHRatio_HR_Per_9_Allowed_YTD,
                        dbvar_G_VHRatio_K_Per_9,
                        dbvar_G_VHRatio_K_Per_9_5G,
                        dbvar_G_VHRatio_K_Per_9_20G,
                        dbvar_G_VHRatio_K_Per_9_YTD,
                        dbvar_G_VHRatio_HitsByPitch_Allowed_YTD_HV,
                        dbvar_G_VHRatio_WalksAllowed,
                        dbvar_G_VHRatio_WalksAllowed_5G,
                        dbvar_G_VHRatio_WalksAllowed_20G,
                        dbvar_G_VHRatio_WalksAllowed_Sum,
                        dbvar_G_VHRatio_WalksAllowed_Sum_5G,
                        dbvar_G_VHRatio_WalksAllowed_Sum_20G,
                        dbvar_G_VHRatio_PowerHits,
                        dbvar_G_VHRatio_PowerHits_5G,
                        dbvar_G_VHRatio_HitsAllowed_5G,
                        dbvar_G_VHRatio_HitsAllowed_20G,
                        dbvar_G_VHRatio_HitsAllowedPer9Innings,
                        dbvar_G_VHRatio_HitsAllowedPer9Innings_5G,
                        dbvar_G_VHRatio_HitsByPitch_5G,
                        dbvar_G_VHRatio_HitsByPitch_20G,
                        dbvar_G_VHRatio_2BRuns,
                        dbvar_G_VHRatio_2BRuns_5G,
                        dbvar_G_VHRatio_2BRuns_20G,
                        dbvar_G_VHRatio_2BRuns_YTD,
                        dbvar_G_VHRatio_2BRuns_Strength,
                        dbvar_G_VHRatio_2BRuns_Strength_5G,
                        dbvar_G_VHRatio_2BRuns_Strength_20G,
                        dbvar_G_VHRatio_2BRuns_Strength_YTD,
                        dbvar_G_VHRatio_3BRuns,
                        dbvar_G_VHRatio_3BRuns_5G,
                        dbvar_G_VHRatio_3BRuns_20G,
                        dbvar_G_VHRatio_3BRuns_YTD,
                        dbvar_G_VHRatio_3BRuns_Strength,
                        dbvar_G_VHRatio_3BRuns_Strength_5G,
                        dbvar_G_VHRatio_3BRuns_Strength_20G,
                        dbvar_G_VHRatio_3BRuns_Strength_YTD,
                        dbvar_G_VHRatio_HomeRuns_5G,
                        dbvar_G_VHRatio_HomeRuns_20G,
                        dbvar_G_VHRatio_DoublePlays_Gained_5G,
                        dbvar_G_VHRatio_DoublePlays_Gained_20G,
                        dbvar_G_VHRatio_DoublePlays_Gained_YTD,
                        dbvar_G_VHRatio_DoublePlays_Allowed_5G,
                        dbvar_G_VHRatio_DoublePlays_Allowed_20G,
                        dbvar_G_VHRatio_DoublePlays_Allowed_YTD,
                        dbvar_G_VHRatio_DoublePlays_Allowed_YTD_HV,
                        dbvar_G_VHRatio_TotalBases,
                        dbvar_G_VHRatio_TotalBases_5G,
                        dbvar_G_VHRatio_TotalBases_20G,     
                        dbvar_G_VHRatio_TotalBases_YTD,       
                        dbvar_G_VHRatio_MenOnBaseTBRatio,
                        dbvar_G_VHRatio_MenOnBaseTBRatio_5G,
                        dbvar_G_VHRatio_MenOnBase,
                        dbvar_G_VHRatio_MenOnBase_Strength,
                        dbvar_G_VHRatio_MenOnBase_Efficiency,
                        dbvar_G_VHRatio_MenOnBase_5G,
                        dbvar_G_VHRatio_MenOnBase_Strength_5G,
                        dbvar_G_VHRatio_MenOnBase_Efficiency_5G,
                        dbvar_G_VHRatio_MenOnBase_20G,
                        dbvar_G_VHRatio_MenOnBase_Strength_20G,
                        dbvar_G_VHRatio_MenOnBase_Efficiency_20G,
                        dbvar_G_VHRatio_MenOnBase_Strength_YTD,
                        dbvar_G_VHRatio_MenOnBase_Allowed,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency,
                        dbvar_G_VHRatio_MenOnBase_Allowed_5G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_5G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_20G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_20G,
                        dbvar_G_VHRatio_MenOnBase_Allowed_YTD,
                        dbvar_G_VHRatio_MenOnBase_Allowed_Efficiency_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                        dbvar_G_VHRatio_StartingPitcher_Score_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Hits_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NP_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                        dbvar_G_VHRatio_StartingPitcher_Score_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                        dbvar_G_VHRatio_StartingPitcher_Score_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikeouts_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBalls_5G,
                        dbvar_G_VHRatio_StartingPitcher_Hits_5G,
                        dbvar_G_VHRatio_StartingPitcher_NP_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitched_5G,
                        dbvar_G_VHRatio_StartingPitcher_Strikes_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeAccuracy_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInning_5G,
                        dbvar_G_VHRatio_StartingPitcher_ScoreImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikeoutsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_BaseOnBallsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_HitsImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_NPImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_InningsPitchedImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_StrikesImpact_5G,
                        dbvar_G_VHRatio_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                        dbvar_G_VHRatio_BallpenOuts,
                        dbvar_G_VHRatio_BallpenOuts_5G,
                        dbvar_G_VHRatio_BallpenOuts_YTD,
                        dbvar_G_VHRatio_BallpenERA_Approx,
                        dbvar_G_VHRatio_BallpenERA_Approx_5G,
                        dbvar_G_VHRatio_BallpenERA_Approx_YTD,
                        dbvar_G_Ivan_BP_DefenseProbability,
                        dbvar_G_Ivan_BP_OffenseProbability,
                        dbvar_G_Ivan_BP_NullProbability,
                        dbvar_G_Ivan_BP_NoLineProbability,
                        dbvar_G_H_AdjBookieProbabilityLine,
                        dbvar_G_PH_Win,
                        dbvar_G_PV_Win,
                        dbvar_G_H_Runs,
                        dbvar_G_H_Run_Prediction,
                        dbvar_G_V_Runs,
                        dbvar_G_V_Run_Prediction,
                        dbvar_G_Actual_Runs_Diff,
                        dbvar_G_ABSActual_Runs_Diff,
                        dbvar_G_ABSActual_Runs_DiffCategory,
                        dbvar_G_Total,
                        dbvar_G_BookieAdjustedTotal,
                        dbvar_G_Total_IsOver,
                        dbvar_G_Bookie_Prob_Bet,
                        dbvar_G_Bookie_FaveWin,
                        dbvar_G_Bookie_DogWin
                ]

MLBdb_H_vars =    [  
                    dbvar_G_H_Id,
                    dbvar_G_Bookie_H_MoneyLine,
                    dbvar_G_Bookie_H_Probability,
                    dbvar_G_H_Opening_MoneyLine,
                    dbvar_G_H_OpeningProbabilityLine,
                    dbvar_G_H_Closing_MoneyLine,
                    dbvar_G_H_ClosingProbabilityLine,
                    dbvar_G_H_CLL_OPL_Prob_Diff,
                    dbvar_G_H_ParkImpactFactor,
                    dbvar_G_H_League,
                    dbvar_G_H_Division,
                    dbvar_G_H_LeagueDiv,
                    dbvar_G_H_Same_LeagueDiv,
                    dbvar_G_H_Same_Div,
                    dbvar_G_H_DaysRest,
                    dbvar_G_H_ContiguousGamesV,
                    dbvar_G_H_ContiguousGamesH,
                    dbvar_G_H_TotalDistanceTravelled_3G,
                    dbvar_G_H_Prev1_Id,
                    dbvar_G_H_Prev1_LeagueDiv,
                    dbvar_G_H_Prev1_SameLeagueDiv,
                    dbvar_G_H_Prev1_SameDiv,
                    dbvar_G_H_Prev1_DistanceTravelled,
                    dbvar_G_H_Prev1Home,
                    dbvar_G_H_Prev1Strength,
                    dbvar_G_H_Prev1StrengthRatio,
                    dbvar_G_H_Prev1Win,
                    dbvar_G_H_Prev1CLL,
                    dbvar_G_H_Prev1_Summary,
                    dbvar_G_H_Prev2_Id,
                    dbvar_G_H_Prev2_LeagueDiv,
                    dbvar_G_H_Prev2_SameLeagueDiv,
                    dbvar_G_H_Prev2_SameDiv,
                    dbvar_G_H_Prev2_DistanceTravelled,
                    dbvar_G_H_Prev2Home,
                    dbvar_G_H_Prev2Strength,
                    dbvar_G_H_Prev2StrengthRatio,
                    dbvar_G_H_Prev2Win,
                    dbvar_G_H_Prev2CLL,
                    dbvar_G_H_Prev2_Summary,
                    dbvar_G_H_Prev3_Id,
                    dbvar_G_H_Prev3_LeagueDiv,
                    dbvar_G_H_Prev3_SameLeagueDiv,
                    dbvar_G_H_Prev3_SameDiv,
                    dbvar_G_H_Prev3_DistanceTravelled,
                    dbvar_G_H_Prev3Home,
                    dbvar_G_H_Prev3Strength,
                    dbvar_G_H_Prev3StrengthRatio,
                    dbvar_G_H_Prev3Win,
                    dbvar_G_H_Prev3CLL,
                    dbvar_G_H_Prev3_Summary,
                    dbvar_G_H_Lookback_Strength,
                    dbvar_G_H_Next1_Id,
                    dbvar_G_H_Next1_LeagueDiv,
                    dbvar_G_H_Next1_SameLeagueDiv,
                    dbvar_G_H_Next1_SameDiv,
                    dbvar_G_H_Next1_DistanceTravelled,
                    dbvar_G_H_Next1Home,
                    dbvar_G_H_Next1Strength,
                    dbvar_G_H_Next1StrengthRatio,
                    dbvar_G_H_Next1_Summary,
                    dbvar_G_H_Next2_Id,
                    dbvar_G_H_Next2_LeagueDiv,
                    dbvar_G_H_Next2_SameLeagueDiv,
                    dbvar_G_H_Next2_SameDiv,
                    dbvar_G_H_Next2_DistanceTravelled,
                    dbvar_G_H_Next2Home,
                    dbvar_G_H_Next2Strength,
                    dbvar_G_H_Next2StrengthRatio,
                    dbvar_G_H_Next2_Summary,
                    dbvar_G_H_Next3_Id,
                    dbvar_G_H_Next3_LeagueDiv,
                    dbvar_G_H_Next3_SameLeagueDiv,
                    dbvar_G_H_Next3_SameDiv,
                    dbvar_G_H_Next3_DistanceTravelled,
                    dbvar_G_H_Next3Home,
                    dbvar_G_H_Next3Strength,
                    dbvar_G_H_Next3StrengthRatio,
                    dbvar_G_H_Next3_Summary,
                    dbvar_G_H_Lookahead_Strength,
                    dbvar_H_ClosingProbabilityLine_HV,
                    dbvar_H_ClosingProbabilityLine_YTD_HV,
                    dbvar_H_Runs_Gained,
                    dbvar_H_Runs_Allowed,
                    dbvar_H_Run_Strength,
                    dbvar_H_Run_Efficiency,
                    dbvar_H_Run_Pythag,
                    dbvar_H_Runs_Gained_5G,
                    dbvar_H_Runs_Allowed_5G,
                    dbvar_H_Run_Strength_5G,
                    dbvar_H_Run_Efficiency_5G,
                    dbvar_H_Run_Pythag_5G,
                    dbvar_H_Runs_Gained_20G,
                    dbvar_H_Runs_Allowed_20G,
                    dbvar_H_Run_Strength_20G,
                    dbvar_H_Run_Efficiency_20G,
                    dbvar_H_Run_Pythag_20G,
                    dbvar_H_Runs_Gained_Sum,
                    dbvar_H_Runs_Allowed_Sum,
                    dbvar_H_Run_Strength_Sum,
                    dbvar_H_Run_Efficiency_Sum,
                    dbvar_H_Run_Pythag_Sum,
                    dbvar_H_Runs_Gained_Sum_5G,
                    dbvar_H_Runs_Allowed_Sum_5G,
                    dbvar_H_Run_Strength_Sum_5G,
                    dbvar_H_Run_Efficiency_Sum_5G,
                    dbvar_H_Runs_Gained_Sum_20G,
                    dbvar_H_Runs_Allowed_Sum_20G,
                    dbvar_H_Run_Strength_Sum_20G,
                    dbvar_H_Run_Efficiency_Sum_20G,
                    dbvar_H_Runs_Gained_Sum_HV,
                    dbvar_H_Runs_Allowed_Sum_HV,
                    dbvar_H_Run_Strength_Sum_HV,
                    dbvar_H_Runs_Gained_HV,
                    dbvar_H_Runs_Allowed_HV,
                    dbvar_H_Run_Strength_HV,
                    dbvar_H_Runs_Gained_YTD,
                    dbvar_H_Runs_Allowed_YTD,
                    dbvar_H_Run_Strength_YTD,
                    dbvar_H_Run_Pythag_YTD,
                    dbvar_H_Runs_Gained_YTD_HV,
                    dbvar_H_Runs_Allowed_YTD_HV,
                    dbvar_H_Run_Strength_YTD_HV,
                    dbvar_H_Runs_5InningsGained,
                    dbvar_H_Runs_5InningsAllowed,
                    dbvar_H_Run_5InningsStrength,
                    dbvar_H_Run_5InningsEfficiency,
                    dbvar_H_Runs_5InningsGained_Sum,
                    dbvar_H_Runs_5InningsAllowed_Sum,
                    dbvar_H_Run_5InningsStrength_Sum,
                    dbvar_H_Run_5InningsEfficiency_Sum,
                    dbvar_H_Runs_5InningsGained_5G,
                    dbvar_H_Runs_5InningsAllowed_5G,
                    dbvar_H_Run_5InningsStrength_5G,
                    dbvar_H_Run_5InningsEfficiency_5G,
                    dbvar_H_Runs_5InningsGained_Sum_5G,
                    dbvar_H_Runs_5InningsAllowed_Sum_5G,
                    dbvar_H_Run_5InningsStrength_Sum_5G,
                    dbvar_H_Run_5InningsEfficiency_Sum_5G,
                    dbvar_H_Runs_5InningsGained_20G,
                    dbvar_H_Runs_5InningsAllowed_20G,
                    dbvar_H_Run_5InningsStrength_20G,
                    dbvar_H_Run_5InningsEfficiency_20G,
                    dbvar_H_Runs_5InningsGained_Sum_20G,
                    dbvar_H_Runs_5InningsAllowed_Sum_20G,
                    dbvar_H_Run_5InningsStrength_Sum_20G,
                    dbvar_H_Run_5InningsEfficiency_Sum_20G,
                    dbvar_H_Runs_5InningsGained_Sum_HV,
                    dbvar_H_Runs_5InningsAllowed_Sum_HV,
                    dbvar_H_Run_5InningsStrength_Sum_HV,
                    dbvar_H_Runs_5InningsGained_HV,
                    dbvar_H_Runs_5InningsAllowed_HV,
                    dbvar_H_Run_5InningsStrength_HV,
                    dbvar_H_Runs_5InningsGained_YTD,
                    dbvar_H_Runs_5InningsAllowed_YTD,
                    dbvar_H_Run_5InningsStrength_YTD,
                    dbvar_H_Pythag_Luck_Factor,
                    dbvar_H_Pythag_Luck_Factor_5G,
                    dbvar_H_Pythag_Luck_Factor_20G,
                    dbvar_H_Pythag_Luck_Factor_YTD,
                    dbvar_H_Run_Differential_Per_Game,
                    dbvar_H_Run_Differential_Per_Game_5G,
                    dbvar_H_Run_Differential_Per_Game_20G,
                    dbvar_H_Run_Differential_Per_Game_YTD,
                    dbvar_H_Weighted_Offense_Index,
                    dbvar_H_Weighted_Offense_Index_5G,
                    dbvar_H_Weighted_Offense_Index_20G,
                    dbvar_H_Weighted_Offense_Index_YTD,
                    dbvar_H_At_Bat,
                    dbvar_H_At_Bat_5G,
                    dbvar_H_At_Bat_20G,
                    dbvar_H_At_Bat_YTD,
                    dbvar_H_At_Bat_HV,
                    dbvar_H_At_Bat_YTD_HV,
                    dbvar_H_OBP,
                    dbvar_H_OBP_5G,
                    dbvar_H_OBP_20G,
                    dbvar_H_OBP_YTD,
                    dbvar_H_SLG,
                    dbvar_H_SLG_5G,
                    dbvar_H_SLG_20G,
                    dbvar_H_SLG_YTD,
                    dbvar_H_wOBA,
                    dbvar_H_wOBA_5G,
                    dbvar_H_wOBA_20G,
                    dbvar_H_wOBA_YTD,
                    dbvar_H_OPS,
                    dbvar_H_OPS_5G,
                    dbvar_H_OPS_20G,
                    dbvar_H_OPS_YTD,
                    dbvar_H_Wins,
                    dbvar_H_Losses,
                    dbvar_H_WinLoss_Strength,
                    dbvar_H_Wins_5G,
                    dbvar_H_Losses_5G,
                    dbvar_H_WinLoss_Strength_5G,
                    dbvar_H_Wins_20G,
                    dbvar_H_Losses_20G,
                    dbvar_H_WinLoss_Strength_20G,
                    dbvar_H_Wins_HV,
                    dbvar_H_Losses_HV,
                    dbvar_H_WinLoss_Strength_HV,
                    dbvar_H_Wins_YTD,
                    dbvar_H_Losses_YTD,
                    dbvar_H_WinLoss_Strength_YTD,
                    dbvar_H_Wins_YTD_HV,
                    dbvar_H_Losses_YTD_HV,
                    dbvar_H_WinLoss_Strength_YTD_HV,
                    dbvar_H_OutsPitched_Sum,
                    dbvar_H_OutsPitched,
                    dbvar_H_OutsPitched_5G,
                    dbvar_H_OutsPitched_20G,
                    dbvar_H_OutsPitched_YTD,
                    dbvar_H_OutsPitched_YTD_HV,
                    dbvar_H_StrikeoutsAllowed,
                    dbvar_H_StrikeoutsGained,
                    dbvar_H_StrikeoutAccuracy,
                    dbvar_H_StrikeoutsAllowed_Sum,
                    dbvar_H_StrikeoutsGained_Sum,
                    dbvar_H_StrikeoutAccuracy_Sum,
                    dbvar_H_StrikeoutsAllowed_5G,
                    dbvar_H_StrikeoutsGained_5G,
                    dbvar_H_StrikeoutAccuracy_5G,
                    dbvar_H_StrikeoutsGained_20G,
                    dbvar_H_StrikeoutsAllowed_YTD,
                    dbvar_H_StrikeoutsGained_YTD,
                    dbvar_H_StrikeoutAccuracy_YTD,
                    dbvar_H_StrikeoutsAllowed_YTD_HV,
                    dbvar_H_StrikeoutsGained_YTD_HV,
                    dbvar_H_StrikeoutAccuracy_YTD_HV,
                    dbvar_H_Hits_Sum,
                    dbvar_H_Hits,
                    dbvar_H_Hits_Sum_5G,
                    dbvar_H_Hits_5G,
                    dbvar_H_Hits_Sum_20G,
                    dbvar_H_Hits_20G,
                    dbvar_H_Hits_YTD,
                    dbvar_H_Hits_YTD_HV,
                    dbvar_H_HitsAllowed_Sum,
                    dbvar_H_HitsAllowed_Sum_5G,
                    dbvar_H_HitsAllowed_Sum_20G,
                    dbvar_H_HitsAllowed,
                    dbvar_H_HitsAllowed_5G,
                    dbvar_H_HitsAllowed_20G,
                    dbvar_H_HitsAllowed_YTD,
                    dbvar_H_HitsAllowed_YTD_HV,
                    dbvar_H_RunsHitsRatio,
                    dbvar_H_RunsHitsRatio_Sum,
                    dbvar_H_RunsHitsRatio_5G,
                    dbvar_H_RunsHitsRatio_Sum_5G,
                    dbvar_H_RunsHitsRatio_20G,
                    dbvar_H_RunsHitsRatio_Sum_20G,
                    dbvar_H_RunsHitsRatio_YTD,
                    dbvar_H_RunsHitsRatio_Allowed,
                    dbvar_H_RunsHitsRatio_Allowed_Sum,
                    dbvar_H_RunsHitsRatio_Allowed_5G,
                    dbvar_H_RunsHitsRatio_Allowed_Sum_5G,
                    dbvar_H_RunsHitsRatio_Allowed_20G,
                    dbvar_H_RunsHitsRatio_Allowed_Sum_20G,
                    dbvar_H_RunsHitsRatio_Allowed_YTD,
                    dbvar_H_FIP,
                    dbvar_H_FIP_5G,
                    dbvar_H_FIP_YTD,
                    dbvar_H_FIP_YTD_HV,
                    dbvar_H_K_Minus_BB_Pct,
                    dbvar_H_K_Minus_BB_Pct_5G,
                    dbvar_H_K_Minus_BB_Pct_20G,
                    dbvar_H_K_Minus_BB_Pct_YTD,
                    dbvar_H_HR_Per_9_Allowed,
                    dbvar_H_HR_Per_9_Allowed_5G,
                    dbvar_H_HR_Per_9_Allowed_20G,
                    dbvar_H_HR_Per_9_Allowed_YTD,
                    dbvar_H_K_Per_9,
                    dbvar_H_K_Per_9_5G,
                    dbvar_H_K_Per_9_20G,
                    dbvar_H_K_Per_9_YTD,
                    dbvar_H_WalksAllowed_Sum,
                    dbvar_H_WalksAllowed,
                    dbvar_H_WalksAllowed_Sum_5G,
                    dbvar_H_WalksAllowed_5G,
                    dbvar_H_WalksAllowed_Sum_20G,
                    dbvar_H_WalksAllowed_20G,
                    dbvar_H_WalksAllowed_YTD,
                    dbvar_H_WalksAllowed_YTD_HV,
                    dbvar_H_WalksGained_Sum,
                    dbvar_H_WalksGained,
                    dbvar_H_WalksGained_5G,
                    dbvar_H_WalksGained_20G,
                    dbvar_H_WalksGained_YTD,
                    dbvar_H_WalksGained_YTD_HV,
                    dbvar_H_HomeRuns_Sum,
                    dbvar_H_HomeRuns,
                    dbvar_H_HomeRuns_5G,
                    dbvar_H_HomeRuns_Sum_5G,
                    dbvar_H_HomeRuns_20G,
                    dbvar_H_HomeRuns_Sum_20G,
                    dbvar_H_HomeRuns_YTD,
                    dbvar_H_HomeRuns_YTD_HV,
                    dbvar_H_HomeRuns_Allowed_Sum,
                    dbvar_H_HomeRuns_Allowed,
                    dbvar_H_HomeRuns_Allowed_5G,
                    dbvar_H_HomeRuns_Allowed_20G,
                    dbvar_H_HomeRuns_Allowed_YTD,
                    dbvar_H_HomeRuns_Allowed_YTD_HV,
                    dbvar_H_5thInnScore,
                    dbvar_H_Duration,
                    dbvar_H_OverTime,
                    dbvar_H_NP_Sum,
                    dbvar_H_NP,
                    dbvar_H_NP_5G,
                    dbvar_H_NP_YTD,
                    dbvar_H_NP_YTD_HV,
                    dbvar_H_Strikes_Sum,
                    dbvar_H_StrikeAccuracy_Sum,
                    dbvar_H_Strikes,
                    dbvar_H_StrikeAccuracy,
                    dbvar_H_Strikes_5G,
                    dbvar_H_StrikeAccuracy_5G,
                    dbvar_H_Strikes_YTD,
                    dbvar_H_StrikeAccuracy_YTD,
                    dbvar_H_Strikes_YTD_HV,
                    dbvar_H_StrikeAccuracy_YTD_HV,
                    dbvar_H_MenOnBase,
                    dbvar_H_MenOnBase_Strength,
                    dbvar_H_MenOnBase_Efficiency,
                    dbvar_H_MenOnBase_5G,
                    dbvar_H_MenOnBase_Strength_5G,
                    dbvar_H_MenOnBase_Efficiency_5G,
                    dbvar_H_MenOnBase_20G,
                    dbvar_H_MenOnBase_Strength_20G,
                    dbvar_H_MenOnBase_Efficiency_20G,
                    dbvar_H_MenOnBase_YTD,
                    dbvar_H_MenOnBase_Strength_YTD,
                    dbvar_H_MenOnBase_Efficiency_YTD,
                    dbvar_H_MenOnBase_Allowed,
                    dbvar_H_MenOnBase_Allowed_Efficiency,
                    dbvar_H_MenOnBase_Allowed_5G,
                    dbvar_H_MenOnBase_Allowed_Efficiency_5G,
                    dbvar_H_MenOnBase_Allowed_20G,
                    dbvar_H_MenOnBase_Allowed_Efficiency_20G,
                    dbvar_H_MenOnBase_Allowed_YTD,
                    dbvar_H_MenOnBase_Allowed_Efficiency_YTD,
                    dbvar_H_LeftOnBase_Sum,
                    dbvar_H_LeftOnBase,
                    dbvar_H_2BRuns_Sum,
                    dbvar_H_2BRuns,
                    dbvar_H_2BRuns_Sum_5G,
                    dbvar_H_2BRuns_5G,
                    dbvar_H_2BRuns_Sum_20G,
                    dbvar_H_2BRuns_20G,
                    dbvar_H_2BRuns_YTD,
                    dbvar_H_2BRuns_Allowed,
                    dbvar_H_2BRuns_Allowed_5G,
                    dbvar_H_2BRuns_Allowed_20G,
                    dbvar_H_2BRuns_Allowed_YTD,
                    dbvar_H_2BRuns_Strength,
                    dbvar_H_2BRuns_Strength_5G,
                    dbvar_H_2BRuns_Strength_20G,
                    dbvar_H_2BRuns_Strength_YTD,
                    dbvar_H_3BRuns_Sum,
                    dbvar_H_3BRuns,
                    dbvar_H_3BRuns_5G,
                    dbvar_H_3BRuns_20G,
                    dbvar_H_3BRuns_YTD,
                    dbvar_H_3BRuns_Allowed,
                    dbvar_H_3BRuns_Allowed_5G,
                    dbvar_H_3BRuns_Allowed_20G,
                    dbvar_H_3BRuns_Allowed_YTD,
                    dbvar_H_3BRuns_Strength,
                    dbvar_H_3BRuns_Strength_5G,
                    dbvar_H_3BRuns_Strength_20G,
                    dbvar_H_3BRuns_Strength_YTD,
                    dbvar_H_ErrorMade_Sum,
                    dbvar_H_ErrorMade,
                    dbvar_H_ErrorMade_Sum_5G,
                    dbvar_H_ErrorMade_5G,
                    dbvar_H_ErrorMade_Sum_20G,
                    dbvar_H_ErrorMade_20G,
                    dbvar_H_ErrorMade_YTD,
                    dbvar_H_ErrorMade_YTD_HV,
                    dbvar_H_ErrorForced_Sum,
                    dbvar_H_ErrorForced_Sum_5G,
                    dbvar_H_ErrorForced_Sum_20G,
                    dbvar_H_ErrorForced,
                    dbvar_H_ErrorForced_5G,
                    dbvar_H_ErrorForced_20G,
                    dbvar_H_ErrorForced_YTD,
                    dbvar_H_HitsByPitch_Sum,
                    dbvar_H_HitsByPitch,
                    dbvar_H_HitsByPitch_Sum_5G,
                    dbvar_H_HitsByPitch_5G,
                    dbvar_H_HitsByPitch_Sum_20G,
                    dbvar_H_HitsByPitch_20G,
                    dbvar_H_HitsByPitch_YTD,
                    dbvar_H_HitsByPitch_Allowed,
                    dbvar_H_HitsByPitch_Allowed_5G,
                    dbvar_H_HitsByPitch_Allowed_20G,
                    dbvar_H_HitsByPitch_Allowed_YTD,
                    dbvar_H_DoublePlays_Gained_Sum,
                    dbvar_H_DoublePlays_Gained,
                    dbvar_H_DoublePlays_Gained_Sum_5G,
                    dbvar_H_DoublePlays_Gained_5G,
                    dbvar_H_DoublePlays_Gained_Sum_20G,
                    dbvar_H_DoublePlays_Gained_20G,
                    dbvar_H_DoublePlays_Gained_YTD,
                    dbvar_H_DoublePlays_Gained_YTD_HV,
                    dbvar_H_DoublePlays_Allowed,
                    dbvar_H_DoublePlays_Allowed_5G,
                    dbvar_H_DoublePlays_Allowed_20G,
                    dbvar_H_DoublePlays_Allowed_YTD,
                    dbvar_H_DoublePlays_Allowed_YTD_HV,
                    dbvar_H_ReliefPitchers,
                    dbvar_H_TotalBases_Sum,
                    dbvar_H_TotalBases,
                    dbvar_H_TotalBases_5G,
                    dbvar_H_TotalBases_20G,
                    dbvar_H_TotalBases_YTD,     
                    dbvar_H_MenOnBaseTBRatio,
                    dbvar_H_MenOnBaseTBRatio_5G,
                    dbvar_H_WalkStrikeoutRatio_Sum,
                    dbvar_H_WalkStrikeoutRatio,
                    dbvar_H_PowerHits_Sum,
                    dbvar_H_PowerHits,
                    dbvar_H_PowerHits_5G,
                    dbvar_H_Innings_OutPitched_Sum,
                    dbvar_H_Innings_OutPitched,
                    dbvar_H_Innings_OutPitched_Sum_5G,
                    dbvar_H_Innings_OutPitched_5G,
                    dbvar_H_Innings_OutPitched_YTD,
                    dbvar_H_SP_HitsAllowed_Sum,
                    dbvar_H_SP_HitsAllowed,
                    dbvar_H_SP_HitsAllowed_5G,
                    dbvar_H_SP_HitsAllowed_YTD,
                    dbvar_H_EarnedRuns_Sum,
                    dbvar_H_EarnedRunAvg_Sum,
                    dbvar_H_EarnedRuns,
                    dbvar_H_EarnedRunAvg,
                    dbvar_H_EarnedRuns_Sum_5G,
                    dbvar_H_EarnedRunAvg_Sum_5G,
                    dbvar_H_EarnedRuns_5G,
                    dbvar_H_EarnedRunAvg_5G,
                    dbvar_H_EarnedRuns_YTD,
                    dbvar_H_EarnedRunAvg_YTD,
                    dbvar_H_HitsAllowedPer9Innings_Sum,
                    dbvar_H_HitsAllowedPer9Innings,
                    dbvar_H_HitsAllowedPer9Innings_5G,
                    dbvar_H_WalksHitsAllowedPerInning,
                    dbvar_H_WalksHitsAllowedPerInning_5G,
                    dbvar_H_WalksHitsAllowedPerInning_YTD,
                    dbvar_G_H_StartingPitcher_Id,
                    dbvar_H_StartingPitcher_DaysRest,
                    dbvar_H_StartingPitcher_Score_All,
                    dbvar_H_StartingPitcher_Strikeouts_All,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_All,
                    dbvar_H_StartingPitcher_BaseOnBalls_All,
                    dbvar_H_StartingPitcher_Hits_All,
                    dbvar_H_StartingPitcher_NP_All,
                    dbvar_H_StartingPitcher_InningsPitched_All,
                    dbvar_H_StartingPitcher_Strikes_All,
                    dbvar_H_StartingPitcher_StrikeAccuracy_All,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_All,
                    dbvar_H_StartingPitcher_Score_YTD,
                    dbvar_H_StartingPitcher_Strikeouts_YTD,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_YTD,
                    dbvar_H_StartingPitcher_BaseOnBalls_YTD,
                    dbvar_H_StartingPitcher_Hits_YTD,
                    dbvar_H_StartingPitcher_NP_YTD,
                    dbvar_H_StartingPitcher_InningsPitched_YTD,
                    dbvar_H_StartingPitcher_Strikes_YTD,
                    dbvar_H_StartingPitcher_StrikeAccuracy_YTD,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                    dbvar_H_StartingPitcher_ScoreImpact_YTD,
                    dbvar_H_StartingPitcher_StrikeoutsImpact_YTD,
                    dbvar_H_StartingPitcher_BaseOnBallsImpact_YTD,
                    dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                    dbvar_H_StartingPitcher_HitsImpact_YTD,
                    dbvar_H_StartingPitcher_NPImpact_YTD,
                    dbvar_H_StartingPitcher_InningsPitchedImpact_YTD,
                    dbvar_H_StartingPitcher_StrikeImpact_YTD,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                    dbvar_H_StartingPitcher_Score_5G,
                    dbvar_H_StartingPitcher_Strikeouts_5G,
                    dbvar_H_StartingPitcher_StrikeoutAccuracy_5G,
                    dbvar_H_StartingPitcher_BaseOnBalls_5G,
                    dbvar_H_StartingPitcher_Hits_5G,
                    dbvar_H_StartingPitcher_NP_5G,
                    dbvar_H_StartingPitcher_InningsPitched_5G,
                    dbvar_H_StartingPitcher_Strikes_5G,
                    dbvar_H_StartingPitcher_StrikeAccuracy_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_5G,
                    dbvar_H_StartingPitcher_ScoreImpact_5G,
                    dbvar_H_StartingPitcher_StrikeoutsImpact_5G,
                    dbvar_H_StartingPitcher_BaseOnBallsImpact_5G,
                    dbvar_H_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                    dbvar_H_StartingPitcher_HitsImpact_5G,
                    dbvar_H_StartingPitcher_NPImpact_5G,
                    dbvar_H_StartingPitcher_InningsPitchedImpact_5G,
                    dbvar_H_StartingPitcher_StrikeImpact_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                    dbvar_H_StartingPitcher_Score_Ratio,
                    dbvar_H_StartingPitcher_Strikeouts_Ratio,
                    dbvar_H_StartingPitcher_BaseOnBalls_Ratio,
                    dbvar_H_StartingPitcher_Hits_Ratio,
                    dbvar_H_StartingPitcher_NP_Ratio,
                    dbvar_H_StartingPitcher_InningsPitched_Ratio,
                    dbvar_H_StartingPitcher_Strikes_Ratio,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                    dbvar_H_StartingPitcher_Score_Ratio_5G,
                    dbvar_H_StartingPitcher_Strikeouts_Ratio_5G,
                    dbvar_H_StartingPitcher_BaseOnBalls_Ratio_5G,
                    dbvar_H_StartingPitcher_Hits_Ratio_5G,
                    dbvar_H_StartingPitcher_NP_Ratio_5G,
                    dbvar_H_StartingPitcher_InningsPitched_Ratio_5G,
                    dbvar_H_StartingPitcher_Strikes_Ratio_5G,
                    dbvar_H_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                    dbvar_H_BallpenOuts,
                    dbvar_H_BallpenOuts_5G,
                    dbvar_H_BallpenOuts_YTD,
                    dbvar_H_BallpenERA_Approx,
                    dbvar_H_BallpenERA_Approx_5G,
                    dbvar_H_BallpenERA_Approx_YTD,
                    dbvar_G_PH_Win,
                    dbvar_G_H_Runs,
                    dbvar_G_H_Run_Prediction
                ]

MLBdb_V_vars =    [  
                    dbvar_G_V_Id,
                    dbvar_G_V_ParkImpactFactor,
                    dbvar_G_Bookie_V_MoneyLine,
                    dbvar_G_Bookie_V_Probability,
                    dbvar_G_V_Opening_MoneyLine,
                    dbvar_G_V_OpeningProbabilityLine,
                    dbvar_G_V_Closing_MoneyLine,
                    dbvar_G_V_ClosingProbabilityLine,
                    dbvar_G_V_CLL_OPL_Prob_Diff,
                    dbvar_G_V_League,
                    dbvar_G_V_Division,
                    dbvar_G_V_LeagueDiv,
                    dbvar_G_V_Same_LeagueDiv,
                    dbvar_G_V_Same_Div,
                    dbvar_G_V_DaysRest,
                    dbvar_G_V_DistanceTravelled,
                    dbvar_G_V_ContiguousGamesV,
                    dbvar_G_V_ContiguousGamesH,
                    dbvar_G_V_TotalDistanceTravelled_3G,
                    dbvar_G_V_Prev1_Id,
                    dbvar_G_V_Prev1_LeagueDiv,
                    dbvar_G_V_Prev1_SameLeagueDiv,
                    dbvar_G_V_Prev1_SameDiv,
                    dbvar_G_V_Prev1_DistanceTravelled,
                    dbvar_G_V_Prev1Home,
                    dbvar_G_V_Prev1Strength,
                    dbvar_G_V_Prev1StrengthRatio,
                    dbvar_G_V_Prev1Win,
                    dbvar_G_V_Prev1CLL,
                    dbvar_G_V_Prev1_Summary,
                    dbvar_G_V_Prev2_Id,
                    dbvar_G_V_Prev2_LeagueDiv,
                    dbvar_G_V_Prev2_SameLeagueDiv,
                    dbvar_G_V_Prev2_SameDiv,
                    dbvar_G_V_Prev2_DistanceTravelled,
                    dbvar_G_V_Prev2Home,
                    dbvar_G_V_Prev2Strength,
                    dbvar_G_V_Prev2StrengthRatio,
                    dbvar_G_V_Prev2Win,
                    dbvar_G_V_Prev2CLL,
                    dbvar_G_V_Prev2_Summary,
                    dbvar_G_V_Prev3_Id,
                    dbvar_G_V_Prev3_LeagueDiv,
                    dbvar_G_V_Prev3_SameLeagueDiv,
                    dbvar_G_V_Prev3_SameDiv,
                    dbvar_G_V_Prev3_DistanceTravelled,
                    dbvar_G_V_Prev3Home,
                    dbvar_G_V_Prev3Strength,
                    dbvar_G_V_Prev3StrengthRatio,
                    dbvar_G_V_Prev3Win,
                    dbvar_G_V_Prev3CLL,
                    dbvar_G_V_Prev3_Summary,
                    dbvar_G_V_Lookback_Strength,
                    dbvar_G_V_Next1_Id,
                    dbvar_G_V_Next1_LeagueDiv,
                    dbvar_G_V_Next1_SameLeagueDiv,
                    dbvar_G_V_Next1_SameDiv,
                    dbvar_G_V_Next1_DistanceTravelled,
                    dbvar_G_V_Next1Home,
                    dbvar_G_V_Next1Strength,
                    dbvar_G_V_Next1StrengthRatio,
                    dbvar_G_V_Next1_Summary,
                    dbvar_G_V_Next2_Id,
                    dbvar_G_V_Next2_LeagueDiv,
                    dbvar_G_V_Next2_SameLeagueDiv,
                    dbvar_G_V_Next2_SameDiv,
                    dbvar_G_V_Next2_DistanceTravelled,
                    dbvar_G_V_Next2Home,
                    dbvar_G_V_Next2Strength,
                    dbvar_G_V_Next2StrengthRatio,
                    dbvar_G_V_Next2_Summary,
                    dbvar_G_V_Next3_Id,
                    dbvar_G_V_Next3_LeagueDiv,
                    dbvar_G_V_Next3_SameLeagueDiv,
                    dbvar_G_V_Next3_SameDiv,
                    dbvar_G_V_Next3_DistanceTravelled,
                    dbvar_G_V_Next3Home,
                    dbvar_G_V_Next3Strength,
                    dbvar_G_V_Next3StrengthRatio,
                    dbvar_G_V_Next3_Summary,
                    dbvar_G_V_Lookahead_Strength,
                    dbvar_V_ClosingProbabilityLine_HV,
                    dbvar_V_ClosingProbabilityLine_YTD_HV,
                    dbvar_V_Runs_Gained,
                    dbvar_V_Runs_Allowed,
                    dbvar_V_Run_Strength,
                    dbvar_V_Run_Efficiency,
                    dbvar_V_Run_Pythag,
                    dbvar_V_Runs_Gained_5G,
                    dbvar_V_Runs_Allowed_5G,
                    dbvar_V_Run_Strength_5G,
                    dbvar_V_Run_Efficiency_5G,
                    dbvar_V_Run_Pythag_5G,
                    dbvar_V_Runs_Gained_20G,
                    dbvar_V_Runs_Allowed_20G,
                    dbvar_V_Run_Strength_20G,
                    dbvar_V_Run_Efficiency_20G,
                    dbvar_V_Run_Pythag_20G,
                    dbvar_V_Runs_Gained_Sum,
                    dbvar_V_Runs_Allowed_Sum,
                    dbvar_V_Run_Strength_Sum,
                    dbvar_V_Run_Efficiency_Sum,
                    dbvar_V_Run_Pythag_Sum,
                    dbvar_V_Runs_Gained_Sum_5G,
                    dbvar_V_Runs_Allowed_Sum_5G,
                    dbvar_V_Run_Strength_Sum_5G,
                    dbvar_V_Run_Efficiency_Sum_5G,
                    dbvar_V_Runs_Gained_Sum_20G,
                    dbvar_V_Runs_Allowed_Sum_20G,
                    dbvar_V_Run_Strength_Sum_20G,
                    dbvar_V_Run_Efficiency_Sum_20G,
                    dbvar_V_Runs_Gained_Sum_HV,
                    dbvar_V_Runs_Allowed_Sum_HV,
                    dbvar_V_Run_Strength_Sum_HV,
                    dbvar_V_Runs_Gained_HV,
                    dbvar_V_Runs_Allowed_HV,
                    dbvar_V_Run_Strength_HV,
                    dbvar_V_Runs_Gained_YTD,
                    dbvar_V_Runs_Allowed_YTD,
                    dbvar_V_Run_Strength_YTD,
                    dbvar_V_Run_Pythag_YTD,
                    dbvar_V_Runs_Gained_YTD_HV,
                    dbvar_V_Runs_Allowed_YTD_HV,
                    dbvar_V_Run_Strength_YTD_HV,
                    dbvar_V_Runs_5InningsGained,
                    dbvar_V_Runs_5InningsAllowed,
                    dbvar_V_Run_5InningsStrength,
                    dbvar_V_Run_5InningsEfficiency,
                    dbvar_V_Runs_5InningsGained_Sum,
                    dbvar_V_Runs_5InningsAllowed_Sum,
                    dbvar_V_Run_5InningsStrength_Sum,
                    dbvar_V_Run_5InningsEfficiency_Sum,
                    dbvar_V_Runs_5InningsGained_5G,
                    dbvar_V_Runs_5InningsAllowed_5G,
                    dbvar_V_Run_5InningsStrength_5G,
                    dbvar_V_Run_5InningsEfficiency_5G,
                    dbvar_V_Runs_5InningsGained_Sum_5G,
                    dbvar_V_Runs_5InningsAllowed_Sum_5G,
                    dbvar_V_Run_5InningsStrength_Sum_5G,
                    dbvar_V_Run_5InningsEfficiency_Sum_5G,
                    dbvar_V_Runs_5InningsGained_20G,
                    dbvar_V_Runs_5InningsAllowed_20G,
                    dbvar_V_Run_5InningsStrength_20G,
                    dbvar_V_Run_5InningsEfficiency_20G,
                    dbvar_V_Runs_5InningsGained_Sum_20G,
                    dbvar_V_Runs_5InningsAllowed_Sum_20G,
                    dbvar_V_Run_5InningsStrength_Sum_20G,
                    dbvar_V_Run_5InningsEfficiency_Sum_20G,
                    dbvar_V_Runs_5InningsGained_Sum_HV,
                    dbvar_V_Runs_5InningsAllowed_Sum_HV,
                    dbvar_V_Run_5InningsStrength_Sum_HV,
                    dbvar_V_Runs_5InningsGained_HV,
                    dbvar_V_Runs_5InningsAllowed_HV,
                    dbvar_V_Run_5InningsStrength_HV,
                    dbvar_V_Runs_5InningsGained_YTD,
                    dbvar_V_Runs_5InningsAllowed_YTD,
                    dbvar_V_Run_5InningsStrength_YTD,
                    dbvar_V_Pythag_Luck_Factor,
                    dbvar_V_Pythag_Luck_Factor_5G,
                    dbvar_V_Pythag_Luck_Factor_20G,
                    dbvar_V_Pythag_Luck_Factor_YTD,
                    dbvar_V_Run_Differential_Per_Game,
                    dbvar_V_Run_Differential_Per_Game_5G,
                    dbvar_V_Run_Differential_Per_Game_20G,
                    dbvar_V_Run_Differential_Per_Game_YTD,
                    dbvar_V_Weighted_Offense_Index,
                    dbvar_V_Weighted_Offense_Index_5G,
                    dbvar_V_Weighted_Offense_Index_20G,
                    dbvar_V_Weighted_Offense_Index_YTD,
                    dbvar_V_At_Bat,
                    dbvar_V_At_Bat_5G,
                    dbvar_V_At_Bat_20G,
                    dbvar_V_At_Bat_YTD,
                    dbvar_V_At_Bat_HV,
                    dbvar_V_At_Bat_YTD_HV,
                    dbvar_V_OBP,
                    dbvar_V_OBP_5G,
                    dbvar_V_OBP_20G,
                    dbvar_V_OBP_YTD,
                    dbvar_V_SLG,
                    dbvar_V_SLG_5G,
                    dbvar_V_SLG_20G,
                    dbvar_V_SLG_YTD,
                    dbvar_V_wOBA,
                    dbvar_V_wOBA_5G,
                    dbvar_V_wOBA_20G,
                    dbvar_V_wOBA_YTD,
                    dbvar_V_OPS,
                    dbvar_V_OPS_5G,
                    dbvar_V_OPS_20G,
                    dbvar_V_OPS_YTD,
                    dbvar_V_Wins,
                    dbvar_V_Losses,
                    dbvar_V_WinLoss_Strength,
                    dbvar_V_Wins_5G,
                    dbvar_V_Losses_5G,
                    dbvar_V_WinLoss_Strength_5G,
                    dbvar_V_Wins_20G,
                    dbvar_V_Losses_20G,
                    dbvar_V_WinLoss_Strength_20G,
                    dbvar_V_Wins_HV,
                    dbvar_V_Losses_HV,
                    dbvar_V_WinLoss_Strength_HV,
                    dbvar_V_Wins_YTD,
                    dbvar_V_Losses_YTD,
                    dbvar_V_WinLoss_Strength_YTD,
                    dbvar_V_Wins_YTD_HV,
                    dbvar_V_Losses_YTD_HV,
                    dbvar_V_WinLoss_Strength_YTD_HV,
                    dbvar_V_OutsPitched_Sum,
                    dbvar_V_OutsPitched,
                    dbvar_V_OutsPitched_5G,
                    dbvar_V_OutsPitched_20G,
                    dbvar_V_OutsPitched_YTD,
                    dbvar_V_OutsPitched_YTD_HV,
                    dbvar_V_StrikeoutsAllowed,
                    dbvar_V_StrikeoutsGained,
                    dbvar_V_StrikeoutAccuracy,
                    dbvar_V_StrikeoutsAllowed_Sum,
                    dbvar_V_StrikeoutsGained_Sum,
                    dbvar_V_StrikeoutAccuracy_Sum,
                    dbvar_V_StrikeoutsAllowed_5G,
                    dbvar_V_StrikeoutsGained_5G,
                    dbvar_V_StrikeoutAccuracy_5G,
                    dbvar_V_StrikeoutsGained_20G,
                    dbvar_V_StrikeoutsAllowed_YTD,
                    dbvar_V_StrikeoutsGained_YTD,
                    dbvar_V_StrikeoutAccuracy_YTD,
                    dbvar_V_StrikeoutsAllowed_YTD_HV,
                    dbvar_V_StrikeoutsGained_YTD_HV,
                    dbvar_V_StrikeoutAccuracy_YTD_HV,
                    dbvar_V_Hits_Sum,
                    dbvar_V_Hits,
                    dbvar_V_Hits_Sum_5G,
                    dbvar_V_Hits_5G,
                    dbvar_V_Hits_Sum_20G,
                    dbvar_V_Hits_20G,
                    dbvar_V_Hits_YTD,
                    dbvar_V_Hits_YTD_HV,
                    dbvar_V_HitsAllowed_Sum,
                    dbvar_V_HitsAllowed_Sum_5G,
                    dbvar_V_HitsAllowed_Sum_20G,
                    dbvar_V_HitsAllowed,
                    dbvar_V_HitsAllowed_5G,
                    dbvar_V_HitsAllowed_20G,
                    dbvar_V_HitsAllowed_YTD,
                    dbvar_V_HitsAllowed_YTD_HV,
                    dbvar_V_RunsHitsRatio,
                    dbvar_V_RunsHitsRatio_Sum,
                    dbvar_V_RunsHitsRatio_5G,
                    dbvar_V_RunsHitsRatio_Sum_5G,
                    dbvar_V_RunsHitsRatio_20G,
                    dbvar_V_RunsHitsRatio_Sum_20G,
                    dbvar_V_RunsHitsRatio_YTD,
                    dbvar_V_RunsHitsRatio_Allowed,
                    dbvar_V_RunsHitsRatio_Allowed_Sum,
                    dbvar_V_RunsHitsRatio_Allowed_5G,
                    dbvar_V_RunsHitsRatio_Allowed_Sum_5G,
                    dbvar_V_RunsHitsRatio_Allowed_20G,
                    dbvar_V_RunsHitsRatio_Allowed_Sum_20G,
                    dbvar_V_RunsHitsRatio_Allowed_YTD,
                    dbvar_V_FIP,
                    dbvar_V_FIP_5G,
                    dbvar_V_FIP_YTD,
                    dbvar_V_FIP_YTD_HV,
                    dbvar_V_K_Minus_BB_Pct,
                    dbvar_V_K_Minus_BB_Pct_5G,
                    dbvar_V_K_Minus_BB_Pct_20G,
                    dbvar_V_K_Minus_BB_Pct_YTD,
                    dbvar_V_HR_Per_9_Allowed,
                    dbvar_V_HR_Per_9_Allowed_5G,
                    dbvar_V_HR_Per_9_Allowed_20G,
                    dbvar_V_HR_Per_9_Allowed_YTD,
                    dbvar_V_K_Per_9,
                    dbvar_V_K_Per_9_5G,
                    dbvar_V_K_Per_9_20G,
                    dbvar_V_K_Per_9_YTD,
                    dbvar_V_WalksAllowed_Sum,
                    dbvar_V_WalksAllowed,
                    dbvar_V_WalksAllowed_Sum_5G,
                    dbvar_V_WalksAllowed_5G,
                    dbvar_V_WalksAllowed_Sum_20G,
                    dbvar_V_WalksAllowed_20G,
                    dbvar_V_WalksAllowed_YTD,
                    dbvar_V_WalksAllowed_YTD_HV,
                    dbvar_V_WalksGained_Sum,
                    dbvar_V_WalksGained,
                    dbvar_V_WalksGained_5G,
                    dbvar_V_WalksGained_20G,
                    dbvar_V_WalksGained_YTD,
                    dbvar_V_WalksGained_YTD_HV,
                    dbvar_V_HomeRuns_Sum,
                    dbvar_V_HomeRuns,
                    dbvar_V_HomeRuns_5G,
                    dbvar_V_HomeRuns_Sum_5G,
                    dbvar_V_HomeRuns_20G,
                    dbvar_V_HomeRuns_Sum_20G,
                    dbvar_V_HomeRuns_YTD,
                    dbvar_V_HomeRuns_YTD_HV,
                    dbvar_V_HomeRuns_Allowed_Sum,
                    dbvar_V_HomeRuns_Allowed,
                    dbvar_V_HomeRuns_Allowed_5G,
                    dbvar_V_HomeRuns_Allowed_20G,
                    dbvar_V_HomeRuns_Allowed_YTD,
                    dbvar_V_HomeRuns_Allowed_YTD_HV,
                    dbvar_V_5thInnScore,
                    dbvar_V_Duration,
                    dbvar_V_OverTime,
                    dbvar_V_NP_Sum,
                    dbvar_V_NP,
                    dbvar_V_NP_5G,
                    dbvar_V_NP_YTD,
                    dbvar_V_NP_YTD_HV,
                    dbvar_V_Strikes_Sum,
                    dbvar_V_StrikeAccuracy_Sum,
                    dbvar_V_Strikes,
                    dbvar_V_StrikeAccuracy,
                    dbvar_V_Strikes_5G,
                    dbvar_V_StrikeAccuracy_5G,
                    dbvar_V_Strikes_YTD,
                    dbvar_V_StrikeAccuracy_YTD,
                    dbvar_V_Strikes_YTD_HV,
                    dbvar_V_StrikeAccuracy_YTD_HV,
                    dbvar_V_MenOnBase,
                    dbvar_V_MenOnBase_Strength,
                    dbvar_V_MenOnBase_Efficiency,
                    dbvar_V_MenOnBase_5G,
                    dbvar_V_MenOnBase_Strength_5G,
                    dbvar_V_MenOnBase_Efficiency_5G,
                    dbvar_V_MenOnBase_20G,
                    dbvar_V_MenOnBase_Strength_20G,
                    dbvar_V_MenOnBase_Efficiency_20G,
                    dbvar_V_MenOnBase_YTD,
                    dbvar_V_MenOnBase_Strength_YTD,
                    dbvar_V_MenOnBase_Efficiency_YTD,
                    dbvar_V_MenOnBase_Allowed,
                    dbvar_V_MenOnBase_Allowed_Efficiency,
                    dbvar_V_MenOnBase_Allowed_5G,
                    dbvar_V_MenOnBase_Allowed_Efficiency_5G,
                    dbvar_V_MenOnBase_Allowed_20G,
                    dbvar_V_MenOnBase_Allowed_Efficiency_20G,
                    dbvar_V_MenOnBase_Allowed_YTD,
                    dbvar_V_MenOnBase_Allowed_Efficiency_YTD,
                    dbvar_V_LeftOnBase_Sum,
                    dbvar_V_LeftOnBase,
                    dbvar_V_2BRuns_Sum,
                    dbvar_V_2BRuns,
                    dbvar_V_2BRuns_Strength,
                    dbvar_V_2BRuns_Sum_5G,
                    dbvar_V_2BRuns_5G,
                    dbvar_V_2BRuns_Strength_5G,
                    dbvar_V_2BRuns_Sum_20G,
                    dbvar_V_2BRuns_20G,
                    dbvar_V_2BRuns_Strength_20G,
                    dbvar_V_2BRuns_YTD,
                    dbvar_V_2BRuns_Strength_YTD,
                    dbvar_V_2BRuns_Allowed,
                    dbvar_V_2BRuns_Allowed_5G,
                    dbvar_V_2BRuns_Allowed_20G,
                    dbvar_V_2BRuns_Allowed_YTD,
                    dbvar_V_3BRuns_Sum,
                    dbvar_V_3BRuns,
                    dbvar_V_3BRuns_5G,
                    dbvar_V_3BRuns_20G,
                    dbvar_V_3BRuns_YTD,
                    dbvar_V_3BRuns_Allowed,
                    dbvar_V_3BRuns_Allowed_5G,
                    dbvar_V_3BRuns_Allowed_20G,
                    dbvar_V_3BRuns_Allowed_YTD,
                    dbvar_V_3BRuns_Strength,
                    dbvar_V_3BRuns_Strength_5G,
                    dbvar_V_3BRuns_Strength_20G,
                    dbvar_V_3BRuns_Strength_YTD,
                    dbvar_V_ErrorMade_Sum,
                    dbvar_V_ErrorMade,
                    dbvar_V_ErrorMade_Sum_5G,
                    dbvar_V_ErrorMade_5G,
                    dbvar_V_ErrorMade_Sum_20G,
                    dbvar_V_ErrorMade_20G,
                    dbvar_V_ErrorMade_YTD,
                    dbvar_V_ErrorMade_YTD_HV,
                    dbvar_V_ErrorForced_Sum,
                    dbvar_V_ErrorForced_Sum_5G,
                    dbvar_V_ErrorForced_Sum_20G,
                    dbvar_V_ErrorForced,
                    dbvar_V_ErrorForced_5G,
                    dbvar_V_ErrorForced_20G,
                    dbvar_V_ErrorForced_YTD,
                    dbvar_V_HitsByPitch_Sum,
                    dbvar_V_HitsByPitch,
                    dbvar_V_HitsByPitch_Sum_5G,
                    dbvar_V_HitsByPitch_5G,
                    dbvar_V_HitsByPitch_Sum_20G,
                    dbvar_V_HitsByPitch_20G,
                    dbvar_V_HitsByPitch_YTD,
                    dbvar_V_HitsByPitch_Allowed,
                    dbvar_V_HitsByPitch_Allowed_5G,
                    dbvar_V_HitsByPitch_Allowed_20G,
                    dbvar_V_HitsByPitch_Allowed_YTD,
                    dbvar_V_DoublePlays_Gained_Sum,
                    dbvar_V_DoublePlays_Gained,
                    dbvar_V_DoublePlays_Gained_Sum_5G,
                    dbvar_V_DoublePlays_Gained_5G,
                    dbvar_V_DoublePlays_Gained_Sum_20G,
                    dbvar_V_DoublePlays_Gained_20G,
                    dbvar_V_DoublePlays_Gained_YTD,
                    dbvar_V_DoublePlays_Gained_YTD_HV,
                    dbvar_V_DoublePlays_Allowed,
                    dbvar_V_DoublePlays_Allowed_5G,
                    dbvar_V_DoublePlays_Allowed_20G,
                    dbvar_V_DoublePlays_Allowed_YTD,
                    dbvar_V_DoublePlays_Allowed_YTD_HV,
                    dbvar_V_ReliefPitchers,
                    dbvar_V_TotalBases_Sum,
                    dbvar_V_TotalBases,
                    dbvar_V_TotalBases_5G,
                    dbvar_V_TotalBases_20G,
                    dbvar_V_TotalBases_YTD,     
                    dbvar_V_MenOnBaseTBRatio,
                    dbvar_V_MenOnBaseTBRatio_5G,
                    dbvar_V_WalkStrikeoutRatio_Sum,
                    dbvar_V_WalkStrikeoutRatio,
                    dbvar_V_PowerHits_Sum,
                    dbvar_V_PowerHits,
                    dbvar_V_PowerHits_5G,
                    dbvar_V_Innings_OutPitched_Sum,
                    dbvar_V_Innings_OutPitched,
                    dbvar_V_Innings_OutPitched_Sum_5G,
                    dbvar_V_Innings_OutPitched_5G,
                    dbvar_V_Innings_OutPitched_YTD,
                    dbvar_V_SP_HitsAllowed_Sum,
                    dbvar_V_SP_HitsAllowed,
                    dbvar_V_SP_HitsAllowed_5G,
                    dbvar_V_SP_HitsAllowed_YTD,
                    dbvar_V_EarnedRuns_Sum,
                    dbvar_V_EarnedRunAvg_Sum,
                    dbvar_V_EarnedRuns,
                    dbvar_V_EarnedRunAvg,
                    dbvar_V_EarnedRuns_Sum_5G,
                    dbvar_V_EarnedRunAvg_Sum_5G,
                    dbvar_V_EarnedRuns_5G,
                    dbvar_V_EarnedRunAvg_5G,
                    dbvar_V_EarnedRuns_YTD,
                    dbvar_V_EarnedRunAvg_YTD,
                    dbvar_V_HitsAllowedPer9Innings_Sum,
                    dbvar_V_HitsAllowedPer9Innings,
                    dbvar_V_HitsAllowedPer9Innings_5G,
                    dbvar_V_WalksHitsAllowedPerInning,
                    dbvar_V_WalksHitsAllowedPerInning_5G,
                    dbvar_V_WalksHitsAllowedPerInning_YTD,
                    dbvar_G_V_StartingPitcher_Id,
                    dbvar_V_StartingPitcher_DaysRest,
                    dbvar_V_StartingPitcher_Score_All,
                    dbvar_V_StartingPitcher_Strikeouts_All,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_All,
                    dbvar_V_StartingPitcher_BaseOnBalls_All,
                    dbvar_V_StartingPitcher_Hits_All,
                    dbvar_V_StartingPitcher_NP_All,
                    dbvar_V_StartingPitcher_InningsPitched_All,
                    dbvar_V_StartingPitcher_Strikes_All,
                    dbvar_V_StartingPitcher_StrikeAccuracy_All,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_All,
                    dbvar_V_StartingPitcher_Score_YTD,
                    dbvar_V_StartingPitcher_Strikeouts_YTD,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_YTD,
                    dbvar_V_StartingPitcher_BaseOnBalls_YTD,
                    dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_YTD,
                    dbvar_V_StartingPitcher_Hits_YTD,
                    dbvar_V_StartingPitcher_NP_YTD,
                    dbvar_V_StartingPitcher_InningsPitched_YTD,
                    dbvar_V_StartingPitcher_Strikes_YTD,
                    dbvar_V_StartingPitcher_StrikeAccuracy_YTD,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_YTD,
                    dbvar_V_StartingPitcher_ScoreImpact_YTD,
                    dbvar_V_StartingPitcher_StrikeoutsImpact_YTD,
                    dbvar_V_StartingPitcher_BaseOnBallsImpact_YTD,
                    dbvar_V_StartingPitcher_HitsImpact_YTD,
                    dbvar_V_StartingPitcher_NPImpact_YTD,
                    dbvar_V_StartingPitcher_InningsPitchedImpact_YTD,
                    dbvar_V_StartingPitcher_StrikeImpact_YTD,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_YTD,
                    dbvar_V_StartingPitcher_Score_5G,
                    dbvar_V_StartingPitcher_Strikeouts_5G,
                    dbvar_V_StartingPitcher_StrikeoutAccuracy_5G,
                    dbvar_V_StartingPitcher_BaseOnBalls_5G,
                    dbvar_V_StartingPitcher_Hits_5G,
                    dbvar_V_StartingPitcher_NP_5G,
                    dbvar_V_StartingPitcher_InningsPitched_5G,
                    dbvar_V_StartingPitcher_Strikes_5G,
                    dbvar_V_StartingPitcher_StrikeAccuracy_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_5G,
                    dbvar_V_StartingPitcher_ScoreImpact_5G,
                    dbvar_V_StartingPitcher_StrikeoutsImpact_5G,
                    dbvar_V_StartingPitcher_BaseOnBallsImpact_5G,
                    dbvar_V_StartingPitcher_BaseOnBallsStrikeouts_Ratio_5G,
                    dbvar_V_StartingPitcher_HitsImpact_5G,
                    dbvar_V_StartingPitcher_NPImpact_5G,
                    dbvar_V_StartingPitcher_InningsPitchedImpact_5G,
                    dbvar_V_StartingPitcher_StrikeImpact_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInningImpact_5G,
                    dbvar_V_StartingPitcher_Score_Ratio,
                    dbvar_V_StartingPitcher_Strikeouts_Ratio,
                    dbvar_V_StartingPitcher_BaseOnBalls_Ratio,
                    dbvar_V_StartingPitcher_Hits_Ratio,
                    dbvar_V_StartingPitcher_NP_Ratio,
                    dbvar_V_StartingPitcher_InningsPitched_Ratio,
                    dbvar_V_StartingPitcher_Strikes_Ratio,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio,
                    dbvar_V_StartingPitcher_Score_Ratio_5G,
                    dbvar_V_StartingPitcher_Strikeouts_Ratio_5G,
                    dbvar_V_StartingPitcher_BaseOnBalls_Ratio_5G,
                    dbvar_V_StartingPitcher_Hits_Ratio_5G,
                    dbvar_V_StartingPitcher_NP_Ratio_5G,
                    dbvar_V_StartingPitcher_InningsPitched_Ratio_5G,
                    dbvar_V_StartingPitcher_Strikes_Ratio_5G,
                    dbvar_V_StartingPitcher_WalkHitsAllowedPerInning_Ratio_5G,
                    dbvar_V_BallpenOuts,
                    dbvar_V_BallpenOuts_5G,
                    dbvar_V_BallpenOuts_YTD,
                    dbvar_V_BallpenERA_Approx,
                    dbvar_V_BallpenERA_Approx_5G,
                    dbvar_V_BallpenERA_Approx_YTD,
                    dbvar_G_PV_Win,
                    dbvar_G_V_Runs,
                    dbvar_G_V_Run_Prediction
                ]

MLBdb_Ivan_vars =    [  
                        dbvar_G_Ivan_BP_DefenseProbability, 	
                        dbvar_G_Ivan_BP_OffenseProbability,
                        dbvar_G_Ivan_BP_NullProbability,
                        dbvar_G_Ivan_BP_NoLineProbability
                    ]

MLBdb_Offense_vars =    [  ]

MLBdb_Defense_vars =    [  ]

TEAM_AVG_ATTRIB =   ["_Runs_Gained", "_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed", "_OutsPitched", "_StrikeoutsAllowed", "_StrikeoutsGained", "_Hits", "_HitsAllowed", "_WalksAllowed", "_WalksGained", "_HomeRuns", "_HomeRuns_Allowed", "_5thInnScore", "_Duration", "_NP", "_Strikes", "_LeftOnBase", "_2BRuns", "_2BRuns_Allowed", "_3BRuns", "_3BRuns_Allowed", "_ErrorMade",  "_ErrorForced", "_HitsByPitch",  "_HitsByPitch_Allowed", "_DoublePlays_Gained", "_DoublePlays_Allowed", "_ReliefPitchers", "_At_Bat"]

TEAM_AVG_BASE_HVATTRIB =   ["_Runs_Gained", "_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed", "_At_Bat" ]
TEAM_AVG_HVATTRIB =   ["_Runs_Gained_HV", "_Runs_Allowed_HV", "_Runs_5InningsGained_HV", "_Runs_5InningsAllowed_HV", "_At_Bat_HV" ]

TEAM_AVG_BASE_IPATTRIB =   ["_StartingPitcher_InningsPitched_YTD"]
TEAM_AVG_IPATTRIB =   ["_Innings_OutPitched"]
TEAM_AVG_IP_5GATTRIB =   ["_Innings_OutPitched_5G"]
TEAM_AVG_IP_YTDATTRIB =   ["_Innings_OutPitched_YTD"]

TEAM_AVG_BASE_HITSALLATTRIB =   ["_StartingPitcher_Hits_YTD"]
TEAM_AVG_HITSALLATTRIB =   ["_SP_HitsAllowed"]
TEAM_AVG_HITSALL_5GATTRIB =   ["_SP_HitsAllowed_5G"]
TEAM_AVG_HITSALL_YTDATTRIB =   ["_SP_HitsAllowed_YTD"]

TEAM_AVG_BASE_5GATTRIB =   ["_Runs_Gained", "_Runs_Allowed","_Runs_5InningsGained", "_Runs_5InningsAllowed", "_OutsPitched","_StrikeoutsAllowed", "_StrikeoutsGained", "_Hits", "_HitsAllowed", "_WalksAllowed", "_WalksGained", "_HomeRuns", "_HomeRuns_Allowed", "_NP","_Strikes","_2BRuns", "_2BRuns_Allowed", "_3BRuns", "_3BRuns_Allowed", "_ErrorMade", "_ErrorForced", "_HitsByPitch", "_HitsByPitch_Allowed", "_DoublePlays_Gained", "_DoublePlays_Allowed", "_At_Bat"]
TEAM_AVG_5GATTRIB =   ["_Runs_Gained_5G", "_Runs_Allowed_5G","_Runs_5InningsGained_5G", "_Runs_5InningsAllowed_5G","_OutsPitched_5G","_StrikeoutsAllowed_5G", "_StrikeoutsGained_5G","_Hits_5G", "_HitsAllowed_5G", "_WalksAllowed_5G", "_WalksGained_5G", "_HomeRuns_5G", "_HomeRuns_Allowed_5G","_NP_5G","_Strikes_5G","_2BRuns_5G", "_2BRuns_Allowed_5G", "_3BRuns_5G", "_3BRuns_Allowed_5G","_ErrorMade_5G", "_ErrorForced_5G", "_HitsByPitch_5G", "_HitsByPitch_Allowed_5G", "_DoublePlays_Gained_5G", "_DoublePlays_Allowed_5G", "_At_Bat_5G"]

TEAM_AVG_BASE_20GATTRIB =   ["_Runs_Gained", "_Runs_Allowed","_Runs_5InningsGained", "_Runs_5InningsAllowed","_OutsPitched","_StrikeoutsGained","_Hits", "_HitsAllowed", "_WalksAllowed", "_WalksGained", "_HomeRuns", "_HomeRuns_Allowed", "_2BRuns", "_2BRuns_Allowed", "_3BRuns", "_3BRuns_Allowed", "_ErrorMade", "_ErrorForced", "_HitsByPitch", "_HitsByPitch_Allowed", "_DoublePlays_Gained", "_DoublePlays_Allowed", "_At_Bat"]
TEAM_AVG_20GATTRIB =   ["_Runs_Gained_20G", "_Runs_Allowed_20G","_Runs_5InningsGained_20G", "_Runs_5InningsAllowed_20G","_OutsPitched_20G", "_StrikeoutsGained_20G", "_Hits_20G", "_HitsAllowed_20G", "_WalksAllowed_20G", "_WalksGained_20G", "_HomeRuns_20G", "_HomeRuns_Allowed_20G", "_2BRuns_20G", "_2BRuns_Allowed_20G", "_3BRuns_20G",  "_3BRuns_Allowed_20G","_ErrorMade_20G", "_ErrorForced_20G", "_HitsByPitch_20G", "_HitsByPitch_Allowed_20G", "_DoublePlays_Gained_20G", "_DoublePlays_Allowed_20G", "_At_Bat_20G"]

TEAM_AVG_BASE_YTDATTRIB = ["_Runs_Gained", "_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed", "_OutsPitched", "_StrikeoutsAllowed", "_StrikeoutsGained", "_Hits", "_HitsAllowed", "_WalksAllowed", "_WalksGained", "_HomeRuns", "_HomeRuns_Allowed", "_NP", "_Strikes", "_2BRuns", "_2BRuns_Allowed", "_3BRuns",  "_3BRuns_Allowed", "_ErrorMade",  "_ErrorForced", "_HitsByPitch",  "_HitsByPitch_Allowed", "_DoublePlays_Gained", "_DoublePlays_Allowed", "_At_Bat"]
TEAM_AVG_YTDATTRIB = ["_Runs_Gained_YTD", "_Runs_Allowed_YTD", "_Runs_5InningsGained_YTD", "_Runs_5InningsAllowed_YTD", "_OutsPitched_YTD", "_StrikeoutsAllowed_YTD", "_StrikeoutsGained_YTD", "_Hits_YTD", "_HitsAllowed_YTD", "_WalksAllowed_YTD", "_WalksGained_YTD", "_HomeRuns_YTD", "_HomeRuns_Allowed_YTD", "_NP_YTD", "_Strikes_YTD", "_2BRuns_YTD", "_2BRuns_Allowed_YTD",  "_3BRuns_YTD",  "_3BRuns_Allowed_YTD", "_ErrorMade_YTD", "_ErrorForced_YTD", "_HitsByPitch_YTD",  "_HitsByPitch_Allowed_YTD", "_DoublePlays_Gained_YTD", "_DoublePlays_Allowed_YTD", "_At_Bat_YTD"]

TEAM_AVG_BASE_YTDHVATTRIB = ["_Runs_Gained","_Runs_Allowed","_OutsPitched","_StrikeoutsAllowed","_StrikeoutsGained","_Hits","_HitsAllowed","_HitsByPitch_Allowed", "_WalksAllowed", "_WalksGained","_HomeRuns","_HomeRuns_Allowed","_NP","_Strikes","_ErrorMade","_DoublePlays_Gained", "_DoublePlays_Allowed", "_At_Bat"]
TEAM_AVG_YTDHVATTRIB = ["_Runs_Gained_YTD_HV","_Runs_Allowed_YTD_HV","_OutsPitched_YTD_HV","_StrikeoutsAllowed_YTD_HV","_StrikeoutsGained_YTD_HV","_Hits_YTD_HV","_HitsAllowed_YTD_HV","_HitsByPitch_Allowed_YTD_HV","_WalksAllowed_YTD_HV","_WalksGained_YTD_HV","_HomeRuns_YTD_HV","_HomeRuns_Allowed_YTD_HV","_NP_YTD_HV","_Strikes_YTD_HV","_ErrorMade_YTD_HV","_DoublePlays_Gained_YTD_HV", "_DoublePlays_Allowed_YTD_HV", "_At_Bat_YTD_HV"]

TEAM_AVG_LINEBASE_ATTRIB = ['_ClosingProbabilityLine'] 
TEAM_AVG_LINE_HVATTRIB = ['_ClosingProbabilityLine_HV'] #union friendly with TEAM_AVG_LINEBASE_ATTRIB
TEAM_AVG_LINE_YTDHVATTRIB = ['_ClosingProbabilityLine_YTD_HV'] #union friendly with TEAM_AVG_LINEBASE_ATTRIB

TEAM_SUM_WLBASE_ATTRIB = ['_Wins', '_Losses']
TEAM_SUM_WL_ATTRIB = ['_Wins', '_Losses']
TEAM_SUM_WL_5GATTRIB = ['_Wins_5G', '_Losses_5G']
TEAM_SUM_WL_20GATTRIB = ['_Wins_20G', '_Losses_20G']
TEAM_SUM_WL_HVATTRIB = ['_Wins_HV', '_Losses_HV']
TEAM_SUM_WL_YTDATTRIB = ['_Wins_YTD', '_Losses_YTD']
TEAM_SUM_WL_YTDHVATTRIB = ['_Wins_YTD_HV', '_Losses_YTD_HV']

TEAM_SUM_BASE_IPATTRIB =   ["_StartingPitcher_InningsPitched_YTD"]
TEAM_SUM_IPATTRIB =   ["_Innings_OutPitched_Sum"]
TEAM_SUM_IP_5GATTRIB =   ["_Innings_OutPitched_Sum_5G"]

TEAM_SUM_BASE_HITSALLATTRIB =   ["_StartingPitcher_Hits_YTD"]
TEAM_SUM_HITSALLATTRIB =   ["_SP_HitsAllowed_Sum"]

TEAM_SUM_STATSBASE_ATTRIB = ["_Runs_Gained", "_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed", "_OutsPitched", "_StrikeoutsAllowed", "_StrikeoutsGained", "_Hits", "_HitsAllowed", "_WalksAllowed", "_WalksGained", "_HomeRuns", "_HomeRuns_Allowed", "_NP", "_Strikes", "_LeftOnBase", "_2BRuns", "_3BRuns", "_ErrorMade", "_ErrorForced", "_HitsByPitch", "_DoublePlays_Gained"]
TEAM_SUM_STATS_ATTRIB = ["_Runs_Gained_Sum", "_Runs_Allowed_Sum", "_Runs_5InningsGained_Sum", "_Runs_5InningsAllowed_Sum", "_OutsPitched_Sum", "_StrikeoutsAllowed_Sum", "_StrikeoutsGained_Sum", "_Hits_Sum", "_HitsAllowed_Sum", "_WalksAllowed_Sum", "_WalksGained_Sum", "_HomeRuns_Sum", "_HomeRuns_Allowed_Sum", "_NP_Sum", "_Strikes_Sum", "_LeftOnBase_Sum", "_2BRuns_Sum", "_3BRuns_Sum", "_ErrorMade_Sum", "_ErrorForced_Sum", "_HitsByPitch_Sum", "_DoublePlays_Gained_Sum"]

TEAM_SUM_STATSBASE_HVATTRIB = ["_Runs_Gained", "_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed"]
TEAM_SUM_STATS_HVATTRIB = ["_Runs_Gained_Sum_HV", "_Runs_Allowed_Sum_HV", "_Runs_5InningsGained_Sum_HV", "_Runs_5InningsAllowed_Sum_HV"]

TEAM_SUM_STATSBASE_5GATTRIB = ["_Runs_Gained","_Runs_Allowed","_Runs_5InningsGained", "_Runs_5InningsAllowed", "_Hits", "_HitsAllowed", "_WalksAllowed", "_HomeRuns", "_2BRuns", "_ErrorMade", "_ErrorForced", "_HitsByPitch", "_DoublePlays_Gained"]
TEAM_SUM_STATS_5GATTRIB = ["_Runs_Gained_Sum_5G", "_Runs_Allowed_Sum_5G", "_Runs_5InningsGained_Sum_5G", "_Runs_5InningsAllowed_Sum_5G", "_Hits_Sum_5G", "_HitsAllowed_Sum_5G", "_WalksAllowed_Sum_5G", "_HomeRuns_Sum_5G", "_2BRuns_Sum_5G", "_ErrorMade_Sum_5G", "_ErrorForced_Sum_5G", "_HitsByPitch_Sum_5G", "_DoublePlays_Gained_Sum_5G"]

TEAM_SUM_STATSBASE_20GATTRIB = ["_Runs_Gained","_Runs_Allowed", "_Runs_5InningsGained", "_Runs_5InningsAllowed", "_Hits", "_HitsAllowed", "_WalksAllowed", "_HomeRuns", "_2BRuns", "_ErrorMade",  "_ErrorForced", "_HitsByPitch", "_DoublePlays_Gained"]
TEAM_SUM_STATS_20GATTRIB = ["_Runs_Gained_Sum_20G", "_Runs_Allowed_Sum_20G", "_Runs_5InningsGained_Sum_20G", "_Runs_5InningsAllowed_Sum_20G", "_Hits_Sum_20G", "_HitsAllowed_Sum_20G", "_WalksAllowed_Sum_20G", "_HomeRuns_Sum_20G", "_2BRuns_Sum_20G", "_ErrorMade_Sum_20G", "_ErrorForced_Sum_20G","_HitsByPitch_Sum_20G", "_DoublePlays_Gained_Sum_20G"]

#No base required for SP (dBASE populates the primitives from the dump and then dGEN and SCION will avg or sum these primitives as appropriate)
PLAYER_AVG_YTDATTRIB = ['_StartingPitcher_Score_YTD','_StartingPitcher_Strikeouts_YTD','_StartingPitcher_BaseOnBalls_YTD','_StartingPitcher_Hits_YTD','_StartingPitcher_NP_YTD','_StartingPitcher_InningsPitched_YTD','_StartingPitcher_Strikes_YTD']
PLAYER_AVG_5GATTRIB = ['_StartingPitcher_Score_5G','_StartingPitcher_Strikeouts_5G','_StartingPitcher_BaseOnBalls_5G','_StartingPitcher_Hits_5G','_StartingPitcher_NP_5G','_StartingPitcher_InningsPitched_5G','_StartingPitcher_Strikes_5G']
PLAYER_AVG_ALLATTRIB = ['_StartingPitcher_Score_All','_StartingPitcher_Strikeouts_All','_StartingPitcher_BaseOnBalls_All','_StartingPitcher_Hits_All','_StartingPitcher_NP_All','_StartingPitcher_InningsPitched_All','_StartingPitcher_Strikes_All']

#Base var for Park Impact Factor JSON lookup table
PARKIF_CNAME = "ParkImpactFactor"

#Base vars for SP attribs (taken from dump)
SP_SCOREATTRIB = "SP_SCORE"
SP_STRIKEOUTATTRIB = "SP_SO"
SP_BASEONBALLSATTRIB = "SP_BB"
SP_HITSATTRIB = "SP_HIT"
SP_NUMPITCHESATTRIB = "SP_NP"
SP_INNINGSPITCHEDATTRIB = "SP_IP"
SP_STRIKESATTRIB = "SP_ST"
SP_AVG_JSONATTRIBS = [SP_SCOREATTRIB, SP_STRIKEOUTATTRIB,SP_BASEONBALLSATTRIB,SP_HITSATTRIB,SP_NUMPITCHESATTRIB,SP_INNINGSPITCHEDATTRIB,SP_STRIKESATTRIB]

HOME_attrib_str = "H_"
VISITOR_attrib_str = "V_"
HF_BetValue = "HF"
HD_BetValue = "HD"
VF_BetValue = "VF"
VD_BetValue = "VD"
P_BetValue = "P"

NUM_TEAMS = 30
NUM_WEEKS = 27
teamnumlist = range(NUM_TEAMS)  # create list of team ids i.e 0 to 29
weeknumlist = range(1,NUM_WEEKS+1)
MONTH_START = 3
MONTH_END = 11
MLB_NORMALGAME_DURATION = 27.0
MAX_DAYS_REST = 10.0
HISTORICAL_GAME_LIMIT = 3
NO_DATA = -1000000
STR_MIDPOINT = 0.5
PLAYERID_BITSIZE = 22
STRENGTH_WINDOW_AVG = 0.500188897 #Run Strength (10 game window)
STRENGTH_WINDOW_STDEV = 0.08417798 #Run Strength (10 game window)
LOOKBACK = 3
LOOKAHEAD = 3
FIRST_LA = 1
SECOND_LA = 2
THIRD_LA = 3
G_WIN = 1
G_TIE = 0
G_LOSE = -1
YES_HOME = 1
NOT_HOME = -1
AVG_SUM = 1
SUM_ONLY = -1
DATE_F = '%Y%m%d'

GC_ATTRIB_NBIT = [dbvar_G_H_StartingPitcher_Id, dbvar_G_V_StartingPitcher_Id]

# The following feature list determines whether or not we have a NEW or NULL pitcher
H_NULLPITCHER_FEATURES = [dbvar_H_StartingPitcher_NP_YTD,dbvar_H_StartingPitcher_InningsPitched_YTD,dbvar_H_StartingPitcher_Strikes_YTD]
V_NULLPITCHER_FEATURES = [dbvar_V_StartingPitcher_NP_YTD,dbvar_V_StartingPitcher_InningsPitched_YTD,dbvar_V_StartingPitcher_Strikes_YTD]

TEAM_ID_LNAME = {0 : "ATLANTA Braves", 1 : "ARIZONA Diamondbacks",
                 2 : "BALTIMORE Orioles", 3 : "BOSTON Red Sox",
                 4 : "LOS ANGELES Angels", 5 : "CHICAGO Cubs",
                 6 : "CINCINNATI Reds", 7 : "CLEVELAND Indians",
                 8 : "COLORADO Rockies", 9 : "CHICAGO White Sox",
                 10 : "DETROIT Tigers", 11 : "FLORIDA Marlins",
                 12 : "HOUSTON Astros", 13 : "KANSAS CITY Royals",
                 14 : "LOS ANGELES Dodgers", 15 : "MINNESOTA Twins",
                 16 : "WASINGTON Nationals", 17 : "MILWAUKEE Brewers",
                 18 : "NEW YORK Mets", 19 : "NEW YORK Yankees",
                 20 : "OAKLAND Athletics", 21 : "PHILADELPHIA Phillis",
                 22 : "PITTSBURGH Pirates", 23 : "SAN DIEGO Padres",
                 24 : "SEATTLE Mariners", 25 : "SAN FRANCISCO Giants",
                 26 : "ST LOUIS Cardinals", 27 : "TAMPA BAY Rays",
                 28 : "TEXAS Rangers", 29 : "TORONTO Blue Jays"} 

TEAM_ID_SNAME = {0 : "ATL", 1 : "ARZ",
                 2 : "BAL", 3 : "BOS",
                 4 : "LAA", 5 : "CHC",
                 6 : "CIN", 7 : "CLE",
                 8 : "COL", 9 : "CWS",
                 10 : "DET", 11 : "FLO",
                 12 : "HOU", 13 : "KC",
                 14 : "LA", 15 : "MIN",
                 16 : "WAS", 17 : "MLW",
                 18 : "NYM", 19 : "NYY",
                 20 : "OAK", 21 : "PHI",
                 22 : "PIT", 23 : "SD",
                 24 : "SEA", 25 : "SF",
                 26 : "STL", 27 : "TB",
                 28 : "TEX", 29 : "TOR"}

#0 = National, 1 = American
#League mappings checked on 12Jan23 against 2022 data and all is good
TEAM_LEAGUE = {0 : 0, 1 : 0, 2 : 1, 3 : 1, 4 : 1, 5 : 0, 6 : 0, 7 : 1, 8 : 0, 9 : 1, 10 : 1, 11 : 0, 12 : 0,
               13 : 1, 14 : 0, 15 : 1, 16 : 0, 17 : 0, 18 : 0, 19 : 1, 20 : 1, 21 : 0, 22 : 0, 23 : 0, 24 : 1,
               25 : 0, 26 : 0, 27 : 1, 28 : 1, 29 : 1}
# 3 Divs per league, so 6 in total, numbered 0 to 5; National League has divs 0, 1, 2 and American League has 3, 4, 5 
TEAM_DIVISION = {0 : 0, 1 : 2, 2 : 2, 3 : 3, 4 : 5, 5 : 1, 6 : 1, 7 : 4, 8 : 2, 9 : 4, 10 : 4, 11 : 0, 12 : 1, 13 : 4,
                 14 : 2, 15 : 4, 16 : 0, 17 : 1, 18 : 0, 19 : 3, 20 : 5, 21 : 0, 22 : 1, 23 : 2, 24 : 5, 25 : 2, 26 : 1,
                 27 : 3, 28 : 5, 29 : 3}

TEAM_LEAGUE_DIVISION = { 0:"L0:D0",1:"L0:D2",2:"L1:D2",3:"L1:D3",4:"L1:D5",5:"L0:D1",6:"L0:D1",7:"L1:D4",8:"L0:D2",9:"L1:D4",
                        10:"L1:D4",11:"L0:D0",12:"L0:D1",13:"L1:D4",14:"L0:D2",15:"L1:D4",16:"L0:D0",17:"L0:D1",18:"L0:D0",19:"L1:D3",
                        20:"L1:D5",21:"L0:D0",22:"L0:D1",23:"L0:D2",24:"L1:D5",25:"L0:D2",26:"L0:D1",27:"L1:D3",28:"L1:D5",29:"L1:D3" }

TEAM_LOC_LONGITUDE = { 0:84.2317, 1:117.5449, 2:76.3645, 3:71.337, 4:117.5258, 5:87.39, 6:84.311, 7:81.4144, 8:104.593, 9:87.4124,
                      10:83.245, 11:80.1138, 12:95.2147, 13:95.146, 14:118.1434, 15:93.1549, 16:77, 17:87.5423, 18:74.023, 19:74.278,
                      20:122.1611, 21:75.951, 22:79.5946, 23:117.923, 24:122.1951, 25:122.256, 26:90.1152, 27:82.3912, 28:96.48, 29:78.5243 }
   
TEAM_LOC_LATITUDE = { 0:33.507, 1:33.4456, 2:39.1725, 3:42.213, 4:33.507, 5:41.51, 6:39.615, 7:41.2958, 8:39.4421, 9:42.228,
                     10:42.1953, 11:25.4626, 12:29.4547, 13:38.5818, 14:34.38, 15:44.5848, 16:38.55, 17:43.22, 18:40.42, 19:40.4251,
                     20:37.4816, 21:39.578, 22:40.2626, 23:32.4255, 24:47.3623, 25:37.463, 26:38.3738, 27:27.466, 28:32.47, 29:42.5311 }


GC_VALUES_SPREADBET_ONE_HOT = {"HF":"1000", "HD":"0100","VF":"0010","VD":"0001", "P":"0000"}

COLTYPE_INT = "int"
COLTYPE_FLOAT = "float"
COLTYPE_STR = "str"

class MiddleLineTypes(enum.Enum):
   Unknown = 0
   Prob = 1
   Money = 2

def SetColType(MLB_df, col_list, col_type):
    for col in col_list:
        MLB_df[col] = MLB_df[col].astype(col_type)
    return MLB_df

def InitialiseMasterMLBColumnTypes(MLB_df):
    #A. Initialise int columns
    MLB_df = SetColType(MLB_df, MLBdb_int_vars, COLTYPE_INT)
    #B. Initialise float columns
    MLB_df = SetColType(MLB_df, MLBdb_float_vars, COLTYPE_FLOAT)
    #C. Initialise str columns
    MLB_df = SetColType(MLB_df, MLBdb_str_vars, COLTYPE_STR)
    
    return MLB_df

def Get_DistanceTravelled_KM(Team1_Id, Team2_Id):
    #returns distance in km between team 1 and team 2 given their IDs
    Lat_Team1=float(TEAM_LOC_LATITUDE.get(Team1_Id))
    Long_Team1=float(TEAM_LOC_LONGITUDE.get(Team1_Id))
    Lat_Team2=float(TEAM_LOC_LATITUDE.get(Team2_Id))
    Long_Team2=float(TEAM_LOC_LONGITUDE.get(Team2_Id))
            
    return (6371.01 * math.acos(math.sin(math.radians(90-Lat_Team2)) * math.sin(math.radians(90-Lat_Team1)) + math.cos(math.radians(90-Lat_Team2)) * math.cos(math.radians(90-Lat_Team1)) * math.cos(math.radians(90-Long_Team2) - math.radians(90-Long_Team1))))

def Calc_DaysRest(currentGameDate, previousGameDate):
    days_rest = (currentGameDate - previousGameDate).days
    if days_rest > MAX_DAYS_REST:
        return MAX_DAYS_REST
    return days_rest

def createMonthWeek(month, day):
    _week = 1
    if day <= 7:
        _week = 1
    elif day <= 14:
        _week = 2
    elif day <= 21:
        _week = 3
    elif day <= 28:
        _week = 4
    else:
        _week = 5

    if _week == 0:
        return month

    return month + _week * 10**-(math.floor(math.log10(_week))+1)

def getRunCategory(runs):
    fieldValue = "ZERO"
    if runs < 2:
        fieldValue = "LTE1"
    elif runs == 2:
        fieldValue = "TWO"
    elif runs == 3:
        fieldValue = "THREE"
    elif runs == 4:
        fieldValue = "FOUR"
    elif runs == 5:
        fieldValue = "FIVE"
    elif runs == 6:
        fieldValue = "SIX"
    elif runs == 7:
        fieldValue = "SEVEN"
    elif runs == 8:
        fieldValue = "EIGHT"
    else:
        fieldValue = "GTE9"
    return fieldValue

def Dictionarykeywithmaxval(d):
    #returns dictionary key of entry with highest value
     """ a) create a list of the dict's keys and values; 
         b) return the key with the max value"""  
     v=list(d.values())
     k=list(d.keys())
     return k[v.index(max(v))]

#function for subtract one list from another
def filter_list(full_list, excludes):
    s = set(excludes)
    return (x for x in full_list if x not in s)

def round_NN_prediction(number):
        return float(round(number * 2.0) / 2.0)

