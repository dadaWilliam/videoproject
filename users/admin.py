from django.contrib import admin
# Register your models here.
from .models import Feedback, QRcode, Repair, Token, Software


class tokenRead(admin.ModelAdmin):
    readonly_fields = ('create_time',)


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('contact', 'image', 'content', 'admin_image')


admin.site.register(Feedback, FeedbackAdmin)


admin.site.register(Repair)
admin.site.register(Software)
admin.site.register(Token, tokenRead)
admin.site.register(QRcode)
