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
    def get_random_char_id():
        """ Get a random 8 character string for the char id """
        return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(8))
        
    @staticmethod
    def get_paste(id=None, char_id=None, include_text=False):
        """
        Get paste by either its numeric ID or char ID
        
        if include_text is True, also include the text content as well
        """
        query = """SELECT * FROM pastes"""
        
        if id != None:
            query += "\nWHERE id = %s"
            paste = cursor.query_to_dict(query, [id])
        elif char_id != None:
            query += "\nWHERE char_id = %s"
            paste = cursor.query_to_dict(query, [char_id])
            
        if include_text == True:
            paste_text = PasteContent.get_paste_text(paste["hash"])
            paste["text"] = paste_text
           
        return paste
    
    @staticmethod
    def add_paste(text, user=None, title="Untitled", expiration=None, visibility=None):
        """
        Add paste with the provided title and text
        
        Returns the paste's char ID if the paste was successfully added, False otherwise
        """
        c = connection.cursor()
        
        query = """INSERT INTO pastes (char_id, submit_user, title, hash, expiration_date, hidden, submitted)
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
            
        if expiration is not Paste.NEVER:
            expiration_datetime = Paste.get_expiration_datetime(expiration)
        else:
            expiration_datetime = None
            
        # Add paste in a transaction
        with transaction.atomic():
            cursor.query(query, [char_id, user_id, title, hash, expiration_datetime, hidden, submitted])
            
            PasteContent.add_paste_text(text)
        
        return char_id
    
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
                   WHERE hidden = false
                   ORDER BY submitted DESC
                   LIMIT %s"""
                   
        results = cursor.query_to_list(query, [limit])
        
        return results