from itertools import *
from django.db import connection

# http://doughellmann.com/2007/12/30/using-raw-sql-in-django.html
def query_to_list(query, query_args):
    """
    Perform a query and return it as a list of dicts
    """
    cursor = connection.cursor()
    
    cursor.execute(query, query_args)
    
    # If no rows were returned, return an empty list instead
    if cursor.description == None:
        return []
    
    col_names = [desc[0] for desc in cursor.description]
    
    results = []
    
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        results.append(row_dict)
        
    return results

def query_to_dict(query, query_args):
    """
    Performs a query and returns its first result as a dict
    """
    result = query_to_list(query, query_args)
    
    if len(result) == 0:
        return None
    else:
        return result[0]
    
def query(query, query_args=[]):
    """
    Performs a query, raising any possible exceptions
    """
    cursor = connection.cursor()
    
    try:
        cursor.execute(query, query_args)
    except:
        raise