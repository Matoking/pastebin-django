from django.db import models, transaction, connection
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.models import User

from django.core.cache import cache
from django_redis import get_redis_connection
from django.utils import timezone

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
        pastes = Paste.objects.filter(removed=Paste.NO_REMOVAL).order_by("-submitted")
                   
        if user != None:
            pastes = pastes.filter(user=user)
            
        if not include_expired:
            current_datetime = timezone.now()
            pastes = pastes.filter(Q(expiration_datetime__isnull=True) | Q(expiration_datetime__gte=current_datetime))
            
        if not include_hidden:
            pastes = pastes.filter(hidden=False)
            
        start = offset
        end = offset + count
        
        pastes = pastes[start:end]
        
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
    
    # Removal types
    NO_REMOVAL = 0
    ADMIN_REMOVAL = 1
    USER_REMOVAL = 2
    
    char_id = models.CharField(max_length=8)
    user = models.ForeignKey(User, null=True, blank=True)
    
    # Version is incremented by one with every paste update
    version = models.IntegerField(default=1)
    
    title = models.CharField(max_length=128)
    format = models.CharField(max_length=32)
    hash = models.CharField(max_length=64)
    
    expiration_datetime = models.DateTimeField(null=True, blank=True)
    
    encrypted = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    
    # Is the paste removed (removed from view but not deleted)
    removed = models.IntegerField(default=0)
    removal_reason = models.TextField(default="")
    
    # Has the paste been deleted (paste content deleted unless another paste
    # also has it)
    deleted = models.BooleanField(default=False)
    
    submitted = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = PasteManager()
    
    def get_new_expiration_datetime(self, expiration):
        """
        Take the current datetime and move it forward by the given timedelta,
        giving us the paste's expiration date
        """
        exp_datetime = timezone.now()
        
        if expiration == self.FIFTEEN_MINUTES:
            exp_datetime += timezone.timedelta(minutes=15)
        elif expiration == self.ONE_HOUR:
            exp_datetime += timezone.timedelta(hours=1)
        elif expiration == self.ONE_DAY:
            exp_datetime += timezone.timedelta(hours=24)
        elif expiration == self.ONE_WEEK:
            exp_datetime += timezone.timedelta(weeks=1)
        elif expiration == self.ONE_MONTH:
            exp_datetime += timezone.timedelta(hours=24*31) # Assume one month means 31 days
            
        return exp_datetime
    
    @staticmethod
    def get_random_char_id():
        """
        Get a random char ID representing a public paste
        """
        con = get_redis_connection("persistent")
        
        result = con.srandmember("public_pastes")
        
        if result == None:
            # We don't have public pastes in Redis, add them
            pastes = Paste.objects.filter(removed=Paste.NO_REMOVAL,
                                          deleted=False,
                                          hidden=False,
                                          encrypted=False,
                                          expiration_datetime=None).only("char_id").values_list()
            
            char_ids = []
            
            for paste in pastes:
                char_ids.append(paste[1])
                print paste[1]
                
            # Add all the public pastes
            if len(char_ids) > 0:
                con.sadd("public_pastes", *char_ids)
            
                return random.choice(char_ids)
            else:
                return None
        else:
            return result
    
    def generate_random_char_id(self):
        """ 
        Generate a random 8 character string for the char id 
        """
        return ''.join(random.SystemRandom().choice(string.uppercase + string.lowercase + string.digits) for _ in xrange(8))
        
    def get_text(self, formatted=True, version=None):
        """
        Get paste's text
        
        If formatted is True, text is returned in its HTML formatted form
        """
        hash = None
        format = None
        
        if version == None:
            hash = self.hash
            format = self.format
        else:
            paste_version = cache.get("paste_version:%s:%s" % (self.char_id, version))
            
            if paste_version == None:
                paste_version = PasteVersion.objects.get(paste=self, version=version)
                cache.set("paste_version:%s:%s" % (self.char_id, version), paste_version)
            
            hash = paste_version.hash
            format = paste_version.format
        
        if formatted and not self.encrypted:
            cache_result = cache.get("paste_content:%s:%s:formatted_text" % (hash, format))
            
            if cache_result != None:
                return cache_result
            
            paste_content = PasteContent.objects.get(hash=hash, format=format)
            
            cache.set("paste_content:%s:%s:formatted_text" % (hash, format), paste_content.text)
        else:
            cache_result = cache.get("paste_content:%s:text" % hash)
            
            if cache_result != None:
                return cache_result
            
            paste_content = PasteContent.objects.get(hash=hash, format="none")
            
            cache.set("paste_content:%s:text" % hash, paste_content.text)
       
        return paste_content.text
    
    def is_expired(self):
        """
        Check if the paste has expired
        
        If paste has an expiration date and has expired, return True
        Otherwise return False
        """
        if self.expiration_datetime == None:
            return False
        
        current_datetime = timezone.now()
        
        if self.expiration_datetime < current_datetime:
            return True
        else:
            return False
        
    def is_removed(self):
        """
        Has the paste been removed (paste still exists but can't be viewed),
        usually due to a paste report
        """
        if self.removed > 0:
            return True
        else:
            return False
    
    def add_paste(self, text, user=None, title="Untitled", expiration=None, visibility=None, format="text", encrypted=False):
        """
        Add paste with the provided title and text
        
        Returns the paste's char ID if the paste was successfully added, False otherwise
        """
        self.char_id = self.generate_random_char_id()
        self.hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        self.title = title
        self.format = format
        
        self.encrypted = encrypted
        
        # Make paste hidden if its visibility is hidden (private visibility may be added later)
        if visibility == Paste.HIDDEN:
            self.hidden = True
        else:
            self.hidden = False
            
        if user is not None:
            self.user = user
            
        if expiration != Paste.NEVER and expiration != None:
            self.expiration_datetime = self.get_new_expiration_datetime(expiration)
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
            
            if not encrypted:
                formatted.add_paste_text(text, format)
                
            first_version = PasteVersion(paste=self,
                                         version=1,
                                         note="Uploaded",
                                         title=self.title,
                                         hash=self.hash,
                                         format=self.format)
            first_version.save()
            cache.set("paste_version:%s:1" % (self.char_id), first_version)
            
            if not self.encrypted and not self.hidden and self.expiration_datetime == None: 
                con = get_redis_connection("persistent")
                
                con.sadd("public_pastes", self.char_id)
        
        return self.char_id
    
    def update_paste(self, text="", title="", visibility=None, format="text", encrypted=False, note=""):
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
            
        self.version += 1
        self.hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            
        self.encrypted = encrypted
            
        with transaction.atomic():
            self.save()
            
            # Save the new paste content both as raw text and with formatting
            unformatted = PasteContent()
            formatted = PasteContent()
            
            unformatted.add_paste_text(text, None)
            
            if not encrypted:
                formatted.add_paste_text(text, format)
            
            new_version = PasteVersion(paste=self,
                                       version=self.version,
                                       note=note,
                                       title=self.title,
                                       hash=self.hash,
                                       format=self.format)
            new_version.save()
            cache.set("paste_version:%s:%s" % (self.char_id, self.version), new_version)
    
    def remove_paste(self, type=ADMIN_REMOVAL, reason=""):
        """
        Remove the paste from being viewed
        """
        with transaction.atomic():
            from users.models import Favorite
            
            # Delete favorites linked to this paste first
            Favorite.objects.filter(paste=self).delete()
            
            self.removed = type
            self.removal_reason = reason
        
            self.save()
            
            con = get_redis_connection("persistent")
            
            con.srem("public_pastes", self.char_id)
            
        return True
    
    def delete_paste(self, type=ADMIN_REMOVAL, reason=""):
        """
        Delete the paste completely
        """    
        with transaction.atomic():
            from users.models import Favorite
            
            # Delete favorites linked to this paste first
            Favorite.objects.filter(paste=self).delete()
            
            self.removed = type
            self.removal_reason = reason
            
            self.deleted = True
            
            hash = self.hash
            
            # If another paste has the same content, don't delete the actual paste content
            if Paste.objects.filter(hash=self.hash, format="none").count() == 1:
                PasteContent.objects.filter(hash=self.hash).delete()
                
            self.hash = "N/A"
            
            self.save()
            
            con = get_redis_connection("persistent")
            
            con.srem("public_pastes", self.char_id)
            
        return True
    
    def get_hit_count(self):
        """
        Get hit count for the paste
        """
        con = get_redis_connection("persistent")
        
        result = con.get("paste:%s:hits" % self.id)
        
        if result == None:
            return 0
        else:
            return int(result)
        
    def add_hit(self, ip_address):
        """
        Add a hit by an IP address if it hasn't been added yet
        """
        con = get_redis_connection("persistent")
        
        if con.get("paste:%s:hit:%s" % (self.char_id, ip_address)):
            hits = con.get("paste:%s:hits" % self.char_id)
            if hits == None:
                return 0
            else:
                return int(hits)
        else:
            # Add an entry for this hit and store it for 24 hours
            con.setex("paste:%s:hit:%s" % (self.char_id, ip_address), 86400, 1)
            return con.incr("paste:%s:hits" % self.char_id)
        
    def save(self, *args, **kwargs):
        """
        Override the save method to also save the result to cache
        """
        super(Paste, self).save(*args, **kwargs)
        
        cache.set("paste:%s" % self.char_id, self)
        
    def __unicode__(self):
        return "%s (%s)" % (self.title, self.char_id)
    
class PasteVersion(models.Model):
    """
    A version entry of a paste
    """
    paste = models.ForeignKey(Paste)
    version = models.IntegerField()
    
    note = models.CharField(max_length=1024,
                            default="")
    
    title = models.CharField(max_length=128)
    hash = models.CharField(max_length=64)
    format = models.CharField(max_length=64)
    
    submitted = models.DateTimeField(auto_now_add=True)
    
class PasteContent(models.Model):
    """
    Handles paste text, which are identified by hashes instead of paste identifiers
    """
    hash = models.CharField(max_length=64)
    format = models.CharField(max_length=32)
    text = models.TextField()
        
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
        
        # Paste text may already exist
        if not PasteContent.objects.filter(hash=hash, format=format).exists():
            paste_content = PasteContent(hash=hash, format=format, text=text)
            paste_content.save()
        
class PasteReport(models.Model):
    """
    Reports regarding pastes
    """
    paste = models.ForeignKey(Paste)
    user = models.ForeignKey(User, null=True, blank=True)
    
    type = models.CharField(max_length=32)
    text = models.TextField()
    
    checked = models.BooleanField(default=False)
        
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
                   
        current_datetime = timezone.now()
                   
        results = cursor.query_to_list(query, [current_datetime, limit])
        
        return results