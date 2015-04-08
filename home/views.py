from django.shortcuts import render, redirect

from pastes.forms import SubmitPasteForm
from pastes.models import Paste, LatestPastes

import highlighting

def home(request):
    """
    Display the index page with the form to submit a paste, as well as the most recent
    pastes
    """
    paste_form = SubmitPasteForm(request.POST or None)
    
    latest_pastes = LatestPastes.get_latest_pastes()
    
    languages = highlighting.settings.LANGUAGES
    
    if paste_form.is_valid():
        paste_data = paste_form.cleaned_data
        
        user = None
        if request.user.is_authenticated():
            user = request.user
        
        char_id = Paste.add_paste(title=paste_data["title"],
                                  user=user,
                                  text=paste_data["text"],
                                  expiration=paste_data["expiration"],
                                  visibility=paste_data["visibility"],
                                  format=paste_data["syntax_highlighting"])
        
        # Redirect to the newly created paste
        return redirect("show_paste", char_id=char_id)
    
    return render(request, 'home/home.html', {"form": paste_form,
                                              "latest_pastes": latest_pastes,
                                              "languages": languages })