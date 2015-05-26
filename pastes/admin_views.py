from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from pastes.models import Paste, PasteReport

def process_report(request, report_ids):
    """
    Process a report for a paste
    """
    reports = PasteReport.objects.filter(id__in=report_ids.split(","))
    
    paste_id = None
    
    for report in reports:
        if paste_id != None and report.paste.id != paste_id:
            return render(request, "pastes/admin/process_report/process_error.html", {"reason": "multiple_pastes"})
            
        if paste_id == None:
            paste_id = report.paste.id
    
    return render(request, "pastes/admin/process_report/process.html")