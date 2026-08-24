# pylint: disable=W,C,R
import sys  # only needed to determine Python version number
import os
from datetime import datetime, date, time, timedelta
import time
import pandas as pd
from pathlib import Path
import shlex #for splitting strings by white space but preserving words within quotes
import json
import copy
import enum
import MLB_dbvar as MLB_dbvar
import MLB_Scion_Globals as MLB_global
# pylint: disable=c0301

class modelCFG:
	def __init__(self):		
		self._model_task_types_active = [MLB_global.TaskTypes.TPROB]
		self._model_task_trun_targets = ["C1","C3"]
		self._model_task_ttotal_targets = ["C1","C3","C1C3","C1C3TRUN","E2"] #C1C3TRUN simply means used the C1 and C3 predictions to form total
		self._model_task_tprob_targets = ["B1","B2","G2","G3"]
		self._model_bitsep_values = ["space","tab","comma","colon"]
		self._model_bit_separator = " " #default is a space but can be changed by config file

	#getters
	@property
	def model_task_trun_targets(self):
		return self._model_task_trun_targets
	@property
	def model_task_ttotal_targets(self):
		return self._model_task_ttotal_targets
	@property
	def model_task_tprob_targets(self):
		return self._model_task_tprob_targets
	@property
	def model_bitsep_values(self):
		return self._model_bitsep_values
	@property
	def model_bit_separator(self):
		return self._model_bit_separator

	def getSysRunTargets(self):
		return self.model_task_trun_targets
	def getSysTotalTargets(self):
		return self.model_task_ttotal_targets
	def getSysProbTargets(self):
		return self.model_task_tprob_targets
	def getSysBitSepSymbols(self):
		return self.model_bitsep_values
	def getSysCurrentBitSep(self):
		return self.model_bit_separator

class scionCFG:
	def __init__(self, system_path, cfgfname_txt):
		self._system_path = system_path
		self._cfgfname_txt = os.path.join(self._system_path, cfgfname_txt) # or Path(self.system_path) / cfgfname_txt
		self.modelcfg = modelCFG() #directly accessible
		self._cfg_variable_assignment = "="
		self._cfg_sys_nnexec_attrib = "SYS_NN_EXEC"
		self._cfg_sys_nn_gid_newline_attrib = "SYS_NN_GID_NEWLINE"
		self._cfg_sys_nn_pattern_bitsep_attrib = "SYS_NN_PATTERN_BITSEP"
		self._cfg_sys_nn_ip_pattern_txt_fname_attrib = "SYS_NN_IP_TESTPATTERN_TXT_FNAME"
		self._cfg_sys_dt_ip_pattern_csv_fname_attrib = "SYS_DT_IP_TESTPATTERN_CSV_FNAME"
		self._cfg_sys_dt_probs_txt_fname_attrib = "SYS_DT_PROBS_TXT_FNAME"
		self._cfg_sys_ols_ip_pattern_csv_fname_attrib = "SYS_OLS_IP_TESTPATTERN_CSV_FNAME"
		self._cfg_sys_ols_intercept_colname_attrib = "SYS_OLS_INTERCEPT_COLNAME"
		self._cfg_sys_run_models_attrib = "SYS_RUN_MODELS"
		self._cfg_sys_run_min_attrib = "SYS_RUN_MIN"
		self._cfg_sys_run_max_attrib = "SYS_RUN_MAX"
		self._cfg_sys_stake_mode_attrib = "SYS_STAKE_MODE"
		self._cfg_sys_fract_kelly_attrib = "SYS_FRACT_KELLY"
		self._cfg_sys_prob_models_attrib = "SYS_PROB_MODELS"
		self._cfg_sys_prob_min_attrib = "SYS_PROB_MIN"
		self._cfg_sys_prob_max_attrib = "SYS_PROB_MAX"
		self._cfg_sys_prob_ensprob_type_attrib = "SYS_PROB_ENSPROB_TYPE" # options defined in MLB_global.EnsembleProbabilityTypes
		self._cfg_sys_prob_base_thresh_attrib = "SYS_PROB_BASE_MODELTHRESH"
		self._cfg_sys_prob_base_bookie_min_attrib = "SYS_PROB_BASE_BOOKIE_MIN"
		self._cfg_sys_prob_base_bookie_max_attrib = "SYS_PROB_BASE_BOOKIE_MAX"
		self._cfg_sys_prob_base_agreethresh_attrib = "SYS_PROB_BASE_AGREETHRESH"
		self._cfg_sys_prob_minprice_attrib = "SYS_PROB_MODEL_MINPRICE"
		self._cfg_sys_prob_maxprice_attrib = "SYS_PROB_MODEL_MAXPRICE"
		self._cfg_sys_prob_edgepp_attrib = "SYS_PROB_EDGEPP_GAP"
		self._cfg_sys_prob_bpvardp_attrib = "SYS_PROB_BPVARDP"
		self._cfg_sys_prob_statsonly_thresh_attrib = "SYS_PROB_STATSONLY_MODELTHRESH"
		self._cfg_sys_prob_statsonly_bookie_min_attrib = "SYS_PROB_STATSONLY_BOOKIE_MIN"
		self._cfg_sys_prob_statsonly_bookie_max_attrib = "SYS_PROB_STATSONLY_BOOKIE_MAX"
		self._cfg_sys_prob_statsonly_agreethresh_attrib = "SYS_PROB_STATSONLY_AGREETHRESH"
		self._cfg_sys_prob_statsonly_minprice_attrib = "SYS_PROB_STATSONLY_MODEL_MINPRICE"
		self._cfg_sys_prob_statsonly_maxprice_attrib = "SYS_PROB_STATSONLY_MODEL_MAXPRICE"
		self._cfg_sys_prob_statsonly_edgepp_attrib = "SYS_PROB_STATSONLY_EDGEPP_GAP"
		self._cfg_sys_prob_statsonly_bpvardp_attrib = "SYS_PROB_STATSONLY_BPVARDP"
		self._cfg_sys_total_models_attrib = "SYS_TOTAL_MODELS"
		self._cfg_sys_total_use_runmodel_attrib = "SYS_TOTAL_USERUNPRED" #if this is active, total_models will be set to 0 and the H and V run pred of RUN module will be used
		self._cfg_sys_dog_history_limit = "SYS_DOG_HISTORY_LIMIT"
		self._cfg_sys_dog_winprice_threshold = "SYS_DOG_WINPRICE_THRESH"
		self._cfg_sys_hf_conf_attrib = "SYS_HF_BASECONFIDENCE"
		self._cfg_sys_hd_conf_attrib = "SYS_HD_BASECONFIDENCE"
		self._cfg_sys_vf_conf_attrib = "SYS_VF_BASECONFIDENCE"
		self._cfg_sys_vd_conf_attrib = "SYS_VD_BASECONFIDENCE"
		self._cfg_sys_lookahead_active_attrib = "SYS_LOOKAHEAD_ACTIVE"
		self._cfg_sys_strength_stats_fname_attrib = "SYS_STRENGTH_STATS_FNAME"
		self._cfg_sys_opshortname_attrib = "SYS_OP_SHORTNAME"
		self._cfg_sys_defaultscale_attrib = "SYS_DEFAULT_SCALE" # the default scaling method is what will be applied to ALL task models IF it is not specified on the model cfg settings
		self._cfg_sys_iqrconst_attrib = "SYS_IQR_CONSTANT"
		self._cfg_sys_logstd_attrib = "SYS_LOGSTD_CONSTANT"
		self._cfg_sys_attribs = 	[
										self._cfg_sys_nnexec_attrib,
										self._cfg_sys_nn_gid_newline_attrib,
										self._cfg_sys_nn_pattern_bitsep_attrib,
										self._cfg_sys_nn_ip_pattern_txt_fname_attrib,
										self._cfg_sys_dt_ip_pattern_csv_fname_attrib,
										self._cfg_sys_ols_ip_pattern_csv_fname_attrib,
										self._cfg_sys_dt_probs_txt_fname_attrib,
										self._cfg_sys_ols_intercept_colname_attrib,
										self._cfg_sys_run_models_attrib,
										self._cfg_sys_total_models_attrib,
										self._cfg_sys_total_use_runmodel_attrib,
										self._cfg_sys_prob_models_attrib,
										self._cfg_sys_prob_min_attrib,
										self._cfg_sys_prob_max_attrib,
										self._cfg_sys_prob_base_thresh_attrib,
										self._cfg_sys_prob_ensprob_type_attrib,
										self._cfg_sys_prob_base_bookie_min_attrib,
										self._cfg_sys_prob_base_bookie_max_attrib,
										self._cfg_sys_prob_base_agreethresh_attrib, 
										self._cfg_sys_prob_minprice_attrib,
										self._cfg_sys_prob_maxprice_attrib,
										self._cfg_sys_prob_edgepp_attrib,
										self._cfg_sys_prob_bpvardp_attrib,
										self._cfg_sys_prob_statsonly_thresh_attrib,
										self._cfg_sys_prob_statsonly_bookie_min_attrib,
										self._cfg_sys_prob_statsonly_bookie_max_attrib,
										self._cfg_sys_prob_statsonly_agreethresh_attrib,
										self._cfg_sys_prob_statsonly_minprice_attrib,
										self._cfg_sys_prob_statsonly_maxprice_attrib,
										self._cfg_sys_prob_statsonly_edgepp_attrib,
										self._cfg_sys_prob_statsonly_bpvardp_attrib,
										self._cfg_sys_run_min_attrib,
										self._cfg_sys_run_max_attrib,
										self._cfg_sys_stake_mode_attrib,
										self._cfg_sys_fract_kelly_attrib,
										self._cfg_sys_dog_history_limit,
										self._cfg_sys_dog_winprice_threshold,
										self._cfg_sys_hf_conf_attrib,
										self._cfg_sys_hd_conf_attrib,
										self._cfg_sys_vf_conf_attrib,
										self._cfg_sys_vd_conf_attrib,
										self._cfg_sys_lookahead_active_attrib,
										self._cfg_sys_strength_stats_fname_attrib,
										self._cfg_sys_opshortname_attrib,
										self._cfg_sys_defaultscale_attrib,
										self._cfg_sys_iqrconst_attrib,
										self._cfg_sys_logstd_attrib
									]
		self._cfg_task_dir_attrib = "_TASK_DIR"
		self._cfg_task_round_preds_attrib = "_TASK_ROUND_PREDS"
		self._cfg_task_model_code_attrib = "_TASK_MODEL_CODE"
		self._cfg_task_model_ensemble_attrib = "_TASK_MODEL_ENSEMBLE"
		self._cfg_task_model_type_attrib = "_TASK_MODEL_TYPE"
		self._cfg_task_model_cfg_fname_attrib = "_TASK_MODEL_CFG_FNAME"
		self._cfg_task_model_windowsize_attrib = "_TASK_MODEL_WINDOW_SIZE"
		self._cfg_task_model_historywithinseason_attrib = "_TASK_MODEL_HISTORY_WITHIN_SEASON"
		self._cfg_task_model_historydecay_attrib = "_TASK_MODEL_HISTORY_DECAY"
		self._cfg_task_model_ip_numfeatures_attrib = "_TASK_MODEL_IP_NUMFEATURES"
		self._cfg_task_model_ip_parkimpactfac_json_fname = "_TASK_MODEL_IP_PARKIMPACTFACTOR_JSONLOOKUP_FNAME"
		self._cfg_task_model_ip_pitcherteamavg_json_fname = "_TASK_MODEL_IP_PITCHERAVGS_JSONLOOKUP_FNAME"
		self._cfg_task_model_ip_varstats_fname_attrib = "_TASK_MODEL_IP_VARSTATS_FNAME"
		self._cfg_task_model_ip_mask_fname_attrib = "_TASK_MODEL_IP_SELECTMASK_FNAME"
		self._cfg_task_model_ip_scaletype_attrib = "_TASK_MODEL_IP_SCALETYPE"
		self._cfg_task_model_ip_categvar_mask_fname_attrib = "_TASK_MODEL_IP_CATEGVAR_MASK_FNAME" 
		self._cfg_task_model_ip_categvar_jsonlookup_fname_attrib = "_TASK_MODEL_IP_CATEGVAR_JSONLOOKUP_FNAME"
		self._cfg_task_model_ip_categvar_insitu_attrib = "_TASK_MODEL_IP_CATEGVAR_INSITU"
		self._cfg_task_model_ip_categvarval_min_attrib = "_TASK_MODEL_IP_CATEGVARVAL_MIN"
		self._cfg_task_model_ip_categvarval_max_attrib = "_TASK_MODEL_IP_CATEGVARVAL_MAX"
		self._cfg_task_model_op_target_attrib = "_TASK_MODEL_OP_TARGET"
		self._cfg_task_model_op_scaletype_attrib = "_TASK_MODEL_OP_SCALETYPE"
		self._cfg_task_model_op_target_descale_attrib = "_TASK_MODEL_OP_DESCALE_TARGET"
		self._cfg_task_model_op_varstats_fname_attrib = "_TASK_MODEL_OP_VARSTATS_FNAME"  
		self._cfg_task_model_op_result_fname_attrib = "_TASK_MODEL_OP_RESULT_FNAME"

		self._cfg_task_model_static_attribs = 	[
													self._cfg_task_dir_attrib, 
													self._cfg_task_round_preds_attrib
												]
		self._cfg_task_model_multiple_instance_attribs = [
															self._cfg_task_model_code_attrib,
															self._cfg_task_model_ensemble_attrib,
															self._cfg_task_model_type_attrib,
															self._cfg_task_model_cfg_fname_attrib,
															self._cfg_task_model_windowsize_attrib,
															self._cfg_task_model_historywithinseason_attrib,
															self._cfg_task_model_historydecay_attrib,
															self._cfg_task_model_ip_numfeatures_attrib,
															self._cfg_task_model_ip_parkimpactfac_json_fname,
															self._cfg_task_model_ip_pitcherteamavg_json_fname,
															self._cfg_task_model_ip_varstats_fname_attrib,
															self._cfg_task_model_ip_mask_fname_attrib,
															self._cfg_task_model_ip_scaletype_attrib,
															self._cfg_task_model_ip_categvar_mask_fname_attrib,
															self._cfg_task_model_ip_categvar_jsonlookup_fname_attrib,
															self._cfg_task_model_ip_categvar_insitu_attrib,
															self._cfg_task_model_ip_categvarval_min_attrib,
															self._cfg_task_model_ip_categvarval_max_attrib,
															self._cfg_task_model_op_target_attrib,
															self._cfg_task_model_op_scaletype_attrib,
															self._cfg_task_model_op_target_descale_attrib,
															self._cfg_task_model_op_varstats_fname_attrib,
															self._cfg_task_model_op_result_fname_attrib
														]
		self._cfg_variable_settings = {
															self._cfg_task_model_code_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ensemble_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_type_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_cfg_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_windowsize_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_historywithinseason_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_historydecay_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_numfeatures_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_parkimpactfac_json_fname:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_pitcherteamavg_json_fname:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_varstats_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_mask_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_scaletype_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_categvar_mask_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_categvar_jsonlookup_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_categvar_insitu_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_categvarval_min_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_ip_categvarval_max_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_op_target_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_op_scaletype_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_op_target_descale_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_op_varstats_fname_attrib:MLB_dbvar.NO_DATA,
															self._cfg_task_model_op_result_fname_attrib:MLB_dbvar.NO_DATA
									}
		self.task_model_settings = {}
		self._parseCFGfile() #parse and execute config file

	#############################################################################################################################################
	##		PRIVATE ACCESSIBLE FUNCS
	#############################################################################################################################################
	def _parseCFGSubset(self, varList):
	#Unknown variables ignored
		try:
			success = True
			#1. Open config file and read data into memory
			path = Path(self._cfgfname_txt)
			with path.open(mode='r') as ip_file:
				config_data = ip_file.readlines() #read all data into memory and store in config_data
				
			num_vars = len(varList) #Operation will fail if not all elements are processed.
			var_ctr = 0
			for line in config_data:
				#check for stopping condition
				if var_ctr == num_vars:
					break #all done!
				#convert line string into a list and then iterate across list
				tokenlist = shlex.split(line)
				previous_operator=""
				previous_variable=""
				for token in tokenlist:
					#strip token of new line and quotes (translate and replace return)
					#new strings hence having to reassign to token)
					token = token.strip('\n')
					token = token.replace('\"','')
					# Uppercase only the operator and variable NAMES (keys), not values.
					# Values like folder names ("Tepper_Prob/") and filenames must
					# preserve their original case for the OS path lookups to work.
					token_upper = token.upper()
					# check if valid command
					if token:                  
						if token_upper == self._cfg_variable_assignment:
							token = token_upper  # "=" stays uppercased (it's an operator)
							if previous_operator != self._cfg_variable_assignment:
								previous_operator = token
							else:
								# invalid syntax so terminate
								print ("\nscionCFG._parseCFGSubset() error - syntax error in " + self._cfgfname_txt + "\n")
								success = False
						elif token_upper not in varList:
							if previous_variable !="" and previous_operator == self._cfg_variable_assignment:
								# assume we have a variable value so add to dictionary
								self._cfg_variable_settings[previous_variable]=token  # store VALUE with original case
								previous_variable=""
						else:
							previous_variable=token_upper  # store KEY uppercased
							var_ctr += 1
							#we have a valid variable so next step, read in value
					if not success: break

			"""
			if var_ctr != num_vars: #double check as we may not have processed ALL vars in desired list as they were missing from cfg file
				print("\nParseCFGSubset() error - incorrect number of variables processed in " + CONFIG_FNAME + "\n")
				success = False
			"""         
		except:
			print("\nscionCFG._parseCFGSubset(): Fatal error processing " + self._cfgfname_txt)
			#raise SystemExit(1)   
			raise
		
		ip_file.close() #probs do not need this
	
		return success

	def _parseCFG_ExtendedVarSet(self):
	#assumes we have a valid value for SYS variables
		success = True
		num_models = 0
		#Add for each task
		for task in self.modelcfg._model_task_types_active:
			num_models = self.getNumTaskModels(task)
			if num_models:	
				#1. First, static vars
				for var in self._cfg_task_model_static_attribs:
					newVar = task.name + var
					# add newVar to CFG dictionary with NO_DATA as the value!
					newItem = {str(newVar) : int(MLB_dbvar.NO_DATA)}
					self._cfg_variable_settings.update(newItem)

				#2. Repeating vars
				for var in self._cfg_task_model_multiple_instance_attribs:
					count = 1
					while count <= num_models:
						newVar = task.name + var + str(count)
						# add newVar to CFG dictionary with NO_DATA as the value!
						newItem = {str(newVar) : int(MLB_dbvar.NO_DATA)}
						self._cfg_variable_settings.update(newItem)
						count += 1  
			else:
				success = False
				break
		return success

	def _parseCFGfile(self):
	# The config file contains SYS variables that must be read first.  SYS_MODULESPERTASK is then used to determine how many additional variables need to be added .
	# The additional variables are then added to the CFG dictionary and the config file is then fully processed with all variables requiring a specific value or NO_DATA
		success = True
		try:
			#1. Read SYS variables
			success = self._parseCFGSubset(self._cfg_sys_attribs)
			if not success: raise Exception
			
			#2. Extend CFG attribs based on sys variables
			success = self._parseCFG_ExtendedVarSet()
			if not success: raise Exception

			#3. Convert CFG dictionary keys to a list and remove sys variables from it
			cfg_list = list(self._cfg_variable_settings.keys()) 
			cfg_nonSYS_list = list(set(cfg_list) - set(self._cfg_sys_attribs)) # '['a', 'b']'
			
			#4. Read non-SYS variables
			success = self._parseCFGSubset(cfg_nonSYS_list)
			if not success: raise Exception

			#5. Perform basic validation
			for k, v in self._cfg_variable_settings.items():
				#only one check, nn_pattern_bitsep_attrib
				if k == self._cfg_sys_nn_pattern_bitsep_attrib:
					#convert to lowercase
					token = self._cfg_variable_settings[k].lower()
					#validate NN_OP_BITSEP
					if token not in self.modelcfg._model_bitsep_values:
						print("\nscionCFG.parseCFGfile(): error - unknown value given for " + str(k) + "\n")
						raise Exception

		except Exception:
			print("scionCFG._parseCFGfile(): Fatal error accessing or processing " + self._cfgfname_txt)
			#raise SystemExit(1)   
			raise
			
	def _validateTaskModelTargets(self, task, modelNum):
		#Assumption: current model cfg settings dict is populated; task and code have already been validated
		#For current model cfg settings in self.task_model_settings, this function validates the model's target output type
		try:
			error_code = 0 #0 = ok, 1 = model task error
			_targetAttrib = self.getCurrentModelTarget()
			if task == MLB_global.TaskTypes.TRUN:
				#check if correct machine learning type chosen
				if _targetAttrib not in self.modelcfg.model_task_trun_targets:
					error_code = 1
					raise Exception
			elif task == MLB_global.TaskTypes.TPROB:
				#check if correct machine learning type chosen
				if _targetAttrib not in self.modelcfg.model_task_tprob_targets:
					error_code = 1
					raise Exception
			else: #must be total 
				if task == MLB_global.TaskTypes.TTOTAL:
					if _targetAttrib not in self.modelcfg.model_task_ttotal_targets:
						error_code = 1
						raise Exception
		except Exception:							
			if error_code == 1:
				print("scionCFG._validateTaskModelTargets(): Error! " + str(task) + " does not have a target type of " +str(_targetAttrib) + ". Please review config settings for " + str(task) + " model " + str(modelNum))
			raise

	def _validateTaskModelTypeEns(self, task, modelNum):
		#Assumption: current model cfg settings dict is populated; This func ensures there are models available for the active tasks
		try:
			modelName = self.task_model_settings[self.cfg_task_model_type_attrib] ##### if modelName == MLB_global.ModelTypes.OLS.name:
			taskName = task.name
			validModelType = MLB_global.hasModelTypeName(modelName)
			if not validModelType:
				raise Exception
			
		except Exception:							
			print("\nscionCFG._validateTaskModelTypeEns(): Error! Machine learning model type not recognised. Please review configuration settings for " + str(taskName) + " model " + str(modelNum))
			raise
	
	#############################################################################################################################################
	##		PUBLIC ACCESSIBLE FUNCS
	#############################################################################################################################################
	#getters
	@property
	def system_path(self): 
		return self._system_path
	@property 
	def cfg_sys_nnexec_attrib(self): return self._cfg_sys_nnexec_attrib 
	@property 
	def cfg_sys_nn_gid_newline_attrib(self): return self._cfg_sys_nn_gid_newline_attrib 
	@property 
	def cfg_sys_nn_pattern_bitsep_attrib(self): return self._cfg_sys_nn_pattern_bitsep_attrib 
	@property 
	def cfg_sys_nn_ip_pattern_txt_fname_attrib(self): return self._cfg_sys_nn_ip_pattern_txt_fname_attrib 
	@property 
	def cfg_sys_dt_ip_pattern_csv_fname_attrib(self): return self._cfg_sys_dt_ip_pattern_csv_fname_attrib
	@property 
	def cfg_sys_dt_probs_txt_fname_attrib(self): return self._cfg_sys_dt_probs_txt_fname_attrib
	@property 
	def cfg_sys_ols_ip_pattern_csv_fname_attrib(self): return self._cfg_sys_ols_ip_pattern_csv_fname_attrib
	@property 
	def cfg_sys_ols_intercept_colname_attrib(self): return self._cfg_sys_ols_intercept_colname_attrib
	@property 
	def cfg_sys_run_models_attrib(self): return self._cfg_sys_run_models_attrib 
	@property 
	def cfg_sys_total_models_attrib(self): return self._cfg_sys_total_models_attrib 
	@property 
	def cfg_sys_total_use_runmodel_attrib(self): return self._cfg_sys_total_use_runmodel_attrib 
	@property 
	def cfg_sys_prob_models_attrib(self): return self._cfg_sys_prob_models_attrib 
	@property 
	def cfg_sys_prob_min_attrib(self): return self._cfg_sys_prob_min_attrib 
	@property 
	def cfg_sys_prob_max_attrib(self): return self._cfg_sys_prob_max_attrib 
	@property 
	def cfg_sys_prob_base_thresh_attrib(self): return self._cfg_sys_prob_base_thresh_attrib 
	@property 
	def cfg_sys_prob_ensprob_type_attrib(self): return self._cfg_sys_prob_ensprob_type_attrib
	@property 
	def cfg_sys_prob_base_bookie_min_attrib(self): return self._cfg_sys_prob_base_bookie_min_attrib 
	@property 
	def cfg_sys_prob_base_bookie_max_attrib(self): return self._cfg_sys_prob_base_bookie_max_attrib 
	@property 
	def cfg_sys_prob_base_agreethresh_attrib(self): return self._cfg_sys_prob_base_agreethresh_attrib 
	@property 
	def cfg_sys_prob_minprice_attrib(self): return self._cfg_sys_prob_minprice_attrib 
	@property 
	def cfg_sys_prob_maxprice_attrib(self): return self._cfg_sys_prob_maxprice_attrib 
	@property 
	def cfg_sys_prob_edgepp_attrib(self): return self._cfg_sys_prob_edgepp_attrib 
	@property 
	def cfg_sys_prob_bpvardp_attrib(self): return self._cfg_sys_prob_bpvardp_attrib
	@property
	def cfg_sys_prob_statsonly_thresh_attrib(self): return self._cfg_sys_prob_statsonly_thresh_attrib
	@property 
	def cfg_sys_prob_statsonly_bookie_min_attrib(self): return self._cfg_sys_prob_statsonly_bookie_min_attrib
	@property 
	def cfg_sys_prob_statsonly_bookie_max_attrib(self): return self._cfg_sys_prob_statsonly_bookie_max_attrib 
	@property 
	def cfg_sys_prob_statsonly_agreethresh_attrib(self): return self._cfg_sys_prob_statsonly_agreethresh_attrib 
	@property 
	def cfg_sys_prob_statsonly_minprice_attrib(self): return self._cfg_sys_prob_statsonly_minprice_attrib 
	@property 
	def cfg_sys_prob_statsonly_maxprice_attrib(self): return self._cfg_sys_prob_statsonly_maxprice_attrib 
	@property 
	def  cfg_sys_prob_statsonly_edgepp_attrib(self): return self._cfg_sys_prob_statsonly_edgepp_attrib 
	@property
	def cfg_sys_prob_statsonly_bpvardp_attrib(self): return self._cfg_sys_prob_statsonly_bpvardp_attrib
	@property 
	def  cfg_sys_run_min_attrib(self): return self._cfg_sys_run_min_attrib 
	@property 
	def  cfg_sys_run_max_attrib(self): return self._cfg_sys_run_max_attrib 
	@property 
	def  cfg_sys_stake_mode_attrib(self): return self._cfg_sys_stake_mode_attrib 
	@property 
	def  cfg_sys_fract_kelly_attrib(self): return self._cfg_sys_fract_kelly_attrib 
	@property
	def  cfg_sys_dog_history_limit(self): return self._cfg_sys_dog_history_limit
	@property
	def  cfg_sys_dog_winprice_threshold(self): return self._cfg_sys_dog_winprice_threshold
	@property 
	def  cfg_sys_hf_conf_attrib(self): return self._cfg_sys_hf_conf_attrib 
	@property 
	def  cfg_sys_hd_conf_attrib(self): return self._cfg_sys_hd_conf_attrib 
	@property 
	def  cfg_sys_vf_conf_attrib(self): return self._cfg_sys_vf_conf_attrib 
	@property 
	def  cfg_sys_vd_conf_attrib(self): return self._cfg_sys_vd_conf_attrib
	@property 
	def  cfg_sys_lookahead_active_attrib(self): return self._cfg_sys_lookahead_active_attrib
	@property 
	def  cfg_sys_strength_stats_fname_attrib(self): return self._cfg_sys_strength_stats_fname_attrib
	@property 
	def  cfg_sys_opshortname_attrib(self): return self._cfg_sys_opshortname_attrib 
	@property 
	def  cfg_sys_defaultscale_attrib(self): return self._cfg_sys_defaultscale_attrib 
	@property 
	def  cfg_sys_iqrconst_attrib(self): return self._cfg_sys_iqrconst_attrib 
	@property 
	def  cfg_sys_logstd_attrib(self): return self._cfg_sys_logstd_attrib 
	@property 
	def  cfg_sys_attribs (self): return self._cfg_sys_attribs 
	@property 
	def  cfg_task_dir_attrib(self): return self._cfg_task_dir_attrib 
	@property 
	def  cfg_task_round_preds_attrib(self): return self._cfg_task_round_preds_attrib 
	@property 
	def  cfg_task_model_code_attrib(self): return self._cfg_task_model_code_attrib 
	@property 
	def  cfg_task_model_ensemble_attrib(self): return self._cfg_task_model_ensemble_attrib 
	@property 
	def  cfg_task_model_type_attrib(self): return self._cfg_task_model_type_attrib 
	@property 
	def  cfg_task_modelcfg_fname_attrib(self): return self._cfg_task_model_cfg_fname_attrib 
	@property 
	def  cfg_task_model_windowsize_attrib(self): return self._cfg_task_model_windowsize_attrib 
	@property 
	def  cfg_task_model_historywithinseason_attrib(self): return self._cfg_task_model_historywithinseason_attrib 
	@property 
	def  cfg_task_model_historydecay_attrib(self): return self._cfg_task_model_historydecay_attrib 
	@property 
	def  cfg_task_model_ip_numfeatures_attrib(self): return self._cfg_task_model_ip_numfeatures_attrib 
	@property 
	def  cfg_task_model_ip_parkimpactfac_json_fname_attrib(self): return self._cfg_task_model_ip_parkimpactfac_json_fname
	@property 
	def  cfg_task_model_ip_pitcherteamavg_json_fname_attrib(self): return self._cfg_task_model_ip_pitcherteamavg_json_fname 
	@property 
	def  cfg_task_model_ip_varstats_fname_attrib(self): return self._cfg_task_model_ip_varstats_fname_attrib 
	@property 
	def  cfg_task_model_ip_mask_fname_attrib(self): return self._cfg_task_model_ip_mask_fname_attrib 
	@property 
	def  cfg_task_model_ip_scaletype_attrib(self): return self._cfg_task_model_ip_scaletype_attrib 
	@property 
	def  cfg_task_model_ip_categvar_mask_fname_attrib(self): return self._cfg_task_model_ip_categvar_mask_fname_attrib 
	@property 
	def  cfg_task_model_ip_categvar_jsonlookup_fname_attrib(self): return self._cfg_task_model_ip_categvar_jsonlookup_fname_attrib 
	@property 
	def  cfg_task_model_ip_categvar_insitu_attrib(self): return self._cfg_task_model_ip_categvar_insitu_attrib 
	@property 
	def  cfg_task_model_ip_categvarval_min_attrib(self): return self._cfg_task_model_ip_categvarval_min_attrib 
	@property 
	def  cfg_task_model_ip_categvarval_max_attrib(self): return self._cfg_task_model_ip_categvarval_max_attrib 
	@property 
	def  cfg_task_model_op_target_attrib(self): return self._cfg_task_model_op_target_attrib 
	@property 
	def  cfg_task_model_op_scaletype_attrib(self): return self._cfg_task_model_op_scaletype_attrib 
	@property 
	def  cfg_task_model_op_target_descale_attrib(self): return self._cfg_task_model_op_target_descale_attrib 
	@property 
	def  cfg_task_model_op_varstats_fname_attrib(self): return self._cfg_task_model_op_varstats_fname_attrib 
	@property 
	def  cfg_task_model_op_result_fname_attrib(self): return self._cfg_task_model_op_result_fname_attrib 
	@property 
	def  cfg_task_model_static_attribs (self): return self._cfg_task_model_static_attribs 
	@property 
	def  cfg_task_model_multiple_instance_attribs (self): return self._cfg_task_model_multiple_instance_attribs 
	@property 
	def  cfg_variable_settings (self): return self._cfg_variable_settings 

 	#getters for sys vars
	def getSysPath(self):
		return self._system_path
	def getSysNNExec(self):
		return self._cfg_variable_settings[self.cfg_sys_nnexec_attrib]
	def getSysNNGidNL(self):
		return self._cfg_variable_settings[self.cfg_sys_nn_gid_newline_attrib]
	def getSysNNBitSep(self): #inefficient
		self._cfg_variable_settings[self.cfg_sys_nn_pattern_bitsep_attrib] = str(self._cfg_variable_settings[self.cfg_sys_nn_pattern_bitsep_attrib]).lower()
		return self._cfg_variable_settings[self.cfg_sys_nn_pattern_bitsep_attrib]
	def getSysNNIpPatternTxt(self):
		return self._cfg_variable_settings[self.cfg_sys_nn_ip_pattern_txt_fname_attrib]
	def getSysOLSIpPatternCSV(self):
		return self._cfg_variable_settings[self.cfg_sys_ols_ip_pattern_csv_fname_attrib]
	def getSysDTIpPatternCSV(self):
		return self._cfg_variable_settings[self.cfg_sys_dt_ip_pattern_csv_fname_attrib]
	def getSysDTProbsTXTFname(self):
		return self._cfg_variable_settings[self.cfg_sys_dt_probs_txt_fname_attrib]
	def getSysNumRunModels(self):
		return self._cfg_variable_settings[self.cfg_sys_run_models_attrib]
	def getSysNumTotalModels(self):
		return self._cfg_variable_settings[self.cfg_sys_total_models_attrib]
	def getSysTotalUseRunModel(self):
		return self._cfg_variable_settings[self.cfg_sys_total_use_runmodel_attrib]
	def getSysNumProbModels(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_models_attrib]
	def getSysProbMin(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_min_attrib]
	def getSysProbMax(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_max_attrib]
	def getSysProbThresh(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_base_thresh_attrib]
	def getSysProbEnsProbType(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_ensprob_type_attrib]
	def getSysProbMinPrice(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_minprice_attrib]
	def getSysProbMaxPrice(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_maxprice_attrib]
	def getSysProbAgreeThresh(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_base_agreethresh_attrib]
	def getSysProbBookieMin(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_base_bookie_min_attrib]
	def getSysProbBookieMax(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_base_bookie_max_attrib]
	def getSysProbPointsGap(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_edgepp_attrib]
	def getSysProbBPVarDP(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_bpvardp_attrib]
	def getSysProbSTATSONLYThresh(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_thresh_attrib]
	def getSysProbSTATSONLYBookieMin(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_bookie_min_attrib]
	def getSysProbSTATSONLYBookieMax(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_bookie_max_attrib]
	def getSysProbSTATSONLYAgreeThresh(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_agreethresh_attrib]
	def getSysProbSTATSONLYModelMin(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_minprice_attrib]
	def getSysProbSTATSONLYModelMax(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_maxprice_attrib]
	def getSysProbSTATSONLYPointsGap(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_edgepp_attrib]
	def getSysProbSTATSONLYBPVarDP(self):
		return self._cfg_variable_settings[self.cfg_sys_prob_statsonly_bpvardp_attrib]
	def getSysRunMin(self):
		return self._cfg_variable_settings[self.cfg_sys_run_min_attrib]
	def getSysRunMax(self):
		return self._cfg_variable_settings[self.cfg_sys_run_max_attrib]
	def getSysStakeMode(self):
		return self._cfg_variable_settings[self.cfg_sys_stake_mode_attrib]
	def getSysKellyFract(self):
		return self._cfg_variable_settings[self.cfg_sys_fract_kelly_attrib]
	def getSysDogHistoryLimit(self):
		return self._cfg_variable_settings[self.cfg_sys_dog_history_limit]
	def getSysDogWinLossPriceThres(self):
		return self._cfg_variable_settings[self._cfg_sys_dog_winprice_threshold]
	def getSysHFConf(self):
		return self._cfg_variable_settings[self.cfg_sys_hf_conf_attrib]
	def getSysHDConf(self):
		return self._cfg_variable_settings[self.cfg_sys_hd_conf_attrib]
	def getSysVFConf(self):
		return self._cfg_variable_settings[self.cfg_sys_vf_conf_attrib]
	def getSysVDConf(self):
		return self._cfg_variable_settings[self.cfg_sys_vd_conf_attrib]
	def getSysLookAheadStatus(self):
		return self._cfg_variable_settings[self.cfg_sys_lookahead_active_attrib]
	def getSysSidePredConf(self, betPos):
		conf = 0.0
		if betPos == MLB_global.ACTION_LINE_HF:
			conf = float(self.getSysHFConf())
		elif betPos == MLB_global.ACTION_LINE_HD:
			conf = float(self.getSysHDConf())
		elif betPos == MLB_global.ACTION_LINE_VF:
			conf = float(self.getSysVFConf())
		else:
			if betPos == MLB_global.ACTION_LINE_VD:
				conf = float(self.getSysVDConf())
		return conf
	def getStrengthStatsPathFname(self):
		_fullFname = os.path.join(self._system_path, self._cfg_variable_settings[self.cfg_sys_strength_stats_fname_attrib]) # or Path(self.system_path) / cfgfname_txt
		return _fullFname
	def getStrengthStatsFname(self):
		return self._cfg_variable_settings[self.cfg_sys_strength_stats_fname_attrib]
	def getSysOpShortName(self):
		return self._cfg_variable_settings[self.cfg_sys_opshortname_attrib]
	def getSysDefaultScale(self):
		return int(self._cfg_variable_settings[self._cfg_sys_defaultscale_attrib])
	def getSysIQRConst(self):
		return self._cfg_variable_settings[self.cfg_sys_iqrconst_attrib]
	def getSysLogStd(self):
		return self._cfg_variable_settings[self.cfg_sys_logstd_attrib]

	def getCurrentTaskModelFolder(self):
		return os.path.join(self._system_path, self.task_model_settings[self.cfg_task_dir_attrib])
	def getCurrentTaskModelEnsemble(self):
		return self.task_model_settings[self.cfg_task_model_ensemble_attrib]
	def getCurrentTaskModelWindowSize(self):
		return self.task_model_settings[self.cfg_task_model_windowsize_attrib]
	def getCurrentModelCategInsitu(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvar_insitu_attrib]	
	def getCurrentModelCode(self):
		return self.task_model_settings[self._cfg_task_model_code_attrib]
	def getCurrentModelTarget(self):
		return self.task_model_settings[self._cfg_task_model_op_target_attrib]
	def getCurrentModelTaskType(self):
		return self.task_model_settings[self._cfg_task_model_type_attrib]
	def getCurrentModelTaskCfgFname(self):
		return self.task_model_settings[self._cfg_task_model_cfg_fname_attrib]
	def getCurrentModelRoundPreds(self):
		return self.task_model_settings[self._cfg_task_round_preds_attrib]
	def getCurrentModelNumIPFeatures(self):
		return self.task_model_settings[self._cfg_task_model_ip_numfeatures_attrib]
	def getCurrentModelIpParkImpactFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_parkimpactfac_json_fname]
	def getCurrentModelIpPitcherTeamAvgFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_pitcherteamavg_json_fname]
	def getCurrentModelIpVarStatsFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_varstats_fname_attrib]
	def getCurrentModelIpMaskFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_mask_fname_attrib]
	def getCurrentModelIpScaleType(self):
		return self.task_model_settings[self._cfg_task_model_ip_scaletype_attrib]
	def getCurrentModelIpCategMaskFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvar_mask_fname_attrib]
	def getCurrentModelIpCategJSONFname(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvar_jsonlookup_fname_attrib]
	def getCurrentModelIpCategInsitu(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvar_insitu_attrib]	
	def getCurrentModelIpCategMinVal(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvarval_min_attrib]	
	def getCurrentModelIpCategMaxVal(self):
		return self.task_model_settings[self._cfg_task_model_ip_categvarval_max_attrib]	

	def getCurrentModelOpTarget(self):
		return self.task_model_settings[self._cfg_task_model_op_target_attrib]
	def getCurrentModelOpScaleType(self):
		return self.task_model_settings[self._cfg_task_model_op_scaletype_attrib]
	def getCurrentModelOpVarStatsFname(self):
		return self.task_model_settings[self._cfg_task_model_op_varstats_fname_attrib]
	def getCurrentModelOpResultFname(self):
		return self.task_model_settings[self._cfg_task_model_op_result_fname_attrib]

	def getTaskModelSettings(self, task, model_number):
		#Assumes all configuration settings have been loaded into self._cfg_variable_settings
		#Given a valid task type and model number, self.task_model_settings will be populated with the relevant subset of variable settings from self._cfg_variable_settings
		try:
			#1. initialise key variables
			success = True
			self.task_model_settings = {}
            #2. validate task
			if task == MLB_global.TaskTypes.TRUN:
				num_models = int(self.getSysNumRunModels())
			elif task == MLB_global.TaskTypes.TTOTAL:
				num_models = int(self.getSysNumTotalModels())
			elif task == MLB_global.TaskTypes.TPROB:
				num_models = int(self.getSysNumProbModels())
			else: #should never get here!
				success = False
            #3. we have a valid task, do we have a valid model_number?
			if model_number < 0 or model_number > num_models:
				success = False
			#4. If not successful, raise error
			if not success:
				print("\nscionCFG.getTaskModelSettings(): Error - either invalid task or model number provided as input, please review the calling function!\n")
				raise Exception
			#5. Game on, build task_model_settings dictionary
            #5.1 Add static variables
			taskName =  task.name
			for var in self._cfg_task_model_static_attribs:
				#create variable name
				staticVarName = taskName + var
				#get item from settings dictionary
				staticVarValue = self._cfg_variable_settings[staticVarName]
				#create new item in dict BUT we want to use the generic var as the key so it can be accessed by the calling program
				newItem = {str(var) : staticVarValue}
				#update task_model_settings dict
				self.task_model_settings.update(newItem)
			#5.2. Add repeating vars
			for var in self._cfg_task_model_multiple_instance_attribs:
				#create variable name
				repeatVarName = taskName + var + str(model_number)
				#get item from settings dictionary
				repeatVarValue = self._cfg_variable_settings[repeatVarName]
				#create new item in dict BUT we want to use the generic var as the key so it can be accessed by the calling program
				newItem = {str(var) : repeatVarValue}
				#update task_model_settings dict
				self.task_model_settings.update(newItem)
		except Exception:
			print("\nscionCFG.getTaskModelSettings(): Fatal error getting configuration settings for a single task-based model!")
			raise

	def getTaskFolder(self, task):
        #Assumes all configuration settings have been loaded into self._cfg_variable_settings
		#Given a valid task type, the task folder will be returned
		try:
			# Check if valid task
			if task not in self.modelcfg._model_task_types_active:
				raise Exception
			#if so construct folder
			taskName = task.name
			sysPath = self.getSysPath()
			task_subfolder = self._cfg_variable_settings[str(taskName + self._cfg_task_dir_attrib)]
			task_folder = os.path.join(sysPath, task_subfolder)

		except Exception:
			print("\nscionCFG.getTaskFolder(): unexpected error getting the task folder - please review inputs passed to this module.")
			raise

		return task_folder

	def getNumTaskModels(self, task):
        #Assumes all configuration settings have been loaded into self._cfg_variable_settings
		#Given a valid task type, the number of models will be returned
		try:
			#1. Get number of models
			if task == MLB_global.TaskTypes.TRUN:
				num_models = int(self.getSysNumRunModels())
			elif task == MLB_global.TaskTypes.TTOTAL:
				num_models = int(self.getSysNumTotalModels())
			elif task == MLB_global.TaskTypes.TPROB:
				num_models = int(self.getSysNumProbModels())
			else: #should never get here!
				num_models = 0
		except:
			print("\nscionCFG.getNumTaskModels(): Unexpected error getting the number of models for a particular task")
			raise

		return num_models

	def validateModelSettings(self, task, modelNum):
    #Assumption: current model cfg settings dict MUST be populated
    #For current model cfg settings in self.task_model_settings, this function validates the ensemble number and model number
		try:
			#a. round preds (cfg dict modified)
			self.task_model_settings[self.cfg_task_round_preds_attrib] = int(self.task_model_settings[self.cfg_task_round_preds_attrib])
			if self.task_model_settings[self.cfg_task_round_preds_attrib] != MLB_global.YES:
				self.task_model_settings[self.cfg_task_round_preds_attrib] = MLB_global.NO
			#b. model code
			#self._validateModelEnsCode(task, modelNum)	
			#c. model type
			self._validateTaskModelTypeEns(task, modelNum)
			#d. model output types
			self._validateTaskModelTargets(task, modelNum)
			#e. check value for self._cfg_sys_nn_pattern_bitsep_attrib
			_bitSep = self.getSysNNBitSep()
			if _bitSep not in self.modelcfg.model_bitsep_values:
				print("\nscionCFG.validateModelSettings(): Unrecognised bit separator " + str(_bitSep) + " given in the system settings. Please review config settings for " + str(self.cfg_sys_nn_pattern_bitsep_attrib))
				raise Exception
		
		except Exception:
			print("\nscionCFG.validateModelSettings(): Error performing key validation of model settings")
			raise

	def getBitSepChar(self):
		try:
			_bitSep = self.getSysNNBitSep()
			if _bitSep not in self.modelcfg.model_bitsep_values:
					print("\nscionCFG.getBitSepChar(): Unrecognised bit separator " + str(_bitSep) + " given in the system settings. Please review config settings for " + str(self.cfg_sys_nn_pattern_bitsep_attrib))
					raise Exception
			if _bitSep == "space":
				return " "
			elif _bitSep == "tab":
				return "	"
			elif _bitSep == "comma":
				return ","
			else:
				return ';'
		except Exception:
			print("\nscionCFG.getBitSepChar(): Error getting a valid bit separator symbol.")
			raise	
	

	

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
  


