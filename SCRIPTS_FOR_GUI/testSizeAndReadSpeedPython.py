import os
from time import time
import re

file_path = '../DATA_TMT10Test/TESTmgffiles10/QE00643T.mgf'
statinfo = os.stat(file_path)

print statinfo.st_size

f = open(file_path, 'r')

# while a = f.readline():
t_1 = time()
i = 0
for line in f:
	# print line
	if re.match(line, 'SCAN'):
		print line
	i += 1
	if i % 1000 == 0:
		print i

print time() - t_1
