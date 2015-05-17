from django.db import models
from django.contrib.auth.models import User

from sql import cursor

from pastes.models import Paste

import datetime

class Comment(models.Model):
    COMMENTS_PER_PAGE = 10
    
    paste = models.ForeignKey(Paste)
    user = models.ForeignKey(User)
    
    text = models.TextField()
    
    submitted = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)