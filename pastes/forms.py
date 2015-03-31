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
        (Paste.NEVER, "never"),
        (Paste.FIFTEEN_MINUTES, "15 minutes"),
        (Paste.ONE_HOUR, "1 hour"),
        (Paste.ONE_DAY, "1 day"),
        (Paste.ONE_WEEK, "1 week"),
        (Paste.ONE_MONTH, "1 month"),
    )
    
    title = forms.CharField(max_length=128,
                            initial="Untitled",
                            required=False)
    text = forms.CharField(min_length=1,
                           max_length=100000)
    expiration = forms.ChoiceField(choices=EXPIRATION_CHOICES)

    visibility = forms.ChoiceField(choices=VISIBILITY_CHOICES)
    
    syntax_highlighting = forms.ChoiceField(choices=highlighting.settings.LANGUAGES)
    
    def clean(self):
        """
        Override the clean procedure to handle empty paste titles
        """
        self.cleaned_data = super(SubmitPasteForm, self).clean()
        
        # If user provides an empty title, replace it with Untitled
        if self.cleaned_data["title"].strip() == "":
            self.cleaned_data["title"] = "Untitled"