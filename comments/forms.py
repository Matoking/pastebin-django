from django import forms

class SubmitCommentForm(forms.Form):
    """
    The form for submitting a comment
    """
    text = forms.CharField(max_length=2000)