# centos_pkts.py
# author: Matthew Stevens

import sys
import re
import os

# This script reads an ifconfig -a file from a centOS linux environment
# and returns a table-ready summary file containing the names, number of
# incoming and outgoing packets, number of incoming and outgoing errors,
# as well as the number of incoming and outgoing bytes.

# This function determines if the given line is the start of
# a new section.
def start_section(line):
	return re.match('\w{1,}:', line)

# This function parses the line for the individiual information
# that is important to each section and returns it.
def parse_info(line):
	if line.find("packets") != -1:
		line = line.strip()
		word = line[10:].strip()
		byte_count = parse_bytes(word)
		end_index = word.find(" ")
		number = word[0:end_index] + " " + byte_count

	if line.find("errors") != -1:
		line = line.strip()
		word = line[9:].strip()
		end_index = word.find(" ")
		number = word[0:end_index]

	return number

# This function parses out the byte count from the
# given line.
def parse_bytes(line):
	parts = line.split(" ")
	byte_count = parts[3]

	return byte_count	

# This function determines if the given line needs to be parsed or not.
def want_line(line):
	if line.strip().startswith("RX"):
		return True
	if line.strip().startswith("TX"):
		return True

	return False

# This function looks for the hostname file in the current directory.
def find_host():
	hostname = ""

	for root, dirs, files in os.walk(os.getcwd()):
		for f in files:
			if re.match("hostname", f):
				hostname = f

	return hostname

f = sys.argv[1]
file_array = []
name = ""
start = False

# Read the file.
with open(f) as infile:
	lines = infile.readlines()

	for line in lines:
		if start_section(line):
			line = line.strip()
			end_index = line.find(":")
			name = line[0:end_index].strip()
			file_array.append(name.strip())

		if want_line(line):
			# check to see if line contains byte information
			# for special handling
			if line.find("bytes") != -1:
				numbers = parse_info(line).split(" ")
				number = numbers[0].strip()
				byte_count = numbers[1].strip()
				
				file_array.append(number)
				file_array.append(byte_count)

			else:
				number = parse_info(line)
				file_array.append(number)

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
outfile.write("Name  Ipkts  Ibytes  Ierrs  Opkts  Obytes  Oerrs\n")

count = 1

# Write output file.
for f in file_array:
	if count < 7:
		outfile.write(f + "  ")
		count += 1

	else:
		outfile.write(f + "\n")
		count = 1

outfile.close()
