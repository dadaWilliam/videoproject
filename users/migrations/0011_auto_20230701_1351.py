# Generated by Django 3.2.5 on 2023-07-01 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_qrcode_used'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='feadback/'),
        ),
        migrations.AlterField(
            model_name='fileclass',
            name='file',
            field=models.FileField(upload_to='file/'),
        ),
    ]