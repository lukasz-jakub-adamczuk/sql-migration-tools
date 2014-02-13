sql-migration-tools
===================

simple but useful scripts for unusual database migrations

## Requirements

All scripts were tested and used with **Python 2.7.2**

## Tools

### sqlDumpSpliter

Script designed to split SQL dumps, basically MySQL dump files. Tables (definitions and data) found in the dump file will be saved in *source.sql* files grouped by directories named by *tables* names. Usage is very simple and easy:

	python sqlDumpSpliter.py filename

but ensure you list only one parameter in that way. If you want to use more options with script type them with param name and value, like:

	python sqlDumpSpliter.py --file=filename --ignore-prefixes=smf_

#### Avaiable params

**--file=filename**, specify SQL dump filename to split definitions and data of found tables

**--ignore-prefixes=prefix**, type prefix or prefixes divided by comma to ignore specific tables from spliting

### sqlDumpConverter

Script designed to convert SQL dumps, basically MySQL dump files. Tables (definitions and data) found in the dump file will be saved in *source.sql* files grouped by directories named by *tables* names. Usage is very simple and easy:

	python sqlDumpConverter.py filename

but ensure you list only one parameter in that way. If you want to use more options with script type them with param name and value, like:

	python sqlDumpConverter.py --file=filename --ignore-prefixes=smf_

#### Avaiable params

**--file=filename**, specify SQL dump filename to split definitions and data of found tables

**--ignore-prefixes=prefix**, type prefix or prefixes divided by comma to ignore specific tables from spliting
