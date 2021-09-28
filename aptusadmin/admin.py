from import_export.admin import ImportExportModelAdmin

from aptusadmin.models import *
from django.contrib import admin
from django.contrib.auth.models import Permission

# Register your models here.
from aptusadmin.resources import CustomUserResource


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'codename', 'name')
    list_filter = ('content_type',)
admin.site.register(Permission, PermissionAdmin)
admin.site.register(Alert)

admin.site.register(Message)
admin.site.register(Attachment)
admin.site.register(Backup)
admin.site.register(CustomGroup)


@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_repr', 'change_message')
    list_filter = ('content_type',)


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_filter = ('content_type',)


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'tmp_pwd', )
    search_fields = ('username', 'first_name', 'last_name')
admin.site.register(CustomUser, CustomUserAdmin)

# class CustomUserAdmin(ImportExportModelAdmin):
#         resource_class = CustomUserResource
# admin.site.register(CustomUser, CustomUserAdmin)

class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'value')
    list_filter = ('name',)
admin.site.register(Choice, ChoiceAdmin)