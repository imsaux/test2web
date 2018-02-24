#coding=utf-8
from django.db import models
from django.contrib.auth.admin import User
# from django.contrib import admin


class Reason(models.Model):  # 问题原因分类
    pid = models.IntegerField(default=0)
    name = models.CharField(max_length=255)

class Site(models.Model):   # 站点
    name = models.CharField(max_length=255)
    order = models.IntegerField(blank=False)
    code = models.CharField(max_length=255, blank=True)
    bureau = models.CharField(max_length=255, blank=True)


class Warn(models.Model):  # 报警分类
    pid = models.IntegerField(default=0)
    name = models.CharField(max_length=255)

class Warning(models.Model):  # 
    date = models.DateField()
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    side = models.CharField(max_length=255)
    line = models.CharField(max_length=100)
    warn_type = models.CharField(max_length=255)
    warn = models.ForeignKey(Warn, on_delete=models.CASCADE)
    reason = models.ManyToManyField(Reason, blank=True)
    pic = models.FileField(upload_to='upload/', blank=True)

class Info(models.Model):
    datetime = models.DateTimeField()
    site = models.CharField(max_length=255)
    sx_h_lie = models.IntegerField(default=0)
    sx_h_liang = models.IntegerField(default=0)
    sx_k_lie = models.IntegerField(default=0)
    sx_k_liang = models.IntegerField(default=0)
    xx_h_lie = models.IntegerField(default=0)
    xx_h_liang = models.IntegerField(default=0)
    xx_k_lie = models.IntegerField(default=0)
    xx_k_liang = models.IntegerField(default=0)

class ClientWarning(models.Model):
    datetime = models.DateTimeField()   # 日期
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    warn = models.ForeignKey(Warn, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)    # 数量

class ClientStatus(models.Model):
    datetime = models.DateTimeField()   # 日期
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    line_1_trains = models.IntegerField(default=0)
    line_2_trains = models.IntegerField(default=0)
    line_1_carriages = models.IntegerField(default=0)
    line_2_carriages = models.IntegerField(default=0)

class DailyReport(models.Model):
    date = models.DateField(default=None, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    reason = models.ManyToManyField(Reason, related_name='Reason_dailyreport')
    warn = models.TextField(default='无')
    carriages_count = models.IntegerField(default=0)
    imgs = models.BinaryField(blank=True)
    status = models.BooleanField(default=False)   # 审批状态

class DailyReport_Meta(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
    problem = models.TextField(default='无')
    track = models.TextField(default='无')