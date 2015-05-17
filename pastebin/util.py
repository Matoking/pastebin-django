import math
import datetime

class Paginator(object):
    @staticmethod
    def get_pages(current_page, entries_per_page, total_entries):
        entries = []
        
        total_pages = math.ceil(float(total_entries) / float(entries_per_page))
        
        # Add the first and previous pages
        if current_page != 1:
            entries.append("first")
            entries.append("previous")
        
        # Add four pages before the current page
        for i in reversed(range(0, 4)):
            page = current_page - i - 1
            
            if page >= 1:
                entries.append(page)
                
        # Add the current page
        entries.append(current_page)
        
        # Add four pages after the current page
        for i in range(0, 4):
            page = current_page + i + 1
            
            if page <= total_pages:
                entries.append(page)
                
        # Add the next and last page
        if current_page != total_pages:
            entries.append("next")
            entries.append("last")
            
        return entries
    
def queryset_to_list(queryset, fields=[], datetime_to_unix=True):
    """
    Converts a given Queryset into a list of dicts
    
    fields takes a list of model fields to retrieve. In addition, field lookups can be used
    and an equals sign can be used to separate the field lookup and the name to be used for the field
    in the result
    (eg. user__username=username)
    
    If datetime_to_unix is True, convert datetime objects to Unix timestamps
    """
    if queryset.count() == 0:
        return []
     
    # A dict of fields
    # Key describes the field lookup to use,
    # value describes the key to use for the retrieved value
    # Eg. user__username=username will have the key 'username' in the dict
    field_names = {}
    
    for field_name in fields:
        if not "=" in field_name:
            field_names[field_name] = field_name
        else:
            field_names[field_name[:field_name.find("=")]] = field_name[field_name.find("=")+1:]
    
    rows = list(queryset.values(*field_names.keys()))
    
    for i, row in enumerate(rows):
        for row_key, row_entry in row.iteritems():
            field_name = field_names[row_key]
            
            # Rename the field if we want a different name
            if row_key != field_name:
                value = row[row_key]
                del rows[i][row_key]
                rows[i][field_name] = value
                
            if datetime_to_unix:
                if type(rows[i][field_name]) is datetime.datetime:
                    rows[i][field_name] = int(rows[i][field_name].strftime("%s"))
                    
    return rows