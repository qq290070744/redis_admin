from django.contrib import admin

# Register your models here.
from .models import *


class RedisConfAdmin(admin.ModelAdmin):
    list_display = ('name', 'host', 'port', 'type')
    search_fields = ('name', 'host',)
    list_filter = ('type',)
    ordering = ('-id',)


admin.site.register(RedisConf, RedisConfAdmin)


class AuthAdmin(admin.ModelAdmin):
    list_display = ('redis', 'pre_auth',)
    search_fields = ('redis', 'pre_auth',)
    list_filter = ('pre_auth',)
    ordering = ('-redis',)


admin.site.register(Auth, AuthAdmin)


class DctUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email',
        'is_staff', 'is_active', 'date_joined',
    )
    search_fields = ('id', 'username',)
    # list_filter = ('id', 'username',)
    ordering = ('-id',)


admin.site.register(DctUser, DctUserAdmin)
