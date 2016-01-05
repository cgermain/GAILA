from flask import Flask, render_template, request
app = Flask(__name__)
from time import time
from SCRIPTS_FOR_GUI import mgf_select_one
# from SCRIPTS_FOR_GUI import helper
import json
from os.path import join
from SCRIPTS_FOR_GUI import combine_selected_mgf_files
from SCRIPTS_FOR_GUI import call_xml_parser
import os
from SCRIPTS_FOR_GUI import combine_xml_mgf
import math
from SCRIPTS_FOR_GUI import utility
from SCRIPTS_FOR_GUI import validation
# from copy import copy
# from science_code import science
from SCRIPTS_FOR_GUI import makeFolderNames

@app.route("/")
def main():
	# print render_template('index.html')
	return render_template('index_new.html')

@app.route("/tab", methods=['GET'])
def tab():
	# tab_num = request.args.get('num')
	# file_name = "tab_" + str(tab_num) + ".html"
	# print file_name
	file_name = str(request.args.get('name')) + '.html'
	# print "fetching gene_files"
	gene_files = utility.get_gene_files_array()
	inverse_files = utility.get_inverse_files_array()
	# print gene_files
	return render_template(file_name, gene_files=gene_files,\
	 inverse_files=inverse_files)


@app.route("/combine_mgf_files", methods=['POST'])
def combine_mgf_files():
	print "combine_mgf_files"
	mgf_read_path = str(request.form['mgfWriteDirPath'])
	merged_dir = join(mgf_read_path, "MERGED")
	print merged_dir
	if not os.path.exists(merged_dir):
		print "Going to make a directory now"
		os.mkdir(merged_dir)
		print "Directory Made"
	else:
		print "Path exists already?"

	mgf_write_path = join(merged_dir, "MERGED.mgf")

	print "MGFWRITEPATH: " + str(mgf_write_path)
	error = combine_selected_mgf_files.concat_mgf_files_given_dirname(mgf_write_path, mgf_read_path)
	if error:
		return error, 500
	else:
		return "Combined"
	
@app.route("/combine_mgf_txt_files", methods=['POST'])
def combine_mgf_txt_files():
	print "combine_mgf_txt_files"
	mgf_read_path = str(request.form['mgfWriteDirPath'])
	merged_dir = join(mgf_read_path, "MERGED")
	print merged_dir
	if not os.path.exists(merged_dir):
		os.mkdir(merged_dir)

	mgf_write_path = join(merged_dir, "MERGED.reporter")
	error = combine_selected_mgf_files.concat_mgf_txt_files_given_dirname(mgf_write_path, mgf_read_path)
	# return "GOOD JOB DOOD"
	if error:
		return error, 500
	else:
		return "Combined"

@app.route("/tab_5_helper_function", methods=['POST'])
def tab_5_helper_function():
	# print request.form
	print "tab 5 helper function"
	valid, validation_error = validation.validate_tab_5(request.form)
	if not valid:
		return validation_error, 500

	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	reporter_type = request.form['reporterIonType']
	geneFile = request.form['geneFile']
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')

	print "parsed form"

	if request.form['mgfOperationToPerform'] == '1':
		print "Looks like we had to select from the mgf folder before this, that means I'll recalculate the mgf_foldername"
		# mgf_txt_foldername = join(request.form['mgfReadDirPath'], 'selected_mgf_txt', '')
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]

	print "parsed form more"

	# should_use_unacceptable = request.form['assignUnacceptableModifications']
	print "should_use_unacceptable: " + str(should_use_unacceptable)
	# unacceptable_mods = request.form.getlist('unacceptableMods[]')
	print "unacceptable_mods: " + str(unacceptable_mods)
	if should_use_unacceptable == "1":
		unacceptable_mods = []


	print "going to ball parse_xtandem stuff from tab 5"

	
	a = call_xml_parser.parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, reporter_type, geneFile, mgf_txt_foldername, unacceptable_mods)

	if a:
		return a, 500
	else:
		return "Looks good"



@app.route("/tab_2_helper_function", methods=['POST'])
def tab_2_helper_function():
	print request.form
	valid, validation_error = validation.validate_tab_2(request.form)
	print valid
	print validation_error
	if not valid:
		print "not valid! error!"
		print "Not valid, error is " + str(validation_error)
		return validation_error, 500
	else:
		print "validation passed, this is being printed inside of tab_2_helper_function"
	# Wow,  that's so much better.
	# Now, to make the values.

	# I'm pretty confident about this, so I'll move on for now.

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

	#Now, to check/make directories 
	print "accessed all of the variables"

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
		print "mgf.txt directory probably already there"
	if not os.path.isdir(mgf_txt_write_dir_path):
		return "selected_mgf_txt directory could not be created", 500

	print "made a directory maybe"
	if should_select == '1':
		try:
			os.makedirs(mgf_write_dir_path)
		except:
			print "mgf directory probably already there"
		if not os.path.isdir(mgf_write_dir_path):
			return "selected_mgf directory could not be created", 500	

		# Still ugly, but that's because it's complicated
	print "maybe made another"


	if perform_recalibration == '1':
		# pass
		print "calling perform_recalibration from 1"
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
		print "calling perform_recalibration from 1"
		# I can do this because I checked for both in validation
		error = mgf_select_one.select_only_one(mgf_read_path, \
			mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, \
			min_intensity, min_reporters, should_select)
		if error:
			print "error in mgf_select_no_recalibrate"
			return error, 500
		else:
			return "mgf_select without recalibration run successfully"



@app.route("/tab_3_function", methods=['POST'])
def tab_3_function():
	print "HANDLE TAB 3"
	xml_read_path = str(request.form['xmlReadPath'])
	# print xml_read_path
	try:
		threshold = int(request.form['threshold'])
		threshold = str(round(threshold / 100.0, 2))
	except ValueError:
		print "bad threshold value"
		return "ERROR: Bad Threshold Value", 500
	try:
		labelMass = str(int(request.form['labelMass']))
	except ValueError:
		print "bad labelMass value"
		return "ERROR: Bad Label Mass Value", 500
	# print labelMass
	geneFile = str(request.form['geneFile'])
	a = call_xml_parser.parse_xtandem(xml_read_path, threshold, labelMass, geneFile)
	to_return =  "Return from parse_xtandem: " + str(a)
	if a:
		return a, 500
	print to_return
	return to_return

@app.route("/combine_parsed_xml_with_parsed_mgf", methods=["POST"])
def combine_parsed_xml_with_parsed_mgf():
	print "COMBINING PARSED XML WITH PARSED MGF"
	mgf_selected_path = request.form['mgfSelectedPath']
	if not mgf_selected_path:
		return "Error: mgf_selected_path is required", 500
	if not os.path.isdir(mgf_selected_path):
		return "Error: mgf_selected_path is not a directory", 500
	xml_directory_path = request.form['xmlDirectoryPath']
	if not xml_directory_path:
		return "Error: xml_directory_path is required", 500
	if not os.path.isdir(xml_directory_path):
		return "Error: mgf_selected_path is not an existing directory", 500
	reporter_type = request.form['reporterIonType']
	if not reporter_type:
		return "Error: No reporter-type specified", 500
	print "All good so far"
	a = combine_xml_mgf.combine_parsed_xml_mgf(mgf_selected_path, xml_directory_path, reporter_type)
	if a:
		print a
		return a, 500
	return "Looking good"



@app.route("/getMGFFiles", methods=['POST'])
def getMGFFiles():
	try:
		mgf_read_dir_path = str(request.form['mgfReadDirPath'])
		files = utility.get_mgf_files_given_directory(mgf_read_dir_path)
		text = json.dumps(files)
		return text
	except:
		return "Error selecting mgf files, make sure you have a proper mgf directory name", 500



@app.route("/submitForm", methods=['POST'])
def submitForm():
	t_1 = time()
	while time() - t_1 < 1:
		i = 0

	print "yoyoyo"
	return "<div>Hello you</div>"	

@app.route("/secondSubmit", methods=['POST'])
def secondSubmit():

	t_1 = time()
	while time() - t_1 < 2:
		i = 0
	print "oyoyoyo"
	# return {'html' : "<div>Submitted</div>"}
	return "<div>Goodbye you</div>"



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
  app.run()
  # app.run(processes=8, debug=True)
  
  # app.run()

