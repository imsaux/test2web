#coding=utf-8
from django.db import models
from django.contrib.auth.admin import User
# from django.contrib import admin


class user_profile(models.Model):
    user = models.OneToOneField(User, unique=True, verbose_name=('用户'), on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=255)

class Dict(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=100)

class Reason(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=255)

class Algo(models.Model):
    pid = models.IntegerField()
    name = models.CharField(max_length=255)

class Site(models.Model):
    name = models.CharField(max_length=255)

class Kind(models.Model):
    name = models.CharField(max_length=255)

class Warning(models.Model):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    side = models.CharField(max_length=255)
    line = models.CharField(max_length=100)
    kind = models.ForeignKey(Kind, on_delete=models.CASCADE)
    warning_type = models.CharField(max_length=255)
    algo = models.ManyToManyField(Algo)
    reason = models.ManyToManyField(Reason, blank=True)
    pic = models.FileField(upload_to='upload/', blank=True)

class Info(models.Model):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    sx_h_lie = models.IntegerField()
    sx_h_liang = models.IntegerField()
    sx_k_lie = models.IntegerField()
    sx_k_liang = models.IntegerField()
    xx_h_lie = models.IntegerField()
    xx_h_liang = models.IntegerField()
    xx_k_lie = models.IntegerField()
    xx_k_liang = models.IntegerField()
