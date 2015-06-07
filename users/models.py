from django.db import models, transaction
from django.core.cache import cache

from django.contrib.auth.models import User

from django_redis import get_redis_connection

from ipware.ip import get_real_ip

from sql import cursor

from pastes.models import Paste
from pastebin import settings

import datetime

class Favorite(models.Model):
    """
    Handles user's favorites
    """
    paste = models.ForeignKey(Paste)
    user = models.ForeignKey(User)
    added = models.DateTimeField(auto_now_add=True)
    
    @staticmethod
    def has_user_favorited_paste(user, paste):
        """
        Returns True or False depending on whether user has favorited the paste
        """
        result = cache.get("paste_favorited:%s:%s" % (user.username, paste.char_id))
        
        if result != None:
            return result
        else:
            result = Favorite.objects.filter(user=user, paste=paste).exists()
            cache.set("paste_favorited:%s:%s" % (user.username, paste.char_id), result)
            
            return result
    
class PastebinUser(object):
    @staticmethod
    def delete_user(user):
        """
        Deletes an user as well as all of his pastes
        """
        with transaction.atomic():
            # Delete favorites
            Favorite.objects.filter(user=user).delete()
            Paste.objects.filter(user=user).delete()
            
            # Django recommends setting User's is_active property to False instead of
            # deleting it entirely, as it may break foreign keys
            user.is_active = False
            
            user.save()

class Limiter(object):
    """
    Throttles the amount of actions an user can do
    """
    PASTE_UPLOAD = 1
    PASTE_EDIT = 2
    COMMENT = 3
    
    @staticmethod
    def get_action_count(request, action):
        """
        Get the raw count of actions a certain IP address has done
        """
        authenticated = request.user.is_authenticated()
        
        if action == Limiter.PASTE_UPLOAD and settings.MAX_PASTE_UPLOADS_PER_USER == -1 and \
                                              settings.MAX_PASTE_UPLOADS_PER_GUEST == -1:
            return 0
        elif action == Limiter.PASTE_EDIT and settings.MAX_PASTE_EDITS_PER_USER == -1:
            return 0
        elif action == Limiter.COMMENT and settings.MAX_COMMENTS_PER_USER == -1:
            return 0
        
        count = 0
        con = get_redis_connection("persistent")
        
        ip = get_real_ip(request)
        
        if action == Limiter.PASTE_UPLOAD:
            count = con.get("paste_upload_count:%s" % ip)
        elif action == Limiter.PASTE_EDIT:
            count = con.get("paste_edit_count:%s" % ip)
        elif action == Limiter.COMMENT:
            count = con.get("comment_count:%s" % ip)
            
        if count == None:
            return 0
        else:
            return int(count)
    
    @staticmethod
    def increase_action_count(request, action, amount=1):
        """
        Increase the amount of actions by a certain amount (default=1)
        """
        authenticated = request.user.is_authenticated()
        
        count = 0
        con = get_redis_connection("persistent")
        
        ip = get_real_ip(request)
        
        if action == Limiter.PASTE_UPLOAD:
            if settings.MAX_PASTE_UPLOADS_PER_USER == -1 and authenticated:
                return 0
            elif settings.MAX_PASTE_UPLOADS_PER_GUEST == -1 and not authenticated:
                return 0
            else:
                count = int(con.incr("paste_upload_count:%s" % ip))
                
                if count == 1:
                    con.expire("comment_count:%s" % ip, settings.MAX_PASTE_UPLOADS_PERIOD)
        elif action == Limiter.PASTE_EDIT:
            if settings.MAX_PASTE_EDITS_PER_USER == -1:
                return 0
            else:
                count = int(con.incr("paste_edit_count:%s" % ip))
                
                if count == 1:
                    con.expire("comment_count:%s" % ip, settings.MAX_PASTE_EDITS_PERIOD)
        elif action == Limiter.COMMENT:
            if settings.MAX_COMMENTS_PER_USER == -1:
                return 0
            else:
                count = int(con.incr("comment_count:%s" % ip))
                
                if count == 1:
                    con.expire("comment_count:%s" % ip, settings.MAX_COMMENTS_PERIOD)
            
        return count
    
    @staticmethod
    def is_limit_reached(request, action, count=None):
        """
        Has the guest/user reached the maximum amount of paste uploads
        """
        authenticated = request.user.is_authenticated()
        
        if action == Limiter.PASTE_UPLOAD and settings.MAX_PASTE_UPLOADS_PER_USER == -1 and \
           authenticated:
            return False
        elif action == Limiter.PASTE_UPLOAD and settings.MAX_PASTE_UPLOADS_PER_GUEST == -1 and \
             not authenticated:
            return False
        elif action == Limiter.PASTE_EDIT and settings.MAX_PASTE_EDITS_PER_USER == -1:
            return False
        elif action == Limiter.COMMENT and settings.MAX_COMMENTS_PER_USER == -1:
            return False
        
        if count == None:
            count = Limiter.get_action_count(request, action)
        
        if action == Limiter.PASTE_UPLOAD:
            if authenticated:
                return count >= settings.MAX_PASTE_UPLOADS_PER_USER
            else:
                return count >= settings.MAX_PASTE_UPLOADS_PER_GUEST
        elif action == Limiter.PASTE_EDIT:
            return count >= settings.MAX_PASTE_EDITS_PER_USER
        elif action == Limiter.COMMENT:
            return count >= settings.MAX_COMMENTS_PER_USER
        
    @staticmethod
    def get_action_limit(request, action):
        """
        Return the maximum amount of actions the guest/user can do
        """
        authenticated = request.user.is_authenticated()
        
        if action == Limiter.PASTE_UPLOAD:
            if authenticated:
                return settings.MAX_PASTE_UPLOADS_PER_USER
            else:
                return settings.MAX_PASTE_UPLOADS_PER_GUEST
        elif action == Limiter.PASTE_EDIT:
            return settings.MAX_PASTE_EDITS_PER_USER
        elif action == Limiter.COMMENT:
            return settings.MAX_COMMENTS_PER_USER