from flask import Flask, render_template, request, make_response
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

TIME_FORMAT =  "%Y-%m-%d_%H-%M-%S"

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

print "Welcome to IDEAA"
print "Currently running at http://127.0.0.1:5000/"
print "Press Ctrl+C to quit"

def nocache(f):
	def new_func(*args, **kwargs):
		resp = make_response(f(*args, **kwargs))
		resp.cache_control.no_cache = True
		return resp
	return update_wrapper(new_func, f)

@app.route("/")
@nocache
def main():
	if not utility.inverse_array_is_correct():
		true_inverse_files = utility.get_true_inverse_array()
		inverse_file_array = utility.get_inverse_files_array()
		return render_template('bad_inverse_names.html', true_inverse_files=true_inverse_files,\
			inverse_file_array=inverse_file_array)

	return render_template('index_new.html')

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
	valid, validation_error = validation.validate_tab_4(request.form)
	if not valid:
		return validation_error, 500

	mgf_txt_write_dir_path = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)
	mgf_file_name = request.form['mgfFileName']
	mgf_read_dir_path = request.form['mgfReadDirPath']
	mgf_txt_write_path = join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter')
	mgf_read_path = join(mgf_read_dir_path, mgf_file_name)

	try:
		os.makedirs(mgf_txt_write_dir_path)
	except:
		#mgf.txt directory probably already there
		pass
		
	if not os.path.isdir(mgf_txt_write_dir_path):
		return "selected_mgf_txt directory could not be created", 500
	
	error = mgf_select_one.plain_parse(mgf_read_path, mgf_txt_write_path)

	if error:
		print "error in plain_parse"
		return error, 500
	else:
		return "mgf_select plain parse ran successfully"

@app.route("/plain_parse_xtandem_combine_with_mgf", methods=['POST'])
def plain_parse_xtandem_combine_with_mgf():
	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	geneFile = request.form['geneFile']
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')

	mgf_txt_foldername = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)

	a = call_xml_parser.plain_parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, geneFile, mgf_txt_foldername, unacceptable_mods)

	if a:
		print "Error in tab 4. Trying cleanup now, either way returning error"
		try:
			clean_up_after_tab_2()
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
	geneFile = request.form['geneFile']
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')
	normalize_intensities = request.form.getlist('normalizeIntensities')

	if request.form['mgfOperationToPerform'] == '1':
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]
		previous_ion_type = check_if_previous_summary_exists_and_get_reporter_type(mgf_txt_foldername)
		if not previous_ion_type:
			return "No previous summary found.  Please reselect reporters and keep the summary.", 500
		if previous_ion_type != reporter_type:
			return "Ion type from summary does not match current selection.", 500

	if should_use_unacceptable == "1":
		unacceptable_mods = []

	a = call_xml_parser.parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, reporter_type, geneFile, mgf_txt_foldername, unacceptable_mods, normalize_intensities)

	if a:
		print "Error in tab 2. Cleaning up."
		try:
			clean_up_after_tab_2()
		finally: #In case it breaks
			return a, 500
	else:
		return "Looks good"

@app.route("/tab_1_helper_function", methods=['POST'])
def tab_1_helper_function():
	valid, validation_error = validation.validate_tab_1(request.form)
	if not valid:
		print "Not valid: error is " + str(validation_error)
		return validation_error, 500

	mgf_read_dir_path = request.form['mgfReadDirPath']
	mgf_file_name = request.form['mgfFileName']
	reporter_type = request.form['reporterIonType']
	min_intensity = request.form['minIntensity']
	min_reporters = request.form['minReporters']

	perform_recalibration = request.form['performRecalibration']
	should_select = request.form['mgfOperationToPerform']

	mz_error = request.form['mzError']

	mz_error_initial_run = request.form['mzErrorInitialRun']
	mz_error_recalibration = request.form['mzErrorRecalibration']

	#Check/make directories 
	if should_select == "1":
		mgf_write_dir_path = makeFolderNames.construct_selected_mgf_path(request.form)
		mgf_write_path = join(mgf_write_dir_path, mgf_file_name)
	else:
		mgf_write_dir_path = "invalid"
		mgf_write_path = "invalid"
	mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)
	mgf_txt_write_path = join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter')
	mgf_read_path = join(mgf_read_dir_path, mgf_file_name)

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
		error = mgf_select_one.select_only_one_recalibrate(mgf_read_path, \
			mgf_write_path, mgf_txt_write_path, mz_error_initial_run,\
			reporter_type, min_intensity, min_reporters, should_select, \
			mz_error_recalibration)
		if error:
			print "error in mgf_select_with_recalibrate"
			return error, 500
		else:
			return "mgf_select run with recalibration"

	else:
		# Can do this because both were validated
		error = mgf_select_one.select_only_one(mgf_read_path, \
			mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, \
			min_intensity, min_reporters, should_select)
		if error:
			print "error in mgf_select_no_recalibrate"
			return error, 500
		else:
			return "mgf_select without recalibration run successfully"

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
			print "There is an existing merged GPM-reporter ion file.  Please delete or rename existing file in selected reporter ion folder and run again."
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
	plain_parsed_file = request.form['plainParseReadPath']
	count_uniques = request.form['countUniques']
	result, error = plaincount.count_proteins(plain_parsed_file, count_uniques)
	if not error:
		return result, 400
	else:
		return result

@app.route("/mergeMS2MS3", methods=['POST'])
@nocache
def mergeMS2MS3():
	
	valid, validation_error = validation.validate_tab_6(request.form)
	if not valid:
		return validation_error, 500

	ms2_ms3_directory = request.form['ms2ms3directory']
	mz_cutoff = request.form['mzCutoff']

	result, error = mergemgf.merge_ms2_ms3(ms2_ms3_directory, mz_cutoff)

	if not error:
		return result, 400
	else:
		return result

@app.route("/writeSummary", methods=['POST'])
@nocache
def writeSummary():
	timestamp = datetime.now().strftime(TIME_FORMAT)
	mgf_intensity_regex = re.compile("MS1 intensity: (.+)")
	mgf_filename_regex = re.compile("(.+.mgf)")

	if request.form['mgfOperationToPerform'] == '1':
		if 'plain_parse' in request.form and request.form['plain_parse'] == "1":
			mgf_txt_write_dir_path = makeFolderNames.construct_plain_parse_reporter_folder_path(request.form)
		else:
			mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)

	else:
		if 'xmlReadPath' in request.form:
			mgf_txt_write_dir_path = request.form['mgfTxtReadDirPath']+"\\"
		else:
			mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(request.form)

	with open(mgf_txt_write_dir_path+'IDEAA_summary_'+timestamp+'.txt', 'w') as out_file:
		out_file.write("IDEAA Summary\n")
		out_file.write(timestamp+"\n\n")
		for option, value in request.form.items():
			if option.startswith("unacceptableMods"):
				if "assignUnacceptableModifications" in request.form and request.form["assignUnacceptableModifications"] == "1":
					continue
				else:
					list_of_mods = request.form.getlist('unacceptableMods[]')
					out_file.write(get_detailed_summary(option, list_of_mods))
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
			else:
				out_file.write(get_detailed_summary(option, value))

		reporters = ""
		if os.path.isfile(mgf_txt_write_dir_path+'intensity_summary.txt'):
			out_file.write("\nTotal Reporter Ion Intensities\n----------\n")
			line_found = False	
			with open (mgf_txt_write_dir_path+'intensity_summary.txt') as summary_file:
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
					if summary_line != "" or summary_line != "\n":
						out_file.write(summary_line)
			os.remove(mgf_txt_write_dir_path+'intensity_summary.txt')
		
		if os.path.isfile(mgf_txt_write_dir_path+'mgf_summary.txt'):
			out_file.write("\n\nTotal Reporter Ion and MS1 Intensities per MGF file\n----------\n")
			out_file.write("MGF File\tMS1 Intensity\t"+reporters)
			with open (mgf_txt_write_dir_path+'mgf_summary.txt') as mgf_summary_file:
				for mgf_line in mgf_summary_file:
					if mgf_line != "" or mgf_line != "\n":
						out_file.write(mgf_line)

			os.remove(mgf_txt_write_dir_path+'mgf_summary.txt')

	makeFolderNames.rename_folders(request.form)
	return "Summary complete."

def clean_up_after_tab_2():
	print "cleaning up possible leaked files if there was an error."
	# tempdest = filename + "_with_duplicates_deleted" is a line in combine_xml_mgf where
	# we make temporary files.
	# testing_filename = mgf_txt_filename.split('.reporter')[0] + '_duplicate_sorted' + '.reporter'
	# is another.
	xml_read_path = request.form['xmlReadPath']
	xml_directory_path = utility.xml_dirname_from_filename(xml_read_path)
	if not xml_directory_path:
		print "Problem with XML directory while cleaning tab 2"
		return
	if (os.path.isfile(xml_read_path + '.txt')):
		os.remove(xml_read_path + '.txt')

	if (os.path.isdir(xml_directory_path)):
		try:
			shutil.rmtree(xml_directory_path)
		except Exception:
			print "Error removing all files.  Possibly read-only files in folder."

	mgf_txt_foldername = None
	if request.form['mgfOperationToPerform'] == '1':
		#Recalculating MGF folder name
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]
	if not mgf_txt_foldername:
		#MGF txt folder missing.  Nothing to delete.
		return

	for item in os.listdir(mgf_txt_foldername):
		full_name = os.path.join(mgf_txt_foldername, item)
		print "Cleaning up: " + full_name
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
		if os.path.splitext(item)[0].startswith("IDEAA_summary"):
			with open(reporter_folder+"\\"+item, "r") as summary:
				summary_lines = summary.readlines()
				with open(reporter_folder+"\intensity_summary.txt","w") as intensity_summary, \
					open(reporter_folder+"\mgf_summary.txt","w") as mgf_summary:
					for count, line in enumerate(summary_lines):
						ion_type_search = re.search("reporterIonType - (.*)", line)
						if start_writing_out and line.strip():
							mgf_summary.write(line)
						elif "--------" in line:
							mgf_line_found = True
						elif mgf_line_found and "MGF File" in line:
							start_writing_out = True
						elif "Total Reporter Ion Intensities" in line:
							intensity_summary.write(summary_lines[count+2])
							intensity_summary.write(summary_lines[count+3].strip())
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
			return option + " - Do not normalize report ions"
	elif option == "unacceptableMods[]":
		mods = [utility.get_modification_dict()[mod] for mod in value]
		return "unacceptableMods - " + ", ".join(mods)+"\n"
	elif option == "assignUnacceptableModifications":
		if value == "0":
			return option + " - Flag modifications\n"
		else:
			return option + " - Do not flag modifications\n"
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
	elif option == "reporterIonType":
		ion_type_and_inverse = option + " - " + value + "\n" "Inverse Values\n"
		this_dir = os.path.dirname(os.path.realpath(__file__))
		inv_path = join(this_dir, "SCRIPTS_FOR_GUI", "inverse_files", value + "-inv.txt")
		inverses = pd.read_table(inv_path, index_col=0)
		return ion_type_and_inverse + inverses.to_string() + "\n"
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

if __name__ == "__main__":
	app.debug = False
	app.run()