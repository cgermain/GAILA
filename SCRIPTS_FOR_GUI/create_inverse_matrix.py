
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
import sys, os, shutil


def create_inverse(full_path_to_crossover):
	# table = pd.read_table(full_path_to_crossover)
	# table_dict = {}
	# for (index, row) in table.iterrows():
	# 	s = sum(row)
	# 	i_s = 1.0 / s
	# 	sub_l = [i_s for p in row]
	# 	l.append(sub_l)
	# table = 
	a = open(full_path_to_crossover, 'r')
	firstline = a.readline()
	a.close()
	firstline = firstline.strip()
	firstline_arr = firstline.split('\t')
	matrix = np.loadtxt(full_path_to_crossover, skiprows=1)
	print "matrix: "
	print matrix
	row_sums = matrix.sum(axis=1)
	normalized_matrix = matrix / row_sums[:, np.newaxis]
	print "normalized matrix: "
	print normalized_matrix
	omitted = []
	for row in normalized_matrix:
		new_row = row[0:len(row)-1]
		omitted.append(new_row)
	print "omitted:"
	print omitted
	new_matrix = np.matrix(omitted)
	inverse = np.linalg.inv(new_matrix)
	new_path = full_path_to_crossover + '-inverse'
	np.savetxt(new_path, inverse, delimiter='\t')
	print "inverse matrix: "
	print inverse


create_inverse('/Users/samlobel/Code/DAD/FINAL_LOBEL_GUI/inverse_creation/tmt6_new.txt')



