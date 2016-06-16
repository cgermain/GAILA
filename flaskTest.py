from flask import Flask, render_template, request, make_response
from functools import update_wrapper
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
from SCRIPTS_FOR_GUI import handle_inverse_posts
# from copy import copy
# from science_code import science
from SCRIPTS_FOR_GUI import makeFolderNames
import shutil


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
		# return "<div>OH HELLO</div>"
		true_inverse_files = utility.get_true_inverse_array()
		inverse_file_array = utility.get_inverse_files_array()
		return render_template('bad_inverse_names.html', true_inverse_files=true_inverse_files,\
			inverse_file_array=inverse_file_array)
	# Right now, the m,ain thing that might mess up is, if someone
	# messed with the names of the inverse files.

	return render_template('index_new.html')

@app.route("/tab", methods=['GET'])
@nocache
def tab():
	file_name = str(request.args.get('name')) + '.html'
	print "fetched " + str(file_name)
	gene_files = utility.get_gene_files_array()
	inverse_files = utility.get_inverse_files_array()
	return render_template(file_name, gene_files=gene_files,\
	 inverse_files=inverse_files)


@app.route("/tab_2_helper_function", methods=['POST'])
def tab_2_helper_function():
	# print request.form
	print "tab 5 helper function"
	valid, validation_error = validation.validate_tab_2(request.form)
	if not valid:
		return validation_error, 500

	xml_read_path = request.form['xmlReadPath']
	log_error_threshold = request.form['logErrorThreshold']
	reporter_type = request.form['reporterIonType']
	geneFile = request.form['geneFile']
	should_use_unacceptable = request.form['assignUnacceptableModifications']
	unacceptable_mods = request.form.getlist('unacceptableMods[]')

	if request.form['mgfOperationToPerform'] == '1':
		print "Looks like we had to select from the mgf folder before this, that means I'll recalculate the mgf_foldername"
		# mgf_txt_foldername = join(request.form['mgfReadDirPath'], 'selected_mgf_txt', '')
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]

	# should_use_unacceptable = request.form['assignUnacceptableModifications']
	# print "should_use_unacceptable: " + str(should_use_unacceptable)
	# unacceptable_mods = request.form.getlist('unacceptableMods[]')
	# print "unacceptable_mods: " + str(unacceptable_mods)
	if should_use_unacceptable == "1":
		unacceptable_mods = []


	# print "going to call parse_xtandem stuff from tab 5"

	a = call_xml_parser.parse_xtandem_combine_with_mgf(xml_read_path, log_error_threshold, reporter_type, geneFile, mgf_txt_foldername, unacceptable_mods)

	if a:
		print "Error in tab 5. Trying cleanup now, either way returning error"
		try:
			clean_up_after_tab_2()
		finally: #In case it breaks
			return a, 500
	else:
		return "Looks good"



@app.route("/tab_1_helper_function", methods=['POST'])
def tab_1_helper_function():
	# print request.form
	valid, validation_error = validation.validate_tab_1(request.form)
	# print valid
	# print validation_error
	if not valid:
		print "not valid! error!"
		print "Not valid, error is " + str(validation_error)
		return validation_error, 500
	# else:
	# 	print "validation passed, this is being printed inside of tab_1_helper_function"
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
	# print "accessed all of the variables"

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

	# print "made a directory maybe"
	if should_select == '1':
		try:
			os.makedirs(mgf_write_dir_path)
		except:
			print "mgf directory probably already there"
		if not os.path.isdir(mgf_write_dir_path):
			return "selected_mgf directory could not be created", 500	

		# Still ugly, but that's because it's complicated
	# print "maybe made another"


	if perform_recalibration == '1':
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
		print "calling mgf_select_no_recalibrate from 1"
		# I can do this because I checked for both in validation
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
	print "checking if gmp merge already exists"
	valid, validation_error = validation.validate_check_for_final_product(request.form)
	if not valid:
		return validation_error, 500

	try:
		if request.form["mgfOperationToPerform"] == "1":
			print "if we need to create the .reporter folder, it can't already exist"
			return {existsAlready : False}

		write_destination_filename = makeFolderNames.construct_merged_gpm_reporter_filename(request.form)
		if os.path.isfile(write_destination_filename):
			print "There is an existing merged GPM-reporter ion file.  Please delete or rename existing file in selected reporter ion folder and run again."
			return "There is an existing merged GPM-reporter ion file.  Please delete or rename existing file in selected reporter ion folder and run again.", 500 
		else:
			print "file does not already exist."
			return "Does not already exist." #That means true
	except:
		print "error creating the foldername. At least that means it doesn't exist"
		return "Does not exist already" #That means true



@app.route("/getMGFFiles", methods=['POST'])
def getMGFFiles():
	try:
		mgf_read_dir_path = str(request.form['mgfReadDirPath'])
		files = utility.get_mgf_files_given_directory(mgf_read_dir_path)
		text = json.dumps(files)
		return text
	except:
		return "Error selecting mgf files, make sure you have a proper mgf directory name", 500


@app.route("/createInverseFiles", methods=['POST'])
@nocache
def createInverseFiles():
	print "createInverseFile called"
	post_obj = request.get_json()
	reporter_type = post_obj['reporterType']
	inverse_string = handle_inverse_posts.create_inverse_file(post_obj)
	print 'inverse_string'
	print inverse_string
	return inverse_string



def clean_up_after_tab_2():
	print "cleaning up possible leaked files, if there was an error somewhere."
	# tempdest = filename + "_with_duplicates_deleted" is a line in combine_xml_mgf where
	# we make temporary files.
	# testing_filename = mgf_txt_filename.split('.reporter')[0] + '_duplicate_sorted' + '.reporter'
	# is another.
	xml_read_path = request.form['xmlReadPath']
	print "xml_read_path: " + xml_read_path
	xml_directory_path = utility.xml_dirname_from_filename(xml_read_path)
	if not xml_directory_path:
		print "Something funky, stop for now"
		return
	if (os.path.isfile(xml_read_path + '.txt')):
		os.remove(xml_read_path + '.txt')

	if (os.path.isdir(xml_directory_path)):
		# I REALLY want to make sure this doesn't delete everything on somebodys computer.
		# Done, in xml_dirname_from_filename
		try:
			shutil.rmtree(xml_directory_path)
		except Exception:
			print "no luck, probably read-only files or something. There's nothing we can do about that."
	print "cleaned up xmldir, now for the temporary files in .reporter directory"
	mgf_txt_foldername = None
	if request.form['mgfOperationToPerform'] == '1':
		print "Looks like we had to select from the mgf folder before this, that means I'll recalculate the mgf_foldername"
		# mgf_txt_foldername = join(request.form['mgfReadDirPath'], 'selected_mgf_txt', '')
		mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(request.form)
	else:
		mgf_txt_foldername = request.form["mgfTxtReadDirPath"]
	if not mgf_txt_foldername:
		print "Something is wrong here, but anyways, nothing to delete"
		return

	for item in os.listdir(mgf_txt_foldername):
		full_name = os.path.join(mgf_txt_foldername, item)
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

	print "Cleaned up successfully"
	return





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
	# app.debug = True
	app.run()
  # app.run(processes=8, debug=True)
  
  # app.run()

