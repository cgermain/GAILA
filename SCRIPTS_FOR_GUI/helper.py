import os

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
	
