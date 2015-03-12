from django.shortcuts import render

from pastes.forms import SubmitPasteForm

def home(request):
    """
    Display the index page with the form to submit a paste, as well as the most recent
    pastes
    """
    paste_form = SubmitPasteForm(None)
    
    return render(request, 'home/home.html', {"form": paste_form})