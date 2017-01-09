import shutil
from os import listdir
from os.path import isfile, join

def concat_mgf_files(output_filename, input_filename_array):
	with open(output_filename,'wb') as wfd:
		for f in input_filename_array:
			with open(f,'rb') as fd:
				shutil.copyfileobj(fd, wfd, 1024*1024*10)
				#10MB per writing chunk to avoid reading big file into memory.
	print "Concatenated"


def concat_mgf_txt_files(output_filename, input_filename_array):
	with open(output_filename,'w') as wf:
		first_file = True
		for f in input_filename_array:
			with open(f, 'rb') as rf:
				first_line = True
				if first_file:
					wf.write(rf.readline())
					first_line = False
					first_file = False
				if first_line:
					rf.readline()
					# That just throws it away
				line = rf.readline()
				while line:
					wf.write(line)
					line = rf.readline()


def concat_mgf_files_given_dirname(output_filename, input_directory_name):
	try:
		filenames = [join(input_directory_name,f) for f in listdir(input_directory_name) if isfile(join(input_directory_name, f))]
		# return filenames
		filenames = [g for g in filenames if g.endswith(".mgf")]
		concat_mgf_files(output_filename, filenames)
	except:
		return "Error concatting mgf files files in this directory"
	print "Concatenated"
	return


def concat_mgf_txt_files_given_dirname(output_filename, input_directory_name):
	try:
		filenames = [join(input_directory_name,f) for f in listdir(input_directory_name) if isfile(join(input_directory_name, f))]
		filenames = [g for g in filenames if g.endswith(".reporter")]
		concat_mgf_txt_files(output_filename, filenames)
	except:
		return "Error concatting mgf_txt files in this directory"
	print "Concatenated"
	return


