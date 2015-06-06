from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from pastebin import settings

from pastebin.util import queryset_to_list

from pastes.models import Paste
from comments.models import Comment
from comments.forms import SubmitCommentForm

from users.models import Limiter

from humanfriendly import format_timespan

import json
import math

def get_comments(request):
    """
    Return comments as JSON
    """
    response = {"status": "success",
                "data": {}}
    
    if "char_id" in request.POST:
        char_id = request.POST["char_id"]
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Paste ID was not provided (POST parameter 'char_id')"
        return HttpResponse(json.dumps(response), status=422)
    
    if "page" in request.POST:
        page = int(request.POST["page"])
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Comment page was not provided (POST parameter 'page')"
        return HttpResponse(json.dumps(response), status=422)
    
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
    else:
        total_comment_count = Comment.objects.filter(paste=paste).count()
        
        start = page * Comment.COMMENTS_PER_PAGE
        end = start + Comment.COMMENTS_PER_PAGE
        
        response["data"]["comments"] = queryset_to_list(Comment.objects.filter(paste=paste) \
                                                                       .select_related("user") \
                                                                       [start:end],
                                                                       fields=["id", "text", "submitted", "edited", "user__username=username"])
        response["data"]["page"] = page
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        
        if response["data"]["pages"] == 0:
            response["data"]["pages"] = 1
        
        response["data"]["total_comment_count"] = total_comment_count
    
    return HttpResponse(json.dumps(response))

def add_comment(request):
    """
    Adds a comment to a paste
    """
    response = {"status": "success",
                "data": {}}
    
    if "char_id" in request.POST:
        char_id = request.POST["char_id"]
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Paste ID was not provided (POST parameter 'char_id')"
        return HttpResponse(json.dumps(response), status=422)
    
    if "text" not in request.POST:
        response["status"] = "fail"
        response["data"]["message"] = "Comment text was not provided (POST parameter 'text')"
        return HttpResponse(json.dumps(response), status=422)
    
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
        return HttpResponse(json.dumps(response), status=422)
    
    if not request.user.is_authenticated() or not request.user.is_active:
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response), status=422)
    
    if Limiter.is_limit_reached(request, Limiter.COMMENT):
        response["status"] = "fail"
        response["data"]["message"] = "You can only post %s comments every %s." % (Limiter.get_action_limit(request, Limiter.COMMENT), format_timespan(settings.MAX_COMMENTS_PERIOD))
        return HttpResponse(json.dumps(response))
    
    submit_form = SubmitCommentForm(request.POST or None)
        
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        comment = Comment(text=comment_data["text"], 
                          user=request.user,
                          paste=paste)
        comment.save()
        
        Limiter.increase_action_count(request, Limiter.COMMENT)
        
        total_comment_count = Comment.objects.filter(paste=paste).count()
        
        response["data"]["comments"] = queryset_to_list(Comment.objects.filter(paste=paste) \
                                                                       .select_related("user") \
                                                                       [0:Comment.COMMENTS_PER_PAGE],
                                                                       fields=["id", "text", "submitted", "edited", "user__username=username"])
        response["data"]["page"] = 0
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        
        if response["data"]["pages"] == 0:
            response["data"]["pages"] = 1
            
        response["data"]["total_comment_count"] = total_comment_count
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Provided text wasn't valid."
        
    return HttpResponse(json.dumps(response))

def edit_comment(request):
    """
    Edit an existing comment
    """
    response = {"status": "success",
                "data": {}}
    
    if "char_id" in request.POST:
        char_id = request.POST["char_id"]
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Paste ID was not provided (POST parameter 'char_id')"
        return HttpResponse(json.dumps(response), status=422)
    
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
        return HttpResponse(json.dumps(response))
    
    if "id" in request.POST:
        id = int(request.POST["id"])
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Comment ID was not provided (POST parameter 'id')"
        return HttpResponse(json.dumps(response), status=422)
    
    if "page" in request.POST:
        page = int(request.POST["page"])
    else:
        page = 0
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response), status=422)
    
    try:
        comment = Comment.objects.get(id=id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The comment doesn't exist."
        return HttpResponse(json.dumps(response), status=400)
    
    if comment.user != request.user:
        response["status"] = "fail"
        response["data"]["message"] = "You are trying to edit someone else's comment."
        return HttpResponse(json.dumps(response), status=422)
    
    submit_form = SubmitCommentForm(request.POST or None)
    
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        comment.text = comment_data["text"]
        comment.save()
        
        total_comment_count = Comment.objects.filter(paste=paste).count()
        
        start = page * Comment.COMMENTS_PER_PAGE
        end = start + Comment.COMMENTS_PER_PAGE
        
        response["data"]["edited_comment_id"] = comment.id
        response["data"]["comments"] = queryset_to_list(Comment.objects.filter(paste=paste) \
                                                                       .select_related("user") \
                                                                       [start:end],
                                                                       fields=["id", "text", "submitted", "edited", "user__username=username"])
        response["data"]["page"] = page
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        
        if response["data"]["pages"] == 0:
            response["data"]["pages"] = 1
            
        response["data"]["total_comment_count"] = total_comment_count
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Provided text wasn't valid."
        
    return HttpResponse(json.dumps(response))

def delete_comment(request):
    response = {"status": "success",
                "data": {}}
    
    if "id" in request.POST:
        id = request.POST["id"]
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Comment ID was not provided (POST parameter 'id')"
        return HttpResponse(json.dumps(response), status=422)
    
    if "char_id" in request.POST:
        char_id = request.POST["char_id"]
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Paste ID was not provided (POST parameter 'char_id')"
        return HttpResponse(json.dumps(response), status=422)
    
    if "page" in request.POST:
        page = int(request.POST["page"])
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Comment page was not provided (POST parameter 'page')"
        return HttpResponse(json.dumps(response), status=422)
    
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
        return HttpResponse(json.dumps(response), status=422)
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response), status=422)
    try:
        comment = Comment.objects.get(id=id)
    except ObjectDoesNotExist:
        response["status"] = "fail"
        response["data"]["message"] = "The comment doesn't exist."
        return HttpResponse(json.dumps(response), status=400)
    
    if comment.user != request.user:
        response["status"] = "fail"
        response["data"]["message"] = "You are trying to delete someone else's comment."
        return HttpResponse(json.dumps(response), status=422)
    
    comment.delete()
    
    total_comment_count = Comment.objects.filter(paste=paste).count()
    
    start = page * Comment.COMMENTS_PER_PAGE
    end = start + Comment.COMMENTS_PER_PAGE
    
    response["data"]["comments"] = queryset_to_list(Comment.objects.filter(paste=paste) \
                                                                   .select_related("user") \
                                                                   [start:end],
                                                                   fields=["id", "text", "submitted", "edited", "user__username=username"])
    response["data"]["page"] = page
    response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
    
    if response["data"]["pages"] == 0:
        response["data"]["pages"] = 1
    
    response["data"]["total_comment_count"] = total_comment_count
    
    return HttpResponse(json.dumps(response))