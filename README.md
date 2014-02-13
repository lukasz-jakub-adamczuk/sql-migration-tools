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

	python sqlDumpSpliter.py --file=filename --exclude-prefixes=smf_

#### Available params

**--file=filename**, specify SQL dump filename to split definitions and data of found tables

**--exclude-prefixes=prefix**, type prefix or prefixes divided by comma to exclude specific tables for spliting

**--exclude=table**, type table name exclude specific table for spliting

**--include-prefixes=prefix**, type prefix or prefixes divided by comma to include specific tables for spliting

**--include=table**, type table name include specific table for spliting

Script splits all tables from dump by default, but it's possible to explude some tables by params. If exclusion is to wide, there possibility to include again some table. **Be careful with using both type params, and remember checking order (include-prefixes, include, exclude-prefixes, exclude)**

### sqlDumpConverter

Script designed to convert SQL dumps, generally `(INSERT INTO)` parts to a new queries. Conversion way is defined in special *config.yml* file. Usage is very simple and easy:

	python sqlDumpConverter.py --table=tablename

but ensure you list only one parameter in that way. If you want to use more options with script type them with param name and value, like:

	python sqlDumpConverter.py --table=tablename

#### Available params

**--table=tablename**, specify table name to convert data

## config.yml

	db: database_name
	table: table_name
	fields:
	  id_article:
	    column: old_a_id
	    default: null
	  id_author:
	    column: old_author
	    default: null
	  id_template:
	    column:
	    default: null
	  title:
	    column: tytul
	    default: "''"
	  slug:
	    column:
	    default: '<slug:tytul>'
	  old_url:
	    column: [d_id, ',', a_alias, ',articles.html']
	    default: null
	  verified:
	    column: good
	    default: 0
	  visible:
	    column: '<map:hidden>'
	    default: 1
	    map:
	      '0': 1
	      '1': 0
	  deleted:
	    column:
	    default: 0

### Configuration explaination

	db: database_name
	table: table_name

Params names `db` and `table` sets output database name and table name.

	fields:
	  id_article:
	    column: old_a_id
	    default: null
	  id_template:
	    column:
	    default: null

Param `fields` defines how to convert expected fields. Be sure to define all field need to create new row in table. Each field is defined by `key` related to a table column name. Genearally, field has a two attributes: `column` and `default`. Use `column` to get value from specified column in dump file. Param `default` value will be used for a new column which doesn't exists in old structure.

	  old_url:
	    column: [d_id, ',', a_alias, ',articles.html']
	    default: null

It possible that column value should be concatenation of other columns or string. For this case `column` need to be defined as array with column names or string used to value output.

	  slug:
	    column:
	    default: '<slug:tytul>'
	  visible:
	    column: '<map:hidden>'
	    default: 1
	    map:
	      '0': 1
	      '1': 0

There's special notation to modify values before using for a query. Params values specified in `<` and `>` with `:` describes special action on specified column. For example modifier `<slug:tytul>` will slugify column `tytul` value.

Map modifier works as a mapper one value to another. Column values specified for mapping are defined in `map` element. For example `<map:hidden>` will map values of `hidden` column. If value equals '0' then returns 1, and return 0 when '1' will be value.

## License

Distributed under the MIT license