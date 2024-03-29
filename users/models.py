import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime, timedelta
from PIL import Image as PilImage
from videoproject import settings


class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', '男'),
        ('F', '女'),
    )

    nickname = models.CharField(blank=True, null=True, max_length=20)
    avatar = models.FileField(upload_to='avatar/')
    mobile = models.CharField(blank=True, null=True, max_length=13)
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    subscribe = models.BooleanField(default=False)
    vip = models.BooleanField(default=True, blank=False, null=False)
    expire = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the model so the file is accessible

        img_path = os.path.join(settings.MEDIA_ROOT, self.avatar.name)

        # Check if the file is an image
        try:
            img = PilImage.open(img_path)
        except IOError:
            # Not an image
            return

        # If it's an RGBA image, convert it to RGB
        if img.mode == 'RGBA':
            # Create a white background
            background = PilImage.new('RGB', img.size, (255, 255, 255))
            background.paste(img, (0, 0), img)
            img = background  # Reset img to the new RGB image

        # If it's an LA image, convert it to L (grayscale without alpha)
        elif img.mode == 'LA':
            img = img.convert('L')

        # Save the image back in JPEG format (overwriting the original file)
        # You can adjust quality as needed

        img.save(img_path, 'JPEG', quality=95)

    class Meta:
        db_table = "v_user"


class Token(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)  # 一对一关系
    token = models.CharField(max_length=64)
    create_time = models.DateTimeField(auto_now=True, auto_now_add=False)

    def __str__(self):
        return self.user.username


class QRcode(models.Model):
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.CharField(max_length=64)
    code = models.CharField(max_length=64)
    verification = models.CharField(max_length=64, blank=True, null=True)
    used = models.BooleanField(default=False)
    create_time = models.DateTimeField(auto_now=True, auto_now_add=False)


class Repair(models.Model):
    ok = models.BooleanField(default=True)
    ok_time = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)


class Software(models.Model):
    version = models.IntegerField(default=1, blank=True)
    force = models.BooleanField(default=False)
    desc = models.CharField(max_length=255, blank=True, null=True)
    time = models.DateTimeField(
        auto_now=False, auto_now_add=False, null=True, blank=True)


class FeedbackQuerySet(models.query.QuerySet):

    def get_count(self):
        return self.count()


class Feedback(models.Model):
    contact = models.CharField(blank=True, null=True, max_length=20)
    content = models.CharField(blank=True, null=True, max_length=200)
    image = models.ImageField(upload_to='feedback/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    objects = FeedbackQuerySet.as_manager()

    class Meta:
        db_table = "v_feedback"

    def admin_image(self):
        return '<img src="%s"/>' % self.image

    admin_image.allow_tags = True
