# Generated by Django 3.2.5 on 2023-06-29 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_fileclass'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='vip',
            field=models.BooleanField(default=True),
        ),
    ]
