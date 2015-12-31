from utility import *
import os
from os.path import join
import makeFolderNames

def validate_tab_2(form):
	# print "bizarrely printing request"
	# print request
	print "validating tab_2"
	print form
	try:
		print "going through options"
		mgf_read_dir_path = form['mgfReadDirPath']
		mgf_file_name = form['mgfFileName']
		reporter_type = form['reporterIonType']
		min_intensity = form['minIntensity']
		min_reporters = form['minReporters']

		print "got through first 5"

		perform_recalibration = form['performRecalibration']
		should_select = form['mgfOperationToPerform']

		print "got through options"

		mz_error = form['mzError']

		mz_error_initial_run = form['mzErrorInitialRun'];
		mz_error_recalibration = form['mzErrorRecalibration'];

		print "got through errors"

		print "got through all"


		print str(mgf_read_dir_path)

		if not os.path.isdir(str(mgf_read_dir_path)):
			print "mgf read directory path is not a directory"
			return False, "mgf read directory path is not a directory"

		print "isdirs"

		if not mgf_file_name.endswith('.mgf'):
			print "mgf file name doesn't end with .mgf, that's fishy"
			return False, "mgf file name doesn't end with .mgf, that's fishy"

		print "endswithmgf"




		if not validate_ion_type(reporter_type):
			print "not a valid ion type"
			return False, "not a valid ion type"

		print "validatedions"

		if not validate_int(min_reporters):
			print "min reporters is not a valid int"
			return False, "min reporters is not a valid int"

		print "validatedminreporters"

		if not validate_int(min_intensity):
			print "min intensity is not a valid int"
			return False, "min intensity is not a valid int"

		print "through most validations"


		if perform_recalibration != "0" and perform_recalibration != "1":
			print "could not determine whether to perform recalibration"
			return False, "could not determine whether to perform recalibration"

		print "validatedpoerfomrrecalibration"
		if perform_recalibration == "0" and not validate_int(mz_error):
			print "mz_error not valid int"
			return False, "mz_error not valid int"

		print "performrecal_0 checked"

		if perform_recalibration == "1":
		 	if not validate_int(mz_error_initial_run):
				print "mz_error initial not valid int"
				return False, "mz_error initial not valid int"
			if not validate_int(mz_error_recalibration):
				print "mz_error recalibration not valid int"
				return False, "mz_error recalibration not valid int"

		print "performrecal_1 checked"


		# I'll make the directories later, this isn't the place for that. Or, maybe it is.
		# Maybe I should make them somewhere else, and check here.


		mgf_read_path = join(mgf_read_dir_path, mgf_file_name)

		if not os.path.isfile(mgf_read_path):
			print "mgf path does not lead to file"
			return False, "mgf_path does not lead to a file"

		print "mgf_read_path checked"

		if should_select != "0" and should_select != "1":
			print "could not determine whether to select from mgf file, ask Sam"
			return False, "could not determine whether to select from mgf file, ask Sam"

		print "shouldselect checked"

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



		print "got through read path, returning true"
		return True, None

	except Exception as e:
		print "Missing form input"
		print "Exception: "
		print e
		return False, "Missing form input"


def validate_tab_5(form):
	# There's a LOT more to do here.
	print "validating tab_5"
	try:
		xml_read_path = form['xmlReadPath']
		log_error_threshold = form['logErrorThreshold']
		reporter_type = form['reporterIonType']
		geneFile = form['geneFile']
		mgf_operation_to_perform = form['mgfOperationToPerform']
		should_use_unacceptable = form['assignUnacceptableModifications']
		unacceptable_mods = request.form.getlist('unacceptableMods[]')

		if (not xml_read_path) or (not str(log_error_threshold)) or (not reporter_type) or (not geneFile):
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

		if mgf_operation_to_perform == "1":
			mgf_txt_foldername = makeFolderNames.construct_reporter_folder_path(form)
		if mgf_operation_to_perform == "0":
			mgf_txt_foldername = form['mgfTxtReadDirPath']
		if not os.path.isdir(mgf_txt_foldername):
			print "mgf_txt foldername doesn't exist for some reason"
			return False, "mgf_txt foldername doesn't exist for some reason"



		if not should_use_unacceptable or (should_use_unacceptable != "0" and should_use_unacceptable != "1"):
			print "should_use_unacceptable is bad"
			return False, "should_use_unacceptable is bad"


		# Now, I think it's pretty good.

		print "looks good you"
		return True, None

	except Exception as e:
		print "Missing form input"
		print "error: " + str(e)
		return False, "Missing form input"



