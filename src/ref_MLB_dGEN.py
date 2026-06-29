# pylint: disable=W,C,R
import argparse
import decimal  # for floating point to string conversion and maintaining precision
import json
import math
import os
import shlex  # for splitting strings by white space but preserving words within quotes
import subprocess
import sys
import time
import traceback
from collections import deque  # for list processing
from collections import OrderedDict
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytz
from dateutil.relativedelta import relativedelta

import MLB_dbvar as MLB_dbvar
import MLB_dGEN_GTP as MLB_gtp
import MLB_dGEN_Lib as MLB_dgen
import MLB_dGEN_MasterDB as MLB_masterdb
import MLB_globals as MLB_global

# pylint: disable=c0301

#Print opening banner to console
APP_VER = "V26.05 (Standard Edition)"
APP_VER_SHORT = "V26.05"
APP_NAME = "MLB dGEN" 
APP_NAME_SHORT = "dGEN" 
APP_BANNER = "** " + APP_NAME + " " + APP_VER + " **"
APP_OWNER = "Perceptronix Ltd (c) 2026"

#Print opening banner to console         
print("\n"+ APP_BANNER + "\n" + APP_OWNER + "\n")        

# Set environment vars and define key global vars
cwd = os.getcwd()
#set up pandas to report floats at relevant DP
pd.set_option('display.precision', MLB_global.NN_DP_PRECISION)
#create new context for use of ctx (to do with floating point/string conversion and maintaining precision)
ctx = decimal.Context()
ctx.prec = MLB_global.NN_DP_PRECISION #set precision based on setup parameter

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser("\nGenerates statistics for MLB games given the following panel of command-line arguments:\n")
    parser.add_argument("--ws", help="an integer stating window size to determine short-term averages, totals etc A window size of 8 will result in the stats being taken from the last 8 games.")
    parser.add_argument("--hws", help="a binary flag indicating whether or not to truncate historical games to the current season (0=No, 1=Yes).")
    parser.add_argument("--hdec", help="a binary flag indicating whether or not to weight the stats based on how current they are where more recent observations will have a higher weighting (0=No, 1=Yes).")
    parser.add_argument("--mdb", help="name of CSV file containing the raw Master MLB flat file database with primitives added from the Master SQL database.")
    parser.add_argument("--gtp", help="name of CSV file containing a list of games to be processed from the Master MLB flat file database.")

    args = parser.parse_args()  # if incorrect operation entered, program will bomb here
    
    try:
        #1. Load and validate master MLB database
        masterDB = MLB_masterdb.scionMASTERDB(cwd, args.mdb)
        #2. Load and validate the gtp file
        gtpDB = MLB_gtp.scionGTP(cwd, args.gtp)
        #3. Init gameData using command-line arguments
        gameData = MLB_dgen.scionDGEN(cwd, masterDB, gtpDB, args.ws, args.hws, args.hdec)
        #4. Now process each game in the gtp file
        numGtp = gtpDB.getNumGTP()
        for gtpIndex in range(0, numGtp):
            #4.1 Get current gtp and store in the gtp dict and update dGEN
            gtpDB.getGTPDict(gtpIndex)
            gameData.getCurrentGTPData()
            #4.2 Report progress to the user
            per_complete = 0.00
            if numGtp > 0:
                per_complete = (gtpIndex+1)/numGtp*100
            print("\rGenerating MLB game --> {0} of {1} ({2:.2f}%)".format(gtpIndex+1, numGtp, per_complete) + " [ {0} | {1} | {2} @ {3} ]".format(str(gtpDB.current_gtp_dict[gtpDB.gtp_gameid_attrib]),
                                                                                                                                                                                    str(gtpDB.current_gtp_dict[gtpDB.gtp_date_attrib]), 
                                                                                                                                                                                    str(gtpDB.current_gtp_dict[gtpDB.gtp_vis_sname_attrib]), 
                                                                                                                                                                                    str(gtpDB.current_gtp_dict[gtpDB.gtp_hom_sname_attrib])), end="                 ")
            sys.stdout.flush()
            #4.3 validate gtp date with respect to the Master DB
            skip_game = False #assume all is okay with the game until we have evidence to the contrary
            if (gtpDB.current_gtp_dict[gtpDB.gtp_date_attrib] < masterDB.masterdb_oldest_game):
                skip_game = True #skip game
                gameData.updateLogStatus(MLB_global.messageGameSkipDateOutOfRange)
            #4.4 If we have a game to process, let's process it! 
            if not skip_game:
                gameData.generateGameData(gtpDB.getCurrentGTPGameId(), (gtpIndex+1)) #data will only be fully generated ONCE per gtp
                skip_game = gameData.getSkipGameStatus()
                if skip_game: #just report we're skipping the game (details will be in the dgen log)
                    print(" ---> game skipped!")
                    #Update log dataframe
                    gameData.updateGameLogDataFrame()
                else:
                    #4.5 Generate two further instances if possible i.e. one with an intermediate moneyline and another with cll (for H and V)
                    gameData.spanToCLL()
            else:  
                #4.6 Update log dataframe
                gameData.updateGameLogDataFrame()
            #4.6 store intermediate copy of generated data so we dont have to start from game `1 if computer power goes. Store after every 20th game.
            #if gtpIndex % 20 == 0:
            #    gameData.storeGeneratedDataSet()
        #5. Store generated data and logs
        gameData.storeGeneratedDataSet()
        gameData.storeGameLogData()
        gameData.displayExitMessage()
                                
    except Exception:
        print("\n\n"+ APP_NAME + " encountered a fatal error and terminated unexpectedly.")        
        _errorReport()