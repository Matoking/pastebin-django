from django.shortcuts import render, redirect
from django.http import HttpResponse

from pastes.forms import SubmitPasteForm
from pastes.models import Paste

from users.models import Favorite
from users.forms import VerifyPasswordForm

import json

def submit_paste(request):
    """
    Process paste data received from a form, and if the paste is uploaded correctly,
    redirect the user to it
    """
    submit_paste_form = SubmitPasteForm(request.POST or None)
    
    if submit_paste_form.is_valid():
        paste_data = submit_paste_form.cleaned_data
        
        user = None
        if request.user.is_authenticated():
            user = request.user
        
        char_id = Paste.add_paste(title=paste_data["paste_title"],
                                  user=user,
                                  text=paste_data["paste_text"],
                                  expiration=paste_data["paste_expiration"],
                                  visibility=paste_data["paste_visibility"])
        
        # Redirect to the newly created paste
        return redirect("show_paste", char_id=char_id)
    else:
        # On error, redirect to home
        return redirect("home:home")
    
def show_paste(request, char_id, raw=False, download=False):
    """
    Show the paste, possibly as raw text or as a download
    """
    # If paste has expired, show the ordinary "paste not found" page
    if Paste.is_paste_expired(char_id=char_id):
        return render(request, "pastes/show_paste/show_error.html", {"reason": "expired"}, status=404)
    
    paste = Paste.get_paste(char_id=char_id, include_text=True)
    
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
            print(paste)
            paste_favorited = Favorite.is_paste_favorited(request.user, id=paste["id"])
            
        return render(request, "pastes/show_paste/show_paste.html", {"paste": paste,
                                                                     "paste_favorited": paste_favorited})
        
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