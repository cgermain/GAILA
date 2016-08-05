import os
from os.path import join
import shutil
from combine_xml_mgf import combine_parsed_xml_mgf 
from combine_xml_mgf import combine_plain_parsed_xml_mgf
import utility
import subprocess


def parse_xtandem_new(full_path_to_xml, error_threshold, reporter_type, genefile, unacceptable_mods):
	print "in parse_xtandem_new"
	this_dir = os.path.dirname(os.path.realpath(__file__))
	full_path_to_genefile = join(this_dir, 'gene_files', genefile)
	# if not os.path.isfile(full_path_to_xml):
	# 	print "XML ISN'T FILE"
	# 	return "XML ISN'T A FILE"
	# if not full_path_to_xml.endswith('.xml'):
	# 	print "XML FILENAME DOES NOT END WITH .xml"
	# 	return "XML FILENAME DOES NOT END WITH .xml"
	# if not os.path.isfile(full_path_to_genefile):
	# 	print "GENEFILE ISN'T FILE"
	# 	return "GENEFILE ISN'T FILE"

	# going on the assumption it's been validated
	mass_val_literal, mod_val_literal, reporter_mods_literal = utility.get_strings_from_unacceptable_mod_form(unacceptable_mods)
	# mass_val_literal, mod_val_literal = utility.multiple_select_to_two_perl_string_literals(unacceptable_mods)
	print "mass_literal: " + str(mass_val_literal)
	print "mod literal: " + str(mod_val_literal)
	print "reporter literal: " + str(reporter_mods_literal)

	label_mass = convert_reporter_to_label_mass(reporter_type)
	if not label_mass:
		print "bad label mass returned"
		return "reporter type not valid"
	# xml_dir_name = full_path_to_xml.partition('.xml')[0]
	# xml_dir_name = join(xml_dir_name, '')
	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	if os.path.isdir(xml_dir_name):
		print "xml directory already exists here, if you don't need it anymore try deleting it and running again"
		return "xml directory already exists here, if you don't need it anymore try deleting it and running again"

	xml_txt_filename = full_path_to_xml + '.txt'
	if os.path.isfile(xml_txt_filename):
		print "xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file"
		return "xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file"

	os.mkdir(xml_dir_name)
	print "created xml directory"

	# try:
	# 	float(error_threshold)
	# except:
	# 	return "error threshold could not be parsed into a float"
	perl_call_array=['perl', join(this_dir, 'parse_xtandem_sam.pl'), full_path_to_xml, \
		xml_dir_name, str(error_threshold), str(label_mass), full_path_to_genefile, \
		mass_val_literal, mod_val_literal, reporter_mods_literal]

	print perl_call_array



	# perl_call = "perl " + join(this_dir, 'parse_xtandem_sam.pl') + ' '+\
	# 	full_path_to_xml + ' ' + xml_dir_name + ' ' + str(error_threshold) + ' ' +\
	# 	str(label_mass) + ' ' + full_path_to_genefile + ' "' + mass_val_literal + \
	# 	'" "' + mod_val_literal + '"'

	# print perl_call
	a = subprocess.call(perl_call_array)
	print a


	if a:
		return "ERROR PARSING XML IN PERL SCRIPT"
	else:
		print "no error in perl script, all good."
		return 0
		# print "no error in perl script. Should delete the xml directory, because we don't need it anymore, just keep the xml.txt"
		# try:
		# 	shutil.rmtree(xml_dir_name)
		# 	return 0
		# except:
		# 	print "trouble deleting the directory afterwards."
		# 	return "Trouble deleting xml directory afterwards"
			# This is safe because it'll only delete the directory that you create.
			# But still, something to be careful about in the future, in case I forget
			# and change something
		# return 0


def parse_xtandem_combine_with_mgf(full_path_to_xml, error_threshold, reporter_type, genefile, selected_mgfdir, unacceptable_mods):
	print "in parse_xtandem_combine_with_mgf"
	resp = parse_xtandem_new(full_path_to_xml, error_threshold, reporter_type, genefile, unacceptable_mods)
	if resp:
		print "from parse_xtandem_combine_with_mgf, error detected in parse_xtandem_new: " + str(resp)
		return resp
	# print "stop here for now"
	# return 0

	print "selected mgfdir:"
	print selected_mgfdir

	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	resp_2 = combine_parsed_xml_mgf(selected_mgfdir, xml_dir_name, reporter_type)
	if resp_2:
		print "from parse_xtandem_combine_with_mgf, error in combine_parsed_xml_mgf: " + str(resp_2)
		return resp_2

	print "Looks good, cleaning up xml directory."
	try:
		shutil.rmtree(xml_dir_name)
		xml_txt_filename = full_path_to_xml + '.txt'
		os.remove(xml_txt_filename)
		print "directory cleaned, well done"
		return 0
	except:
		print "trouble deleting the directory afterwards."
		return "Trouble deleting xml directory afterwards"

	# return 0

def plain_parse_xtandem_combine_with_mgf(full_path_to_xml, error_threshold, genefile, selected_mgfdir, unacceptable_mods):
	print "in parse_xtandem_combine_with_mgf"
	print full_path_to_xml
	#kinda hacky, but we're gonna drop the labels column anyway
	resp = parse_xtandem_new(full_path_to_xml, error_threshold, "TMT0", genefile, unacceptable_mods)
	if resp:
		print "from plain_parse_xtandem_combine_with_mgf, error detected in parse_xtandem_new: " + str(resp)
		return resp
	# print "stop here for now"
	# return 0

	print "selected mgfdir:"
	print selected_mgfdir

	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	resp_2 = combine_plain_parsed_xml_mgf(selected_mgfdir, xml_dir_name)
	if resp_2:
		print "from plain_parse_xtandem_combine_with_mgf, error in combine_plain_parsed_xml_mgf: " + str(resp_2)
		return resp_2

	print "Looks good, cleaning up xml directory."
	try:
		shutil.rmtree(xml_dir_name)
		xml_txt_filename = full_path_to_xml + '.txt'
		os.remove(xml_txt_filename)
		print "directory cleaned, well done"
	except:
		print "trouble deleting the directory afterwards."
		return "Trouble deleting xml directory afterwards"

	print "Looks good, cleaning up reporter files."
	try:
		for item in os.listdir(selected_mgfdir):
			full_name = os.path.join(selected_mgfdir, item)
			if os.path.isfile(full_name) and full_name.endswith('.reporter'):
				os.remove(full_name)
	except:
		print "trouble removing reporters"
		return "trouble removing reporters"

	#TODO integrate this earlier
	print "renaming xml folder"
	try:
		#print "selected mgf directory to rename: " + selected_mgfdir
		#print "will be renamed to: " + full_path_to_xml[:-4]+"plainparse"
		os.rename(selected_mgfdir, full_path_to_xml[:-4]+"_plain_parse")
	except:
		print "trouble renaming"
		return "trouble renaming plain parse directory"
	# return 0







# def xml_dirname_from_filename(full_path_to_xml):
# 	almost_xml_dir_name = full_path_to_xml.partition('.xml')[0]
# 	xml_dir_name = join(almost_xml_dir_name, '')
# 	return xml_dir_name


def convert_reporter_to_label_mass(reporter):
	mapping = {
		'TMT0' : '225',
		'TMT2' : '225',
		'TMT6' : '229',
		'TMT6OLD' : '229',
		'TMT10' : '229',
		'iTRAQ4' : '144',
		'iTRAQ8': '304'
	}
	if reporter not in mapping:
		return None
	return mapping[reporter]



if __name__ == '__main__':
	xml_path = "/Users/samlobel/Code/DAD/filesforSam/NewMGFformat/GPM33300000085.xml"
	error_threshold = "20" #???
	reporter_type="TMT10" #???
	genefile="Human_GRCh38p5_PTGND.txt" #???
	unacceptable_mods=[]
	a = parse_xtandem_new(xml_path, error_threshold, reporter_type, genefile, unacceptable_mods)
	print a




