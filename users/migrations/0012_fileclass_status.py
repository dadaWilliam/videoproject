# Generated by Django 3.2.5 on 2023-07-02 09:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20230701_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='fileclass',
            name='status',
            field=models.CharField(blank=True, choices=[('0', '发布中'), ('1', '未发布')], max_length=1, null=True),
        ),
    ]
