from pyteomics import mgf
from datetime import datetime
import os
import sys

#MZ_CUTOFF = 140
TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
FUZZY_RT_VALUE = 5

def merge_ms2_ms3(ms2_ms3_directory, mz_cutoff):

	if not os.path.isdir(ms2_ms3_directory):
		print "Please check that you are passing in the MS2/MS3 directory."
		return

	#get the full path to the MGF files
	filenames = listdir_fullpath(ms2_ms3_directory)
	mgf_files = [filename for filename in filenames if os.path.isfile(filename) and filename.endswith(".mgf")]

	#the chunker and merging require an even number of MGF files
	if len(mgf_files) % 2 == 0:
		#mgf_files.sort(key=str.lower)
		mgf_files.sort()
	elif len(mgf_files) == 0:
		print "Directory must contain at least 2 MGF files."
	else:
		print "Directory must contain an even number of MGF files to merge."
		return

	timestamp = datetime.now().strftime(TIME_FORMAT)

	#run through the pairs once to make sure the MS2/MS3 filenames match
	for ms2_ms3_pair in chunker(mgf_files,2):
		if ms2_ms3_file_pair_mismatch(ms2_ms3_pair):
			print "MS2/MS3 file mismatch:"
			print ms2_ms3_pair[0]
			print ms2_ms3_pair[1]
			print "Please check the file names."
			return "MS2/MS3 file mismatch, please check file names.", 0
		if output_file_exists(ms2_ms3_pair):
			print "Merged MS2/MS3 file already exists in directory."
			print "Remove and rerun."
			return "Merged MS2/MS3 file already exists in directory.", 0
		if os.path.isdir(generate_output_directory_name(ms2_ms3_pair[0], timestamp)):
			print "Merged output directory already exists."
			print "Remove and rerun."
			return "Merged output directory already exists.", 0

	try:
		#execute the merge and save the new MGF file for each MS2/MS3 pair
		for ms2_ms3_pair in chunker(mgf_files,2):
			merge_result = merge_mgf_files(ms2_ms3_pair[0], ms2_ms3_pair[1], mz_cutoff)
			save_mgf_output(merge_result, ms2_ms3_pair[0], ms2_ms3_directory, timestamp)
			print_merge_stats(merge_result)
			del merge_result #attempt to free up memory
	except:
		return "Error during merge.", 0

	print "Merging complete"
	return "Merging complete", 1

def merge_mgf_files(ms2_file, ms3_file, mz_cutoff):
	ms2_count = 0
	ms3_count = 0
	current_count = 0
	merged_count = 0

	#preloading the files into memory
	#ms2 - so we have a total spectra count for the progress bar
	#ms3 - so we don't have to read in repeatedly per ms2 spectra
	merged_mgf = []
	ms2_spectrum_list = []
	ms3_spectrum_list = []

	print "Reading MS2 file: " + ms2_file
	with mgf.read(ms2_file) as ms2_reader:
		for ms2_temp in ms2_reader:
			ms2_spectrum_list.append(ms2_temp)
			ms2_count += 1

	print "Reading MS3 file: " + ms3_file
	with mgf.read(ms3_file) as ms3_reader:
		for ms3_temp in ms3_reader:
			ms3_spectrum_list.append(ms3_temp)
			ms3_count+=1

	#Loop through all MS2/MS3 spectra looking for fuzzy matches.
	for ms2_spectrum in ms2_spectrum_list:
		for ms3_index, ms3_spectrum in enumerate(ms3_spectrum_list):
			if compare_spectrums_with_fuzzy_rt(ms2_spectrum, ms3_spectrum):
				merged_xy = merge_xy_arrays(ms2_spectrum, ms3_spectrum, mz_cutoff)
				ms2_spectrum['m/z array'] = merged_xy[0]
				ms2_spectrum['intensity array'] = merged_xy[1]					
				merged_count += 1
				#remove the element we just found from the list to avoid dupes and save time
				del ms3_spectrum_list[ms3_index]
				break
		merged_mgf.append(ms2_spectrum) #add no matter if it was merged or not
		current_count += 1
		write_progress_bar(current_count, ms2_count)

	return {
		"merged_mgf":merged_mgf,
		"ms2_count":ms2_count,
		"ms3_count":ms3_count,
		"merged_count":merged_count
		}

def compare_spectrums_with_fuzzy_rt(ms2_spectrum, ms3_spectrum):
	return (ms2_spectrum['params']['pepmass'] == ms3_spectrum['params']['pepmass'] and
		ms2_spectrum['params']['charge'] == ms3_spectrum['params']['charge'] and
		abs(float(ms2_spectrum['params']['rtinseconds'])-float(ms3_spectrum['params']['rtinseconds'])) < FUZZY_RT_VALUE)

def merge_xy_arrays(ms2_spectrum, ms3_spectrum, mz_cutoff):
	merge_mz = []
	merge_intensity = []
	
	#Take all of the X,Y pairs that have X values lower than MZ_CUTOFF and add them to the merged array
	#Start with ms3 so they remain in sorted order
	for index, x_value in enumerate(ms3_spectrum['m/z array']):
		if (float(x_value) < mz_cutoff):
			merge_mz.append(x_value)
			merge_intensity.append(ms3_spectrum['intensity array'][index])
		else: # skip the rest if over MZ_CUTOFF
			break # can do this since it is ordered

	for index, x_value in enumerate(ms2_spectrum['m/z array']):
		if (float(x_value) >= mz_cutoff):
			merge_mz.append(x_value)
			merge_intensity.append(ms2_spectrum['intensity array'][index])

	return [merge_mz, merge_intensity] 

def write_progress_bar(current_count, total_count):
	width = 60
	complete_length = int(round(width * current_count / float(total_count)))

	percent_complete = round(100.0 * current_count / float(total_count), 1)
	bar = '=' * complete_length + '-' * (width - complete_length)

	sys.stdout.write('Merging: [%s] %s%s \r' % (bar, percent_complete, '%'))
	sys.stdout.flush()

def listdir_fullpath(directory):
	return [os.path.join(directory, filename) for filename in os.listdir(directory)]

def chunker(sequence, size):
	return (sequence[index:index + size] for index in xrange(0, len(sequence), size))

#checking to make sure that the ms2 and ms3 filenames match properly
def ms2_ms3_file_pair_mismatch(chunk):
	ms2_file = chunk[0]
	ms3_file = chunk[1]

	try:	
		return not ("MS2" in ms2_file and
			"MS3" in ms3_file and
			ms2_file.split("MS2")[0] == ms3_file.split("MS3")[0])
	except:
		return True

def output_file_exists(chunk):
	ms2_file = chunk[0]
	ms3_file = chunk[1]

	try:
		return ("MS2_MS3" in ms2_file or "MS2_MS3" in ms3_file)
	except:
		return True

def save_mgf_output(merge_result, ms2_file, ms2_ms3_directory, timestamp):
	#create merged directory and save renamed file out to it
	output_directory = generate_output_directory_name(ms2_file, timestamp)
	if not os.path.isdir(output_directory):
		os.makedirs(output_directory)

	merged_mgf_filename = generate_output_merged_mgf_name(ms2_file, timestamp)
	print "\nWriting merged MGF: " + merged_mgf_filename
	mgf.write(merge_result["merged_mgf"], output=merged_mgf_filename)
	
def print_merge_stats(merge_result):
	print "MS2 Count  : " + str(merge_result["ms2_count"])
	print "MS3 Count  : " + str(merge_result["ms3_count"])
	print "Merged Count: " + str(merge_result["merged_count"])

def generate_output_directory_name(ms2_file, timestamp):
	directory_path = os.path.dirname(ms2_file)
	output_directory = os.path.join(directory_path, "merged_MS2_MS3_" + timestamp)
	return output_directory

def generate_output_merged_mgf_name(ms2_file, timestamp):
	directory_path = os.path.dirname(ms2_file)
	base_name = os.path.basename(ms2_file).split("MS2")[0]
	output_directory = generate_output_directory_name(ms2_file, timestamp)
	merged_mgf_filename = os.path.join(output_directory, base_name + "_MS2_MS3.mgf")
	return merged_mgf_filename

if __name__ == "__main__":
	main()
	raw_input("press ENTER to exit")