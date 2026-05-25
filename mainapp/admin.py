from django.contrib import admin

from .models import Category, Instructor, Note, Section, Series, Video


@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "series", "instructor", "category")
    list_filter = ("category", "series", "instructor")
    search_fields = ("name", "series__title", "instructor__name", "category__name")


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section")
    list_filter = ("section", "section__category")
    search_fields = ("title", "section__name", "section__instructor__name", "section__category__name")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "video", "updated_at", "timestamp")
    list_filter = ("updated_at", "video__section", "video__section__category")
    search_fields = ("user__username", "video__title", "content")
