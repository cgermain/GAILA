from os.path import join
import os
from datetime import datetime

TIME_FORMAT =  "%m-%d-%Y_%H-%M-%S"

"""
SelectedMGFSpectra_Min(Field1)(Field2)ions_MinIntensity(Field3)_MassError(Field4)ppm
SelectedReporters_Min(Field1)(Field2)ions_MinIntensity(Field3)_MassError(Field4)ppm
SelectedReporters_Min(Field1)(Field2)ions_MinIntensity(Field3)_InitialMassError(Field4)ppm_RecalMassError(Field5)

Field1=minimum reporters with said intensity
Field2= value from reporter type field
Field3=Minimum Intensity per reporter
Field4=m/z error for initial runthrough
Field5=m/z error for initial runthrough

"""


def construct_selected_mgf_path(form):

	if form['performRecalibration'] == "0":
		a = "MGFSpectraSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_MassError" + str(form['mzError']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')
		return full_path

	elif form['performRecalibration'] == "1":
		a = "MGFSpectraSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_InitialMassError" + str(form['mzErrorInitialRun']) + \
			"ppm_RecalMassError" + str(form['mzErrorRecalibration']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')
		return full_path

	else:
		raise Exception("Did not catch anything, must be a bad input")


def construct_reporter_folder_path(form):
	if form['performRecalibration'] == "0":
		a = "ReportersSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_MassError" + str(form['mzError']) + "ppm"
		a = a.replace('.','-')

		full_path = join(form['mgfReadDirPath'], a, '')

		return full_path

	elif form['performRecalibration'] == "1":
		a = "ReportersSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
			"_MinIntensity" + str(form['minIntensity']) + "_InitialMassError" + str(form['mzErrorInitialRun']) + \
			"ppm_RecalMassError" + str(form['mzErrorRecalibration']) + "ppm"
		a = a.replace('.','-')
		
		full_path = join(form['mgfReadDirPath'], a, '')

		return full_path

	else:
		raise Exception("Did not catch anything, must be a bad input")


def construct_short_reporter_folder_path(form):
	timestamp = datetime.now().strftime(TIME_FORMAT)
	fullpath = join(form['mgfReadDirPath'], "ReporterSelect_"+timestamp , "")
	return fullpath


def construct_plain_parse_reporter_folder_path(form):
	a = os.path.splitext(os.path.basename(str(form['xmlReadPath'])))[0]+'_plain_parse'
	full_path = join(form['mgfReadDirPath'], a, '')
	return full_path


def construct_merged_gpm_reporter_filename(form):
	reporter_path = None
	if form['mgfOperationToPerform'] == '1':
		reporter_path = construct_reporter_folder_path(form)
	reporter_path = form['mgfTxtReadDirPath']
	parent_xml_basename = os.path.basename(os.path.normpath(form["xmlReadPath"]))
	parent_xml_filename = parent_xml_basename.rsplit('.', 1)[0]
	outfile_name = join(reporter_path, parent_xml_filename + '-pep-reporter-merged.txt')
	return outfile_name


def rename_folders(form):
	#TODO - pull timestamp in from end of runtime
	timestamp = datetime.now().strftime(TIME_FORMAT)

	if form['mgfOperationToPerform'] == '0':
		#tab 1 - select reporters
		if 'xmlReadPath' not in form:
			mgf_folder_name = construct_reporter_folder_path(form)
			new_mgf_folder_name = join(form['mgfReadDirPath'], "rep_sel_"+timestamp, '')
			os.rename(mgf_folder_name, new_mgf_folder_name)
			return
		#tab 2 - use pre extracted reporters
		else:
			# don't rename
			return
	else:
		#tab 1 - select reporters and make mgf
		if 'xmlReadPath' not in form:
			mgf_folder_name = construct_selected_mgf_path(form)
			new_mgf_folder_name = join(form['mgfReadDirPath'], "mgf_sel_"+timestamp, '')
			os.rename(mgf_folder_name, new_mgf_folder_name)
			reporter_folder_name = construct_reporter_folder_path(form)
			new_reporter_folder_name = join(form['mgfReadDirPath'], "rep_sel_"+timestamp, '')
			os.rename(reporter_folder_name, new_reporter_folder_name)
			return

		#tab 4 - plain parse
		if 'plain_parse' in form:
			reporter_folder_name = construct_plain_parse_reporter_folder_path(form)
			new_reporter_folder_name = join(form['mgfReadDirPath'], "plain_parse_"+timestamp, '')
			os.rename(reporter_folder_name, new_reporter_folder_name)
			return
		#tab 2 - use raw mgf
		else:
			mgf_folder_name = construct_selected_mgf_path(form)
			new_mgf_folder_name = join(form['mgfReadDirPath'], "mgf_sel_"+timestamp, '')
			os.rename(mgf_folder_name, new_mgf_folder_name)
			reporter_folder_name = construct_reporter_folder_path(form)
			new_reporter_folder_name = join(form['mgfReadDirPath'], "rep_sel_"+timestamp, '')
			os.rename(reporter_folder_name, new_reporter_folder_name)
			return