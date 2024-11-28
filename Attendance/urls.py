from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.attendance, name='attendance'),
    path("mark/", views.scan_qr_code, name="mark_attendance"),
    path("access-area/", views.scan_qr_code, name="access_area")

]

# path('students/<str:slug>/', views.view_student, name='view_student'),
# path('edit/<str:slug>/', views.edit_student, name='edit_student'),
# path('delete/<str:slug>/', views.delete_student, name='delete_student'),

