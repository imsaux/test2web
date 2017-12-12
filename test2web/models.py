from django.db import models

class Dict(models.Model):
    id = models.AutoField(primary_key=True)
    pid = models.IntegerField()
    name = models.CharField(max_length=100)

class Warning(models.Model):
    pic = models.BinaryField()
    pub_date = models.DateField()
    id = models.AutoField(primary_key=True)
    reason = models.ManyToManyField(Dict)
