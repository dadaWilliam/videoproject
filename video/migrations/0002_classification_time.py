# Generated by Django 3.2.5 on 2022-07-07 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='classification',
            name='time',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]