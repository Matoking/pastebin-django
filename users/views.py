from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect
from django.db import transaction

from django_redis import get_redis_connection

from users.models import PastebinUser

from users.forms import RegisterForm, LoginForm, ChangePreferencesForm, ChangePasswordForm, VerifyPasswordForm
from users.models import Favorite, SiteSettings

from pastes.models import Paste

from pastebin.util import Paginator

import math

def register_view(request):
    """
    Register a new user
    """
    # Check if the user is authenticated
    if request.user.is_authenticated():
        # User is already authenticated
        return render(request, 'users/register/already_logged_in.html')
    else:
        register_form = RegisterForm(request.POST or None)
        
        if request.method == 'POST': # Form data was submitted
            if register_form.is_valid(): # Form data is valid
                # Create the user
                with transaction.atomic():
                    user = User.objects.create_user(register_form.cleaned_data['username'],
                                                    "N/A", # we don't deal with email addresses
                                                    register_form.cleaned_data['password'])
                    PastebinUser.create_user(user)
                                                  
                # TODO: Show a different message if the registration fails
                return render(request, 'users/register/register_success.html')
                
    # Show the registration page
    return render(request, "users/register/register.html", { "form": register_form })
    
def login_view(request):
    """
    Log the user in
    """
    # Check if the user is authenticated
    if request.user.is_authenticated():
        # User is authenticated
        return render(request, "users/login/logged_in.html")
    else:
        login_form = LoginForm(request.POST or None)
        
        # User is NOT authenticated
        if request.method == 'POST': # Form data was submitted
            if login_form.is_valid(): # Form data is valid
                user = authenticate(username = login_form.cleaned_data['username'],
                                    password = login_form.cleaned_data['password'])
                
                if user is not None and user.is_active:
                    login(request, user)
                    return render(request, "users/login/logged_in.html")
                else:
                    # Couldn't authenticate, either the username or password is wrong
                    error = "User doesn't exist or the password is incorrect."
                    login_form._errors['password'] = login_form.error_class([error])
                    
    # Show the login form
    return render(request, "users/login/login.html", { "form": login_form })

def logout_view(request):
    """
    Logout the user and show the logout page
    """
    if request.user.is_authenticated():
        logout(request)
        
    return render(request, 'users/logout/logged_out.html')

def profile(request, username, tab="home", page=1):
    """
    Show a publicly visible profile page
    """
    page = int(page)
    
    try:
        profile_user = cache.get("user:%s" % username)
        
        if profile_user == None:
            profile_user = User.objects.get(username=username)
            cache.set("user:%s" % username, profile_user)
        elif profile_user == False:
            return render(request, "users/profile/profile_error.html", {"reason": "not_found"}, status=404)
    except ObjectDoesNotExist:
        cache.set("user:%s" % username, False)
        return render(request, "users/profile/profile_error.html", {"reason": "not_found"}, status=404)
    
    # Get user's settings
    profile_settings = cache.get("site_settings:%s" % username)
    
    if profile_settings == None:
        try:
            profile_settings = SiteSettings.objects.get(user=profile_user)
        except ObjectDoesNotExist:
            profile_settings = SiteSettings(user=profile_user)
            profile_settings.save()
        cache.set("site_settings:%s" % username, profile_settings)
    
    if not profile_user.is_active:
        return render(request, "users/profile/profile_error.html", {"reason": "not_found"}, status=404)
    
    if request.user != profile_user:
        total_paste_count = cache.get("user_public_paste_count:%s" % profile_user.username)
    else:
        total_paste_count = cache.get("user_paste_count:%s" % profile_user.username)
    
    # If user is viewing his own profile, also include hidden pastes
    if total_paste_count == None and request.user != profile_user:
        total_paste_count = Paste.objects.filter(user=profile_user, removed=Paste.NO_REMOVAL).filter(hidden=False).count()
        cache.set("user_public_paste_count:%s" % profile_user.username, total_paste_count)
    elif total_paste_count == None and request.user == profile_user:
        total_paste_count = Paste.objects.filter(user=profile_user, removed=Paste.NO_REMOVAL).count()
        cache.set("user_paste_count:%s" % profile_user.username, total_paste_count)
        
    total_favorite_count = cache.get("user_favorite_count:%s" % profile_user.username)
    
    if total_favorite_count == None:
        total_favorite_count = Favorite.objects.filter(user=profile_user).count()
        cache.set("user_favorite_count:%s" % profile_user.username, total_favorite_count)
    
    args = {"profile_user": profile_user,
            "profile_settings": profile_settings,
            "current_page": page,
            "tab": tab,
            
            "total_favorite_count": total_favorite_count,
            "total_paste_count": total_paste_count}
    
    if tab == "home":
        return home(request, args)
    elif tab == "pastes":
        return pastes(request, profile_user, args, page)
    elif tab == "favorites":
        return favorites(request, profile_user, args, page)
    # The remaining pages require authentication, so redirect through settings()
    else:
        return settings(request, profile_user, args, tab)
    
def settings(request, username, args={}, tab="change_password"):
    """
    Show a page which allows the user to change his settings
    """
    if not request.user.is_authenticated():
        return render(request, "users/settings/settings_error.html", {"reason": "not_logged_in"})
    
    profile_user = User.objects.get(username=username)
    
    if request.user.id != profile_user.id:
        return render(request, "users/settings/settings_error.html", {"reason": "incorrect_user"})
    
    if tab == "change_preferences":
        return change_preferences(request, args)
    if tab == "change_password":
        return change_password(request, args)
    elif tab == "delete_account":
        return delete_account(request, args)
    
def home(request, args):
    """
    Display user profile's home with the most recent pastes and favorites
    """
    # Get favorites only if user has made them public
    if args["profile_settings"].public_favorites or request.user == args["profile_user"]:
        args["favorites"] = cache.get("profile_favorites:%s" % args["profile_user"].username)
        
        if args["favorites"] == None:
            args["favorites"] = Favorite.objects.filter(user=args["profile_user"]).order_by('-added').select_related('paste')[:10]
            cache.set("profile_favorites:%s" % args["profile_user"].username, args["favorites"])
            
    if request.user == args["profile_user"]:
        args["pastes"] = cache.get("profile_pastes:%s" % args["profile_user"].username)
        
        if args["pastes"] == None:
            args["pastes"] = Paste.objects.get_pastes(args["profile_user"], include_hidden=True, count=10)
            cache.set("profile_pastes:%s" % args["profile_user"].username, args["pastes"])
    else:
        args["pastes"] = cache.get("profile_public_pastes:%s" % args["profile_user"].username)
        
        if args["pastes"] == None:
            args["pastes"] = Paste.objects.get_pastes(args["profile_user"], include_hidden=False, count=10)
            cache.set("profile_public_pastes:%s" % args["profile_user"].username, args["pastes"])
    
    return render(request, "users/profile/home/home.html", args)
    
def pastes(request, user, args, page=1):
    """
    Show all of user's pastes
    """
    PASTES_PER_PAGE = 15
    
    args["total_pages"] = int(math.ceil(float(args["total_paste_count"]) / float(PASTES_PER_PAGE)))
    
    if page > args["total_pages"]:
        page = max(int(args["total_pages"]), 1)
    
    offset = (page-1) * PASTES_PER_PAGE
    
    if request.user == user:
        args["pastes"] = cache.get("user_pastes:%s:%s" % (user.username, page))
        
        if args["pastes"] == None:
            args["pastes"] = Paste.objects.get_pastes(user, count=PASTES_PER_PAGE, include_hidden=True, offset=offset)
            cache.set("user_pastes:%s:%s" % (user.username, page), args["pastes"])
    else:
        args["pastes"] = cache.get("user_public_pastes:%s:%s" % (user.username, page))
        
        if args["pastes"] == None:
            args["pastes"] = Paste.objects.get_pastes(user, count=PASTES_PER_PAGE, include_hidden=False, offset=offset)
            cache.set("user_public_pastes:%s:%s" % (user.username, page), args["pastes"])
        
    args["pages"] = Paginator.get_pages(page, PASTES_PER_PAGE, args["total_paste_count"])
    args["current_page"] = page
    
    return render(request, "users/profile/pastes/pastes.html", args)
    
def favorites(request, user, args, page=1):
    """
    Show all of user's favorites
    """
    FAVORITES_PER_PAGE = 15
    
    if not args["profile_settings"].public_favorites and request.user != args["profile_user"]:
        # Don't show pastes to other users if the user doesn't want to
        return render(request, "users/profile/favorites/favorites_hidden.html", args)
    
    args["total_pages"] = int(math.ceil(float(args["total_favorite_count"]) / float(FAVORITES_PER_PAGE)))
    
    if page > args["total_pages"]:
        page = max(int(args["total_pages"]), 1)
        
    start = (page-1) * FAVORITES_PER_PAGE
    end = start + FAVORITES_PER_PAGE
    
    args["favorites"] = cache.get("user_favorites:%s:%s" % (user.username, page))
    
    if args["favorites"] == None:
        args["favorites"] = Favorite.objects.filter(user=user).select_related("paste")[start:end]
        cache.set("user_favorites:%s:%s" % (user.username, page), args["favorites"])
        
    args["pages"] = Paginator.get_pages(page, FAVORITES_PER_PAGE, args["total_favorite_count"])
    args["current_page"] = page
    
    return render(request, "users/profile/favorites/favorites.html", args)

def remove_favorite(request):
    """
    Remove a favorite and redirect the user back to the favorite listing
    """
    if "favorite_id" not in request.POST or not int(request.POST["favorite_id"]):
        return HttpResponse("Favorite ID was not valid.", status=422)
    
    if "page" not in request.POST or not int(request.POST["page"]):
        return HttpResponse("Page was not valid.", status=422)
    
    favorite_id = int(request.POST["favorite_id"])
    page = int(request.POST["page"])
    
    favorite = Favorite.objects.get(id=favorite_id)
    
    if not request.user.is_authenticated():
        return HttpResponse("You are not authenticated", status=422)
    
    if favorite.user != request.user:
        return HttpResponse("You can't delete someone else's favorites.", status=422)
    
    favorite.delete()
    
    cache.delete("profile_favorites:%s" % request.user.username)
    cache.delete("user_favorite_count:%s" % request.user.username)
    
    return HttpResponseRedirect(reverse("users:favorites", kwargs={"username": request.user.username,
                                                                   "page": page}))

def change_preferences(request, args):
    """
    Change various profile-related preferences
    """
    site_settings = SiteSettings.objects.get(user=request.user)
    
    form = ChangePreferencesForm(request.POST or None, initial={"public_favorites": site_settings.public_favorites})
    
    preferences_changed = False
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        site_settings.public_favorites = cleaned_data["public_favorites"]
        
        site_settings.save()
        
        cache.set("site_settings:%s" % request.user.username, site_settings)
        
        preferences_changed = True
        
    args["form"] = form
        
    args["preferences_changed"] = preferences_changed
        
    return render(request, "users/settings/change_preferences/change_preferences.html", args)

def change_password(request, args):
    """
    Change the user's password
    """
    form = ChangePasswordForm(request.POST or None, user=request.user)
    
    password_changed = False
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        
        request.user.set_password(cleaned_data["new_password"])
        request.user.save()
        
        # Session auth hash needs to be updated after changing the password
        # or the user will be logged out
        update_session_auth_hash(request, request.user)
        
        password_changed = True
        
    args["form"] = form
    args["password_changed"] = password_changed
        
    return render(request, "users/settings/change_password/change_password.html", args)

def delete_account(request, args):
    """
    Delete the user's account
    """
    form = VerifyPasswordForm(request.POST or None, user=request.user)
    
    if form.is_valid():
        PastebinUser.delete_user(request.user)
        logout(request)
        
        return render(request, "users/settings/delete_account/account_deleted.html")
    
    args["form"] = form
    
    return render(request, "users/settings/delete_account/delete_account.html", args)