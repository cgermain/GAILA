import re
import os
import shutil


def all_fields_nonblank(form, fields):
	try:
		for f in fields:
			if not str(form[f]):
				return False
		return True
	except:
		return False


def validate_float(num):
	strnum = str(num)
	matched = re.match('^\-?\d+\.?\d*$', strnum)
	return matched
	# pass


def validate_int(num):
	# pass
	strnum = str(num)
	matched = re.match('^\-?\d+$', strnum)
	return matched

def validate_ion_type(ion_type):
	possibilities = ['iTRAQ4','iTRAQ8','TMT10','TMT2','TMT6','TMT6OLD','TMT0']
	return (ion_type in possibilities)


def validate_gene_file(genefile):
	this_dir = os.path.dirname(os.path.realpath(__file__))
	genefile_fullpath = os.path.join(this_dir, 'gene_files', genefile)
	return os.path.isfile(genefile_fullpath)


def validate_error_input(error_input):
	strnum = str(error_input)
	re_1 = '^\d+\.?\d*$'
	re_2 = '^\d+\.?\d*[eE]\-\d+'
	return (re.match(re_1, strnum) or re.match(re_2, strnum))


def multiple_select_to_two_arrays(unacceptable_mods):
	long_string = ','.join(unacceptable_mods)
	good_array = long_string.split(',')
	two_d_array = [i.split('@') for i in good_array]
	mass_val_arr = [j[0] for j in two_d_array]
	mod_val_arr = [k[1] for j in two_d_array]
	return mass_val_arr, mod_val_arr

def multiple_select_to_two_comma_separated_strings(unacceptable_mods):
	if len(unacceptable_mods) == 0:
		return "", ""

	mass_val_arr, mod_val_arr = multiple_select_to_two_arrays(unacceptable_mods)
	mass_val_literal = ', '.join(mass_val_arr)
	mod_val_literal = ', '.join(mod_val_arr)
	return mass_val_literal, mod_val_literal


def get_arrays_from_unacceptable_mod_form(unacceptable_mods):
	TEXT_FOR_LABEL="ISOBARIC_LABEL"
	if len(unacceptable_mods) == 0:
		return "", "", ""

	long_string = ','.join(unacceptable_mods)
	good_array = long_string.split(',')

	mod_masses,mod_labels,reporter_mod_labels= [],[],[]

	for i in range(len(good_array)):
		mod=good_array[i]
		mod_mass, mod_name =mod.split("@")
		if mod_mass==TEXT_FOR_LABEL:
			reporter_mod_labels.append(mod_name)
		else:
			mod_masses.append(mod_mass)
			mod_labels.append(mod_name)

	return mod_masses,mod_labels,reporter_mod_labels

def get_strings_from_unacceptable_mod_form(unacceptable_mods):
	if len(unacceptable_mods) == 0:
		return "", "", ""

	mod_masses, mod_labels, reporter_mod_labels = get_arrays_from_unacceptable_mod_form(unacceptable_mods)
	return ",".join(mod_masses), ",".join(mod_labels), ",".join(reporter_mod_labels)


def check_if_summary_exists(directory):
	for f in os.listdir(directory):
		if f.endswith("intensity_summary.txt"):
			return True
	return False

def get_mgf_files_given_directory(directory):
	mgf_array = []
	for f in os.listdir(directory):
		if f.endswith(".mgf"):
			mgf_array.append(f)
	return mgf_array


def get_reporter_files_given_directory(directory):
	reporter_array = []
	for f in os.listdir(directory):
		if f.endswith(".reporter"):
			reporter_array.append(f)
	return reporter_array


def get_gene_files_array():
	gene_file_array = []
	this_dir = os.path.dirname(os.path.realpath(__file__))
	for f in os.listdir(os.path.join(this_dir, "gene_files")):
		if f.endswith('.txt'):
			gene_file_array.append(f)
	return gene_file_array


def get_true_inverse_array():
	this_dir = os.path.dirname(os.path.realpath(__file__))
	inverse_file_array_calculated = []
	for f in os.listdir(os.path.join(this_dir, "inverse_files")):
		if f.endswith('-inv.txt'):
			inverse_file_array_calculated.append(f)
	return inverse_file_array_calculated

def get_inverse_files_array():
	# I think I need to hardcode this now, considering that people are
	# going to mess with the files in there.
	inverse_file_array = [
		'iTRAQ4-inv.txt',
		'iTRAQ8-inv.txt',
		'TMT10-inv.txt',
		'TMT0-inv.txt',
		'TMT2-inv.txt',
		'TMT6-inv.txt',
		'TMT6OLD-inv.txt'
	]
	return inverse_file_array

def get_modification_dict():
	mod_dict = {
		"ISOBARIC_LABEL@Y" : "Reporter Ion modifies with Y-hydroxyl",
		"15.994915@M" : "Oxidation (M)",
		"31.98983@M" : "Dioxidation (M)",
		"15.994915@W" : "Oxidation (W)",
		"31.98983@W" : "Dioxidation (W)",
		"0.984016@N" : "Deamidation (N)",
		"0.984016@Q" : "Deamidation (Q)",
		"21.982@D,21.982@E" : "Cation:Na (E,D)",
		"37.955885@D,37.955885@E" : "Cation:K (E,D)",
		"15.994915@P" : "Hydroxy (P)",
		"79.966331@S" : "Phospho (S)",
		"79.966331@T" : "Phospho (T)",
		"79.966331@Y" : "Phospho (Y)",
		"79.956815@Y" : "Sulfo (Y)",
		"42.010565@K" : "Acetyl (K)",
		"43.989829@E" : "gamma-carboxyl (E)",
		"43.005814@[" : "Carbamyl (nt)",
		"43.005814@K" : "Carbamyl (K)",
		"57.021464@[" : "Carbamidomethyl (nt)",
		"57.021464@K" : "Carbamidomethyl (K)",
		"27.994915@K" : "formyl (K)",
		"27.994915@[" : "formyl (nt)"
	}
	return mod_dict



def inverse_array_is_correct():
	true_inverse_array = get_true_inverse_array()
	inverse_file_array = get_inverse_files_array()
	if set(true_inverse_array) != set(inverse_file_array):
		return False
	return True


def xml_dirname_from_filename(full_path_to_xml):
	if not full_path_to_xml:
		print "bad, no full_path_to_xml"
		return False
	almost_xml_dir_name = full_path_to_xml.partition('.xml')[0]
	if not almost_xml_dir_name:
		print "bad, no almost_xml_dir_name"
		return False
	# check to make sure we don't delete the home directory or something crazy.
	after_slash = almost_xml_dir_name.rpartition(os.sep)[2]
	if not after_slash:
		print "passed in something like aaa/.xml, that's dangerous"
		return False
	xml_dir_name = os.path.join(almost_xml_dir_name, '')
	return xml_dir_name

def xml_dirname_from_filename_plain_parse(full_path_to_xml):
	if not full_path_to_xml:
		print "bad, no full_path_to_xml"
		return False
	almost_xml_dir_name = full_path_to_xml.partition('.xml')[0]
	if not almost_xml_dir_name:
		print "bad, no almost_xml_dir_name"
		return False
	# check to make sure we don't delete the home directory or something crazy.
	after_slash = almost_xml_dir_name.rpartition(os.sep)[2]
	if not after_slash:
		print "passed in something like aaa/.xml, that's dangerous"
		return False
	xml_dir_name = os.path.join(almost_xml_dir_name,'')
	return xml_dir_name


def tests():
	assert validate_float('-0.5')
	assert not validate_float('--0.5')
	assert not validate_float('-.')
	assert not validate_float('-')
	assert not validate_float('-2.a0')
	assert validate_float('0.5')
	assert validate_float('10.')
	assert not validate_float('.5')
	assert validate_int('123')
	assert validate_int('-123')
	assert not validate_int('--123')
	assert not validate_int('123.5')
	assert not validate_int('123a')
	assert not validate_float('')
	assert not validate_int('')
	assert validate_error_input('1e-10')
	assert validate_error_input('1E-10')
	assert validate_error_input('5e-10')
	assert validate_error_input('1.e-10')
	assert not validate_error_input('.5e-10')
	assert validate_error_input('60.1234234')
	assert not validate_error_input('-5')
	assert not validate_error_input('-0.005')
	assert not validate_error_input('-2e6')
	assert not validate_error_input('-2')
