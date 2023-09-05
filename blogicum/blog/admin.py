from django.contrib import admin

from .models import Category, Location, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'location',
        'category',
        'created_at',
        'pub_date',
        'is_published',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'author',
        'category',
        'location',
        'is_published',
    )
    search_fields = (
        'title',
    )
    list_display_links = (
        'title',
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'slug',
        'created_at',
        'is_published',
    )
    list_display_links = (
        'title',
    )
    search_fields = (
        'title',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'is_published',
    )


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'created_at',
        'is_published',
    )
    list_display_links = (
        'name',
    )
    search_fields = (
        'name',
    )
    list_editable = (
        'is_published',
    )
    list_filter = (
        'is_published',
    )


admin.site.empty_value_display = 'Не задано'
admin.site.site_title = 'Администирирование Блогикум'
admin.site.site_header = 'Администирирование Блогикум'
