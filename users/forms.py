from django import forms

from django.contrib.auth.models import User
from django.contrib.auth import authenticate

from django.core.urlresolvers import reverse, NoReverseMatch

from pastes.models import Paste

class RegisterForm(forms.Form):
    """
    User registration form
    """
    username = forms.CharField(max_length=64,
                               required=True)
    password = forms.CharField(min_length=6,
                               max_length=128,
                               widget = forms.TextInput(attrs={ 'type': 'password' }))
    confirm_password = forms.CharField(min_length=6,
                                       max_length=128,
                                       widget = forms.TextInput(attrs={ 'type': 'password' }))
    
    def clean_username(self):
        """
        Check that the username isn't already in use and that it doesn't conflict
        with an existing URL
        """
        username = self.cleaned_data.get("username")
        
        # Ehh, nobody will notice
        if User.objects.filter(username__iexact=username).count() > 0:
            # The username exists
            raise forms.ValidationError("The username is already in use.")
                
        # Make sure the username doesn't conflict with the URLs
        url_conflict = True
        try:
            test = reverse('users:' + username)
        except NoReverseMatch:
            url_conflict = False
            
        if url_conflict:
            # The username can't be used because it conflicts with an URL
            raise forms.ValidationError("This username can't be used.")
        
        return username
    
    def clean_confirm_password(self):
        """
        Check that the provided passwords match
        """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")
        
        if password != confirm_password:
            raise forms.ValidationError("The provided password didn't match.")
        
        return confirm_password
    
class LoginForm(forms.Form):
    """
    User login form
    """
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=128,
                               widget = forms.TextInput(attrs={ 'type': 'password' }))
    
class ChangePasswordForm(forms.Form):
    """
    Form to change the user's password
    """
    current_password = forms.CharField(max_length=128,
                                       widget=forms.TextInput(attrs={'type': 'password'}))
    
    new_password = forms.CharField(min_length=6,
                                   max_length=128,
                                   widget=forms.TextInput(attrs={'type': 'password'}))
    confirm_new_password = forms.CharField(min_length=6,
                                           max_length=128,
                                           widget=forms.TextInput(attrs={'type': 'password'}))
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        
        if self.user == None:
            raise AttributeError("'%s' requires a valid Django user object as its user parameter" % self.__class__.__name__)
        
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        
    def clean_current_password(self):
        """
        Check that the user has logged in and provided the correct password
        """
        if not self.user or not self.user.is_authenticated():
            raise forms.ValidationError("You are not logged in.")
        
        password = self.cleaned_data.get('current_password')
        
        if authenticate(username=self.user.username, password=password) == None:
            raise forms.ValidationError("The provided password was not correct")
        
        return password
    
    def clean_confirm_new_password(self):
        """
        Check that the provided new passwords match
        """
        new_password = self.cleaned_data.get("new_password")
        confirm_new_password = self.cleaned_data.get("confirm_new_password")
        
        if new_password != confirm_new_password:
            raise forms.ValidationError("The provided passwords didn't match.")
        
        return confirm_new_password
    
class VerifyPasswordForm(forms.Form):
    """
    Form to verify the user's password
    """
    password = forms.CharField(max_length=128,
                               widget=forms.TextInput(attrs={ 'type': 'password' }),
                               help_text="You need to enter your password to perform this action.")
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        
        if self.user == None:
            raise AttributeError("'%s' requires a valid Django user object as its user parameter" % self.__class__.__name__)
        
        super(VerifyPasswordForm, self).__init__(*args, **kwargs)
    
    def clean_password(self):
        """
        Check that the user has logged in and provided the correct password
        """
        if not self.user or not self.user.is_authenticated():
            raise forms.ValidationError("You are not logged in.")
        
        password = self.cleaned_data.get('password')
        
        if authenticate(username=self.user.username, password=password) == None:
            raise forms.ValidationError("The provided password was not correct.")
        
        return password