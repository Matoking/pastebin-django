from django.test.runner import DiscoverRunner
from sql import cursor

from pastebin import settings

import os

class SQLTestRunner(DiscoverRunner):
    """
    A test runner that runs SQL queries to create databases when setting up the test environment
    and drops the said tables after the tests have been ran
    """
    def setup_databases(self, **kwargs):
        result = super(SQLTestRunner, self).setup_databases(**kwargs)
        
        # Run SQL queries to create the databases        
        self.run_sql_file("../sql/drop_tables.sql")
        self.run_sql_file("../sql/create_tables.sql")
        
        return result
    
    def run_sql_file(self, filepath):
        """
        Runs the SQL queries in the file
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        with open(current_dir + "/" + filepath) as f:
            query = f.read()
            
            cursor.query(query)