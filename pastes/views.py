from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

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
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
    
    if paste.is_paste_expired():
        return render(request, "pastes/show_paste/show_error.html", {"reason": "expired"}, status=404)
    
    # Get the formatted paste text unless the user is downloading the paste or viewing it as raw text
    formatted = True
    if raw == True or download == True:
        formatted = False
        
    if raw:
        text = paste.get_text(formatted=False)
        response = HttpResponse(text, content_type='text/plain')
        return response
    elif download:
        text = paste.get_text(formatted=False)
        response = HttpResponse(text, content_type='application/octet-stream')
        response["Content-Disposition"] = 'attachment; filename="%s.txt"' % char_id
        return response
    else:
        # Display the paste as normal
        paste_favorited = False
        
        if request.user.is_authenticated():
            paste_favorited = Favorite.objects.filter(user=request.user, paste=paste).exists()
            
        comment_count = Comment.objects.all().count()
            
        return render(request, "pastes/show_paste/show_paste.html", {"paste": paste,
                                                                     "paste_favorited": paste_favorited,
                                                                     
                                                                     "comment_count": comment_count})
        
def edit_paste(request, char_id):
    """
    Edit the paste
    """
    if not request.user.is_authenticated():
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_logged_in"})
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_found"})
    
    if paste.user != request.user and not request.user.is_staff:
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_owner"})
    
    if paste.hidden:
        visibility = "hidden"
    else:
        visibility = "public"
    
    edit_form = EditPasteForm(request.POST or None, initial={"title": paste.title,
                                                             "visibility": visibility,
                                                             "syntax_highlighting": paste.format})
    
    if edit_form.is_valid():
        paste_data = edit_form.cleaned_data
        
        paste.update_paste(title=paste_data["title"],
                           text=paste_data["text"],
                           visibility=paste_data["visibility"],
                           format=paste_data["syntax_highlighting"])
        
        return redirect("show_paste", char_id=char_id)
    
    paste_text = paste.get_text(formatted=False)
    
    return render(request, "pastes/edit_paste/edit_paste.html", {"paste": paste,
                                                                 "paste_text": paste_text,
                                                                 
                                                                 "form": edit_form})
        
def delete_paste(request, char_id):
    """
    Delete a single paste
    """
    if not request.user.is_authenticated():
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_logged_in"})
    
    try:
        paste = Paste.objects.get(char_id=char_id)
    except ObjectDoesNotExist:
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_found"})
    
    # Check that the user can delete the paste
    if paste.user != request.user and not request.user.is_staff:
        return render(request, "pastes/delete_paste/delete_error.html", {"reason": "not_owner"})
    
    form = VerifyPasswordForm(request.POST or None, user=request.user)
    
    if form.is_valid():
        paste.delete_paste()
        
        return render(request, "pastes/delete_paste/paste_deleted.html")
    
    return render(request, "pastes/delete_paste/delete_paste.html", {"paste": paste,
                                                                     "form": form})
    
        
def change_paste_favorite(request):
    """
    Add/remove paste from user's favorites, and respond with JSON
    """
    response = {"status": "success",
                "data": {}}
    
    char_id = None or request.POST["char_id"]
    action = None or request.POST["action"]
    
    if not request.user.is_authenticated():
        response["status"] = "fail"
        response["data"]["message"] = "Not logged in."
    else:
        if action == "add":
            favorite = Favorite(user=request.user, paste=Paste.objects.get(char_id=char_id))
            favorite.save()
            response["data"]["char_id"] = char_id
            response["data"]["favorited"] = True
        elif action == "remove":
            result = Favorite.objects.filter(user=request.user, paste__char_id=char_id).delete()
            response["data"]["char_id"] = char_id
            response["data"]["favorited"] = False
        else:
            response["status"] = "fail"
            response["data"]["message"] = "Valid action wasn't provided."
            
    return HttpResponse(json.dumps(response))