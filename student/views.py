import datetime
import os
import string
from io import BytesIO
import cv2
import qrcode
import winsound
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ImagePalette import random
from django.contrib.auth.decorators import login_required
from django.core.files import File
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, get_object_or_404,redirect
from django.urls import reverse

from home_auth.models import CustomUser
from superuser.models import Student, StudentArea, Area
from .models import *
from django.contrib import messages
from Attendance.views import cipher

@login_required
def dashboard(request):
    # Fetch the logged-in user
    current_user = request.user

    # Get the corresponding student details if applicable
    student = Student.objects.filter(email=current_user.email).first()
    currentDate = datetime.datetime.now()
    context = {
        'user': current_user,
        'student': student,
        'current_date': currentDate
    }
    return render(request, "students/student-dashboard.html", context)



@login_required
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


def areas(request):
    student = Student.objects.filter(email=request.user.email).first();
    if student is None:
        messages.warning(request, "Student not found")
        return redirect(reverse('dashboard'))

    student_areas = StudentArea.objects.filter(student=student).all()
    areas = Area.objects.all()

    context = {
        'student_areas': student_areas,
        'areas' : areas
    }
    return render(request, "students/areas.html", context)


def success(request, area_id):
    student = Student.objects.filter(email=request.user.email).first()
    if not area_id:
        return HttpResponse("Area ID is required", status=400)  # Handle missing area_id gracefully

    decrypted_area_id = decrypt_id(area_id);
    area = Area.objects.filter(id=decrypted_area_id).first()

    context = {
        'student': student,
        'area': area
    }
    return render(request, "students/success.html", context)



def decrypt_id(encrypted_id):
    """Decrypt an ID."""
    try:
        return int(cipher.decrypt(encrypted_id.encode()).decode())
    except Exception as e:
        return None