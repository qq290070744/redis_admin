#!/usr/bin/env python
# coding:utf-8
__author__ = 'jiangwenhui'
__date__ = '2024/03/01'

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'redis_admin.settings'
import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()