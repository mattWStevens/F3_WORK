# suse_pkt.py
# author: Matthew Stevens

import sys
import os
import re

# This script reads an ifconfig -a file from a SUSE linux environment and
# returns a table-ready summary file containing the names, number of incoming
# and outgoing packets, number of incoming and outgoing errors, as well as
# the number of incoming and outgoing bytes.


# This function parses the lines containing the
# the input/output packet information.
def parse_pkt_info(line):
	line = line.strip() # remove excess whitespace
	words = line.split(":")
	
	# obtain first number
	first_extract = words[1]
	first_end_index = first_extract.find(" ")
	first_num = first_extract[0:first_end_index]

	# obtain second number
	second_extract = words[2]
	second_end_index = second_extract.find(" ")
	second_num = second_extract[0:second_end_index]

	# return numbers in easily split string
	return_string = first_num + " " + second_num

	return return_string

# This function determines if the information on this line
# is important.
def want_line(line):
	return line.startswith("RX") or line.startswith("TX")

# This function looks for the hostname file in the current directory.
def find_host():
	hostname = ""

	for root, dirs, files in os.walk(os.getcwd()):
		for f in files:
			if re.match("hostname", f):
				hostname = f

	return hostname

f = sys.argv[1]
got_name = False
file_array = []
name = ""

# Read the file.
with open(f) as infile:
	lines = infile.readlines()

	for line in lines:
		if not got_name:
			if not line.startswith("#"):
				name = line.split(" ")[0].strip()
				got_name = True
				file_array.append(name)

		if line.startswith("Base"):
			got_name = False

		if got_name:
			if want_line(line):
				append_string = parse_pkt_info(line)
				file_array.append(append_string)

# Look for hostname in current directory and
# create output filename from it if it is present.
# Otherwise, create the output filename from the
# input filename.
if find_host() != "":
	hostname = ""

	with open(find_host()) as hostfile:
		lines = hostfile.readlines()

		for line in lines:
			hostname += line.strip()

	outname = hostname + "_pkts.out"

else:
	end_index = f.find(".")
	outname = f[0:end_index] + "_pkts.out"

outfile = open(outname, "w+")

# Write headers.
outfile.write("Name  Ipkts  Ierrs  Opkts  Oerrs  Ibytes  Obytes\n")

column = 1

# Write the file.
for f in file_array:
	if column != 7:
		outfile.write(f + "  ")

	if column == 7:
		outfile.write(f + "\n")
		column = 1 # reset column count for new line

	column += 1

outfile.close()
