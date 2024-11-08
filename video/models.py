import os

from django.conf import settings
from django.db import models
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericRelation

from history.models import History
from notifications.models import Notification


class VideoQuerySet(models.query.QuerySet):

    def get_count(self):
        return self.count()

    def get_published_count(self):
        return self.filter(status=0).count()

    def get_not_published_count(self):
        return self.filter(status=1).count()

    def get_vip_count(self):
        return self.filter(status=0, vip=True).count()

    def get_published_list(self):
        return self.filter(status=0).order_by('-create_time')

    def get_search_list(self, q):
        if q:
            return self.filter(title__contains=q).order_by('-create_time')
        else:
            return self.order_by('-create_time')

    def get_recommend_list(self):
        return self.filter(status=0).order_by('-view_count')[:4]

    def get_index_show(self):
        return self.filter(status=0).exclude(index_show=0).order_by('index_show')


class Classification(models.Model):
    list_display = ("title",)
    title = models.CharField(max_length=100, blank=True, null=True)
    status = models.BooleanField(default=True)
    time = models.DateTimeField(
        auto_now=True, auto_now_add=False, null=True, blank=True)
    vip = models.BooleanField(default=True, blank=False, null=False)

    def __str__(self):
        return self.title or '未知UNKNOWN'

    class Meta:
        db_table = "v_classification"


class Video(models.Model):
    STATUS_CHOICES = (
        ('0', '发布中'),
        ('1', '未发布'),
    )

    title = models.CharField(max_length=100, blank=True, null=True)
    desc = models.CharField(max_length=255, blank=True, null=True)
    classification = models.ForeignKey(
        Classification, on_delete=models.CASCADE, null=True,)
    file = models.FileField(max_length=255)
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    status = models.CharField(
        max_length=1, choices=STATUS_CHOICES, blank=True, null=True)
    view_count = models.IntegerField(default=0, blank=True)
    index_show = models.IntegerField(default=0, blank=True)

    vip = models.BooleanField(default=True, blank=False, null=False)

    liked = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                   blank=True, related_name="liked_videos")
    collected = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                       blank=True, related_name="collected_videos")
    create_time = models.DateTimeField(
        auto_now_add=True, blank=True, max_length=20)

    objects = VideoQuerySet.as_manager()

    histories = GenericRelation(History, content_type_field='content_type',
                                object_id_field='object_id', related_query_name='history')
    notifications = GenericRelation(Notification, content_type_field='target_content_type',
                                    object_id_field='target_object_id', related_query_name='notification')

    def __str__(self):
        return self.title or '未知UNKNOWN'

    class Meta:
        db_table = "v_video"

    def increase_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])

    def switch_like(self, user):
        if user in self.liked.all():
            self.liked.remove(user)
        else:
            self.liked.add(user)

    def count_likers(self):
        return self.liked.count()

    def user_liked(self, user):
        if user in self.liked.all():
            return 0
        else:
            return 1

    def switch_collect(self, user):
        if user in self.collected.all():
            self.collected.remove(user)

        else:
            self.collected.add(user)

    def count_collecters(self):
        return self.collected.count()

    def user_collected(self, user):
        if user in self.collected.all():
            return 0
        else:
            return 1


@receiver(models.signals.post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    删除FileField文件
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
