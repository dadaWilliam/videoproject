from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta
class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )

    nickname = models.CharField(blank=True, null=True, max_length=20)
    avatar = models.FileField(upload_to='avatar/')
    mobile = models.CharField(blank=True, null=True, max_length=13)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES,blank=True, null=True)
    subscribe = models.BooleanField(default=False)
    expire = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)


    class Meta:
        db_table = "v_user"

class Token(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)  # 一对一关系
    token = models.CharField(max_length=64)
    create_time = models.DateTimeField(auto_now=True, auto_now_add=False)

class Repair(models.Model):
    ok = models.BooleanField(default=True)
    ok_time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

class Software(models.Model):
    version = models.IntegerField(default=1, blank=True)
    force = models.BooleanField(default=False)
    desc = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

class Feedback(models.Model):
    contact = models.CharField(blank=True, null=True, max_length=20)
    content = models.CharField(blank=True, null=True, max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "v_feedback"
