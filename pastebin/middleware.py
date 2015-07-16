from pastes.models import PasteReport
from django.core.signals import Signal
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out

class PastebinMiddleware(object):
    def process_request(self, request):
        """
        Include the amount of unread paste reports if the current user is an admin
        """
        add_data_into_request(request)
            
@receiver(user_logged_in)
def on_user_logged_in(sender, **kwargs):
    add_data_into_request(kwargs["request"])

def add_data_into_request(request):
    if request.user.is_authenticated():
        if request.user.is_staff:
            request.unread_paste_report_count = PasteReport.objects.filter(checked=False).count()
    
@receiver(user_logged_out)
def remove_data_from_request(sender, **kwargs):
    request = kwargs["request"]
    
    try:
        del request.unread_paste_report_count
    except AttributeError:
        pass