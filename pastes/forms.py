from django import forms

class SubmitPasteForm(forms.Form):
    """
    Form to submit the paste
    
    Contains paste text, title and optionally, time until expiration
    """
    paste_text = forms.SlugField(widget=forms.Textarea,
                                 max_length=100000)
    paste_title = forms.CharField(max_length=128)