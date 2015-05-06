from django.db import models, transaction, connection
from django.db.models import Q

from django.contrib.auth.models import User

from sql import cursor

import highlighting

import random
import string
import hashlib
import datetime

class PasteManager(models.Manager):
    """
    Handles retrieving multiple pastes
    """
    def get_pastes(self, user=None, include_expired=False, include_hidden=True, count=30, offset=0):
        """
        Get pastes, optionally filtering by user and starting from a provided offset
        
        If count is None, -1 or "all", retrieve all records
        By default only 30 entries are retrieved
        """
        pastes = Paste.objects.order_by("-submitted")
                   
        if user != None:
            pastes = pastes.filter(user=user)
            
        if not include_expired:
            current_datetime = datetime.datetime.now()
            pastes = pastes.filter(Q(expiration_datetime__isnull=True) | Q(expiration_datetime__lte=current_datetime))
            
        if not include_hidden:
            pastes = pastes.filter(hidden=False)
            
        pastes = pastes[offset:count]
        
        return pastes

class Paste(models.Model):
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
    
    char_id = models.CharField(max_length=8)
    user = models.ForeignKey(User, null=True, blank=True)
    
    title = models.CharField(max_length=128)
    format = models.CharField(max_length=32)
    hash = models.CharField(max_length=64)
    
    expiration_datetime = models.DateTimeField(null=True, blank=True)
    
    hidden = models.BooleanField(default=False)
    
    submitted = models.DateTimeField(auto_now_add=True)
    
    objects = PasteManager()
    
    def get_new_expiration_datetime(self, expiration):
        """
        Take the current datetime and move it forward by the given timedelta,
        giving us the paste's expiration date
        """
        exp_datetime = datetime.datetime.now()
        
        if expiration == self.FIFTEEN_MINUTES:
            exp_datetime += datetime.timedelta(minutes=15)
        elif expiration == self.ONE_HOUR:
            exp_datetime += datetime.timedelta(hours=1)
        elif expiration == self.ONE_DAY:
            exp_datetime += datetime.timedelta(hours=24)
        elif expiration == self.ONE_WEEK:
            exp_datetime += datetime.timedelta(weeks=1)
        elif expiration == self.ONE_MONTH:
            exp_datetime += datetime.timedelta(hours=24*31) # Assume one month means 31 days
            
        return exp_datetime
    
    def get_random_char_id(self):
        """ Get a random 8 character string for the char id """
        return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(8))
        
    def get_text(self, formatted=True):
        """
        Get paste's text
        
        If formatted is True, text is returned in its HTML formatted form
        """
        if self.id == None:
            self.id = self.get_id()
            
        if formatted:
            paste_content = PasteContent.objects.get(hash=self.hash, format=self.format)
        else:
            paste_content = PasteContent.objects.get(hash=self.hash, format="none")
       
        return paste_content.get_text()
    
    def is_paste_expired(self):
        """
        Check if the paste has expired
        
        If paste has an expiration date and has expired, return True
        Otherwise return False
        """
        if self.expiration_datetime == None:
            return False
        
        current_datetime = datetime.datetime.now()
        
        if self.expiration_datetime > current_datetime:
            return True
        else:
            return False
    
    def add_paste(self, text, user=None, title="Untitled", expiration=None, visibility=None, format="text"):
        """
        Add paste with the provided title and text
        
        Returns the paste's char ID if the paste was successfully added, False otherwise
        """
        self.char_id = self.get_random_char_id()
        self.hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        self.title = title
        self.format = format
        
        # Make paste hidden if its visibility is hidden (private visibility may be added later)
        if visibility == Paste.HIDDEN:
            self.hidden = True
        else:
            self.hidden = False
            
        if user is not None:
            self.user = user
            
        if expiration != Paste.NEVER and expiration != None:
            self.expiration_datetime = Paste.get_new_expiration_datetime(expiration)
        else:
            self.expiration_datetime = None
            
        # Generating a duplicate char ID is extremely unlikely, but let's check for that to be sure
        # eg. in case we don't have enough entropy and we start generating the same strings,
        # in which case it's probably better to stop than continue
        if Paste.objects.filter(char_id=self.char_id).exists():
            raise RuntimeError("A duplicate char ID was generated. Consider participating in a lottery instead.")
            
        # Add paste in a transaction
        with transaction.atomic():
            self.save()
            
            # Save the paste content both as raw text and with formatting
            unformatted = PasteContent()
            formatted = PasteContent()
            
            unformatted.add_paste_text(text, None)
            formatted.add_paste_text(text, format)
        
        return self.char_id
    
    def update_paste(self, text="", title="", visibility=None, format="text"):
        """
        Change the paste text on an existing paste
        """
        # Make paste hidden if its visibility is hidden (private visibility may be added later)
        if visibility == Paste.HIDDEN:
            self.hidden = True
        else:
            self.hidden = False
            
        self.title = title
        self.format = format
            
        self.hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            
        with transaction.atomic():
            self.save()
            
            # Save the new paste content both as raw text and with formatting
            PasteContent.add_paste_text(text, None)
            PasteContent.add_paste_text(text, format)
    
    def delete_paste(self):
        """
        Delete the paste
        """
        if char_id != None:
            id = Paste.get_id(char_id)
            
        with transaction.atomic():
            # Delete favorites linked to this paste first
            Favorite.objects.filter(paste=self).delete()
            
            self.delete()
            
        return True
    
class PasteContent(models.Model):
    """
    Handles paste text, which are identified by hashes instead of paste identifiers
    """
    hash = models.CharField(max_length=64)
    format = models.CharField(max_length=32)
    text = models.TextField()
    
    def get_text(self):
        """
        Returns paste text, either as-is or formatted to be displayed in HTML
        """
        if self.text == "":
            self.text = self.objects.get(hash=self.hash, format=self.format).text
            
        return self.text
        
    def add_paste_text(self, text, format=None):
        """
        Adds paste text if it hasn't been added yet
        
        If format other than None is provided, Pygments will be used to highlight the text
        """
        hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        if format != None:
            text = highlighting.format_text(text, format)
        elif format == None:
            format = "none"
        
        paste_content = PasteContent(hash=hash, format=format, text=text)
        paste_content.save()
        
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