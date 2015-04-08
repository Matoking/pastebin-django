from django.shortcuts import render, redirect
from django.http import HttpResponse

from pastes.forms import SubmitPasteForm, EditPasteForm
from pastes.models import Paste

from comments.models import Comment

from users.models import Favorite
from users.forms import VerifyPasswordForm

import json
    
def show_paste(request, char_id, raw=False, download=False):
    """
    Show the paste, possibly as raw text or as a download
    """
    # If paste has expired, show the ordinary "paste not found" page
    if Paste.is_paste_expired(char_id=char_id):
        return render(request, "pastes/show_paste/show_error.html", {"reason": "expired"}, status=404)
    
    # Get the formatted paste text unless the user is downloading the paste or viewing it as raw text
    formatted = True
    if raw == True or download == True:
        formatted = False
    
    paste = Paste.get_paste(char_id=char_id, include_text=True, formatted=formatted)
    
    if paste == None:
        return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
    
    if raw:
        response = HttpResponse(paste["text"], content_type='text/plain')
        return response
    elif download:
        response = HttpResponse(paste["text"], content_type='application/octet-stream')
        response["Content-Disposition"] = 'attachment; filename="%s.txt"' % char_id
        return response
    else:
        # Display the paste as normal
        paste_favorited = False
        
        if request.user.is_authenticated():
            paste_favorited = Favorite.is_paste_favorited(request.user, id=paste["id"])
            
        comment_count = Comment.get_comment_count(paste_id=paste["id"])
            
        return render(request, "pastes/show_paste/show_paste.html", {"paste": paste,
                                                                     "paste_favorited": paste_favorited,
                                                                     
                                                                     "comment_count": comment_count})
        
def edit_paste(request, char_id):
    """
    Edit the paste
    """
    paste = Paste.get_paste(char_id=char_id, include_text=True, formatted=False)
    
    edit_form = EditPasteForm(request.POST or None)
    
    if edit_form.is_valid():
        cleaned_data = edit_form.cleaned_data
        
        Paste.change_paste_text(cleaned_data["text"], id=paste["id"])
        
        return redirect("show_paste", char_id=char_id)
    
    return render(request, "pastes/edit_paste/edit_paste.html", {"paste": paste})
        
def delete_paste(request, char_id):
    """
    Delete a single paste
    """
    if not request.user.is_authenticated():
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_logged_in"})
    
    paste = Paste.get_paste(char_id=char_id)
    
    # Check that the paste exists
    if paste == None:
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_found"})
    
    # Check that the user deleting the paste is the one who uploaded it
    if paste["user_id"] != request.user.id:
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_owner"})
    
    form = VerifyPasswordForm(request.POST or None, user=request.user)
    
    if form.is_valid():
        Paste.delete_paste(id=paste["id"])
        
        return render(request, "pastes/delete_paste/paste_deleted.html")
    
    return render(request, "pastes/delete_paste/delete_paste.html", {"paste": paste,
                                                                     "form": form})
    
        
def change_paste_favorite(request):
    """
    Add/remove paste from user's favorites, and respond with JSON
    """
    response = {"action": "none"}
    
    char_id = None or request.POST["char_id"]
    action = None or request.POST["action"]
    
    if not request.user.is_authenticated():
        response["error"] = "not_logged_in"
    else:
        if action == "add":
            result = Favorite.add_favorite(request.user, char_id=char_id)
            response["action"] = "added_favorite"
            response["result"] = result
        elif action == "remove":
            result = Favorite.remove_favorite(request.user, char_id=char_id)
            response["action"] = "removed_favorite"
            response["result"] = result
        else:
            response["error"] = "valid_action_not_provided"
            
    return HttpResponse(json.dumps(response))