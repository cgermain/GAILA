from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import sys, os, shutil

from os.path import join


# get THIS directory! All of the initial files have got to be relative to this directory!


this_dir = os.path.dirname(os.path.realpath(__file__))

def remove_duplicate_lines(filename):
	print "removing duplicate lines"
	suffix = '_with_duplicates_removed'
	lines_seen = set()
	write_dest = filename + suffix
	# os.remove(outfile) # there were errors before because it was appending instead of overwriting.
	outfile = open(write_dest, "w")
	for line in open(filename, "r"):
		if line not in lines_seen:
			outfile.write(line)
			lines_seen.add(line)
		else:
			print "duplicate line removed: " + str(line)
	outfile.close()
	os.remove(filename)
	os.rename(write_dest, filename)


def clear_directory_of_files(directory):
	print "clearing dir of files"
	for item in os.listdir(directory):
		if os.path.isfile(item):
			toRemove = directory + os.sep + item
			os.remove(directory + os.sep + item)
			print toRemove + " removed"


def transform_firstline_for_n_and_c(firstline):
	stripped = firstline.strip()
	split = stripped.split('\t')
	num_fields = len(split)
	i = 0
	while i < num_fields - 1:
		first = split[i]
		second = split[i+1]
		if second.endswith('.1'):
			pre_end = second.partition('.1')[0]
			if pre_end != first:
				print "Changeing first line so rep. ions end in N or C instead of .1. " +\
							" This should only happen when two rep. ions have the same integer-mass." +\
							" For some reason it is happening elsewhere. Printing old first line for debugging."
				print firstline
				raise Exception("very strange these headers are not equal, they should be.")
			new_first = pre_end + "N"
			new_second = pre_end + "C"
			split[i] = new_first
			split[i+1]=new_second
			i += 1
		i += 1
	new_firstline = '\t'.join(split)
	return new_firstline
	

def add_a_or_b_label_to_sorted_mfg_txt_file(filename):
	print "adding a and b labels "
	a = open(filename, "r")
	temp_filename = filename + "_PLACEHOLDER"
	temp_file = open(temp_filename, "w")

	first_line = a.readline()
	# print "first line: " + str(first_line)
	first_line = transform_firstline_for_n_and_c(first_line)
	# print "new first line: " + str(first_line)

	temp_file.write(first_line.strip() + "\treplicate_spec_flag\n")
	first_line_arr = first_line.split('\t')
	filename_index = first_line_arr.index("filename")
	scan_index = first_line_arr.index("scan")
	if scan_index == -1 or filename_index == -1:
		raise Exception("something is wrong with the file formatting")
	scan_list = []
	first = True
	most_recent = (None, None)
	for line in a:
		line_arr = line.split("\t")
		curr_scan = line_arr[scan_index]
		curr_filename = line_arr[filename_index]
		tup = (curr_filename, curr_scan)
		if (not first) and (not (most_recent[1] == tup[1])):
			if len(scan_list) == 0:
				raise Exception("Something is funky, shouldn't be zero")
			elif len(scan_list) == 1:
				temp_file.write(scan_list[0].strip() + "\tA\n")
			else:
				for l in scan_list:
					temp_file.write(l.strip() + "\tB\n")
			scan_list = []
		scan_list.append(line)
		most_recent = tup
		first = False
	if len(scan_list) == 0:
		raise Exception("Something is funky, shouldn't be zero")
	elif len(scan_list) == 1:
		temp_file.write(scan_list[0].strip() + "\tA\n")
	else:
		for l in scan_list:
			temp_file.write(l.strip() + "\tB\n")
	a.close()
	temp_file.close()
	os.remove(filename)
	os.rename(temp_filename,filename)
	print "a and b labels added"

# REMEMBER TO DO ONE AT THE END TOO!


def add_c_labels_to_duplicate_marker_column(filename):
	print "adding c labels "
	a = open(filename, "r")
	temp_filename = filename + "_PLACEHOLDER"
	temp_file = open(temp_filename, "w")

	first_line = a.readline()
	temp_file.write(first_line)
	first_line_arr = first_line.split('\t')
	filename_index = first_line_arr.index("filename")
	scan_index = first_line_arr.index("scan")
	duplicate_index = first_line_arr.index("replicate_spec_flag")
	log_e_index = first_line_arr.index("peptide expectation") #Hopefully it's there
	if scan_index == -1 or filename_index == -1 or duplicate_index == -1 or log_e_index == -1:
		raise Exception("something is wrong with the file formatting")
	scan_list = []
	first = True
	most_recent = (None, None)
	for line in a:
		line_arr = line.split("\t")
		curr_scan = line_arr[scan_index]
		curr_filename = line_arr[filename_index]
		curr_replicate_spec_flag = line_arr[duplicate_index]
		tup = (curr_filename, curr_scan)
		if (not first) and (not (most_recent[1] == tup[1])):
			if len(scan_list) == 0:
				raise Exception("Something is funky, shouldn't be zero")
			elif len(scan_list) == 1:
				temp_file.write("\t".join(scan_list[0]))
			else:
				new_list = [(float(l[log_e_index]), l) for l in scan_list]
				new_list = sorted(new_list)
				for i in range(len(new_list)):
					arr = new_list[i][1]
					arr[duplicate_index] = "C" + str(i + 1)
					temp_file.write("\t".join(arr)) 
			scan_list = []
		scan_list.append(line_arr)
		most_recent = tup
		first = False
	if len(scan_list) == 0:
		raise Exception("Something is funky, shouldn't be zero")
	elif len(scan_list) == 1:
		temp_file.write("\t".join(scan_list[0]))
	else:
		new_list = [(float(l[log_e_index]), l) for l in scan_list]
		new_list = sorted(new_list)
		for i in range(len(new_list)):
			arr = new_list[i][1]
			arr[duplicate_index] = "C" + str(i + 1)
			temp_file.write("\t".join(arr)) 
	a.close()
	temp_file.close()
	os.remove(filename)
	os.rename(temp_filename,filename)

# REMEMBER TO DO ONE AT THE END TOO!




def take_in_file_sorted_by_filename_scan_output_file_with_duplicate_marker_column(filename):
	a = open(filename, "r")
	temp_file = open(filename + "_PLACEHOLDER", "w")
	
	first_line = a.readline()
	temp_file.write(first_line.strip() + "\treplicate_spec_flag\n")

	first_line_arr = first_line.split('\t')
	log_e_index = first_line_arr.index("peptide expectation") #Hopefully it's there
	scan_index = first_line_arr.index("scan")
	filename_index = first_line_arr.index("filename")
	if scan_index == -1 or filename_index == -1:
		raise Exception("something is wrong with the file formatting")
	scan_list = []
	curr_values = (None, None)
	for line in a:
		line_arr = line.split("\t")
		curr_scan = line_arr[scan_index]
		curr_log_e = float(line_arr[log_e_index])
		curr_filename = line_arr[filename_index]
		tup = (curr_filename, curr_scan)
		if curr_values == tup:
			print "dealing with duplicate! Line is as follows:"
			print line
			scan_list.append((log_e, line))
		else:
			scan_list = sorted(scan_list)
			lines = [elem[1] for elem in scan_list]
			if len(lines) == 0:
				raise Exception("length zero?")
			elif len(lines) == 1:
				for i in range(len(lines)):
					print "yo"
			else:
				print "yoda"







def remove_log_e_duplicates(filename):
	a = open(filename, "r")

	first_line = a.readline()
	first_line_arr = first_line.split('\t')
	log_e_index = first_line_arr.index("peptide expectation") #Hopefully it's there
	scan_index = first_line_arr.index("scan")

	scan_set = set()
	least_dict = {}
	duplicates_set = set()

	# reads rest of file
	for line in a:
		line_arr = line.split("\t")
		scan = line_arr[scan_index]
		log_e = float(line_arr[log_e_index])

		if scan not in scan_set:
			scan_set.add(scan)
			least_dict[scan] = log_e
		else: #we've seen it before
			least_dict[scan] = min(least_dict[scan], log_e)
			duplicates_set.add(scan) #find the smallest scan, add it to duplicates
		# Here, we've run through the file, found all the duplicates, found the smallest value.
		# Now, we just need to re-run through, writing the least only.

	a.close()
	a = open(filename, "r") #get to the beginning again
	tempdest = filename + "_with_duplicates_deleted" 
	# os.remove(tempdest)  # there were errors before because it was appending instead of overwriting. 
	b = open(tempdest, "w")

	first_line = a.readline()
	b.write(first_line)

	already_written = set() #this is a little annoying, but what if there's two things with the same
							#scan and the same error? Then we get duplicates. And certainty is worth speed.

	for line in a:
		line_arr = line.split("\t")
		scan = line_arr[scan_index]
		log_e = float(line_arr[log_e_index])

		if scan not in already_written:
			if log_e == least_dict[scan]:
				b.write(line)
				already_written.add(scan)
	b.close()
	a.close()

	os.remove(filename) #On windows you've got to remove the destination first.
	os.rename(tempdest, filename)



def check_for_selected_xmldir_lineup(selected_mgfdir, xmldir):
	if not os.path.isdir(selected_mgfdir):
		return False, "Selected mgf directory doesn't exist"
	if not os.path.isdir(xmldir):
		return False, "xmldir doesn't exist"
	for filename in os.listdir(xmldir):
			if filename.endswith('.reporter'):
				reporter_filename = join(selected_mgfdir, filename)
				if not os.path.isfile(reporter_filename):
					return False, str(filename) + " does not exist in the selected mgfdir"
	return True, None

def combine_plain_parsed_xml_mgf(selected_mgfdir, xmldir):
	try:
		this_dir = os.path.dirname(os.path.realpath(__file__))	

		# I should check here to make sure the files line up.
		linesup, message = check_for_selected_xmldir_lineup(selected_mgfdir, xmldir)
		if not linesup:
			print "doesn't line up"
			return message

		#not using because no reporter ion type
		#corr_path = join(this_dir, "inverse_files", reporter_ion_type + "-inv.txt")
		#if not os.path.isfile(corr_path):
		#	return "Cannot find inverse file"
		#print "reading pd table"
		#corr = pd.read_table(corr_path)
		#print "pd table read"
		#corr=corr.drop('Unnamed: 0', axis=1)
		# xmldir,sep,ext = xmlfile.rpartition('.')
		print "something dropped"
		xmldir = join(xmldir,"")
		parent_xml_filename = os.path.basename(os.path.normpath(xmldir))
		print "about to loop files"
		# Problem is that it's an empty folder!
		for filename in os.listdir(xmldir):
			if filename.endswith('.reporter'):
				xml_filename = join(xmldir, filename)
				mgf_txt_filename = join(selected_mgfdir, filename)
				mgf = pd.read_table(mgf_txt_filename, index_col=['filename','scan','charge'])
				print "read mgf_txt filename"
				mgf.sort_index()
				print "did initial work on them"
				testing_filename = mgf_txt_filename.split('.reporter')[0] + '_duplicate_sorted' + '.reporter'
				mgf.to_csv(testing_filename, sep='\t')
				print "wrote one csv"
				add_a_or_b_label_to_sorted_mfg_txt_file(testing_filename)
				print "about to read mgf table"
				mgf = pd.read_table(testing_filename, index_col=['filename','scan','charge'])
				print "mgf table read."
				xml = pd.read_table(xml_filename, index_col=['filename','scan','charge'])
				#print xml
				print "read xml filename"
				print "about to merge"
				dfc=pd.merge(mgf,xml, left_index=True, right_index=True)
				print "merged. about to dropna"
				dfc_=dfc.dropna()
				dfc_=dfc_.drop("labeling",1)
				csv_filename = join(xmldir, filename + '_nocal_table.txt')
				print "Writing to " + str(csv_filename)
				dfc_.to_csv(csv_filename,sep='\t')
				print "written to csv"

				os.remove(testing_filename)
				data = pd.read_table(csv_filename)
				#this should be able to be combined with naming above
				this_filename = join(xmldir, filename + '_nocal_table_corrected.txt')
				data.to_csv(this_filename,sep='\t',index=False)

		first=1
		outfile_name = join(selected_mgfdir, parent_xml_filename + '-pep-merged.txt')
		with open(outfile_name, 'w') as outfile:
			for filename in os.listdir(xmldir):

				if filename.endswith('_nocal_table_corrected.txt'):
					with open(join(xmldir, filename)) as infile:
						for line in infile:
							if (not 'other proteins' in line) or (first==1):
								first = 0
								outfile.write(line)
		print outfile_name
		add_c_labels_to_duplicate_marker_column(outfile_name)
		print "Done!"
		return
	except Exception as err:
		print "error"
		print err
		return "Error combining xml and mgf"

def combine_parsed_xml_mgf(selected_mgfdir, xmldir, reporter_ion_type):
	try:
		this_dir = os.path.dirname(os.path.realpath(__file__))
		print "checking reporter ion type"
		if reporter_ion_type=='iTRAQ4':
			start_col=reporter_ion_type+'-114'
			end_col=reporter_ion_type+'-117'
			label_mass_int=144
		elif reporter_ion_type=='iTRAQ8':
			start_col=reporter_ion_type+'-113'
			end_col=reporter_ion_type+'-121'
			label_mass_int=304
		elif reporter_ion_type=='TMT0':
			start_col=reporter_ion_type+'-126'
			end_col=reporter_ion_type+'-126'
			label_mass_int=225
		elif reporter_ion_type=='TMT2':
			start_col=reporter_ion_type+'-126'
			end_col=reporter_ion_type+'-127'
			label_mass_int=225
		elif reporter_ion_type=='TMT6':
			start_col=reporter_ion_type+'-126'
			end_col=reporter_ion_type+'-131'
			label_mass_int=229
		elif reporter_ion_type=='TMT6OLD':
			start_col=reporter_ion_type+'-126'
			end_col=reporter_ion_type+'-131'
			label_mass_int=229
		elif reporter_ion_type=='TMT10':
			start_col=reporter_ion_type+'-126'
			end_col=reporter_ion_type+'-131'
			label_mass_int=229
		else:
			print "bad reporter ion type"
			return "BAD REPORTER ION TYPE"
		print "good reporter ion type"

		# I should check here to make sure the files line up.
		linesup, message = check_for_selected_xmldir_lineup(selected_mgfdir, xmldir)
		if not linesup:
			print "doesn't line up"
			return message

		corr_path = join(this_dir, "inverse_files", reporter_ion_type + "-inv.txt")
		if not os.path.isfile(corr_path):
			return "Cannot find inverse file"
		print "reading pd table"
		corr = pd.read_table(corr_path)
		print "pd table read"
		corr=corr.drop('Unnamed: 0', axis=1)
		# xmldir,sep,ext = xmlfile.rpartition('.')
		print "something dropped"
		xmldir = join(xmldir,"")
		parent_xml_filename = os.path.basename(os.path.normpath(xmldir))
		print "about to loop files"
		# Problem is that it's an empty folder!
		for filename in os.listdir(xmldir):
			if filename.endswith('.reporter'):
				print filename
				xml_filename = join(xmldir, filename)
				print xml_filename
				mgf_txt_filename = join(selected_mgfdir, filename)
				print mgf_txt_filename
				mgf = pd.read_table(mgf_txt_filename, index_col=['filename','scan','charge'])
				print "read mgf_txt filename"
				mgf.sort_index()
				print "did initial work on them"
				testing_filename = mgf_txt_filename.split('.reporter')[0] + '_duplicate_sorted' + '.reporter'
				mgf.to_csv(testing_filename, sep='\t')
				print "wrote one csv"
				add_a_or_b_label_to_sorted_mfg_txt_file(testing_filename)
				print "about to read mgf table"
				mgf = pd.read_table(testing_filename, index_col=['filename','scan','charge'])
				print "mgf table read."
				xml = pd.read_table(xml_filename, index_col=['filename','scan','charge'])
				#print xml
				print "read xml filename"
				print "about to merge"
				dfc=pd.merge(mgf,xml, left_index=True, right_index=True)
				print "merged. about to dropna"
				dfc_=dfc.dropna()
				csv_filename = join(xmldir, filename + '_nocal_table.txt')
				print "Writing to " + str(csv_filename)
				dfc_.to_csv(csv_filename,sep='\t')
				print "written to csv"

				os.remove(testing_filename)
				print "1"
				data = pd.read_table(csv_filename)
				print "2"
				#for k in range(len(data)):
					#print k,len(data),start_col,end_col,data
					#print data.ix[k,start_col:end_col]
					
					# this next line gets the kth row, and the start_col to end_col columns, which are strings like iTRAQ-115.
					#print start_col
					#print end_col
					#print data
				#	temp=np.dot(data.ix[k,start_col:end_col].values,corr.values)
					#print "data: " + str(data.ix[k,start_col:end_col].values)
					#print "temp: " + str(temp)
					#print "corr: " + str(corr.values)
				#	temp=temp.astype(float)
				#	temp[temp<0]=0
				#	temp/=sum(temp)
				#	data.ix[k,start_col:end_col]=temp
				print "3"
				this_filename = join(xmldir, filename + '_nocal_table_corrected.txt')
				print "4"
				data.to_csv(this_filename,sep='\t',index=False)
				print "5"

		first=1
		outfile_name = join(selected_mgfdir, parent_xml_filename + '-pep-reporter-merged.txt')
		with open(outfile_name, 'w') as outfile:
			for filename in os.listdir(xmldir):

				if filename.endswith('_nocal_table_corrected.txt'):
					with open(join(xmldir, filename)) as infile:
						for line in infile:
							if (not 'other proteins' in line) or (first==1):
								first = 0
								outfile.write(line)
		print outfile_name
		add_c_labels_to_duplicate_marker_column(outfile_name)
		print "Done!"
		return
	except Exception as err:
		print "error"
		print err
		return "Error combining xml and mgf"







	# I'm trying to make this function only do one thing, if I want more I can chain them with
	# async calls. So, I don't need a lot of this stuff.
	# mgf already selected from, xml is already processed. Just combine them here.

	








						
							