# Register your models here.
from django.contrib import admin
from .models import Student, AccessControl, Area, StudentArea


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'gender', 'date_of_birth', 'course', 'level', 'mobile_number')
    search_fields = ('first_name', 'last_name', 'unique_id', 'course', 'level')
    list_filter = ('gender', 'course', 'level')
    readonly_fields = ('image',)  # Optional: makes the image field read-only

@admin.register(AccessControl)
class AccessControlAdmin(admin.ModelAdmin):
    list_display = ('student', 'unique_id')  # Adjust the fields to your needs
    search_fields = ('student__first_name', 'student__last_name', 'unique_id')
    readonly_fields = ('unique_id','qr_code',)



@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Adjust the fields to your needs
    search_fields = ('name',)

@admin.register(StudentArea)
class StudentAreaAdmin(admin.ModelAdmin):
    list_display = ('student', 'area',)  # Adjust the fields to your needs
    search_fields = ('student__first_name', 'student__last_name', 'area__name')