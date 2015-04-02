from django.db import models, transaction
from django.contrib.auth.models import User

from sql import cursor

from pastes.models import Paste

import datetime

class Favorite(object):
    """
    Handles user's favorites
    """
    @staticmethod
    def add_favorite(user, char_id=None, id=None):
        """
        Add a paste to user's favorites
        """
        if char_id != None:
            id = Paste.get_id(char_id)
                
        if id == None:
            return False
                
        current_datetime = datetime.datetime.now()
                
        query = """INSERT INTO favorites (paste_id, user_id, added)
                   SELECT %s, %s, %s
                   WHERE NOT EXISTS ( SELECT 1 FROM favorites WHERE paste_id = %s AND user_id = %s )"""
                   
        result = cursor.query_to_dict(query, [id, user.id, current_datetime, id, user.id])
        
        return True
        
    @staticmethod
    def remove_favorite(user, char_id=None, id=None):
        """
        Remove a paste from user's favorites
        """
        if char_id != None:
            id = Paste.get_id(char_id)
        
        if id == None:
            return False
            
        query = """DELETE FROM favorites
                   WHERE user_id = %s AND paste_id = %s"""
                   
        result = cursor.query_to_dict(query, [user.id, id])
        
        return True
    
    @staticmethod
    def is_paste_favorited(user, char_id=None, id=None):
        """
        Return True if this paste has been favorited by the user, False if not
        """
        if char_id != None:
            id = Paste.get_id(char_id)
            
        query = """SELECT id FROM favorites
                   WHERE user_id = %s AND paste_id = %s"""
                   
        result = cursor.query_to_list(query, [user.id, id])
        
        if len(result) > 0:
            return True
        else:
            return False
        
    @staticmethod
    def get_favorites(user, count=30, offset=0):
        """
        Get a certain amount of user's favorites, starting from a defined offset
        """
        query = """SELECT favorites.id, favorites.paste_id, pastes.char_id, pastes.title, favorites.added FROM favorites
                   INNER JOIN pastes ON favorites.paste_id = pastes.id
                   WHERE favorites.user_id = %s
                   ORDER BY favorites.added DESC
                   OFFSET %s LIMIT %s"""
                   
        result = cursor.query_to_list(query, [user.id, offset, count])
        
        return result
    
    @staticmethod
    def get_favorite_count(user):
        """
        Get the amount of favorites the user currently has
        """
        query = """SELECT COUNT(*) AS count FROM favorites
                   WHERE user_id = %s"""
                   
        result = cursor.query_to_dict(query, [user.id])
        
        return result["count"]
    
class PastebinUser(object):
    @staticmethod
    def delete_user(user):
        """
        Deletes an user as well as all of his pastes
        """
        with transaction.atomic():
            # Delete favorites
            query = """DELETE FROM favorites
                       WHERE EXISTS (SELECT id FROM pastes WHERE id = favorites.paste_id AND user_id = %s)"""
                       
            cursor.query(query, [user.id])
            
            # Delete pastes
            query = """DELETE FROM pastes
                       WHERE user_id = %s"""
                       
            cursor.query(query, [user.id])
            
            # Django recommends setting User's is_active property to False instead of
            # deleting it entirely, as it may break foreign keys
            query = """UPDATE auth_user
                       SET is_active = FALSE
                       WHERE id = %s"""
                       
            cursor.query(query, [user.id])