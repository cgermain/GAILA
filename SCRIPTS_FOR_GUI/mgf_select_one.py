from __future__ import print_function
from __future__ import absolute_import
import os
from os.path import join
from os.path import basename
import subprocess
from pyteomics import mgf
import csv
import re
import pandas as pd
from . import utility
import multiprocessing
import atexit
import signal
import glob

debug = False

#all of the initial files have got to be relative to this directory.
this_dir = os.path.dirname(os.path.realpath(__file__))

def run_perl(perl_command):
	mgf_name = os.path.basename(perl_command[4]).split(".")[0]+".mgf"
	utility.print_timestamp("MGF selection - Start - " + mgf_name)
	try:
		a = subprocess.call(perl_command)
		if a:
			#raise 
			return "Error selecting from mgf (no recalibration)"
		else:
			utility.print_timestamp("MGF selection - Complete - " + mgf_name)
			return 0
	except:
		raise

def select_only_one(mgf_read_dir_path, mgf_write_path, mgf_txt_write_dir_path, mz_error, reporter_type, inverse_file, min_intensity, min_reporters, should_select, mgf_file_list):
	perl_file = 'mgf_select_only_one.pl'

	for mgf_file_name in mgf_file_list:
		mgf_txt_write_path = join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter')
		if os.path.isfile(mgf_txt_write_path):
			return "mgf_txt_write_path is already a file"
		if should_select == "1" and os.path.isfile(mgf_write_path):
			return "mgf_write_path is already a file"

	this_dir = os.path.dirname(os.path.realpath(__file__))
	corr_path = join(this_dir, "inverse_files", inverse_file)
	if not os.path.isfile(corr_path):
		return "Cannot find inverse file"
	corr = pd.read_table(corr_path)
	corr=corr.drop('Unnamed: 0', axis=1)
	matrixreal_string = utility.get_matrixreal_string_from_dataframe(corr)

	perl_command_list = [('perl', join(this_dir, perl_file), join(mgf_read_dir_path, mgf_file_name), join(mgf_write_path, mgf_file_name), join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter'), str(mz_error), reporter_type, str(min_intensity), str(min_reporters), str(should_select), matrixreal_string) for mgf_file_name in mgf_file_list]

	pool = multiprocessing.Pool(multiprocessing.cpu_count())

	utility.print_timestamp("MGF Selection - Using " + str(multiprocessing.cpu_count()) + " threads")

	try:
		pool.map(run_perl, perl_command_list)

	except:
		pool.terminate()
		pool.join()
		raise

	return 0

def select_only_one_recalibrate(mgf_read_dir_path, mgf_write_path, mgf_txt_write_dir_path, mz_error, reporter_type, inverse_file, min_intensity, min_reporters, should_select, recal_mz_error, mgf_file_list):
	perl_file = 'mgf_select_only_one_with_recalibrate.pl'

	for mgf_file_name in mgf_file_list:
		mgf_txt_write_path = join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter')
		if os.path.isfile(mgf_txt_write_path):
			return "mgf_txt_write_path is already a file"
		if should_select == "1" and os.path.isfile(mgf_write_path):
			return "mgf_write_path is already a file"

	this_dir = os.path.dirname(os.path.realpath(__file__))
	corr_path = join(this_dir, "inverse_files", inverse_file)
	if not os.path.isfile(corr_path):
		return "Cannot find inverse file"
	corr = pd.read_table(corr_path)
	corr=corr.drop('Unnamed: 0', axis=1)
	matrixreal_string = utility.get_matrixreal_string_from_dataframe(corr)

	perl_command_list = [('perl', join(this_dir, perl_file), join(mgf_read_dir_path, mgf_file_name), join(mgf_write_path, mgf_file_name), join(mgf_txt_write_dir_path, mgf_file_name.split('.mgf')[0] + '.reporter'), str(mz_error), reporter_type, str(min_intensity), str(min_reporters), str(should_select), str(recal_mz_error), matrixreal_string) for mgf_file_name in mgf_file_list]

	pool = multiprocessing.Pool(multiprocessing.cpu_count())

	utility.print_timestamp("MGF Selection w/ Recalibrate - Using " + str(multiprocessing.cpu_count()) + " threads")

	try:
		pool.map(run_perl, perl_command_list)

	except:
		pool.terminate()
		pool.join()
		raise
		
	return 0

def call_mgf_reader(mgf_list_for_pool):
	utility.print_timestamp("Plain Parse MGF - Start - " + basename(mgf_list_for_pool[0]))

	with open(mgf_list_for_pool[1],'w') as mgf_csv:
		with mgf.read(mgf_list_for_pool[0]) as mgf_reader:
			csv_writer = csv.writer(mgf_csv, delimiter='\t')
			csv_writer.writerow(['filename', 'scan', 'charge', 'rt', 'ms1 intensity'])
			for spectrum in mgf_reader:
				scans = spectrum['params']['scans']
				charge = re.sub(r'[^\d.]+', '', str(spectrum['params']['charge']))
				rt = spectrum['params']['rtinseconds']
				ms1_intensity = spectrum['params']['pepmass'][1]
				csv_writer.writerow([os.path.basename(mgf_list_for_pool[0]), scans, charge, rt, ms1_intensity])

	utility.print_timestamp("Plain Parse MGF - Complete - " + basename(mgf_list_for_pool[0]))

def plain_parse(mgf_read_dir_path, mgf_txt_write_dir_path):
	this_dir = os.path.dirname(os.path.realpath(__file__))

	mgf_file_list = [f for f in os.listdir(mgf_read_dir_path) if f.endswith('.mgf')]
	
	mgf_list_for_pool = [(join(mgf_read_dir_path, mgf_file), join(mgf_txt_write_dir_path, mgf_file.split('.mgf')[0] + '.reporter')) for mgf_file in mgf_file_list]

	pool = multiprocessing.Pool(multiprocessing.cpu_count())
	utility.print_timestamp("Plain Parse MGF - Using " + str(multiprocessing.cpu_count()) + " threads")

	try:
		pool.map(call_mgf_reader, mgf_list_for_pool)

	except:
		pool.terminate()
		pool.join()
		raise
		
	return 0

