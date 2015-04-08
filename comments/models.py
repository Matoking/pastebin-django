from django.db import models

from sql import cursor

from pastes.models import Paste

class Comment(object):
    @staticmethod
    def get_comment_count(paste_id=None, char_id=None):
        """
        Get amount of comments on a paste
        """
        if char_id != None:
            paste_id = Paste.get_id(char_id)
                
        if paste_id == None:
            return 0
        
        query = """SELECT COUNT(*) AS count FROM comments
                   WHERE paste_id = %s"""
                   
        result = cursor.query_to_dict(query, [paste_id])
        
        return result["count"]