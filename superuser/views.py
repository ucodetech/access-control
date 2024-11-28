import datetime
import os
import random
import string
from contextlib import contextmanager
from io import BytesIO
from os.path import exists

import cv2
import qrcode
import winsound
from PIL import Image, ImageDraw, ImageFont, ImageOps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.core.mail import send_mail
from django.http import HttpResponseForbidden, HttpResponse, request
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse

from Attendance.models import Attendance
from Attendance.views import attendance
from course.models import Course
from home_auth.models import CustomUser
from .models import *
from django.contrib import messages
# Create your views here.

@login_required
def superuser(request):
    unread_notification = request.user.notification_set.filter(is_read=False)
    count_student = Student.objects.all().count()
    count_course = Course.objects.all().count()
    count_areas = Area.objects.all().count()
    attendance_today = Attendance.objects.filter(date=datetime.today()).count()
    context = {
        'count_student': count_student,
        'count_course': count_course,
        'count_areas' : count_areas,
        'count_attendance': attendance_today
    }
    return render(request, "superuser/superuser.html", context)

def add_student(request):
    courses = Course.objects.all()
    levels = ["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"]

    context = {
        'courses': courses,
        'levels': levels
    }
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        level = request.POST.get('level')
        course = request.POST.get('course')
        mobile_number = request.POST.get('mobile_number')
        # department = request.POST.get('department')
        image = request.FILES.get('image')

        if Student.objects.filter(email=email).exists():
            messages.warning(request, f"A student with this {email} already exist!")
            return redirect(reverse('add_student'))

        if Student.objects.filter(mobile_number=mobile_number).exists():
            messages.warning(request, f"A student with this {mobile_number} already exist!")
            return redirect(reverse('add_student'))

        unique_id = generate_unique_id(request)
        user_details = {
            'unique_id':unique_id,
            'email':email,
            'first_name':first_name,
            'last_name':last_name,
            'course':course
        }
        qr_code = generate_qrcode(user_details)


        # save unique  information
        access_control = AccessControl.objects.create(
            qr_code= File(qr_code, name=f"{unique_id}_qr.png"),
            unique_id= unique_id
        )

        # Save student information
        student = Student.objects.create(
            first_name= first_name,
            last_name= last_name,
            email= email,
            gender= gender,
            date_of_birth= date_of_birth,
            course= course,
            mobile_number = mobile_number,
            level = level,
            # department = department,
            image = image,
            access_control = access_control
        )
        # Generate a default password
        default_password = generate_password()
        # Create the user
        customUser = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        customUser.set_password(default_password)
        customUser.is_student = True
        customUser.save()

        # Send registration email
        subject = "Welcome to the Student Portal"
        message = f"""
                  Dear {student.first_name},

                  Your registration has been successful! Below are your login details:

                  Username: {student.email}
                  Password: {default_password}

                  Please log in to your account and update your password immediately.

                  Best regards,
                  Admin Team
                  """
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [student.email]

        send_mail(subject, message, from_email, recipient_list)

        # create_notification(request.user, f"Added Student: {student.first_name} {student.last_name}")
        messages.success(request, "Student added Successfully")
        # return render(request, "student_list")
    return render(request,"superuser/add-student.html", context)

@login_required
def student_list(request):
    student_list = Student.objects.select_related('access_control').all()
    unread_notification = request.user.notification_set.filter(is_read=False)
    context = {
        'student_list': student_list,
        'unread_notification': unread_notification
    }
    return render(request, "superuser/students.html", context)

@login_required
def edit_student(request,slug):
    student = get_object_or_404(Student, slug=slug)
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('date_of_birth')
        level = request.POST.get('level')
        course = request.POST.get('course')
        mobile_number = request.POST.get('mobile_number')
        # department = request.POST.get('department')
        image = request.FILES.get('image')  if request.FILES.get('image') else student.image

#  update student information

        student.first_name= first_name
        student.last_name= last_name
        student.gender= gender
        student.date_of_birth= date_of_birth
        student.course= course
        student.mobile_number = mobile_number
        student.level = level
        # student.department = department
        student.image = image
        student.save()
        # create_notification(request.user, f"Updated Student: {student.first_name} {student.last_name}")

        return redirect("student_list")
    return render(request, "superuser/edit-student.html",{'student':student} )

@login_required
def view_student(request, slug):
    student = get_object_or_404(Student, slug = slug)
    context = {
        'student': student
    }
    return render(request, "superuser/student-details.html", context)

@login_required
def delete_student(request,slug):
    if request.method == "POST":
        student = get_object_or_404(Student, slug=slug)
        student_name = f"{student.first_name} {student.last_name}"
        access_control = student.access_control
        student.delete()
        access_control.delete()
        # create_notification(request.user, f"Deleted student: {student_name}")
        return redirect ('student_list')
    return HttpResponseForbidden()


def generate_qrcode(user_details):
    """
        Generate a QR code containing user details.

        Args:
        user_details (dict): Dictionary with user details.
        file_name (str): Output file name for the QR code image.
        """
    # Convert user details to a string
    data = f"ID: {user_details['unique_id']}\nEmail: {user_details['email']}\nFirstName: {user_details['first_name']}\nLastName: {user_details['last_name']}\nCourse: {user_details['course']}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    filename = user_details['email']+".png"
    img = qr.make_image(fill='black', back_color='white')
    qr_code_img = BytesIO()

    img.save(qr_code_img, format='PNG')
    qr_code_img.seek(0)
    print(f"QR Code saved")

    return qr_code_img

def generate_unique_id(request):
    characters = ''.join(random.choices(string.ascii_letters + string.digits, k=11))
    return characters.upper()


def generate_student_card(request, student_id):
    # Get the student object
    student = get_object_or_404(Student, id=student_id)

    # Load the QR code image
    try:
        qr_img_path = student.access_control.qr_code.path  # Use the file path of the QR code
        qr_img = Image.open(qr_img_path)
    except Exception as e:
        return HttpResponse(f"Error loading QR code: {e}", status=400)

    # Create the card canvas
    card_width = 400
    card_height = 400
    card = Image.new("RGB", (card_width, card_height), "white")

    # Initialize a drawing context
    draw = ImageDraw.Draw(card)

    # Load font
    try:
        font_path = "arial.ttf"  # Adjust this path as needed
        font = ImageFont.truetype(font_path, 30)
    except Exception:
        font = ImageFont.load_default()

    # Full name of the student
    name = f"{student.first_name} {student.last_name}"

    # Add centered text: Name
    name_text = name
    name_bbox = draw.textbbox((0, 0), name_text, font=font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (card_width - name_width) // 2
    name_y = 20
    draw.text((name_x, name_y), name_text, fill="black", font=font)

    # Add centered text: Student ID
    id_text = f"{student.access_control.unique_id}"
    id_bbox = draw.textbbox((0, 0), id_text, font=font)
    id_width = id_bbox[2] - id_bbox[0]
    id_x = (card_width - id_width) // 2
    id_y = name_y + (name_bbox[3] - name_bbox[1]) + 10
    draw.text((id_x, id_y), id_text, fill="black", font=font)

    # Add the student's photo if it exists, after the unique ID
    if student.image and os.path.exists(student.image.path):
        try:
            # Open and resize the photo
            photo = Image.open(student.image.path)
            photo = photo.resize((80, 80))  # Resize photo to fit the card

            # Create a circular mask
            mask = Image.new("L", photo.size, 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, photo.size[0], photo.size[1]), fill=255)

            # Apply the mask to make the photo rounded
            rounded_photo = ImageOps.fit(photo, mask.size, centering=(0.5, 0.5))
            rounded_photo.putalpha(mask)

            # Calculate position for the photo
            photo_x = (card_width - 80) // 2
            photo_y = id_y + (id_bbox[3] - id_bbox[1]) + 20
            card.paste(rounded_photo, (photo_x, photo_y), mask=rounded_photo.split()[-1])
        except Exception as e:
            error_text = "Photo not available"
            error_bbox = draw.textbbox((0, 0), error_text, font=font)
            error_width = error_bbox[2] - error_bbox[0]
            error_x = (card_width - error_width) // 2
            error_y = id_y + (id_bbox[3] - id_bbox[1]) + 20
            draw.text((error_x, error_y), error_text, fill="gray", font=font)

    # Resize and paste the QR code below the profile photo
    qr_size = 200
    qr_img = qr_img.resize((qr_size, qr_size))
    qr_x = (card_width - qr_size) // 2
    qr_y = photo_y + 100  # Add spacing after the photo
    card.paste(qr_img, (qr_x, qr_y))

    # Save the card to a BytesIO buffer
    buffer = BytesIO()
    card.save(buffer, format="PNG")
    buffer.seek(0)

    # Return the card as a downloadable file
    response = HttpResponse(buffer, content_type="image/png")
    response["Content-Disposition"] = f"attachment; filename={student.access_control.unique_id}_card.png"
    return response


def generate_password(length=10):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

@login_required()
def add_area(request):
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')

        area = Area.objects.create(
                name = name,
                image = image
          )

        messages.success(request, "Area added Successfully")
    return render(request,"superuser/areas/add-area.html")

def list_areas(request):
    areas = Area.objects.all()
    context = {
        'areas': areas,
    }
    return render(request,"superuser/areas/areas.html", context)


def edit_area(request, id):
    area = get_object_or_404(Area, id=id)
    context = {
        'area': area
    }
    if request.method == "POST":
        name = request.POST.get('name')
        image = request.FILES.get('image')  if request.FILES.get('image') else area.image

        area.name=name,
        area.image=image
        area.save()

        messages.success(request, "Area Updated Successfully")
        return redirect("list_areas")

    return render(request, "superuser/areas/edit-area.html", context)


def delete_area():
    return None


def map_area(request):
    areas = Area.objects.all()
    students = Student.objects.all()

    context = {
        'areas': areas,
        'students' : students
    }
    if request.method == "POST":
        area_id = request.POST.get('area_id')
        student_id = request.POST.get('student_id')

        area = Area.objects.filter(id=area_id).first()
        student = Student.objects.filter(id=student_id).first()

        if area is None or student is None:
            messages.warning(request, f"Area not found and Student can not be found")
            return redirect(reverse('map_area'))

        exist = StudentArea.objects.filter(student=student, area=area).first()
        if exist is not None:
            messages.warning(request, f"You have already mapped this area ({area.name}) to the student!")
            return redirect(reverse('map_area'))


        StudentArea.objects.create(
            area = area,
            student = student
        )

        messages.success(request, f"Area successfully mapped to student")
        return redirect(reverse('map_area'))
    return  render(request, "superuser/areas/map-student.html", context)


def student_areas(request):
    mappings = StudentArea.objects.select_related('student', 'area').all()

    # Group areas by student
    student_area_mapping = {}
    for mapping in mappings:
        if mapping.student not in student_area_mapping:
            student_area_mapping[mapping.student] = []
        student_area_mapping[mapping.student].append(mapping.area)

    # Convert to a list of dictionaries for the template
    context = {
        'student_area_mapping': [
            {
                'student': student,
                'areas': areas
            }
            for student, areas in student_area_mapping.items()
        ]
    }

    return render(request, 'superuser/areas/student-areas.html', context)


def delete_student_area(request, student_id, area_id):
    try:
        # Get the specific StudentArea object
        student_area = get_object_or_404(StudentArea, student_id=student_id, area_id=area_id)

        # Delete the object
        student_area.delete()

        # Success message
        messages.success(request,f"Mapping for {student_area.student.name} and {student_area.area.name} has been deleted successfully.")
    except Exception as e:
        # Handle any unexpected errors
        messages.error(request, f"An error occurred: {str(e)}")

    return redirect(reverse('student_areas'))
