#!/bin/python

import time
import hashlib
import os, sys
import shutil
import json

import yaml
import yaml.constructor

from slugify import slugify

# import re
# import unidecode

# def slugify(str):
#     str = unidecode.unidecode(str).lower()
#     return re.sub(r'\W+','-',str)


try:
    # included in standard lib from Python 2.7
    from collections import OrderedDict
except ImportError:
    # try importing the backported drop-in replacement
    # it's available on PyPI
    from ordereddict import OrderedDict

class OrderedDictYAMLLoader(yaml.Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError, exc:
                raise yaml.constructor.ConstructorError('while constructing a mapping',
                    node.start_mark, 'found unacceptable key (%s)' % exc, key_node.start_mark)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


def mapFields(oldFields, newFields, config, values):
	fields = []
	for new in newFields:
		column = config['fields'][new]['column']
		if isinstance(column, list):
			value = ''
			for item in column:
				if item in oldFields:
					value += str(values[oldFields[item]])[1:-1]
				else:
					value += str(item)
			fields.append("'" + value + "'")
		elif column == None:
			# column is None
			value = ''
			default = config['fields'][new]['default']
			if default == None:
				value = "NULL"
			elif isinstance(default, str) and default[0] == '<':
				# special function
				splits = default[1:-1].split(':')
				action = splits[0]
				col = splits[1]
				if action == 'slug':
					value = "'" + str(slugify(values[oldFields[col]][1:-1])) + "'"
				if action == 'categories':
					key = values[oldFields[col]][1:-1].replace('_', '-').replace('-1', '').replace('--', '-')
					key = key.replace('fantasy-2', 'fantasy').replace('livealive', 'live-a-live').replace('3582', '358-2').replace('x2', 'x-2').replace('recoded', 're-coded')
					value = "'" + str(categories[key]) + "'"
			else:
				value = default
			# print str(new) + ' -> ' + str(column) + ' -> ... -> ' + str(default)
			fields.append(value)
		else:
			if isinstance(column, str) and column[0] == '<':
				splits = column[1:-1].split(':')
				action = splits[0]
				col = splits[1]
				if action == 'map':
					map = config['fields'][new]['map']

					key = values[oldFields[col]]
					if len(key) > 0 and key[0] == "'":
						key = key[1:-1]
					else:
						key = key
					
					if key in map:
						value = "'" + str(map[key]) + "'"
					else:
						print 'Key problem:'
						value = "'" + config['fields'][new][default] + "'"
					fields.append(value)
			else:
				key = oldFields[column]
				# print column
				# print key
				# print values[key]
				# print str(new) + ' -> ' + str(column) + ' -> ' + str(key) + ' -> ' + values[key]
				fields.append(values[key])

	q = ''
	for field in fields:
		q += str(field) + ','
	q = q[0:-1]
	return q


def splitValues(values):
	# print values

	parts = values.split(',')

	fields = []
	tmp = False

	for chars in parts:
		if tmp:
			tmp += ',' + chars
		else:
			tmp = chars

		# query begin and first value
		if len(tmp) > 6 and tmp[0:6] == 'INSERT':
			pos = tmp.index('(')
			fields.append(tmp[pos+1:])
			tmp = False
		else:
			if len(tmp) > 1 and tmp[-2:] == ');':
				pos = tmp.index(')')
				fields.append(tmp[0:pos])
				tmp = False
			else:
				# fields without comma
				# if tmp[0] == "'" and tmp[-1] == "'" and tmp[-2] != "\\":
				if tmp[0] == "'" and tmp[-1] == "'":
					if tmp[-2] != "\\" or (tmp[-3:-1] == "\\\\" and tmp[-4] != "\\") or (tmp[-5:-1] == "\\\\\\\\" and tmp[-6] != "\\"):
						# print tmp[-5:-1]
						fields.append(tmp)
						# fields.append(tmp[-5:])
						tmp = False
				else:
					if tmp.isdigit():
						fields.append(tmp)
						tmp = False
	# print fields
	return fields


# main code
if len(sys.argv) < 1:
	print 'Not enough arguments'
	sys.exit(1)
else:
	source = sys.argv[1]


input = open('category.json')
lines = input.read()
categories = json.loads(lines)
input.close()


config = 'tables/' + source + '/config.yml'

input = open(config)
mapping = yaml.load(input, Loader=OrderedDictYAMLLoader)
input.close()

table = mapping['table']


filename = 'tables/' + source + '/source.sql'

input = open(filename)
lines = input.read().splitlines()
input.close()


oldFields = {}
i = 0
# getting old table fields list
for line in lines:
	if len(line) > 3 and line[2] == '`':
		pos = line.index('`', 3)
		oldFields[line[3:pos]] = i
		i += 1


newFields = mapping['fields'].keys()

# table fields to final sql
tableFields = ''
for field in mapping['fields'].keys():
	tableFields += '`' + field + '`, '
tableFields = tableFields[0:-2] 


# analyzing flags
copy = False
records = ''

delay = 0

queries = []
values = []

queries_cnt = 0
values_cnt = 0

i = 0
for line in lines:
	if line[0:6] == 'INSERT':
		queries.append(line.split('),('))
		i += 1

i = 0
for query in queries:
	j = 0
	for value in query:
		values.append(splitValues(value))
		i += 1



sql = "USE `renaissance`;\n";
sql += "TRUNCATE TABLE `" + table + "`;\n";

i = 0
for query in queries:
	sql += 'INSERT INTO `' + table + '`'
	sql += ' (' + tableFields + ')'
	sql += ' VALUES '
	for value in query:
		sql += '(' + mapFields(oldFields, newFields, mapping, values[i]) + ')'
		sql += ','
		i += 1
	sql = sql[:-1]
	sql += ";\n"


output = open('tables/' +  source + '/' + 'output.sql', 'w')
output.write(sql)
output.close()

# print len(queries)
# print len(values)

# print values[2812][0]
# print values[2812][1]
# print values[2812][2]
# print values[2812][3]
# print values[2812][4]
# print values[2812][5]

