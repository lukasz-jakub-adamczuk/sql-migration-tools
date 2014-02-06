#!/bin/python

import time
import hashlib
import os, sys
import shutil


def parseArgs(args):
	options = {}
	for param in args:
		if len(param) > 2:
			if param[0:2] == '--':
				pos = param.index('=')
				key = param[2:pos]
				val = param[pos+1:]
				if val == 'false' or val == 'true':
					val = bool()
				options[key] = val
	return options

def isIgnoredTable(table):
	for prefix in ignored_prefixes:
		if table[0:len(prefix)] == prefix:
			return True
	return False

# options
# --ignore-prefixes
# --file

# main code
if len(sys.argv) < 1:
	print 'Not enough arguments'
	sys.exit(1)
else:
	options = parseArgs(sys.argv)

# print sys.argv
# print options

if options['file']:
	filename = options['file']
else:
	sys.exit(1)

ignored_prefixes = []
if options['ignore-prefixes']:
	ignored_prefixes = options['ignore-prefixes'].split(',')
	
# read dump and split file content
input = open(filename)
lines = input.read().splitlines()
input.close()


# definitions of limiters
ldelim = 'CREATE TABLE'
rdelim = 'UNLOCK TABLES;';


# workflow flags
ignore = False
copy = False
save = False

# records ready to copy and save
records = ''

# summary variables
copied = []
ignored = []

for line in lines:
	if line[0:12] == ldelim:
		start = line.index('`') + 1
		stop = line.index('`', start)
		table = line[start:stop]
		if isIgnoredTable(table):
			copy = False
			ignore = True
			ignored.append(table)
			# print 'Table `' + str(table) + '` was ignored'
		else:
			copy = True
			copied.append(table)
			# print 'Table `' + str(table) + '` was copied'
		# print line
		# delay = 0

	if line == rdelim:
		# print line
		copy = False
		if ignore == False:
			save = True
		else:
			save = False
			ignore = False

	if copy == True:
		records += line + "\n"

	if delay == 12:
		copy = False
	delay += 1


	if save == True:
		path = 'tables/' + table

		if (os.path.exists(path) == False):
			os.makedirs(path)

		output = open(path + '/' + 'source.sql', 'w')
		output.write(records)
		output.close()
		records = ''
		save = False;

print '\nSUMMARY'
print 'Copied tables:  ' + str(len(copied))
print 'Ignored tables: ' + str(len(ignored))
