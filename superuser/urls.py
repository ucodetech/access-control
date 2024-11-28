from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("", views.superuser, name='superuser'),
    path("student_list/", views.student_list, name='student_list'),
    path("add/", views.add_student, name="add_student"),
    path('student/<str:slug>', views.view_student, name='view_student'),
    path('download-card/<int:student_id>/', views.generate_student_card, name='download_card'),
    path('edit/<str:slug>', views.edit_student, name='edit_student'),
    path('delete/<str:slug>', views.delete_student, name='delete_student'),
    path('course/', include('course.urls')),
    path("add-area/", views.add_area, name="add_area"),
    path('areas/', views.list_areas, name='list_areas'),
    path('edit-area/<int:id>/', views.edit_area, name='edit_area'),
    path('delete-area/<int:id>/', views.delete_area, name='delete_area'),
    path('map-area/', views.map_area, name='map_area'),
    path('student-areas/', views.student_areas, name='student_areas'),
    path('delete-student-area/<int:student_id>/<int:area_id>/', views.delete_student_area, name='delete_student_area'),

]
