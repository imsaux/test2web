# Generated by Django 2.0 on 2017-12-15 08:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test2web', '0003_auto_20171215_0153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Algo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField()),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='warning',
            name='algo',
            field=models.ManyToManyField(to='test2web.Algo'),
        ),
    ]
