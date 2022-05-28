from django.contrib import admin
# Register your models here.
from .models import User,Token
class tokenRead(admin.ModelAdmin):
    readonly_fields = ('create_time',)
admin.site.register(User)
admin.site.register(Token, tokenRead)