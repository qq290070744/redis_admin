#!/usr/bin/env python
# coding:utf-8
__author__ = 'jiangwenhui'
__date__ = '2024/03/01'

import os

DEBUG = True

LOG_LEVEL = 'INFO'

# redis
base = {
    'seperator': ':',
    'maxkeylen': 100
}
socket_timeout = 2
scan_batch = 10000  # scan 限制获取数据量
search_scan_batch = 100000  # 搜索 scan 限制获取数据量
show_key_self_count = False

mail_host = 'smtp.exmail.qq.com'
mail_user = 'test@test.com'
mail_pass = ''
mail_receivers = ["test@test.com", "test2@test.com"]
admin_mail = ["test@test.com"]  # 管理员邮箱
PYTHONENV = os.getenv('PYTHONENV')
db_name = os.getenv("db_name")
db_user = os.getenv("db_user")
db_pwd = os.getenv("db_pwd")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
if db_name:
    database = {
        "name": db_name,
        "host": db_host,
        "username": db_user,
        "password": db_pwd,
        "port": db_port,
    }
else:
    database = {
        "name": "redis_admin",
        "host": "10.237.44.179",
        "username": "sql_audit",
        "password": "Sql_@#Audit2ws",
        "port": "3306",
    }
