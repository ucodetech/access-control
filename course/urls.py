from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_courses, name='list_courses'),
    path('create/', views.create_course, name='create_course'),
    path('delete/<int:course_id>', views.delete_course, name='delete_course'),
    path('edit/<int:course_id>', views.edit_course, name='edit_course'),
]

