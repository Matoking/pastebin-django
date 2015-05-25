from django.contrib import admin

from pastes.models import Paste, PasteReport

class PasteAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "submitted")

admin.site.register(Paste, PasteAdmin)
admin.site.register(PasteReport)