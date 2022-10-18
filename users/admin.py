from django.contrib import admin
# Register your models here.
from .models import Repair,Token,Software
class tokenRead(admin.ModelAdmin):
    readonly_fields = ('create_time',)
admin.site.register(Repair)
admin.site.register(Software)
admin.site.register(Token, tokenRead)