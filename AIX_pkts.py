# AIX_pkts.py
# author: Matthew Stevens

import sys
import re

# This script reads an AIX netstat_-i file and produces an output file based upon
# the host name containing a table-ready description of the names, the number of
# incoming and outgoing packets, as well as the number of incoming and outgoing
# errors.

# This function returns whether or not the line
# to begin reading at has been reached yet.
def start_parsing(line):
	return line.startswith("Name")

# This function creates an array with only the desired elements.
def make_append_array(start_array):
	append_array = []

	for i in range(len(start_array)):
		if i == 0 or i == 3 or i == 4 or i == 5 or i == 6:
			append_array.append(start_array[i])

	return append_array

# This function retrieves the hostname from the target file
# and returns the output filename.
def make_output_filename(line):
	line = line[2:].strip()
	hostname = line.split(":")[1].strip()
	end_index = hostname.find(".")
	hostname = hostname[0:end_index]
	filename = hostname + "_pkts.out"

	return filename

# This function formats an output string to be written to the
# output file.
def format_output(output_array):
	output_string = ""

	for i in range(len(output_array)):
		if i != len(output_array) - 1:
			add_string = output_array[i] + "  "
			output_string += add_string
		else:
			add_string = output_array[i] + "\n"
			output_string += add_string

	return output_string			

f = sys.argv[1]
file_array = []
start = False
output_file = ""

# Read the file!
with open(f) as infile:
	lines = infile.readlines()

	for line in lines:
		if line[2:].strip().startswith("Hostname"):
			output_file = make_output_filename(line)

		if start_parsing(line):
			start = True
			continue	# skip headers

		if start:
			line = line.strip() # remove unwanted whitespace
			words = re.split('\s{1,}', line)		

			# make sure only includes 8 elements
			if len(words) == 9:
				del words[3]

			add_items = make_append_array(words)
			file_array.append(add_items)
			
outfile = open(output_file, "w+")

# Generate output file headers.
outfile.write("Name  Ipkts  Ierrs  Opkts  Oerrs\n")

# Write the outfile!
for f_list in file_array:
	write_string = format_output(f_list)
	outfile.write(write_string)

outfile.close()
