from django.shortcuts import render, redirect
from pastes.forms import SubmitPasteForm
from pastes.models import Paste

def submit_paste(request):
    submit_paste_form = SubmitPasteForm(request.POST or None)
    
    if submit_paste_form.is_valid():
        paste_data = submit_paste_form.cleaned_data
        
        char_id = Paste.add_paste(title=paste_data["paste_title"],
                                  text=paste_data["paste_text"],
                                  expiration=paste_data["paste_expiration"],
                                  visibility=paste_data["paste_visibility"])
        
        # Redirect to the newly created paste
        return redirect("show_paste", char_id=char_id)
    else:
        # On error, redirect to home
        return redirect("home:home")
    
def show_paste(request, char_id):
    paste = Paste.get_paste(char_id=char_id, include_text=True)
    
    return render(request, "pastes/show_paste.html", {"paste": paste})
    pass