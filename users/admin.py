from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ['pk']
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
