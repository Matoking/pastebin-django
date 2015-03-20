from django import forms
from pastes.models import Paste

class RegisterForm(forms.Form):
    """
    Form to register
    """
    username = forms.CharField(max_length=64,
                               required=True)
    password = forms.CharField(min_length=6,
                               max_length=128,
                               widget = forms.TextInput(attrs={ 'type': 'password' }))
    confirm_password = forms.CharField(min_length=6,
                                       max_length=128,
                                       widget = forms.TextInput(attrs={ 'type': 'password' }))