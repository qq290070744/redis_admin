from django.contrib import admin

# Register your models here.
from .models import *


class OperationInfoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'server', 'db',
        'key', 'old_value', 'value',
        'type', 'add_time'
    )
    search_fields = ('id', 'username', 'server', 'type')
    list_filter = ('username', 'server', 'type')
    ordering = ('-id',)


admin.site.register(OperationInfo, OperationInfoAdmin)
