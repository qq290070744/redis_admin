# coding:utf-8
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class RedisConf(models.Model):
    TYPE_CHOICES = (
        (0, u'单机'),
        (1, u'cluster')
    )
    name = models.CharField(max_length=255, verbose_name=u"名称")
    host = models.CharField(max_length=255, verbose_name=u"IP地址")
    port = models.IntegerField(default=6379, verbose_name=u"端口")
    username = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"用户名")
    password = models.CharField(null=True, blank=True, max_length=255, verbose_name=u"密码")
    database = models.IntegerField(default=16, verbose_name=u"db数")
    type = models.IntegerField(default=0, choices=TYPE_CHOICES, verbose_name=u"类型")

    class Meta:
        verbose_name = "redis配置"
        verbose_name_plural = verbose_name
        db_table = 'redis_config'


class Auth(models.Model):
    PREMISSION_CHOICES = (
        (0, u'超级管理员'),
        (1, u'查看'),
        (2, u'查看, 编辑'),
        (3, u'查看, 编辑, 删除'),
    )
    redis = models.IntegerField(verbose_name=u'redis配置')
    pre_auth = models.IntegerField(default=1, choices=PREMISSION_CHOICES, verbose_name=u"权限级别")

    class Meta:
        verbose_name = u"权限"
        verbose_name_plural = verbose_name
        db_table = 'premission'

    def __str__(self):
        return str(self.redis) + ' - ' + dict(Auth.PREMISSION_CHOICES)[self.pre_auth]


class DctUser(AbstractUser):
    img = models.CharField(default='/static/img/default.jpg', max_length=200, verbose_name=u'用户头像')
    auths = models.ManyToManyField(Auth, default=None, blank=True)

    class Meta:
        verbose_name = u'用户管理'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username
