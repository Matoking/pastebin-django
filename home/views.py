from django.shortcuts import render

from pastes.forms import SubmitPasteForm
from pastes.models import Paste, LatestPastes

import highlighting

def home(request):
    """
    Display the index page with the form to submit a paste, as well as the most recent
    pastes
    """
    paste_form = SubmitPasteForm(None)
    
    latest_pastes = LatestPastes.get_latest_pastes()
    
    languages = highlighting.settings.LANGUAGES
    
    return render(request, 'home/home.html', {"form": paste_form,
                                              "latest_pastes": latest_pastes,
                                              "languages": languages })