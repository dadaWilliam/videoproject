import os

from django.dispatch import receiver
from ckeditor.fields import RichTextField
# django-ckeditor
from django.db import models


class FileClassQuerySet(models.query.QuerySet):

    def get_count(self):
        return self.count()

    def get_published_count(self):
        return self.filter(status=0).count()

    def get_not_published_count(self):
        return self.filter(status=1).count()

    def get_vip_count(self):
        return self.filter(status=0, vip=True).count()


class FileClass(models.Model):
    file = models.FileField(upload_to='file/')
    desc = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(
        auto_now=True, auto_now_add=False, null=True, blank=True)
    vip = models.BooleanField(default=True, blank=False, null=False)
    view_count = models.IntegerField(default=0, blank=True)
    code = models.CharField(max_length=64, null=True, blank=True)
    objects = FileClassQuerySet.as_manager()
    STATUS_CHOICES = (

        ('0', '发布中'),
        ('1', '未发布'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, blank=True, null=True)

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ArticleQuerySet(models.query.QuerySet):

    def get_count(self):
        return self.count()

    def get_published_count(self):
        return self.filter(status=0).count()

    def get_not_published_count(self):
        return self.filter(status=1).count()

    def get_vip_count(self):
        return self.filter(status=0, vip=True).count()

    def get_recommend_list(self):
        return self.filter(status=0).order_by('-view_count')[:4]


class Article(models.Model):
    # file = models.FileField(upload_to='file/')
    title = models.CharField(max_length=100, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    body = RichTextField()
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    view_count = models.IntegerField(default=0, blank=True)
    time = models.DateTimeField(
        auto_now=True, auto_now_add=False, null=True, blank=True)
    vip = models.BooleanField(default=True, blank=False, null=False)
    STATUS_CHOICES = (
        ('0', '发布中'),
        ('1', '未发布'),
    )
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, blank=True, null=True)
    objects = ArticleQuerySet.as_manager()

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


@receiver(models.signals.post_delete, sender=FileClass)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    删除FileField文件
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
