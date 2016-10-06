from os.path import join
import os


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

	print "constructing reporter folder path"
	print form

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

def construct_plain_parse_reporter_folder_path(form):

	print "constructing folder path for plain parse"
	#a = "MGFSpectraSelected_Min" + str(form['minReporters']) + str(form['reporterIonType']) + "ions" + \
	#	"_MinIntensity" + str(form['minIntensity']) + "_MassError" + str(form['mzError']) + "ppm"
	#a = a.replace('.','-')
	a = os.path.splitext(os.path.basename(str(form['xmlReadPath'])))[0]+'_plain_parse'
	full_path = join(form['mgfReadDirPath'], a, '')
	return full_path



def construct_merged_gpm_reporter_filename(form):
	reporter_path = None
	if form['mgfOperationToPerform'] == '1':
		reporter_path = construct_reporter_folder_path(form)
	reporter_path = form['mgfTxtReadDirPath']
	print "reporter path is: " + str(reporter_path)
	parent_xml_basename = os.path.basename(os.path.normpath(form["xmlReadPath"]))
	print "parent path basename is: " + str(parent_xml_basename)
	parent_xml_filename = parent_xml_basename.rsplit('.', 1)[0]
	print "parent path filename is: " + str(parent_xml_filename)
	outfile_name = join(reporter_path, parent_xml_filename + '-pep-reporter-merged.txt')
	print "outfile_name: " + str(outfile_name)
	return outfile_name




