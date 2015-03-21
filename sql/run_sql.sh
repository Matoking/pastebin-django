#!/bin/sh
psql pastesite < drop_tables.sql
psql pastesite < create_tables.sql
psql pastesite < add_test_data.sql