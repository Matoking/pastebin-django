from pastes.models import PasteReport

class PastebinMiddleware(object):
    def process_request(self, request):
        """
        Include the amount of unread paste reports if the current user is an admin
        """
        if request.user and request.user.is_staff:
            request.unread_paste_report_count = PasteReport.objects.filter(checked=False).count()