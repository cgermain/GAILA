from __future__ import print_function
from __future__ import absolute_import
import os
from os.path import join
from os.path import basename
import shutil
from .combine_xml_mgf import combine_parsed_xml_mgf 
from .combine_xml_mgf import combine_plain_parsed_xml_mgf
from .combine_xml_mgf import finish_fast_parse
from . import utility
import subprocess
from . import makeFolderNames


def parse_xtandem_new(full_path_to_xml, error_threshold, reporter_type, genefile_array, unacceptable_mods, mgf_list):
	this_dir = os.path.dirname(os.path.realpath(__file__))
	full_path_to_genefile = ",".join([join(this_dir, 'gene_files', genefile) for genefile in genefile_array])

	# going on the assumption it's been validated
	mass_val_literal, mod_val_literal, reporter_mods_literal = utility.get_strings_from_unacceptable_mod_form(unacceptable_mods)

	label_mass = convert_reporter_to_label_mass(reporter_type)
	if not label_mass:
		print("bad label mass returned")
		return "reporter type not valid"

	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	if os.path.isdir(xml_dir_name):
		print("xml directory already exists here, if you don't need it anymore try deleting it and running again")
		return "xml directory already exists here, if you don't need it anymore try deleting it and running again"

	xml_txt_filename = full_path_to_xml + '.txt'
	if os.path.isfile(xml_txt_filename):
		print("xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file")
		return "xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file"

	os.mkdir(xml_dir_name)

	utility.print_timestamp("XML Parse - Start - " + basename(full_path_to_xml))

	perl_call_array=['perl', join(this_dir, 'parse_xtandem_sam.pl'), full_path_to_xml, \
		xml_dir_name, str(error_threshold), str(label_mass), full_path_to_genefile, \
		mass_val_literal, mod_val_literal, reporter_mods_literal, mgf_list]

	a = subprocess.call(perl_call_array)

	if a:
		return "ERROR PARSING XML IN PERL SCRIPT"
	else:
		utility.print_timestamp("XML Parse - Complete - " + basename(full_path_to_xml))
		#Perl script exectued
		return 0

def parse_xtandem_fast(full_path_to_xml, error_threshold, genefile, unacceptable_mods, plain_parsing, mgf_list):
	this_dir = os.path.dirname(os.path.realpath(__file__))
	full_path_to_genefile = join(this_dir, 'gene_files', genefile)

	# going on the assumption it's been validated
	mass_val_literal, mod_val_literal, reporter_mods_literal = utility.get_strings_from_unacceptable_mod_form(unacceptable_mods)

	xml_dir_name = utility.xml_dirname_from_filename_fast_parse(full_path_to_xml)
	if os.path.isdir(xml_dir_name):
		print("xml directory already exists here, if you don't need it anymore try deleting it and running again")
		return "xml directory already exists here, if you don't need it anymore try deleting it and running again"

	xml_txt_filename = full_path_to_xml + '.txt'
	if os.path.isfile(xml_txt_filename):
		print("xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file")
		return "xml txt file already exists there, either you've already run this in the past or you have a residual file you don't want. Consider deleting or moving that file"

	os.mkdir(xml_dir_name)

	perl_call_array=['perl', join(this_dir, 'quick_parse_xtandem.pl'), full_path_to_xml, \
		xml_dir_name, str(error_threshold), full_path_to_genefile, \
		mass_val_literal, mod_val_literal, plain_parsing, mgf_list]

	if plain_parsing == "0":
		utility.print_timestamp("XML Fast Parse - Start - " + basename(full_path_to_xml))
	else:
		utility.print_timestamp("XML Plain Parse - Start - " + basename(full_path_to_xml))

	a = subprocess.call(perl_call_array)

	if a:
		return "ERROR FAST PARSING XML IN PERL SCRIPT"
	else:
		if plain_parsing == "0":
			utility.print_timestamp("XML Fast Parse - Complete - " + basename(full_path_to_xml))
		else:
			utility.print_timestamp("XML Plain Parse - Complete - " + basename(full_path_to_xml))
		#Perl script exectued
		return 0

def parse_xtandem_combine_with_mgf(full_path_to_xml, error_threshold, reporter_type, genefile, selected_mgfdir, unacceptable_mods, normalize_intensities, timestamp, keep_na, mgf_list):
	resp = parse_xtandem_new(full_path_to_xml, error_threshold, reporter_type, genefile, unacceptable_mods, mgf_list)
	if resp:
		print("from parse_xtandem_combine_with_mgf, error detected in parse_xtandem_new: " + str(resp))
		return resp

	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	resp_2 = combine_parsed_xml_mgf(selected_mgfdir, xml_dir_name, reporter_type, normalize_intensities, timestamp, keep_na)
	if resp_2:
		print("from parse_xtandem_combine_with_mgf, error in combine_parsed_xml_mgf: " + str(resp_2))
		return resp_2

	#cleaning up XML directory
	try:
		shutil.rmtree(xml_dir_name)
		xml_txt_filename = full_path_to_xml + '.txt'
		os.remove(xml_txt_filename)
		return 0
	except:
		print("trouble deleting the directory afterwards.")
		return "Trouble deleting xml directory afterwards"


def plain_parse_xtandem_combine_with_mgf(full_path_to_xml, error_threshold, genefile, selected_mgfdir, unacceptable_mods, timestamp, mgf_list):
	resp = parse_xtandem_fast(full_path_to_xml, error_threshold, genefile, unacceptable_mods, "1", mgf_list)
	if resp:
		print("from plain_parse_xtandem_combine_with_mgf, error detected in parse_xtandem_fast: " + str(resp))
		return resp

	xml_dir_name = utility.xml_dirname_from_filename_fast_parse(full_path_to_xml)
	resp_2 = combine_plain_parsed_xml_mgf(selected_mgfdir, xml_dir_name, timestamp)
	if resp_2:
		print("from plain_parse_xtandem_combine_with_mgf, error in combine_plain_parsed_xml_mgf: " + str(resp_2))
		return resp_2

	#Cleaning up XML directory
	try:
		shutil.rmtree(xml_dir_name)
		xml_txt_filename = full_path_to_xml + '.txt'
		os.remove(xml_txt_filename)
	except:
		print("trouble deleting the directory afterwards.")
		return "Trouble deleting xml directory afterwards"

	#cleaning up reporter files
	try:
		for item in os.listdir(selected_mgfdir):
			full_name = os.path.join(selected_mgfdir, item)
			if os.path.isfile(full_name) and full_name.endswith('.reporter'):
				os.remove(full_name)
	except:
		print("trouble removing reporters")
		return "trouble removing reporters"

	return 0

def fast_parse_xtandem(full_path_to_xml, error_threshold, genefile, unacceptable_mods, timestamp):
	resp = parse_xtandem_fast(full_path_to_xml, error_threshold, genefile, unacceptable_mods, "0", "")
	if resp:
		print("from fast_parse_xtandem, error detected in parse_xtandem_fast: " + str(resp))
		return resp

	xml_dir_name = utility.xml_dirname_from_filename(full_path_to_xml)
	resp_2 = finish_fast_parse(xml_dir_name, timestamp)
	if resp_2:
		print("from plain_parse_xtandem_combine_with_mgf, error in combine_plain_parsed_xml_mgf: " + str(resp_2))
		return resp_2

	return 0

def convert_reporter_to_label_mass(reporter):
	mapping = {
		'TMT0' : '225',
		'TMT2' : '225',
		'TMT6' : '229',
		'TMT6OLD' : '229',
		'TMT10' : '229',
		'TMT11' : '229',
		'TMT16' : '304',
		'iTRAQ4' : '144',
		'iTRAQ8': '304'
	}
	if reporter not in mapping:
		return None
	return mapping[reporter]