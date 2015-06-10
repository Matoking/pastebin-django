from django import forms

class ProcessReportForm(forms.Form):
    """
    Form to process a set of paste reports
    """
    removal_reason = forms.CharField(max_length=1024,
                                     required=False,
                                     initial="")