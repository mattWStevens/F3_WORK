# errpt_format.py
# author: Matthew Stevens

import sys
import re
import os

# This script takes in an AIX errpt file and returns a summarized,
# table-ready layout for the desired host including each type of 
# resource name, the oldest and newest timestamps for each resource
# name, the description for each resource name, as well as the number
# of timestamps in total per resource name. The contents of the output
# file are also sorted in order by resource name.

# This function determines the hostname of the file.
def parse_hostname(line):
	hostname = line.split(":")[1]
	return hostname.strip()

# This function determines where to start parsing.
def start_parse(line):
	return line.startswith("IDENTIFIER")

# This function determines the oldest timestamp and the
# newest timestamp and then returns an array with the oldest
# timestamp followed by the newest timestamp.
def make_old_new_array(times_array):
	oldest = times_array[0]
	newest = 0
	new_array = []

	for time in times_array:
		if int(time) < int(oldest):
			oldest = time
		if int(time) > int(newest):
			newest = time
	
	new_array.append(oldest)
	new_array.append(newest)

	return new_array

home = os.getcwd() # store current path for later
master_dictionary = {}
des_dictionary = {}
count_dictionary = {}
start = False
f = sys.argv[1]
hostname = ""

# Read the file and store the import information in
# hash tables.
with open(f) as infile:
	lines = infile.readlines()

	for line in lines:
		if line[2:].strip().startswith("Hostname"):
			hostname = parse_hostname(line)

		if start_parse(line):
			start = True
			continue

		if start:		
			words = re.split('\s{1,}', line)
			des_array = words[5:]
			words = words[:5] # grab first 5 words
			description = " ".join(des_array)
			k = words[4]
			des_dictionary[k] = description		

			if master_dictionary.get(words[4]) == None:
				times = []
				times.append(words[1])
				key = words[4]
				master_dictionary[key] = times

			else:
				key = words[4]
				time = words[1]
				master_dictionary[key].append(time)					

# Go through and determine the count of the timestamps per resource type.
for key, values in master_dictionary.items():
	count = len(values)
	count_dictionary[key] = count


# Go through and determine the oldest and newest timestamps for
# each resource type.
for key, values in master_dictionary.items():
	values = make_old_new_array(values)
	master_dictionary[key] = values

filename = hostname + ".tmp"
outfile = open(filename, "w+")

index = 0

# Write the temporary outfile.
for key, values in master_dictionary.items():
	for value in values:
		outfile.write(value + "  ")
		index += 1

		# add in count information after timestamp info
		if index == 2:
			outfile.write(str(count_dictionary.get(key)) + "  ")
			index = 0

	outfile.write(key + "  " + des_dictionary.get(key) + "\n")

outfile.close()

# Write the final file.
final_filename = hostname + "_errpt.txt"
final_file = open(final_filename, "w+")

# Prep headers for final file
final_file.write("OLDEST  NEWEST  COUNT  RESOURCE_NAME  DESCRIPTION\n")

with open(filename) as f_file:
	lines = f_file.readlines()

	for line in sorted(lines, key=lambda line: line.split("  ")[3]):
		final_file.write(line)

final_file.close()
	
# Remove temporary file.
r_file = home + "/" + filename
os.remove(r_file)	
