import re
import os



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
	possibilities = ['iTRAQ4','iTRAQ8','TMT10','TMT2','TMT6','TMT0']
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





def get_mgf_files_given_directory(directory):
	mgf_array = []
	for f in os.listdir(directory):
		if f.endswith(".mgf"):
			mgf_array.append(f)
	return mgf_array


def get_gene_files_array():
	gene_file_array = []
	this_dir = os.path.dirname(os.path.realpath(__file__))
	for f in os.listdir(os.path.join(this_dir, "gene_files")):
		if f.endswith('.txt'):
			gene_file_array.append(f)
	return gene_file_array

def get_inverse_files_array():
	inverse_file_array = []
	this_dir = os.path.dirname(os.path.realpath(__file__))
	for f in os.listdir(os.path.join(this_dir, "inverse_files")):
		if f.endswith('-inv.txt'):
			inverse_file_array.append(f)
	return inverse_file_array





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
	
	
	
	# Good, that actually helped me catch an error, well done sammy boy


# tests()

