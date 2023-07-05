from django.contrib import admin
from .models import *


class ClassificationTimeRead(admin.ModelAdmin):
    readonly_fields = ('time',)


admin.site.register(Classification, ClassificationTimeRead)
admin.site.register(Video)
