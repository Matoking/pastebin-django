import math

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