#!/usr/bin/env python
# coding:utf-8
__author__ = 'jiangwenhui'
__date__ = '2024/03/01'
from django import forms
from .models import DctUser


class LoginForms(forms.Form):
	username = forms.CharField(required=True)
	password = forms.CharField(required=True)


class UserInfoForm(forms.ModelForm):
	class Meta:
		model = DctUser
		fields = ['username']
