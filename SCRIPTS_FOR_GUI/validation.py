from utility import *
import os
from os.path import join
import makeFolderNames
	
def validate_tab_2(form):
	print "validating tab_2"
	try:
		mgf_read_dir_path = form['mgfReadDirPath']
		mgf_file_name = form['mgfFileName']
		reporter_type = form['reporterIonType']
		min_intensity = form['minIntensity']
		min_reporters = form['minReporters']
		perform_recalibration = form['performRecalibration']
		should_select = form['mgfOperationToPerform']
		mz_error = form['mzError']
		mz_error_initial_run = form['mzErrorInitialRun']
		mz_error_recalibration = form['mzErrorRecalibration']
	except Exception as e:
		print "Field probably missing in tab 2"
		print form
		return False, "Missing form input in Tab 2 Helper Function"
	
	try:
		if (not mgf_read_dir_path) or (not mgf_file_name) or \
			 (not reporter_type) or (not min_intensity) or \
			 (not min_reporters) or (not perform_recalibration) or \
			 (not should_select):
			print "Field is missing"
			print form
			return False, "Field is missing"
	except Exception as e:
		print "Error here, field is most likely missing"
		print e
		return False, "Field is missing"

	try:
		print str(mgf_read_dir_path)

		if not os.path.isdir(str(mgf_read_dir_path)):
			print "mgf read directory path is not a directory"
			return False, "mgf read directory path is not a directory"

		if not mgf_file_name.endswith('.mgf'):
			print "mgf file name doesn't end with .mgf, that's fishy"
			return False, "mgf file name doesn't end with .mgf, that's fishy"

		if not validate_ion_type(reporter_type):
			print "not a valid ion type"
			return False, "not a valid ion type"

		if not validate_int(min_reporters):
			print "min reporters is not a valid int"
			return False, "min reporters is not a valid int"

		if not validate_float(min_intensity):
			print "min intensity is not a valid decimal"
			return False, "min intensity is not a valid decimal"

		if perform_recalibration != "0" and perform_recalibration != "1":
			print "could not determine whether to perform recalibration"
			return False, "could not determine whether to perform recalibration"

		if perform_recalibration == "0" and not validate_float(mz_error):
			print "mz_error not valid decimal"
			return False, "mz_error not valid decimal"

		if perform_recalibration == "1":
		 	if not validate_float(mz_error_initial_run):
				print "mz_error initial not valid decimal"
				return False, "mz_error initial not valid decimal"
			if not validate_float(mz_error_recalibration):
				print "mz_error recalibration not valid decimal"
				return False, "mz_error recalibration not valid decimal"


		mgf_read_path = join(mgf_read_dir_path, mgf_file_name)

		if not os.path.isfile(mgf_read_path):
			print "mgf path does not lead to file"
			return False, "mgf_path does not lead to a file"

		if should_select != "0" and should_select != "1":
			print "could not determine whether to select from mgf file, ask Sam"
			return False, "could not determine whether to select from mgf file, ask Sam"

		if should_select == "1":
			mgf_write_dir_path = makeFolderNames.construct_selected_mgf_path(form)
			mgf_write_path = join(mgf_write_dir_path, mgf_file_name)
			if os.path.isfile(mgf_write_path):
				print "path where we write selected mgf already has a file there"
				return False, "path where we write selected mgf already has a file there"

		mgf_txt_write_dir_path = makeFolderNames.construct_reporter_folder_path(form)
		mgf_txt_write_path = join(mgf_txt_write_dir_path, mgf_file_name + '.txt')
		if os.path.isfile(mgf_txt_write_path):
			print "path where we write mgf.txt already has a file there"
			return False, "path where we write mgf.txt already has a file there"



		print "tab_2 validated, returning true"
		return True, None

	except Exception as e:
		print "Error in validation"
		print "Exception: "
		print e
		return False, "Error in Tab 2 validation"


def validate_tab_5(form):
	print "validating tab_5"
	try:
		xml_read_path = form['xmlReadPath']
		log_error_threshold = form['logErrorThreshold']
		reporter_type = form['reporterIonType']
		geneFile = form['geneFile']
		mgf_operation_to_perform = form['mgfOperationToPerform']
		should_use_unacceptable = form['assignUnacceptableModifications']
		unacceptable_mods = form.getlist('unacceptableMods[]')

		if (not xml_read_path) or (not str(log_error_threshold)) or \
			 (not reporter_type) or (not geneFile) or (not mgf_operation_to_perform):
			print "Missing form input (one is blank)"
			return False, "Missing form input (one is blank)"

		if not xml_read_path.endswith('.xml'):
			print "xml file doesn't end with .xml, that's fishy"
			return False, "xml file doesn't end with .xml, that's fishy"

		if not os.path.isfile(xml_read_path):
			print "could not open xml file at that path"
			return False, "could not open xml file at that path"

		if not validate_error_input(log_error_threshold):
			print "threshold must be positive, and either a decimal or in scientific notation"
			return False, "threshold must be a decimal"

		if not validate_ion_type(reporter_type):
			print "Invalid reporter type"
			return False, "Invalid reporter type"

		# this_dir = os.path.dirname(os.path.realpath(__file__))
		if not validate_gene_file(geneFile):
			print "invalid gene file"
			return False, "Invalid gene file"

		if not mgf_operation_to_perform or (mgf_operation_to_perform != "0" and mgf_operation_to_perform != "1"):
			print "mgf_operation_to_perform is bad"
			return False, "Invalid mgfOperationToPerform"

		# The folder shouldn't exist if it's operation 1.

		if mgf_operation_to_perform == "1":
			mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(form)
		if mgf_operation_to_perform == "0":
			mgf_txt_foldername = form['mgfTxtReadDirPath']
		if not os.path.isdir(mgf_txt_foldername):
			print "mgf_txt foldername doesn't exist for some reason"
			return False, "mgf_txt foldername doesn't exist for some reason"

		reporter_files = get_reporter_files_given_directory(mgf_txt_foldername)
		if not len(reporter_files):
			print "The directory you returned doesn't have any .reporter files."
			return False, "The directory you returned doesn't have any .reporter files."



		if not should_use_unacceptable or (should_use_unacceptable != "0" and should_use_unacceptable != "1"):
			print "should_use_unacceptable is bad"
			return False, "should_use_unacceptable is bad"

		xml_txt_filename = xml_read_path + ".txt"
		if os.path.isfile(xml_txt_filename):
			print "an xml.txt file exists, probably as a remnant of a previous run. Please delete this and re-run"
			return False, "An xml.txt file exists, probably as a remnant of a previous run. Please delete this and re-run"

		xml_dir_name = xml_dirname_from_filename(xml_read_path)
		if not xml_dir_name:
			print "Something is funky with your xml_read_path."
			return False, "Something is off about your xml_read_path, please check it and try again"
		if os.path.isdir(xml_dir_name):
			print "the xml directory exists, probably as a remnant of a previous run. It only contains temporary files generated by the scripts, please delete this directory and then re-run."
			return False, "the xml directory exists, probably as a remnant of a previous run. It only contains temporary files generated by the scripts, please delete this directory and then re-run."

		print "tab_5 validated, returning true"
		return True, None

	except Exception as e:
		print "Missing form input"
		print "error: " + str(e)
		return False, "Missing form input"



def validate_check_for_final_product(form):
	print "validating check_if_gpm_merge_already_exists"
	try:
		mgf_operation_to_perform = form['mgfOperationToPerform']
		xml_read_path = form['xmlReadPath']
		if not xml_read_path:
			print "Bad form input, missing xml file path"
			return False, "Bad form input, missing xml file path"
		if not mgf_operation_to_perform:
			print "Bad form input, missing mgfOperationToPerform"
			return False, "Bad form input, missing mgfOperationToPerform"
		if not mgf_operation_to_perform or (mgf_operation_to_perform != "0" and mgf_operation_to_perform != "1"):
			print "mgf_operation_to_perform is bad"
			return False, "Invalid mgfOperationToPerform"

		return True, None
	except Exception as e:
		print "Missing form input"
		print "error: " + str(e)
		print form
		return False, "Missing form input"



