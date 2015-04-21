from django.shortcuts import render
from django.http import HttpResponse

from pastes.models import Paste
from comments.models import Comment
from comments.forms import SubmitCommentForm

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
    
    paste_id = Paste.get_id(char_id)
    
    if paste_id ==  None:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
    else:
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                        offset=page*Comment.COMMENTS_PER_PAGE,
                                        count=Comment.COMMENTS_PER_PAGE,
                                        datetime_as_unix=True)
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
    
    paste_id = Paste.get_id(char_id)
    
    if paste_id == None:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found"
        return HttpResponse(json.dumps(response), status=422)
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response), status=422)
    
    submit_form = SubmitCommentForm(request.POST or None)
        
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        Comment.add_comment(comment_data["text"], request.user, paste_id)
        
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                        offset=0,
                                        count=Comment.COMMENTS_PER_PAGE,
                                        datetime_as_unix=True)
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
    
    paste_id = Paste.get_id(char_id)
    
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
    
    comment = Comment.get_comment(id)
    
    if comment == None:
        response["status"] = "fail"
        response["data"]["message"] = "The comment doesn't exist."
        return HttpResponse(json.dumps(response), status=400)
    
    if comment["user_id"] != request.user.id:
        response["status"] = "fail"
        response["data"]["message"] = "You are trying to edit someone else's comment."
        return HttpResponse(json.dumps(response), status=422)
    
    submit_form = SubmitCommentForm(request.POST or None)
    
    if submit_form.is_valid():
        comment_data = submit_form.cleaned_data
        
        Comment.update_comment(comment_data["text"], id)
        
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["edited_comment_id"] = comment["id"]
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                                            offset=page*Comment.COMMENTS_PER_PAGE,
                                                            count=Comment.COMMENTS_PER_PAGE,
                                                            datetime_as_unix=True)
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
    
    paste_id = Paste.get_id(char_id)
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "You are not logged in."
        return HttpResponse(json.dumps(response), status=422)
    
    comment = Comment.get_comment(id)
    
    if comment == None:
        response["status"] = "fail"
        response["data"]["message"] = "The comment doesn't exist."
        return HttpResponse(json.dumps(response), status=400)
    
    if comment["user_id"] != request.user.id:
        response["status"] = "fail"
        response["data"]["message"] = "You are trying to delete someone else's comment."
        return HttpResponse(json.dumps(response), status=422)
    
    Comment.delete_comment(id)
    
    if paste_id ==  None:
        response["status"] = "fail"
        response["data"]["message"] = "The paste couldn't be found."
    else:
        total_comment_count = Comment.get_comment_count(paste_id=paste_id)
        
        response["data"]["comments"] = Comment.get_comments(paste_id=paste_id,
                                        offset=page*Comment.COMMENTS_PER_PAGE,
                                        count=Comment.COMMENTS_PER_PAGE,
                                        datetime_as_unix=True)
        response["data"]["page"] = page
        response["data"]["pages"] = math.ceil(float(total_comment_count) / float(Comment.COMMENTS_PER_PAGE))
        
        if response["data"]["pages"] == 0:
            response["data"]["pages"] = 1
        
        response["data"]["total_comment_count"] = total_comment_count
    
    return HttpResponse(json.dumps(response))