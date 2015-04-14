from django.shortcuts import render
from django.http import HttpResponse

from pastes.models import Paste
from comments.models import Comment
from comments.forms import SubmitCommentForm

import json
import math

def get_comments(request, char_id, page=0):
    """
    Return comments as JSON
    """
    response = {"status": "success",
                "data": {}}
    
    paste_id = Paste.get_id(char_id)
    
    if paste_id ==  None:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
    else:
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                        offset=page*Comment.COMMENTS_PER_PAGE,
                                        count=Comment.COMMENTS_PER_PAGE)
        response["data"]["page"] = page
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        response["data"]["total_comment_count"] = total_comment_count
    
    return HttpResponse(json.dumps(response))

def add_comment(request, char_id):
    """
    Adds a comment to a paste
    """
    response = {"status": "success",
                "data": {}}
    
    paste_id = Paste.get_id(char_id)
    
    if paste_id == None:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found"
        return HttpResponse(json.dumps(response))
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response))
    
    submit_form = SubmitCommentForm(request.POST or None)
        
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        Comment.add_comment(comment_data["text"], request.user, paste_id)
        
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                        offset=0,
                                        count=Comment.COMMENTS_PER_PAGE)
        response["data"]["page"] = 0
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        response["data"]["total_comment_count"] = total_comment_count
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Provided text wasn't valid."
        
    return HttpResponse(json.dumps(response))

def edit_comment(request, id):
    """
    Edit an existing comment
    """
    response = {"status": "success",
                "data": {}}
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response))
    
    comment = Comment.get_comment(id)
    
    if comment == None:
        response["status"] = "fail"
        response["data"]["message"] = "The comment doesn't exist."
        return HttpResponse(json.dumps(response))
    
    if comment["user_id"] != request.user.id:
        response["status"] = "fail"
        response["data"]["message"] = "You are trying to edit someone else's comment."
        return HttpResponse(json.dumps(response))
    
    submit_form = SubmitCommentForm(request.POST or None)
    
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        Comment.update_comment(comment_data["text"], id)
        
        # Get the page where the edited comment is
        page = math.ceil(float(comment["id"]) / float(Comment.COMMENTS_PER_PAGE))
        
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["edited_comment_id"] = comment["id"]
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                                            offset=page*Comment.COMMENTS_PER_PAGE,
                                                            count=Comment.COMMENTS_PER_PAGE)
        response["data"]["page"] = page
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        response["data"]["total_comment_count"] = total_comment_count
    else:
        response["status"] = "fail"
        response["data"]["message"] = "Provided text wasn't valid."
        
    return HttpResponse(json.dumps(response))