from django.db import transaction, connection
from sql import cursor

import random
import string
import hashlib
import datetime

class Paste(object):
    """
    Handles adding, updating and retrieving single pastes
    """
    # Visibility
    PUBLIC = "public"
    HIDDEN = "hidden"
    
    # Expiration
    NEVER = "never"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1month"
    
    @staticmethod
    def get_expiration_datetime(expiration):
        """
        Take the current datetime and move it forward by the given timedelta,
        giving us the paste's expiration date
        """
        exp_datetime = datetime.datetime.now()
        
        if expiration == Paste.FIFTEEN_MINUTES:
            exp_datetime += datetime.timedelta(minutes=15)
        elif expiration == Paste.ONE_HOUR:
            exp_datetime += datetime.timedelta(hours=1)
        elif expiration == Paste.ONE_DAY:
            exp_datetime += datetime.timedelta(hours=24)
        elif expiration == Paste.ONE_WEEK:
            exp_datetime += datetime.timedelta(weeks=1)
        elif expiration == Paste.ONE_MONTH:
            exp_datetime += datetime.timedelta(hours=24*31) # Assume one month means 31 days
            
        return exp_datetime
    
    @staticmethod
    def get_id(char_id):
        """
        Get paste's id by its char ID
        """
        query = """SELECT id FROM pastes
                   WHERE char_id = %s"""
                   
        result = cursor.query_to_dict(query, [char_id])
        
        if result != None:
            return result["id"]
        else:
            return None
    
    @staticmethod
    def get_random_char_id():
        """ Get a random 8 character string for the char id """
        return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(8))
        
    @staticmethod
    def get_paste(id=None, char_id=None, include_text=False):
        """
        Get paste by either its numeric ID or char ID
        
        if include_text is True, also include the text content as well
        """
        query = """SELECT pastes.id, char_id, user_id, auth_user.username AS username, title,
                          hash, expiration_date, hidden, submitted FROM pastes
                   LEFT JOIN auth_user ON pastes.user_id = auth_user.id"""
        
        if id != None:
            query += "\nWHERE id = %s"
            paste = cursor.query_to_dict(query, [id])
        elif char_id != None:
            query += "\nWHERE char_id = %s"
            paste = cursor.query_to_dict(query, [char_id])
            
        if paste == None:
            return None
            
        if include_text:
            paste_text = PasteContent.get_paste_text(paste["hash"])
            paste["text"] = paste_text
           
        return paste
    
    @staticmethod
    def is_paste_expired(id=None, char_id=None):
        """
        Check if the paste has expired
        
        If paste has an expiration date and has expired, return True
        Otherwise return False
        """
        query = """SELECT 1 FROM pastes"""
        parameters = []
        
        if id != None:
            query += "\nWHERE id = %s"
            parameters.append(id)
        elif char_id != None:
            query += "\nWHERE char_id = %s"
            parameters.append(char_id)
            
        query += " AND expiration_date IS NOT NULL AND expiration_date <= %s"
        
        current_datetime = datetime.datetime.now()
        parameters.append(current_datetime)
        
        result = cursor.query_to_list(query, parameters)
        
        if len(result) >= 1:
            return True
        else:
            return False
    
    @staticmethod
    def add_paste(text, user=None, title="Untitled", expiration=None, visibility=None):
        """
        Add paste with the provided title and text
        
        Returns the paste's char ID if the paste was successfully added, False otherwise
        """
        query = """INSERT INTO pastes (char_id, user_id, title, hash, expiration_date, hidden, submitted)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        
        # Generate a random 8 character string for the char ID
        char_id = Paste.get_random_char_id()
        hash = hashlib.sha256(text).hexdigest()
        submitted = datetime.datetime.now()
        
        # Make paste hidden if its visibility is hidden (private visibility may be added later)
        if visibility == Paste.HIDDEN:
            hidden = True
        else:
            hidden = False
            
        user_id = None
        if user is not None:
            user_id = user.id
            
        if expiration != Paste.NEVER:
            expiration_datetime = Paste.get_expiration_datetime(expiration)
        else:
            expiration_datetime = None
            
        # Add paste in a transaction
        with transaction.atomic():
            cursor.query(query, [char_id, user_id, title, hash, expiration_datetime, hidden, submitted])
            
            PasteContent.add_paste_text(text)
        
        return char_id
    
    @staticmethod
    def delete_paste(id=None, char_id=None):
        """
        Delete the paste
        """
        if char_id != None:
            id = Paste.get_id(char_id)
            
        with transaction.atomic():
            # Delete favorites linked to this paste first
            query = """DELETE FROM favorites
                       WHERE paste_id = %s"""
                       
            cursor.query(query, [id])
            
            # After that, delete the actual paste
            query = """DELETE FROM pastes
                       WHERE id = %s"""
            
            cursor.query(query, [id])
            
        return True
    
    @staticmethod
    def get_pastes(user, count=30, offset=0):
        """
        Get pastes by user starting from the provided offset
        If count is None, -1 or "all", retrieve all records
        """
        query = """SELECT id, char_id, title, submitted FROM pastes
                   WHERE user_id = %s
                   ORDER BY submitted DESC
                   OFFSET %s LIMIT %s"""
                   
        # If count is not provided or it's "all",
        # assume user wants to retrieve all records
        if count == None or count == -1 or count == "all":
            count = "ALL"
                   
        result = cursor.query_to_list(query, [user.id, offset, count])
        
        return result
    
    @staticmethod
    def get_paste_count(user):
        """
        Get the amount of pastes the user has uploaded
        """
        query = """SELECT COUNT(*) AS count FROM pastes
                   WHERE user_id = %s"""
                   
        result = cursor.query_to_dict(query, [user.id])
        
        return result["count"]
    
class PasteContent(object):
    """
    Handles paste text, which are identified by hashes instead of paste identifiers
    """
    @staticmethod
    def get_paste_text(hash, formatted=False):
        """
        Returns paste text, either as-is or formatted to be displayed in HTML
        """
        query = """SELECT * FROM paste_content
                   WHERE hash = %s"""
                   
        paste_content = cursor.query_to_dict(query, [hash])
        
        if paste_content is not None:
            return paste_content["text"]
        else:
            return None
        
    @staticmethod
    def add_paste_text(text):
        """
        Adds paste text if it hasn't been added yet
        """
        hash = hashlib.sha256(text).hexdigest()
        
        # Insert into paste_content only if a row with the same hash doesn't exist
        query = """INSERT INTO paste_content (hash, text, formatted_text)
                   SELECT %s, %s, %s
                   WHERE NOT EXISTS ( SELECT 1 FROM paste_content WHERE hash = %s )"""
                   
        cursor.query(query, [hash, text, text, hash])
        
class LatestPastes(object):
    @staticmethod
    def get_latest_pastes(limit=10):
        """
        Get the titles and char IDs of latest pastes by a limit (default 10)
        """
        query = """SELECT char_id, title, submitted FROM pastes
                   WHERE hidden = false AND (expiration_date IS NULL OR expiration_date >= %s)
                   ORDER BY submitted DESC
                   LIMIT %s"""
                   
        current_datetime = datetime.datetime.now()
                   
        results = cursor.query_to_list(query, [current_datetime, limit])
        
        return results