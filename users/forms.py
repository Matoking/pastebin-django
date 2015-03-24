from django import forms
from django.contrib.auth.models import User

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
    
    def clean(self):
        """
        Check that the passwords match and the username is not in use
        """
        cleaned_data = super(RegisterForm, self).clean()
        
        # Check that passwords match
        if cleaned_data.get('password') != cleaned_data.get('confirm_password'):
            # Passwords don't match
            error = "The provided password didn't match."
            self._errors['confirm_password'] = self.error_class([error])
            
            # The password is not valid, so remove it
            if 'confirm_password' in cleaned_data:
                del cleaned_data['confirm_password']
        
        # Check that the username is not in use
        if cleaned_data.get('username'):
            # Ehh, nobody will notice
            if User.objects.filter(username__iexact=cleaned_data['username']).count() > 0:
                # The username exists
                error = "The username is already in use."
                self._errors['username'] = self.error_class([error])
                
                if 'username' in cleaned_data:
                    del cleaned_data['username']
        
        return cleaned_data
    
class LoginForm(forms.Form):
    username = forms.CharField(max_length=64)
    password = forms.CharField(max_length=128,
                               widget = forms.TextInput(attrs={ 'type': 'password' }))