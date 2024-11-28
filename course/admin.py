from django.contrib import admin

from course.models import Course


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_name', 'short_code')  # Adjust the fields to your needs
    search_fields = ('course_name', 'short_code')
