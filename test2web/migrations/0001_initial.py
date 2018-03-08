# Generated by Django 2.0.1 on 2018-02-24 08:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClientStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('line_1_trains', models.IntegerField(default=0)),
                ('line_2_trains', models.IntegerField(default=0)),
                ('line_1_carriages', models.IntegerField(default=0)),
                ('line_2_carriages', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ClientWarning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DailyReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, default=None)),
                ('warn', models.TextField(default='无')),
                ('carriages_count', models.IntegerField(default=0)),
                ('imgs', models.BinaryField(blank=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='DailyReport_Meta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('problem', models.TextField(default='无')),
                ('track', models.TextField(default='无')),
            ],
        ),
        migrations.CreateModel(
            name='Info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField()),
                ('site', models.CharField(max_length=255)),
                ('sx_h_lie', models.IntegerField(default=0)),
                ('sx_h_liang', models.IntegerField(default=0)),
                ('sx_k_lie', models.IntegerField(default=0)),
                ('sx_k_liang', models.IntegerField(default=0)),
                ('xx_h_lie', models.IntegerField(default=0)),
                ('xx_h_liang', models.IntegerField(default=0)),
                ('xx_k_lie', models.IntegerField(default=0)),
                ('xx_k_liang', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Reason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('order', models.IntegerField()),
                ('code', models.CharField(blank=True, max_length=255)),
                ('bureau', models.CharField(blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Warn',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pid', models.IntegerField(default=0)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Warning',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('side', models.CharField(max_length=255)),
                ('line', models.CharField(max_length=100)),
                ('warn_type', models.CharField(max_length=255)),
                ('pic', models.FileField(blank=True, upload_to='upload/')),
                ('reason', models.ManyToManyField(blank=True, to='test2web.Reason')),
                ('site', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='test2web.Site')),
                ('warn', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2web.Warn')),
            ],
        ),
        migrations.AddField(
            model_name='dailyreport_meta',
            name='site',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='test2web.Site'),
        ),
        migrations.AddField(
            model_name='dailyreport',
            name='reason',
            field=models.ManyToManyField(related_name='Reason_dailyreport', to='test2web.Reason'),
        ),
        migrations.AddField(
            model_name='dailyreport',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2web.Site'),
        ),
        migrations.AddField(
            model_name='clientwarning',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2web.Site'),
        ),
        migrations.AddField(
            model_name='clientwarning',
            name='warn',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2web.Warn'),
        ),
        migrations.AddField(
            model_name='clientstatus',
            name='site',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='test2web.Site'),
        ),
    ]