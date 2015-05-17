from django.db import models, transaction
from django.contrib.auth.models import User

from sql import cursor

from pastes.models import Paste

import datetime

class Favorite(models.Model):
    """
    Handles user's favorites
    """
    paste = models.ForeignKey(Paste)
    user = models.ForeignKey(User)
    added = models.DateTimeField(auto_now_add=True)
    
class PastebinUser(object):
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
            user.is_active = True
            
            user.save()