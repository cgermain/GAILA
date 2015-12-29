import mgf_select_one

from time import time



def test_one():
	# def select_only_one_recalibrate(mgf_read_path, mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, min_intensity, min_reporters, should_select, recal_mz_error):
	mgf_read_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/QE00643T.mgf'
	mgf_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_files/QE00643T_RECAL.mgf'
	mgf_txt_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_txt_files/QE00643T_RECAL.mgf.txt'
	mz_error = 20
	reporter_type = 'TMT10'
	min_intensity = 1000
	min_reporters = 2
	should_select = '1'
	recal_mz_error = 5
	a = mgf_select_one.select_only_one_recalibrate(mgf_read_path, mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, min_intensity, min_reporters, should_select, recal_mz_error)
	print "a: " + str(a)
	print "done"

def test_two():
	# def select_only_one_recalibrate(mgf_read_path, mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, min_intensity, min_reporters, should_select, recal_mz_error):
	mgf_read_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/QE00643T.mgf'
	mgf_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_files/QE00643T.mgf'
	mgf_txt_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_txt_files/QE00643T.mgf.txt'
	mz_error = 20
	reporter_type = 'TMT10'
	min_intensity = 1000
	min_reporters = 2
	should_select = '1'
	# recal_mz_error = 5
	a = mgf_select_one.select_only_one(mgf_read_path, mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, min_intensity, min_reporters, should_select)
	print "a: " + str(a)
	print "done"


def timeit():
	now = time()
	mgf_read_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/QE00643T.mgf'
	mgf_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_files/timing_QE00643T_RECAL.mgf'
	mgf_txt_write_path = '/Users/samlobel/Code/DAD/Lobel_GUI/DATA_TMT10test/TESTmgffiles10/mgf_txt_files/timing_QE00643T_RECAL.mgf.txt'
	mz_error = 20
	reporter_type = 'TMT10'
	min_intensity = 1000
	min_reporters = 2
	should_select = '1'
	recal_mz_error = 5
	a = mgf_select_one.select_only_one_recalibrate(mgf_read_path, mgf_write_path, mgf_txt_write_path, mz_error, reporter_type, min_intensity, min_reporters, should_select, recal_mz_error)
	print "a: " + str(a)
	print "done"
	print "Time difference is " + str(time() - now)


# timeit() 
# With the last skipping, it took 6.26912117004 seconds
# Without it takes 9.67227983475. That's a 50% speedup! Or a 33% reduction!


# test_two()

# test_one()
