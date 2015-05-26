from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect

from pastes.models import Paste, PasteReport
from pastes import admin_views

class PasteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "submitted")
    
class PasteReportAdmin(admin.ModelAdmin):
    list_display = ("checked", "user", "paste", "text")
    actions = ["mark_report_as_read", "process_reports"]
    ordering = ("checked",)
    
    def get_urls(self):
        urls = super(PasteReportAdmin, self).get_urls()
        my_urls = [
            url(r'^process_report/(?P<report_ids>.*)/$', admin_views.process_report, name="pastes_pastereport_process_report"),
        ]
        
        return my_urls + urls
    
    def mark_report_as_read(self, request, queryset):
        """
        Mark report as read without responding to the report
        """
        reports = queryset.update(checked=True)
        
        self.message_user(request, "%s report(s) were marked as read." % reports)
        
    def process_reports(self, request, queryset):
        """
        Process reports so that an action is performed on the paste that was reported
        """
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return HttpResponseRedirect(reverse("admin:pastes_pastereport_process_report", kwargs={"reports": ",".join(selected)}))

admin.site.register(Paste, PasteAdmin)
admin.site.register(PasteReport, PasteReportAdmin)