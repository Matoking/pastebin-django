from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.exceptions import ObjectDoesNotExist

from users.models import PastebinUser

from users.forms import RegisterForm, LoginForm, ChangePasswordForm, VerifyPasswordForm
from users.models import Favorite

from pastes.models import Paste

from pastesite.util import Paginator

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
                user = User.objects.create_user(register_form.cleaned_data['username'],
                                                "N/A", # we don't deal with email addresses
                                                register_form.cleaned_data['password'])
                                                  
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
        profile_user = User.objects.get(username=username)
    except ObjectDoesNotExist:
        return render(request, "users/profile/profile_error.html", {"reason": "not_found"}, status=404)
    
    if not profile_user.is_active:
        return render(request, "users/profile/profile_error.html", {"reason": "not_found"}, status=404)
    
    args = {"profile_user": profile_user,
            "current_page": page,
            "tab": tab,
            
            "total_favorite_count": Favorite.get_favorite_count(profile_user),
            "total_paste_count": Paste.get_paste_count(profile_user)}
    
    if tab == "home":
        return home(request, args)
    elif tab == "pastes":
        return pastes(request, profile_user, args, page)
    elif tab == "favorites":
        return favorites(request, profile_user, args, page)
    
def settings(request, username, tab="change_password"):
    """
    Show a page which allows the user to change his settings
    """
    if not request.user.is_authenticated():
        return render(request, "users/settings/settings_error.html", {"reason": "not_logged_in"})
    
    profile_user = User.objects.get(username=username)
    
    if request.user.id != profile_user.id:
        return render(request, "users/settings/settings_error.html", {"reason": "incorrect_user"})
    
    if tab == "change_password":
        return change_password(request)
    elif tab == "delete_account":
        return delete_account(request)
    
def home(request, args):
    """
    Display user profile's home with the most recent pastes and favorites
    """
    args["favorites"] = Favorite.get_favorites(args["profile_user"], count=10)
    args["pastes"] = Paste.get_pastes(args["profile_user"], count=10)
    
    return render(request, "users/profile/home/home.html", args)
    
def pastes(request, user, args, page=1):
    """
    Show all of user's pastes
    """
    PASTES_PER_PAGE = 15
    offset = (page-1) * PASTES_PER_PAGE
    
    args["pastes"] = Paste.get_pastes(user, count=PASTES_PER_PAGE, offset=offset)
    args["pages"] = Paginator.get_pages(page, PASTES_PER_PAGE, args["total_paste_count"])
    args["total_pages"] = math.ceil(float(args["total_paste_count"]) / float(PASTES_PER_PAGE))
    
    return render(request, "users/profile/pastes/pastes.html", args)
    
def favorites(request, user, args, page=1):
    """
    Show all of user's favorites
    """
    FAVORITES_PER_PAGE = 15
    offset = (page-1) * FAVORITES_PER_PAGE
    
    args["favorites"] = Favorite.get_favorites(user, count=FAVORITES_PER_PAGE, offset=offset)
    args["pages"] = Paginator.get_pages(page, FAVORITES_PER_PAGE, args["total_favorite_count"])
    args["total_pages"] = math.ceil(float(args["total_favorite_count"]) / float(FAVORITES_PER_PAGE))
    
    return render(request, "users/profile/favorites/favorites.html", args)

def change_password(request):
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
        
    return render(request, "users/settings/change_password/change_password.html", {"profile_user": request.user,
                                                                                   "form": form,
                                                                                   
                                                                                   "tab": "change_password",
                                                                                   "password_changed": password_changed})

def delete_account(request):
    """
    Delete the user's account
    """
    form = VerifyPasswordForm(request.POST or None, user=request.user)
    
    if form.is_valid():
        PastebinUser.delete_user(request.user)
        logout(request)
        
        return render(request, "users/settings/delete_account/account_deleted.html")
    
    return render(request, "users/settings/delete_account/delete_account.html", {"profile_user": request.user,
                                                                                 "form": form,
                                                                                 
                                                                                 "tab": "delete_account"})