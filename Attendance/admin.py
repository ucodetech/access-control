from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'time', 'status')
    list_filter = ('date', 'time', 'status')
    search_fields = ('student__first_name', 'student__last_name')
