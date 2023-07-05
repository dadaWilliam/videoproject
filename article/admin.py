from django.contrib import admin
from article.models import Article, FileClass

# class tokenRead(admin.ModelAdmin):
#     readonly_fields = ('create_time',)

admin.site.register(FileClass)
admin.site.register(Article)
