#!/bin/sh
psql pastesite < drop_tables.sql
psql pastesite < create_tables.sql
