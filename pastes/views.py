from django.shortcuts import render, redirect
from django.http import HttpResponse

from pastes.forms import SubmitPasteForm
from pastes.models import Paste

def submit_paste(request):
    submit_paste_form = SubmitPasteForm(request.POST or None)
    
    if submit_paste_form.is_valid():
        paste_data = submit_paste_form.cleaned_data
        
        user = None
        if request.user.is_authenticated():
            user = request.user
        
        char_id = Paste.add_paste(title=paste_data["paste_title"],
                                  user=user,
                                  text=paste_data["paste_text"],
                                  expiration=paste_data["paste_expiration"],
                                  visibility=paste_data["paste_visibility"])
        
        # Redirect to the newly created paste
        return redirect("show_paste", char_id=char_id)
    else:
        # On error, redirect to home
        return redirect("home:home")
    
def show_paste(request, char_id, raw=False, download=False):
    # If paste has expired, show the ordinary "paste not found" page
    if Paste.is_paste_expired(char_id=char_id):
        return render(request, "pastes/paste_error.html", {"reason": "expired"}, status=404)
    
    paste = Paste.get_paste(char_id=char_id, include_text=True)
    
    if paste is None:
        return render(request, "pastes/paste_error.html", {"reason": "not_found"}, status=404)
    
    if raw == True:
        response = HttpResponse(paste["text"], content_type='text/plain')
        return response
    elif download == True:
        response = HttpResponse(paste["text"], content_type='application/octet-stream')
        response["Content-Disposition"] = 'attachment; filename="%s.txt"' % char_id
        return response
    else:
        return render(request, "pastes/show_paste.html", {"paste": paste})