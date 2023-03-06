from django.contrib import admin

from unite_compress.courses.models import Course


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    pass
