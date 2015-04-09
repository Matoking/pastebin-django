from django import forms
from pastes.models import Paste

import highlighting

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
        (Paste.NEVER, "Never"),
        (Paste.FIFTEEN_MINUTES, "15 minutes"),
        (Paste.ONE_HOUR, "1 hour"),
        (Paste.ONE_DAY, "1 day"),
        (Paste.ONE_WEEK, "1 week"),
        (Paste.ONE_MONTH, "1 month"),
    )
    
    title = forms.CharField(max_length=128,
                            required=False,
                            widget=forms.TextInput(attrs={"placeholder": "Untitled"}))
    text = forms.CharField(min_length=1,
                           max_length=100000)
    expiration = forms.ChoiceField(choices=EXPIRATION_CHOICES)

    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    
    syntax_highlighting = forms.ChoiceField(choices=highlighting.settings.LANGUAGES)
    
    def clean_title(self):
        """
        Replace the title with Untitled if it is not provided
        """
        title = self.cleaned_data.get("title")
        
        # If user provides an empty title, replace it with Untitled
        if title.strip() == "":
            title = "Untitled"
            
        return title
    
class EditPasteForm(forms.Form):
    """
    Form to edit the paste
    """
    title = forms.CharField(max_length=128,
                            required=False,
                            widget=forms.TextInput(attrs={"placeholder": "Untitled"}))
    visibility = forms.ChoiceField(choices=SubmitPasteForm.VISIBILITY_CHOICES)
    
    syntax_highlighting = forms.ChoiceField(choices=highlighting.settings.LANGUAGES)
    text = forms.CharField(min_length=1,
                           max_length=100000)
    
    def clean_title(self):
        """
        Replace an empty title with "Untitled"
        """
        title = self.cleaned_data.get("title")
        
        if title.strip() == "":
            title = "Untitled"
            
        return title