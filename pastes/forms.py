from django import forms
from pastes.models import Paste

class SubmitPasteForm(forms.Form):
    """
    Form to submit the paste
    
    Contains paste text, title and optionally, time until expiration
    """
    VISIBILITY_CHOICES = (
        (Paste.PUBLIC, "Public"),
        (Paste.HIDDEN, "Hidden")
    )
    
    EXPIRATION_CHOICES = (
        (Paste.NEVER, "never"),
        (Paste.FIFTEEN_MINUTES, "15 minutes"),
        (Paste.ONE_HOUR, "1 hour"),
        (Paste.ONE_DAY, "1 day"),
        (Paste.ONE_WEEK, "1 week"),
        (Paste.ONE_MONTH, "1 month"),
    )
    
    paste_title = forms.CharField(max_length=128)
    paste_text = forms.CharField(min_length=1,
                                 max_length=100000)
    paste_expiration = forms.ChoiceField(choices=EXPIRATION_CHOICES)

    paste_visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)