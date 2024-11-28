from contextlib import contextmanager

from django.core.exceptions import ValidationError
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from course.models import Course
from django.contrib import messages



# Create your views here.
def list_courses(request):
    courses = Course.objects.all().order_by('course_name', '-id').values()
    context = {
        'course_list':courses
    }

    return render(request, "superuser/course/courses.html", context)


def create_course(request):

    if request.method == "POST":
        course_name = request.POST.get('course_name')
        short_code = request.POST.get('short_code')

        if Course.objects.filter(course_name=course_name.title()).exists():
            messages.warning(request, "Course already exists")
            return render(request, 'superuser/course/create-course.html')
        else:
            course = Course.objects.create(
                course_name = course_name.title(),
                short_code = short_code.upper()
            )

            messages.success(request, "Course added successfully")

    return render(request, "superuser/course/create-course.html")




def delete_course(request, course_id):
    if request.method == "POST":
        course = get_object_or_404(Course, id=course_id)
        course_name = f"{course.course_name} ({course.short_code})"
        course.delete()
        # create_notification(request.user, f"Deleted course: {course_name}")
        messages.info(request, f"{course_name} deleted successfully")
        return redirect('list_courses')
    return HttpResponseForbidden()


def edit_course(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == "POST":
        course_name = request.POST.get('course_name')
        short_code = request.POST.get('short_code')

        if Course.objects.filter(course_name=course_name.title()).exclude(id=course_id).exists():
            messages.warning(request, "Course already exists")
            return render(request, 'superuser/course/create-course.html')
        else:
            course.course_name = course_name.title()
            course.short_code = short_code.upper()
            course.save()

            messages.success(request, "Course updated successfully")
            return redirect('list_courses')

    return render(request, "superuser/course/edit-course.html", {'course':course})
