from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.dashboard, name='dashboard'),
    path("attendance/", include('Attendance.urls')),
    path('download-card/<int:student_id>/', views.generate_student_card, name='generate_card'),
    path('areas/', views.areas, name='areas'),
    path('success/<str:area_id>', views.success, name='success'),
]
