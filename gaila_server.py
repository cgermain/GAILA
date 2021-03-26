from __future__ import print_function
from flask import Flask, render_template, request, make_response, jsonify 
from functools import update_wrapper
app = Flask(__name__)
from time import time
from SCRIPTS_FOR_GUI import mgf_select_one
import json
from os.path import join
from SCRIPTS_FOR_GUI import combine_selected_mgf_files
from SCRIPTS_FOR_GUI import call_xml_parser
import os
from SCRIPTS_FOR_GUI import combine_xml_mgf
import math
from SCRIPTS_FOR_GUI import utility
from SCRIPTS_FOR_GUI import validation
from SCRIPTS_FOR_GUI import handle_inverse_posts
from SCRIPTS_FOR_GUI import makeFolderNames
from SCRIPTS_FOR_GUI import plaincount
import shutil
from datetime import datetime
import pandas as pd
import re
import logging
from decimal import Decimal
from SCRIPTS_FOR_GUI import mergemgf
import sys
import glob
import stat
from ast import literal_eval
import threading
import signal
import atexit


TIME_FORMAT =  "%Y-%m-%d_%H-%M-%S"

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def signal_handler(sig, frame):
	if os.path.isdir(join(sys.path[0], "Temp")):
		shutil.rmtree(join(sys.path[0], "Temp"))
	sys.exit(0)

def nocache(f):
	def new_func(*args, **kwargs):
		resp = make_response(f(*args, **kwargs))
		resp.cache_control.no_cache = True
		return resp
	return update_wrapper(new_func, f)

@app.route("/")
@nocache
def main():
	try:
		return render_template('index_new.html')

	except KeyboardInterrupt:
		print("Shutdown requested...exiting")
		sys.exit(0)

@app.route("/tab", methods=['GET'])
@nocache
def tab():
	file_name = str(request.args.get('name')) + '.html'
	gene_files = utility.get_gene_files_array()
	inverse_files = utility.get_inverse_files_array()
	return render_template(file_name, gene_files=gene_files,\
	 inverse_files=inverse_files)

@app.route("/tab_4_helper_function", methods=['POST'])
def tab_4_helper_function():
	# valid, validation_error = validation.validate_tab_4(request.form)
	# if not valid:
	# 	return validation_error, 500
	mgf_txt_write_dir_path = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)
	mgf_read_dir_path = request.form['mgfReadDirPath']

	try:
		os.makedirs(mgf_txt_write_dir_path)
	except:
		#mgf.txt directory probably already there
		pass
		
	if not os.path.isdir(mgf_txt_write_dir_path):
		return "selected_mgf_txt directory could not be created", 500
	
	error = mgf_select_one.plain_parse(mgf_read_dir_path, mgf_txt_write_dir_path)

	if error:
		print("error in plain_parse")
		return error, 500
	else:
		return "mgf_select plain parse ran successfully"

@app.route("/plain_parse_xtandem_combine_with_mgf", methods=['POST'])
def plain_parse_xtandem_combine_with_mgf():
	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	geneFile = request.form.getlist('geneFile[]')
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')
	timestamp = request.form['timestamp']

	mgf_txt_foldername = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)

	mgf_read_dir_path = request.form['mgfReadDirPath']
	mgf_list = ",".join(utility.get_mgf_files_given_directory(mgf_read_dir_path))

	a = call_xml_parser.plain_parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, geneFile, mgf_txt_foldername, unacceptable_mods, timestamp, mgf_list)

	if a:
		print("Error in tab 4. Trying cleanup now, either way returning error")
		try:
			clean_up_after_tab_2()
		finally: #In case it breaks
			return a, 500
	else:
		return "Looks good"

@app.route("/fast_parse", methods=['POST'])
def fast_parse():
	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	geneFile = request.form.getlist('geneFile[]')
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')
	timestamp = request.form['timestamp']

	xml_folder = makeFolderNames.construct_fast_parse_folder_path(request.form)

	a = call_xml_parser.fast_parse_xtandem(xml_read_path, log_error_threshold, geneFile, unacceptable_mods, timestamp)

	if a:
		print("Error in tab 7. Trying cleanup now, either way returning error")
		try:
			print("Cleaning up")
		finally: #In case it breaks
			return a, 500
	else:
		return "Looks good"

@app.route("/tab_2_helper_function", methods=['POST'])
def tab_2_helper_function():
	valid, validation_error = validation.validate_tab_2(request.form)
	if not valid:
		return validation_error, 500

	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	reporter_type = request.form['reporterIonType']
	geneFile = request.form.getlist('geneFile[]')
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')
	normalize_intensities = request.form.getlist('normalizeIntensities')
	timestamp = request.form['timestamp']
	keep_na = request.form['writeAllSpectra']

	if request.form['mgfOperationToPerform'] == '1':
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]
		previous_ion_type = check_if_previous_summary_exists_and_get_reporter_type(mgf_txt_foldername)
		if not previous_ion_type:
			return "No previous summary found.  Please reselect reporters and keep the summary.", 500
		if previous_ion_type != reporter_type:
			return "Ion type from summary does not match current selection.", 500

	mgf_read_dir_path = request.form['mgfReadDirPath']
	mgf_list = ",".join(utility.get_mgf_files_given_directory(mgf_read_dir_path))

	if should_use_unacceptable == "1":
		unacceptable_mods = []

	a = call_xml_parser.parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, reporter_type, geneFile, mgf_txt_foldername, unacceptable_mods, normalize_intensities, timestamp, keep_na, mgf_list)

	if a:
		print("Error in tab 2. Cleaning up.")
		try:
			clean_up_after_tab_2()
		finally: #In case it breaks
			return a, 500
	else:
		return "Looks good"

@app.route("/tab_1_helper_function", methods=['POST'])
def tab_1_helper_function():
	#valid, validation_error = validation.validate_tab_1(request.form)
	# if not valid:
	# 	print("Not valid: error is " + str(validation_error))
	# 	return validation_error, 500
	mgf_read_dir_path = request.form['mgfReadDirPath']
	reporter_type = request.form['reporterIonType']
	inverse_file = request.form['reporterInverseFiles']
	min_intensity = request.form['minIntensity']
	min_reporters = request.form['minReporters']
	mgf_file_list = request.form['mgfFileList']
	mgf_file_list = literal_eval(mgf_file_list)

	perform_recalibration = request.form['performRecalibration']
	should_select = request.form['mgfOperationToPerform']

	mz_error = request.form['mzError']

	mz_error_initial_run = request.form['mzErrorInitialRun']
	mz_error_recalibration = request.form['mzErrorRecalibration']

	#Check/make directories 
	if should_select == "1":
		mgf_write_dir_path = makeFolderNames.construct_selected_mgf_path(request.form)
	else:
		mgf_write_dir_path = "invalid"
		
	mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)

	try:
		os.makedirs(mgf_txt_write_dir_path)
	except:
		# selected_mgf_txt directory probably already there"
		pass
	if not os.path.isdir(mgf_txt_write_dir_path):
		return "selected_mgf_txt directory could not be created", 500

	if should_select == '1':
		try:
			os.makedirs(mgf_write_dir_path)
		except:
			#MGF direcotry already found
			pass
		if not os.path.isdir(mgf_write_dir_path):
			return "selected_mgf directory could not be created", 500	

	if perform_recalibration == '1':
		error = mgf_select_one.select_only_one_recalibrate(mgf_read_dir_path, \
			mgf_write_dir_path, mgf_txt_write_dir_path, mz_error_initial_run,\
			reporter_type, inverse_file, min_intensity, min_reporters, should_select, \
			mz_error_recalibration, mgf_file_list)
		if error:
			print("Error in Selection w/ Recalibration")
			print(error)
			if os.path.isdir(mgf_txt_write_dir_path):
				shutil.rmtree(mgf_txt_write_dir_path)
			if os.path.isdir(mgf_write_dir_path):
				shutil.rmtree(mgf_write_dir_path)
			return error, 500
		else:
			return("MGF Selection w/ Recalibration completed successfully")

	else:
		# Can do this because both were validated
		error = mgf_select_one.select_only_one(mgf_read_dir_path,\
			mgf_write_dir_path, mgf_txt_write_dir_path, mz_error, reporter_type, \
			inverse_file, min_intensity, min_reporters, should_select, mgf_file_list)
		if error:
			print("Error in Selection")
			print(error)
			if os.path.isdir(mgf_txt_write_dir_path):
				shutil.rmtree(mgf_txt_write_dir_path)
			if os.path.isdir(mgf_write_dir_path):
				shutil.rmtree(mgf_write_dir_path)
			return error, 500
		else:
			return("MGF Selection completed successfully")

	return "MGF Selection completed successfully"

@app.route("/check_if_gpm_merge_already_exists", methods=["POST"])
def check_if_gpm_merge_already_exists():
	valid, validation_error = validation.validate_check_for_final_product(request.form)
	if not valid:
		return validation_error, 500

	try:
		if request.form["mgfOperationToPerform"] == "1":
			#if we need to create the .reporter folder, it can't already exist
			return {existsAlready : False}

		write_destination_filename = makeFolderNames.construct_merged_gpm_reporter_filename(request.form)
		
		if os.path.isfile(write_destination_filename):
			print("There is an existing merged GPM-reporter ion file.  Please delete or rename existing file in selected reporter ion folder and run again.")
			return "There is an existing merged GPM-reporter ion file.  Please delete or rename existing file in selected reporter ion folder and run again.", 500 
		else:
			return "Does not already exist." #That means true

	except:
		#error creating the foldername. At least that means it doesn't exist
		return "Does not exist already" #That means true

@app.route("/getMGFFiles", methods=['POST'])
def getMGFFiles():
	try:
		mgf_read_dir_path = str(request.form['mgfReadDirPath'])
		if utility.check_if_summary_exists(mgf_read_dir_path):
			return "Temp summary file still exists, remove and rerun", 500
		files = utility.get_mgf_files_given_directory(mgf_read_dir_path)
		text = json.dumps(files)
		return text
	except:
		return "Error selecting mgf files, make sure you have a proper mgf directory name", 500

@app.route("/createInverseFiles", methods=['POST'])
@nocache
def createInverseFiles():
	post_obj = request.get_json()
	reporter_type = post_obj['reporterType']
	inverse_string = handle_inverse_posts.create_inverse_file(post_obj)
	return inverse_string

@app.route("/plainCountProteins", methods=['POST'])
@nocache
def plainCountProteins():

	valid, validation_error = validation.validate_tab_6(request.form)
	if not valid:
		return validation_error, 500

	plain_parsed_file = request.form['plainParseReadPath']
	# count_uniques = request.form['countUniques']
	timestamp = request.form['timestamp']
	output_dir = request.form['outDirPath']

	result, error = plaincount.count_proteins(plain_parsed_file, output_dir, timestamp)
	if not error:
		return result, 400
	else:
		return result

@app.route("/mergeMS2MS3", methods=['POST'])
@nocache
def mergeMS2MS3():
	
	valid, validation_error = validation.validate_tab_5(request.form)
	if not valid:
		return validation_error, 500

	ms2_ms3_directory = request.form['ms2ms3directory']
	mz_cutoff = request.form['mzCutoff']
	ms2_suffix = request.form['ms2Suffix']
	ms3_suffix = request.form['ms3Suffix']
	output_dir = request.form['outDirPath']
	timestamp = request.form['timestamp']

	result, error = mergemgf.merge_ms2_ms3(ms2_ms3_directory, mz_cutoff, ms2_suffix, ms3_suffix, output_dir, timestamp)

	if not error:
		return result, 400
	else:
		this_dir = os.path.dirname(os.path.realpath(__file__))
		suffix_path = os.path.join(this_dir, "SCRIPTS_FOR_GUI", "settings_files", "ms2ms3_suffix.txt")
		with open(suffix_path, "w") as suffix_file:
			suffix_file.write(ms2_suffix+"\n")
			suffix_file.write(ms3_suffix)
		return result

@app.route("/ms2ms3suffix", methods=['POST'])
@nocache
def get_ms2_ms3_suffix():
	ms2_suffix = get_ms2_suffix()
	ms3_suffix = get_ms3_suffix()
	return json.dumps([ms2_suffix.rstrip(), ms3_suffix.rstrip()])

@app.route("/writeSummary", methods=['POST'])
@nocache
def writeSummary():
	timestamp = request.form['timestamp']
	mgf_intensity_regex = re.compile("MS1 intensity: (.+)")
	mgf_filename_regex = re.compile("(.+.mgf)")

	if request.form['mgfOperationToPerform'] == '1':
		if 'plain_parse' in request.form and request.form['plain_parse'] == "1":
			mgf_txt_write_dir_path = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)
		elif 'fast_parse' in request.form and request.form['fast_parse'] == "1":
			mgf_txt_write_dir_path = makeFolderNames.construct_fast_parse_folder_path(request.form)
		else:
			mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)

	else:
		if 'xmlReadPath' in request.form:
			mgf_txt_write_dir_path = request.form['mgfTxtReadDirPath']
		else:
			mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)

	with open(join(mgf_txt_write_dir_path, 'GAILA_summary_'+timestamp+'.txt'), 'w') as out_file:
		out_file.write("GAILA Summary\n")
		out_file.write(timestamp+"\n\n")
		for option, value in request.form.items():
			if option.startswith("unacceptableMods"):
				if "assignUnacceptableModifications" in request.form and request.form["assignUnacceptableModifications"] == "1":
					continue
				else:
					list_of_mods = request.form.getlist('unacceptableMods[]')
					if len(list_of_mods) == 0:
						out_file.write("FlaggedMods - None selected\n")
					else:
						out_file.write(get_detailed_summary(option, list_of_mods))
			elif option.startswith("geneFile[]"):
				list_of_genefiles = request.form.getlist('geneFile[]')
				if len(list_of_genefiles) == 0:
					continue
				else:
					out_file.write(get_detailed_summary(option, list_of_genefiles))
			elif option.startswith("mgfOperationToPerform") and "fast_parse" in request.form:
				continue
			elif option.startswith("mgfOperationToPerform") and "plain_parse" in request.form:
				continue
			elif option.startswith("mgfTxtReadDirPath") and request.form["mgfOperationToPerform"] == "1":
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("minIntensity") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("minReporters") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif "mgfTxtReadDirPath" in request.form and option == "mzError" and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("mzErrorRecalibration") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("mzErrorInitialRun") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("performRecalibration") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif "mgfTxtReadDirPath" in request.form and option.startswith("mgfReadDirPath") and request.form["mgfOperationToPerform"] == "0" and request.form["mgfTxtReadDirPath"] != "":	
				continue
			elif option.startswith("mzErrorRecalibration") and request.form["performRecalibration"] == "0":
				continue
			elif option.startswith("mzErrorInitialRun") and request.form["performRecalibration"] == "0":
				continue
			elif option.startswith("mgfTxtReadDirPath") and request.form["mgfOperationToPerform"] == "1":
				continue
			elif option == "mzError" and request.form["performRecalibration"] == "1":
				continue
			elif option == "timestamp":
				continue
			elif option == "concat":
				continue
			else:
				out_file.write(get_detailed_summary(option, value))

		reporters = ""
		intensity_totals = []
		if os.path.isfile(join(mgf_txt_write_dir_path, 'intensity_summary.txt')):
			out_file.write("\nTotal Reporter Ion and MS1 Intensities per MGF file\n----------\n")
			line_found = False	
			with open (join(mgf_txt_write_dir_path, 'intensity_summary.txt')) as summary_file:
				for summary_line in summary_file:
					if not line_found:
						line_found = True
						summary_line = summary_line.lstrip()
						reporters = summary_line
						if reporters == "TMT10-126\tTMT10-127\tTMT10-127\tTMT10-128\tTMT10-128\tTMT10-129\tTMT10-129\tTMT10-130\tTMT10-130\tTMT10-131\n":
							reporters = "TMT10-126\tTMT10-127N\tTMT10-127C\tTMT10-128N\tTMT10-128C\tTMT10-129N\tTMT10-129C\tTMT10-130N\tTMT10-130C\tTMT10-131\n"
							summary_line = reporters
						if reporters == "TMT11-126\tTMT11-127\tTMT11-127\tTMT11-128\tTMT11-128\tTMT11-129\tTMT11-129\tTMT11-130\tTMT11-130\tTMT11-131\tTMT11-131\n":
							reporters = "TMT11-126\tTMT11-127N\tTMT11-127C\tTMT11-128N\tTMT11-128C\tTMT11-129N\tTMT11-129C\tTMT11-130N\tTMT11-130C\tTMT11-131N\tTMT11-131C\n"
							summary_line = reporters
						if reporters == "TMT16-126\tTMT16-127\tTMT16-127\tTMT16-128\tTMT16-128\tTMT16-129\tTMT16-129\tTMT16-130\tTMT16-130\tTMT16-131\tTMT16-131\tTMT16-132\tTMT16-132\tTMT16-133\tTMT16-133\tTMT16-134":
							reporters = "TMT16-126\tTMT16-127N\tTMT16-127C\tTMT16-128N\tTMT16-128C\tTMT16-129N\tTMT16-129C\tTMT16-130N\tTMT16-130C\tTMT16-131N\tTMT16-131C\tTMT16-132N\tTMT16-132C\tTMT16-133N\tTMT16-133C\tTMT16-134N"
							summary_line = reporters
						num_reporters = len(reporters.split("\t"))
						#initialize the intensity_totals array to all zeros
						intensity_totals = [0 for i in range(num_reporters)]

			os.remove(join(mgf_txt_write_dir_path, 'intensity_summary.txt'))
		
		if os.path.isfile(join(mgf_txt_write_dir_path, 'mgf_summary.txt')):
			out_file.write("MGF File\tMS1 Intensity\t"+reporters)
			with open(join(mgf_txt_write_dir_path, 'mgf_summary.txt')) as mgf_summary_file:
				for mgf_line in mgf_summary_file:
					if mgf_line != "" or mgf_line != "\n":
						out_file.write(mgf_line)
						#skip the mgf name and ms1 intensity and create a list of the intensities for this mgf
						numeric_intensities = [int(n) for n in mgf_line.split('\t')[2:]]
						#add each of these intensities to the total intensity
						intensity_totals = [x+y for x,y in zip(intensity_totals, numeric_intensities)]
				out_file.write("\nTotal Reporter Ion Intensities\n----------\n")
				out_file.write(reporters)
				out_file.write('\t'.join([str(val) for val in intensity_totals]))
				
			os.remove(join(mgf_txt_write_dir_path, 'mgf_summary.txt'))

	if 'concat' in request.form:
		concat = request.form['concat']
		if concat == "1":
			mgf_directory = makeFolderNames.construct_reporter_folder_path(request.form)
			all_files = glob.glob(join(mgf_directory, "*.reporter"))
			df_from_each_file = (pd.read_csv(f) for f in all_files)
			concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
			concatenated_df.to_csv(join(mgf_directory, "rep_sel_"+timestamp+".reporter"), index=False)

	makeFolderNames.rename_folders(request.form)
	if os.path.isdir(join(sys.path[0], "Temp")):
		shutil.rmtree(join(sys.path[0], "Temp"))
	utility.print_timestamp("GAILA processing - FINISHED\n" )
	return "Summary complete."

@app.route("/reporterIonType", methods=['POST'])
@nocache
def get_inverse_filenames_from_ion_type():
	ion_type = str(request.form["ionType"])
	return json.dumps(utility.get_inverse_filenames_from_ion_type(ion_type))

def clean_up_after_tab_2():
	print("cleaning up possible leaked files if there was an error.")
	# tempdest = filename + "_with_duplicates_deleted" is a line in combine_xml_mgf where
	# we make temporary files.
	# testing_filename = mgf_txt_filename.split('.reporter')[0] + '_duplicate_sorted' + '.reporter'
	# is another.
	xml_read_path = request.form['xmlReadPath']
	xml_directory_path = utility.xml_dirname_from_filename(xml_read_path)
	if not xml_directory_path:
		print("Problem with XML directory while cleaning tab 2")
		return
	if (os.path.isfile(xml_read_path + '.txt')):
		os.remove(xml_read_path + '.txt')

	if (os.path.isdir(xml_directory_path)):
		try:
			shutil.rmtree(xml_directory_path)
		except Exception:
			print("Error removing all files.  Possibly read-only files in folder.")

	mgf_txt_foldername = None
	if request.form['mgfOperationToPerform'] == '1':
		#Recalculating MGF folder name
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]
	if not mgf_txt_foldername:
		#MGF txt folder missing.  Nothing to delete.
		return

	mgf_write_dir_path = makeFolderNames.construct_selected_mgf_path(request.form)
	mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)
	if os.path.isdir(mgf_txt_write_dir_path):
		shutil.rmtree(mgf_txt_write_dir_path)
	if os.path.isdir(mgf_write_dir_path):
		shutil.rmtree(mgf_write_dir_path)

	for item in os.listdir(mgf_txt_foldername):
		full_name = join(mgf_txt_foldername, item)
		print("Cleaning up: " + full_name)
		if os.path.isfile(full_name):
			if full_name.ends_with('_with_duplicates_deleted'):
				os.remove(full_name)
				continue
			if full_name.ends_with('_duplicate_sorted.reporter'):
				os.remove(full_name)
				continue
			if full_name.ends_with('_PLACEHOLDER'):
				os.remove(full_name)
				continue
			if full_name.ends_with('intensity_summary.txt'):
				os.remove(full_name)
				continue
	return

def check_if_previous_summary_exists_and_get_reporter_type(reporter_folder):
	ion_type = ""
	mgf_line_found = False
	start_writing_out = False
	for item in os.listdir(reporter_folder):
		if os.path.splitext(item)[0].startswith("GAILA_summary"):
			with open(join(reporter_folder, item), "r") as summary:
				summary_lines = summary.readlines()
				with open(join(reporter_folder, "intensity_summary.txt"),"w") as intensity_summary, \
					open(join(reporter_folder, "mgf_summary.txt"),"w") as mgf_summary:
					for count, line in enumerate(summary_lines):
						ion_type_search = re.search("reporterIonType - (.*)", line)
						if "Total Reporter Ion Intensities" in line and start_writing_out:
							intensity_summary.write(summary_lines[count+2])
							break
						elif start_writing_out and line.strip():
							mgf_summary.write(line)
						elif "MGF File\tMS1 Intensity" in line:
							start_writing_out = True
						elif ion_type_search:
							ion_type = ion_type_search.group(1)
						else:
							continue
				return ion_type
	return None

def get_detailed_summary(option, value):
	if option == "performRecalibration":
		if value == "1":
			return option + " - Perform recalibration\n"
		else:
			return option + " - DO NOT Perform recalibration\n"
	elif option == "mgfOperationToPerform":
		if value == "0":
			return option + " - Only Extract reporter ion intensities\n"
		else:
			return option + " - Extract reporter ion intensities and select viable spectra\n"
	elif option == "normalizeIntensities":
		if value == "0":
			return option + " - Normalize each report ion to its own total intensity\n"
		else:
			return option + " - Do not normalize report ions\n"
	elif option == "geneFile[]":
		return "Gene Files - " + ", ".join(value)+"\n"
	elif option == "unacceptableMods[]":
		mods = [utility.get_modification_dict()[mod] for mod in value]
		return "FlaggedMods - " + ", ".join(mods)+"\n"
	elif option == "assignUnacceptableModifications":
		if value == "0":
			return "Flag modifications – Yes\n"
		else:
			return "Flag modifications – No\n"
	elif option == "mgfTxtReadDirPath":
		if value == "":
			return ""
		else:
			return option + " - " + value+'\n'
	elif option == "plain_parse":
		if value == "1":
			return option + " - Plain parse MGF and XML\n"
		else:
			return ""
	elif option == "fast_parse":
		if value =="1":
			return option+ " - Fast parse XML without MGF\n"
		else:
			return ""
	elif option == "reporterIonType":
		return option + " - " + value + "\n"

	elif option == "reporterInverseFiles":
		ion_type_and_inverse = "InverseFile - " + value + "\n" "Inverse Values\n"
		this_dir = os.path.dirname(os.path.realpath(__file__))
		inv_path = join(this_dir, "SCRIPTS_FOR_GUI", "inverse_files", value)
		inverses = pd.read_table(inv_path, index_col=0)
		return ion_type_and_inverse + inverses.to_string() + "\n"

	elif option == "writeAllSpectra":
		if value == "0":
			return "WriteAllSpectra - No\n"
		else:
			return "WriteAllSpectra - Yes\n"

	elif option == "logErrorThreshold":
		return "WritePSMsPeptideExpectation <= " + value + "\n"

	elif option=="removeMGF":
		if value == "1":
			return "SaveFilteredMGF - Yes\n"
		else:
			return "SaveFilteredMGF - No\n"

	elif option == "removeReporters":
		if value == "1":
			return "SaveTemporaryReporterFiles - Yes\n"
		else:
			return "SaveTemporaryReporterFiles - No\n"
	else:
		return option + " - " + value+'\n'

def return_form_copy():
	to_return = {}
	for key in request.form:
		to_return[key] = request.form[key]
	return to_return	

def multiple_select_to_two_arrays(unacceptable_mods):
	long_string = ','.join(unacceptable_mods)
	good_array = long_string.split(',')
	two_d_array = [i.split('@') for i in good_array]
	mass_val_arr = [j[0] for j in two_d_array]
	mod_val_arr = [k[1] for j in two_d_array]
	return mass_val_arr, mod_val_arr

def get_ms2_suffix():
	this_dir = os.path.dirname(os.path.realpath(__file__))
	suffix_path = os.path.join(this_dir, "SCRIPTS_FOR_GUI", "settings_files", "ms2ms3_suffix.txt")
	with open(suffix_path) as suffix_file:
		ms2_suffix = suffix_file.readline()
		return ms2_suffix

def get_ms3_suffix():
	this_dir = os.path.dirname(os.path.realpath(__file__))
	suffix_path = os.path.join(this_dir, "SCRIPTS_FOR_GUI", "settings_files", "ms2ms3_suffix.txt")
	with open(suffix_path) as suffix_file:
		suffix_file.readline()
		ms3_suffix = suffix_file.readline()
		return ms3_suffix

if __name__ == "__main__":
	cli = sys.modules['flask.cli']
	cli.show_server_banner = lambda *x: None
	app.debug = False
	
	signal.signal(signal.SIGINT, signal_handler)

	#generate the default Archive folder on first run if none exists
	if not os.path.isdir(join(sys.path[0], "Archive")):
		os.makedirs(join(sys.path[0], "Archive"))

	#if a previous temp folder exists, delete it
	if os.path.isdir(join(sys.path[0], "Temp")):
		shutil.rmtree(join(sys.path[0], "Temp"))
	
	print("Welcome to GAILA")
	print("Currently running at http://127.0.0.1:5000/")
	print("Press Ctrl+C to quit\n")
	
	app.run(threaded=True, use_reloader=False)