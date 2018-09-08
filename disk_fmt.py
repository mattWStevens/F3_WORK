# disk_fmt.py
# author: Matthew Stevens

# This script breaks down both AIX sar -d file and iostat files
# into multiple columns containing the information for each
# individual disk, including the timestamp if present. The output
# files are in a table-ready format.

# NOTE: Pass in "-i" for iostat files and "-s" for sar files.
# The arguments for file-type are case-insensitive.

import sys
import re

# This function determines when to start processing the data.
def start_processing(line):
	return line.lower().startswith("device") or line.lower().startswith("disk")

# This function makes sure that there is no extraneous information being
# extracted.
def ready(line):
	if line.startswith(" "):
		return False
	if line.startswith("---"):
		return False
	if line.startswith("\n"):
		return False
	if line.startswith("\t"):
		return False

	return True

f = sys.argv[2]
disks = {}
times, headers = [], []
start, time_interval = False, False
file_type = sys.argv[1]

# Process the iostat file.
if file_type.lower() == "-i":
	# Read the file.
	with open(f) as infile:
		lines = infile.readlines()

		for line in lines:
			if start_processing(line):
				start = True
				headers = re.split('\s{1,}', line.strip())[1:]
				continue	# already got headers, so skip to next line

			if start and ready(line):
				disk_name = re.split('\s{1,}', line.strip())[0]

				if disks.get(disk_name) == None:
					key = disk_name
					disks[key] = []
					# data for disk
					disk_info = re.split('\s{1,}', line.strip())[1:]

					# add a newline character after number to be inserted
					# into the list if it is the last number on the line
					for i in range(len(disk_info)):
						if i < len(disk_info) - 1:
							disks[key].append(disk_info[i].strip())

						else:
							disks[key].append(disk_info[i].strip() + "\n")

				else:
					key = disk_name
					info = re.split('\s{1,}', line.strip())[1:]

					# add a newline character after number to be inserted
					# into the list if it is the last number on the line
					for i in range(len(info)):
						if i < len(info) - 1:
							disks[key].append(info[i].strip())

						else:
							disks[key].append(info[i].strip() + "\n")

		first = True

		# Create output files.
		for key, values in disks.items():
			outname = "iostat." + key + ".out"
			outfile = open(outname, "w+")

			if first:
				# apply headers
				for i in range(len(headers)):
					if i < len(headers) - 1:
						outfile.write(headers[i] + "  ")

					else:
						outfile.write(headers[i] + "\n")

				first = False

			for value in values:
				if not value.endswith("\n"):
					outfile.write(value + "  ")

				else:
					outfile.write(value)

			headers.clear()	# clean list
			outfile.close()

# Process sar file.
elif file_type.lower() == "-s":
	# Read the file.
	with open(f) as infile:
		lines = infile.readlines()

		for line in lines:
			if "device" in line:
				start = True
				headers = re.split('\s{1,}', line.strip())[2:]
				continue

			if start and not re.match('^\s{1,}$', line):	# make sure to skip blank lines
				if time_interval and re.match('^\d\d:', line):
					time_interval = False
					times.clear()

				if not time_interval and re.match('^\d\d:', line):
					time = re.split('\s{1,}', line)[0].strip()
					times.append(time)
					time_interval = True

				if time_interval:
					if re.match('^\d\d:', line):
						info = re.split('\s{1,}', line)
						info = info[1:] # already gathered timestamp

						disk_name = info[0].strip()
						info = info[1:] # already gathered name

					else:
						if "average" in line or "Average" in line:
							break # done processing!

						else:
							info = re.split('\s{1,}', line.strip())
							disk_name = info[0].strip()
							info = info[1:] # already gathered name

					if disks.get(disk_name) == None:
						disks[disk_name] = []
						disks[disk_name].append(times[0])

						# add a newline character after number to be inserted
						# into the list if it is the last number on the line
						for i in range(len(info)):
							if i < len(info) - 1:
								disks[disk_name].append(info[i].strip())

							else:
								disks[disk_name].append(info[i].strip() + "\n")

						info.clear() # reset info list

					else:
						disks[disk_name].append(times[0])

						# add a newline character to end of line
						for i in range(len(info)):
							if i < len(info) - 1:
								disks[disk_name].append(info[i].strip())

							else:
								disks[disk_name].append(info[i].strip() + "\n")

						info.clear() # reset info list


	# Create output files.
	for key, values in disks.items():
		outname = "sar." + key + ".out"
		outfile = open(outname, "w+")

		outfile.write("timestamp" + "  ")

		for i in range(len(headers)):
			if i < len(headers) - 1:
				outfile.write(headers[i] + "  ")

			else:
				outfile.write(headers[i] + "\n")

		for value in values:
			if not value.endswith("\n"):
				outfile.write(value + "  ")

			else:
				outfile.write(value)

		outfile.close()

# Invalid file-type.
else:
	print("Invalid file-type:", file_type)
