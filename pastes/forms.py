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
                           max_length=100000,
                           error_messages={"required": "The paste can't be empty."})
    expiration = forms.ChoiceField(choices=EXPIRATION_CHOICES)

    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    
    syntax_highlighting = forms.ChoiceField(choices=highlighting.settings.LANGUAGES,
                                            help_text="Languages marked with * are also supported with encrypted pastes.")
    
    encrypted = forms.BooleanField(initial=False,
                                   widget=forms.HiddenInput(),
                                   required=False)
    
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
    note = forms.CharField(max_length=1024,
                           required=False,
                           help_text="Optional note describing what was changed in the paste")
    title = forms.CharField(max_length=128,
                            required=False,
                            widget=forms.TextInput(attrs={"placeholder": "Untitled"}))
    visibility = forms.ChoiceField(choices=SubmitPasteForm.VISIBILITY_CHOICES)
    
    syntax_highlighting = forms.ChoiceField(choices=highlighting.settings.LANGUAGES,
                                            help_text="Languages marked with * are also supported with encrypted pastes.")
    text = forms.CharField(min_length=1,
                           max_length=100000,
                           error_messages={"required": "The paste can't be empty."})
    
    encrypted = forms.BooleanField(initial=False,
                                   widget=forms.HiddenInput(),
                                   required=False)
        
    def clean_title(self):
        """
        Replace an empty title with "Untitled"
        """
        title = self.cleaned_data.get("title")
        
        if title.strip() == "":
            title = "Untitled"
            
        return title
    
class RemovePasteForm(forms.Form):
    """
    Form to remove the paste
    """
    removal_reason = forms.CharField(max_length=512,
                                     required=False,
                                     help_text="You can provide a reason why you removed the paste.")
        
class ReportPasteForm(forms.Form):
    """
    Form to report a paste
    """
    REASONS = (
        ("illegal_content", "Illegal content"),
        ("adult_content", "Adult content"),
        ("spam", "Spam"),
        ("personal_information", "Personal information"),
        ("other", "Other")
    )
    
    reason = forms.ChoiceField(choices=REASONS)
    text = forms.CharField(min_length=1,
                           max_length=4096,
                           required=False,
                           widget=forms.Textarea)