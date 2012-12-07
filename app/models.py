# -*- coding:utf-8 -*-
# Create your models here.
from django.db import models




class conf(models.Model):
    u"""
    """
    key = models.CharField(u'key',max_length=200,primary_key=True)
    value = models.TextField(u'value',max_length=200)
    create_time = models.DateTimeField(auto_now_add=True)
    sk = models.CharField(u'sk',max_length=100)


