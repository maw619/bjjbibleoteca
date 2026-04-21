from django.contrib import admin

from .models import Category, Note, Section, Video


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category")
    list_filter = ("category",)
    search_fields = ("name", "category__name")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section")
    list_filter = ("section", "section__category")
    search_fields = ("title", "section__name", "section__category__name")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "video", "updated_at", "timestamp")
    list_filter = ("updated_at", "video__section", "video__section__category")
    search_fields = ("user__username", "video__title", "content")
