# Generated by Django 3.2.5 on 2023-07-03 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileclass',
            name='view_count',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
