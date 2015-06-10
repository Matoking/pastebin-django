from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from django.db import transaction

from pastes.models import Paste, PasteReport

from pastes.admin_forms import ProcessReportForm

def process_report(request, report_ids):
    """
    Process a report for a paste
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponse("You are not an admin!", status=422)
    
    reports = PasteReport.objects.filter(id__in=report_ids.split(","))
    
    pastes = None
    paste_ids = []
    
    for report in reports:
        if report.paste.id not in paste_ids:
            paste_ids.append(report.paste.id) 
            
    pastes = Paste.objects.filter(id__in=paste_ids)
    
    paste_results = []
    
    for paste in pastes:
        result = {"paste": paste,
                  "paste_text": paste.get_text(False)}
        paste_results.append(result)
    
    form = ProcessReportForm(request.POST or None)
    
    if form.is_valid():
        cleaned_data = form.cleaned_data
        if "ignore" in request.POST:
            reports.update(checked=True)
            
            return render(request, "pastes/admin/process_report/process_success.html", {"action": "ignore"})
        elif "remove" in request.POST:
            with transaction.atomic():
                for paste in pastes:
                    paste.remove_paste(reason=cleaned_data["removal_reason"])
                    
                reports.update(checked=True)
                
            return render(request, "pastes/admin/process_report/process_success.html", {"action": "remove"})
        elif "delete" in request.POST:
            with transaction.atomic():
                for paste in pastes:
                    paste.delete_paste(reason=cleaned_data["removal_reason"])
                    
                reports.update(checked=True)
                
            return render(request, "pastes/admin/process_report/process_success.html", {"action": "delete"})
        
    return render(request, "pastes/admin/process_report/process.html", {"reports": reports,
                                                                        "report_ids": report_ids,
                                                                        
                                                                        "paste_results": paste_results})