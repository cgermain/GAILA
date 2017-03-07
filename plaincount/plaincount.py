import csv, sys, re, os, pprint
from collections import defaultdict
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
HEADER = ("Filename", "Protein", "Gene Name", "Count")

def main(plain_parse_file):
	#file_tree[filename][protein][gene_name] = count
	file_tree = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

	base_directory = os.path.split(plain_parse_file)[0]
	gpm_filename = os.path.split(plain_parse_file)[1].split(".txt")[0]

	with open(plain_parse_file, "rb") as in_file:
		csvreader = csv.reader(in_file, delimiter='\t')
		next(csvreader) #skip header
		for row in csvreader:
			filename = row[0]
			protein = row[16]
			gene_name = row[18]
			file_tree[filename][protein][gene_name] += 1

	timestamp = datetime.now().strftime(TIME_FORMAT)
	out_filename = os.path.join(base_directory, gpm_filename+"_count_"+timestamp+".csv")

	with open(out_filename, 'wb') as out_file:
		csvwriter = csv.writer(out_file)
		csvwriter.writerow(HEADER)
		for line in [(filename, protein, gene_name, file_tree[filename][protein][gene_name]) \
					for filename in file_tree \
					for protein in file_tree[filename] \
					for gene_name in file_tree[filename][protein]]:
			csvwriter.writerow(line)

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1].endswith(".txt"):
		main(sys.argv[1])
	else:
		print "Usage: python plaincount.py plain_parse_file"
	raw_input("press ENTER to exit")