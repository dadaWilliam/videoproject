# Generated by Django 3.2.5 on 2023-07-03 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('article', '0002_fileclass_view_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileclass',
            name='code',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]