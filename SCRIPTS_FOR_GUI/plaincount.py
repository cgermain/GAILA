import csv, sys, os
from collections import defaultdict
from datetime import datetime

TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
HEADER = ("Filename", "Protein", "Broad ID", "Count")

def count_proteins(plain_parse_file, output_dir, timestamp):
	#file_tree[filename][protein][broad_id] = count
	file_tree = defaultdict(lambda:defaultdict(lambda:defaultdict(lambda:0)))

	base_directory = os.path.split(plain_parse_file)[0]
	gpm_filename = os.path.split(plain_parse_file)[1].split(".txt")[0]

	total_line_count = 0
	current_line_count = 0

	if output_dir == 'Default IDEAA Archive':
		output_dir = os.path.join(sys.path[0], "Archive", "")

	try:
		total_line_count = buffered_line_count(plain_parse_file)
		with open(plain_parse_file, "rb") as in_file:
			previous_percentage_complete = 0
			csvreader = csv.reader(in_file, delimiter='\t')
			header = next(csvreader) #skip header
			filename_index = header.index("filename")
			protein_index = header.index("protein")
			broad_index = header.index("broad_id")

			if filename_index != -1 and protein_index != -1 and broad_index != -1:
				print "Total lines in plain parse file: " + str(total_line_count)
				print "Reading plain parse file..."
				for row in csvreader:
					current_line_count += 1
					filename = row[filename_index]
					protein = row[protein_index]
					broad_id = row[broad_index]
					file_tree[filename][protein][broad_id] += 1
					
					percentage_complete = 100*current_line_count/total_line_count
					if percentage_complete > previous_percentage_complete:
						previous_percentage_complete = percentage_complete
						sys.stdout.write(".")
			else:
				return "Error in formatting of plain parse file.  Header index not found.", False
	except IOError as e:
		return "Error opening plain parse file: " + plain_parse_file, 0
	except ValueError as e:
		return "Error: Column header improperly formatted in plain parse file.", 0
	except:
		return "Error in count proteins while reading.", 0

	if not os.path.isdir(os.path.join(output_dir, "protein_count_"+timestamp)):
		os.makedirs(os.path.join(output_dir, "protein_count_"+timestamp))
		
	out_filename = os.path.join(output_dir, "protein_count_"+timestamp, gpm_filename+"_count_"+timestamp+".txt")
	print "\n"
	print "Writing..."
	try:
		with open(out_filename, 'wb') as out_file:
			previous_percentage_complete = 0
			current_line_count = 0
			csvwriter = csv.writer(out_file, delimiter='\t')
			csvwriter.writerow(HEADER)
			out_lines = [(filename, protein, broad_id, file_tree[filename][protein][broad_id]) \
						for filename in file_tree \
						for protein in file_tree[filename] \
						for broad_id in file_tree[filename][protein]]
			total_lines = len(out_lines)
			for line in out_lines:
				current_line_count += 1
				csvwriter.writerow(line)
				percentage_complete = 100*current_line_count/total_lines
				if percentage_complete > previous_percentage_complete:
					previous_percentage_complete = percentage_complete
					sys.stdout.write(".")

		print "\nSaved: " + out_filename + "\n"
		return out_filename, 1
	except IOError as e:
		return "Error opening output file.", 0
	except:
		return "Error in count proteins while writing.", 0

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