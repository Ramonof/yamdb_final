from django.contrib import admin
from .models import Category, Genre, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['pk']
    empty_value_display = '-empty-'


class GenreAdmin(admin.ModelAdmin):
    list_display = ['pk']
    empty_value_display = '-empty-'


class TitleAdmin(admin.ModelAdmin):
    list_display = ['pk']
    empty_value_display = '-empty-'


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
