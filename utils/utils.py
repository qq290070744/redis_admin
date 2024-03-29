#!/usr/bin/env python
# coding:utf-8
__author__ = 'jiangwenhui'
__date__ = '2024/03/01'

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):

    @method_decorator(login_required(login_url='/login/'))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


def is_binary(data):
    return isinstance(data, (bytes, bytearray))
