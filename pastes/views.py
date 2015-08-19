from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from django_redis import get_redis_connection

from pastes.forms import SubmitPasteForm, EditPasteForm, RemovePasteForm, ReportPasteForm
from pastes.models import Paste, PasteReport, PasteVersion

from comments.models import Comment

from users.models import Favorite, Limiter
from users.forms import VerifyPasswordForm

from ipware.ip import get_real_ip

from pastebin.util import Paginator

import math
import json
    
def show_paste(request, char_id, raw=False, download=False, version=None):
    """
    Show the paste, possibly as raw text or as a download
    """
    # If paste has expired, show the ordinary "paste not found" page
    try:
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            paste = Paste.objects.select_related("user").get(char_id=char_id)
            cache.set("paste:%s" % char_id, paste)
        elif paste == False:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
        
        if version == None:
            version = paste.version
            
        paste_version = cache.get("paste_version:%s:%s" % (char_id, version))
        
        if paste_version == None:
            paste_version = PasteVersion.objects.get(paste=paste, version=version)
            cache.set("paste_version:%s:%s" % (char_id, version), paste_version)
    except ObjectDoesNotExist:
        cache.set("paste:%s" % char_id, False)
        return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
    
    if paste.is_expired():
        return render(request, "pastes/show_paste/show_error.html", {"reason": "expired"}, status=404)
    if paste.is_removed():
        if paste.removed == Paste.USER_REMOVAL:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "user_removed",
                                                                         "removal_reason": paste.removal_reason}, status=404)
        elif paste.removed == Paste.ADMIN_REMOVAL:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "admin_removed",
                                                                         "removal_reason": paste.removal_reason}, status=404)
        
    if raw:
        text = paste.get_text(formatted=False, version=version)
        response = HttpResponse(text, content_type='text/plain')
        return response
    elif download:
        text = paste.get_text(formatted=False, version=version)
        response = HttpResponse(text, content_type='application/octet-stream')
        response["Content-Disposition"] = 'attachment; filename="%s.txt"' % char_id
        return response
    else:
        # Display the paste as normal
        paste_favorited = False
        
        if request.user.is_authenticated():
            paste_favorited = Favorite.has_user_favorited_paste(request.user, paste)
            
        # Add a hit to this paste if the hit is an unique (1 hit = 1 IP address once per 24 hours)
        ip_address = get_real_ip(request)
        
        if ip_address != None:
            paste_hits = paste.add_hit(ip_address)
        else:
            paste_hits = paste.get_hit_count()
            
        comment_count = cache.get("paste_comment_count:%s" % char_id)
        
        if comment_count == None:
            comment_count = Comment.objects.filter(paste=paste).count()
            cache.set("paste_comment_count:%s" % char_id, comment_count)
        
        paste_text = paste.get_text(version=version)
            
        return render(request, "pastes/show_paste/show_paste.html", {"paste": paste,
                                                                     "paste_version": paste_version,
                                                                     "paste_text": paste_text,
                                                                     
                                                                     "version": version,
                                                                     
                                                                     "paste_favorited": paste_favorited,
                                                                     "paste_hits": paste_hits,
                                                                     
                                                                     "comment_count": comment_count})
        
def paste_history(request, char_id, page=1):
    """
    Show the earlier versions of the paste
    """
    VERSIONS_PER_PAGE = 15
    
    try:
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            paste = Paste.objects.select_related("user").get(char_id=char_id)
            cache.set("paste:%s" % char_id, paste)
        elif paste == False:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
        
    except ObjectDoesNotExist:
        return render(request, "pastes/show_paste/show_error.html", {"reason": "not_found"}, status=404)
    
    if paste.is_expired():
        return render(request, "pastes/show_paste/show_error.html", {"reason": "expired"}, status=404)
    if paste.is_removed():
        if paste.removed == Paste.USER_REMOVAL:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "user_removed",
                                                                         "removal_reason": paste.removal_reason}, status=404)
        elif paste.removed == Paste.ADMIN_REMOVAL:
            return render(request, "pastes/show_paste/show_error.html", {"reason": "admin_removed",
                                                                         "removal_reason": paste.removal_reason}, status=404)
    
    total_version_count = PasteVersion.objects.filter(paste=paste).count()
    total_pages = int(math.ceil(float(total_version_count) / float(VERSIONS_PER_PAGE)))
    
    if page > total_pages:
        page = max(int(total_pages), 1)
        
    offset = (page-1) * VERSIONS_PER_PAGE
    
    start = offset
    end = offset + VERSIONS_PER_PAGE
    
    history = cache.get("paste_history:%s:%s" % (char_id, page))
    
    if history == None:
        history = PasteVersion.objects.filter(paste=paste).order_by("-submitted")[start:end]
        cache.set("paste_history:%s:%s" % (char_id, page), history)
        
    pages = Paginator.get_pages(page, VERSIONS_PER_PAGE, total_version_count)
    
    return render(request, "pastes/paste_history/paste_history.html", {"paste": paste,
                                                                       "history": history,
                                                                       
                                                                       "current_page": page,
                                                                       
                                                                       "total_version_count": total_version_count,
                                                                       
                                                                       "total_pages": total_pages,
                                                                       "pages": pages})
        
def edit_paste(request, char_id):
    """
    Edit the paste
    """
    if not request.user.is_authenticated():
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_logged_in"})
    try:
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            paste = Paste.objects.select_related("user").get(char_id=char_id)
            cache.set("paste:%s" % char_id, paste)
        elif paste == False:
            return render(request, "pastes/edit_paste/show_error.html", {"reason": "not_found"}, status=404)
    except ObjectDoesNotExist:
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_found"})
    
    if paste.user != request.user and not request.user.is_staff:
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "not_owner"})
    
    if paste.is_expired():
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "expired"})
    if paste.is_removed():
        return render(request, "pastes/edit_paste/edit_error.html", {"reason": "removed"})
    
    if paste.hidden:
        visibility = "hidden"
    else:
        visibility = "public"
    
    edit_form = EditPasteForm(request.POST or None, request=request,
                                                    initial={"title": paste.title,
                                                             "visibility": visibility,
                                                             "syntax_highlighting": paste.format})
    
    if edit_form.is_valid():
        paste_data = edit_form.cleaned_data
        
        paste.update_paste(title=paste_data["title"],
                           text=paste_data["text"],
                           visibility=paste_data["visibility"],
                           format=paste_data["syntax_highlighting"],
                           encrypted=paste_data["encrypted"],
                           note=paste_data["note"])
        
        Limiter.increase_action_count(request, Limiter.PASTE_EDIT)
        
        return redirect("show_paste", char_id=char_id)
    
    paste_text = paste.get_text(formatted=False)
    
    return render(request, "pastes/edit_paste/edit_paste.html", {"paste": paste,
                                                                 "paste_text": paste_text,
                                                                 
                                                                 "form": edit_form})
        
def remove_paste(request, char_id):
    """
    Remove a single paste
    """
    if not request.user.is_authenticated():
        return render(request, "pastes/remove_paste/remove_error.html", {"reason": "not_logged_in"})
    
    try:
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            paste = Paste.objects.select_related("user").get(char_id=char_id)
            cache.set("paste:%s" % char_id, paste)
        elif paste == False:
            return render(request, "pastes/remove_paste/show_error.html", {"reason": "not_found"}, status=404)
    except ObjectDoesNotExist:
        return render(request, "pastes/remove_paste/remove_error.html", {"reason": "not_found"})
    
    # Check that the user can delete the paste
    if paste.user != request.user and not request.user.is_staff:
        return render(request, "pastes/remove_paste/remove_error.html", {"reason": "not_owner"})
    
    if paste.is_expired():
        return render(request, "pastes/remove_paste/remove_error.html", {"reason": "expired"})
    if paste.is_removed():
        return render(request, "pastes/remove_paste/remove_error.html", {"reason": "removed"})
    
    verify_form = VerifyPasswordForm(request.POST or None, user=request.user)
    remove_form = RemovePasteForm(request.POST or None)
    
    if verify_form.is_valid() and remove_form.is_valid():
        if remove_form.cleaned_data["removal_reason"].strip() == "":
            paste.remove_paste(type=Paste.USER_REMOVAL)
        else:
            paste.remove_paste(type=Paste.USER_REMOVAL, reason=remove_form.cleaned_data["removal_reason"])
        
        return render(request, "pastes/remove_paste/paste_removed.html")
    
    return render(request, "pastes/remove_paste/remove_paste.html", {"paste": paste,
                                                                     
                                                                     "verify_form": verify_form,
                                                                     "remove_form": remove_form})
    
def report_paste(request, char_id):
    """
    Report a paste
    """
    try:
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            paste = Paste.objects.select_related("user").get(char_id=char_id)
            cache.set("paste:%s" % char_id, paste)
        elif paste == False:
            return render(request, "pastes/report_paste/show_error.html", {"reason": "not_found"}, status=404)
    except ObjectDoesNotExist:
        return render(request, "pastes/report_paste/report_error.html", {"reason": "not_found"})
    
    if paste.is_expired():
        return render(request, "pastes/report_paste/report_error.html", {"reason": "expired"})
    if paste.is_removed():
        return render(request, "pastes/report_paste/report_error.html", {"reason": "removed"})
    
    user = None
    
    if request.user.is_authenticated():
        user = request.user
    
    form = ReportPasteForm(request.POST or None)
    
    if form.is_valid():
        report_data = form.cleaned_data
        report = PasteReport(paste=paste,
                             user=user,
                             
                             type=report_data["reason"],
                             text=report_data["text"])
        
        report.save()
        
        return render(request, "pastes/report_paste/paste_reported.html")
    
    return render(request, "pastes/report_paste/report_paste.html", {"paste": paste,
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
        paste = cache.get("paste:%s" % char_id)
        
        if paste == None:
            try:
                paste = Paste.objects.select_related("user").get(char_id=char_id)
                cache.set("paste:%s" % char_id, paste)
            except ObjectDoesNotExist:
                cache.set("paste:%s" % char_id, False)
                
                response["status"] = "fail"
                response["data"]["message"] = "The paste has been removed and can no longer be added to favorites."
                return HttpResponse(json.dumps(response))
        elif paste == False:
            response["status"] = "fail"
            response["data"]["message"] = "The paste has been removed and can no longer be added to favorites."
            return HttpResponse(json.dumps(response))
        
        if action == "add":
            if Favorite.objects.filter(user=request.user, paste=Paste.objects.get(char_id=char_id)).exists():
                response["status"] = "fail"
                response["data"]["message"] = "You can't favorite a paste multiple times"
                return HttpResponse(json.dumps(response))
            
            favorite = Favorite(user=request.user, paste=Paste.objects.get(char_id=char_id))
            favorite.save()
            cache.set("paste_favorited:%s:%s" % (request.user.username, char_id), True)
            
            # Update/clear related cache entries
            con = get_redis_connection()
            con.delete("user_favorite_count:%s" % request.user.username)
            
            response["data"]["char_id"] = char_id
            response["data"]["favorited"] = True
        elif action == "remove":
            result = Favorite.objects.filter(user=request.user, paste__char_id=char_id).delete()
            cache.set("paste_favorited:%s:%s" % (request.user.username, char_id), False)
            
            # Update/clear related cache entries
            con = get_redis_connection()
            con.delete("user_favorite_count:%s" % request.user.username)
            
            response["data"]["char_id"] = char_id
            response["data"]["favorited"] = False
        else:
            response["status"] = "fail"
            response["data"]["message"] = "Valid action wasn't provided."
            
    return HttpResponse(json.dumps(response))