# Generated by Django 2.0 on 2017-12-15 01:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2web', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='warning',
            name='pic',
            field=models.FileField(upload_to='./upload/'),
        ),
    ]
