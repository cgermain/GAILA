import csv, sys, os
from collections import defaultdict
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
HEADER = ("Filename", "Protein", "Gene Name", "Count")

def count_proteins(plain_parse_file):
	#file_tree[filename][protein][gene_name] = count
	file_tree = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

	base_directory = os.path.split(plain_parse_file)[0]
	gpm_filename = os.path.split(plain_parse_file)[1].split(".txt")[0]

	total_line_count = buffered_line_count(plain_parse_file)
	current_line_count = 0

	print "Plaincount's total runtime depends on filesize.\n"

	with open(plain_parse_file, "rb") as in_file:
		previous_percentage_complete = 0
		csvreader = csv.reader(in_file, delimiter='\t')
		next(csvreader) #skip header
		print "Reading..."
		for row in csvreader:
			current_line_count += 1
			filename = row[0]
			protein = row[16]
			gene_name = row[18]
			file_tree[filename][protein][gene_name] += 1
			
			percentage_complete = 100*current_line_count/total_line_count
			if percentage_complete > previous_percentage_complete:
				previous_percentage_complete = percentage_complete
				print "total lines: " + str(total_line_count) + "  |  current line: " + str(current_line_count) + "  |  percentage complete: " + str(percentage_complete) + "%\r",
				sys.stdout.flush()

	timestamp = datetime.now().strftime(TIME_FORMAT)
	out_filename = os.path.join(base_directory, gpm_filename+"_count_"+timestamp+".txt")
	print "\n"
	print "Writing",
	with open(out_filename, 'wb') as out_file:
		previous_percentage_complete = 0
		current_line_count = 0
		total_line_count = len(file_tree.keys())
		csvwriter = csv.writer(out_file, delimiter='\t')
		csvwriter.writerow(HEADER)
		for line in [(filename, protein, gene_name, file_tree[filename][protein][gene_name]) \
					for filename in file_tree \
					for protein in file_tree[filename] \
					for gene_name in file_tree[filename][protein]]:
			csvwriter.writerow(line)
			sys.stdout.write(".")

	print "\nSaved: " + out_filename + "\n"

def buffered_line_count(filename):
    f = open(filename)                  
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines\

if __name__ == "__main__":
	if len(sys.argv) == 2 and sys.argv[1].endswith(".txt"):
		main(sys.argv[1])
	else:
		print "Usage: python plaincount.py plain_parse_file.txt"
		print "or drop plain_parse_file.txt onto the plaincount.exe icon"
	raw_input("press ENTER to exit")