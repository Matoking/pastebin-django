from django.shortcuts import render, redirect
from django.db.models import Q

from django.utils import timezone

from pastes.forms import SubmitPasteForm
from pastes.models import Paste, LatestPastes

from pastebin.util import Paginator

import highlighting
import math

def home(request):
    """
    Display the index page with the form to submit a paste, as well as the most recent
    pastes
    """
    paste_form = SubmitPasteForm(request.POST or None)
    
    latest_pastes = Paste.objects.get_pastes(include_expired=False, include_hidden=False,
                                             count=15)
    
    languages = highlighting.settings.LANGUAGES
    
    if paste_form.is_valid():
        paste_data = paste_form.cleaned_data
        
        user = None
        if request.user.is_authenticated():
            user = request.user
        
        paste = Paste()
        char_id = paste.add_paste(title=paste_data["title"],
                                  user=user,
                                  text=paste_data["text"],
                                  expiration=paste_data["expiration"],
                                  visibility=paste_data["visibility"],
                                  format=paste_data["syntax_highlighting"],
                                  encrypted=paste_data["encrypted"])
        
        # Redirect to the newly created paste
        return redirect("show_paste", char_id=char_id)
    
    return render(request, "home/home.html", {"form": paste_form,
                                              "latest_pastes": latest_pastes,
                                              "languages": languages })
    
def latest_pastes(request, page=1):
    """
    Show all of the pastes starting from the newest
    """
    PASTES_PER_PAGE = 15
    
    page = int(page)
    
    current_datetime = timezone.now()
    
    offset = (page-1) * PASTES_PER_PAGE
    total_paste_count = Paste.objects.filter(hidden=False).filter(Q(expiration_datetime__isnull=True) | Q(expiration_datetime__lte=current_datetime)).count()    
    
    pastes = Paste.objects.get_pastes(count=PASTES_PER_PAGE, offset=offset, include_hidden=False)
    pages = Paginator.get_pages(page, PASTES_PER_PAGE, total_paste_count)
    total_pages = math.ceil(float(total_paste_count) / float(PASTES_PER_PAGE))
    
    return render(request, "latest_pastes/latest_pastes.html", {"current_page": page,
                                                                "pastes": pastes,
                                                                "pages": pages,
                                                                "total_pages": total_pages,
                                                                "total_paste_count": total_paste_count})
    
def random_paste(request):
    """
    Redirect to a random paste
    """
    char_id = Paste.get_random_char_id()
    
    if char_id:
        return redirect("show_paste", char_id=char_id)
    else:
        return redirect("home:home")