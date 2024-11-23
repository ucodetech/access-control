# import datetime
# import string
# from io import BytesIO
# import cv2
# import qrcode
# import winsound
# from PIL.ImagePalette import random
# from django.core.files import File
# from django.http import HttpResponseForbidden
# from django.shortcuts import render, get_object_or_404,redirect
# from .models import *
# from django.contrib import messages
# # Create your views here.
#
#
#
# def add_student(request):
#     if request.method == "POST":
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         gender = request.POST.get('gender')
#         date_of_birth = request.POST.get('date_of_birth')
#         level = request.POST.get('level')
#         course = request.POST.get('course')
#         mobile_number = request.POST.get('mobile_number')
#         department = request.POST.get('department')
#         image = request.FILES.get('image')
#
#         # Retrieve special data
#
#         unique_id = generate_unique_id()
#         user_details = {
#             'unique_id':unique_id,
#             'first_name':first_name,
#             'last_name':last_name,
#             'course':course,
#             'email':email,
#             'department':department
#         }
#         qr_code = generate_qrcode(user_details)
#
#
#         # save unique  information
#         access_control = AccessControl.objects.create(
#             qr_code= File(qr_code, name=f"{unique_id}_qr.png"),
#             unique_id= unique_id
#         )
#
#         # Save student information
#         student = Student.objects.create(
#             first_name= first_name,
#             last_name= last_name,
#             email= email,
#             gender= gender,
#             date_of_birth= date_of_birth,
#             course= course,
#             mobile_number = mobile_number,
#             level = level,
#             department = department,
#             image = image,
#             access_control = access_control
#         )
#         # create_notification(request.user, f"Added Student: {student.first_name} {student.last_name}")
#         messages.success(request, "Student added Successfully")
#         # return render(request, "student_list")
#
#
#     return render(request,"students/add-student.html")
#
#
# def student_list(request):
#     student_list = Student.objects.select_related('parent').all()
#     unread_notification = request.user.notification_set.filter(is_read=False)
#     context = {
#         'student_list': student_list,
#         'unread_notification': unread_notification
#     }
#     return render(request, "students/students.html", context)
#
#
# def edit_student(request,slug):
#     student = get_object_or_404(Student, slug=slug)
#     parent = student.parent if hasattr(student, 'parent') else None
#     if request.method == "POST":
#         first_name = request.POST.get('first_name')
#         last_name = request.POST.get('last_name')
#         email = request.POST.get('email')
#         gender = request.POST.get('gender')
#         date_of_birth = request.POST.get('date_of_birth')
#         level = request.POST.get('student_level')
#         course = request.POST.get('course')
#         mobile_number = request.POST.get('mobile_number')
#         department = request.POST.get('department')
#         image = request.FILES.get('image')  if request.FILES.get('image') else student.student_image
#
# #  update student information
#
#         student.first_name= first_name
#         student.last_name= last_name
#         student.email= email
#         student.gender= gender
#         student.date_of_birth= date_of_birth
#         student.course= course
#         student.mobile_number = mobile_number
#         student.level = level
#         student.department = department
#         student.image = image
#         student.save()
#         # create_notification(request.user, f"Updated Student: {student.first_name} {student.last_name}")
#
#         return redirect("student_list")
#     return render(request, "students/edit-student.html",{'student':student} )
#
#
# def view_student(request, slug):
#     student = get_object_or_404(Student, student_id = slug)
#     context = {
#         'student': student
#     }
#     return render(request, "students/student-details.html", context)
#
#
# def delete_student(request,slug):
#     if request.method == "POST":
#         student = get_object_or_404(Student, slug=slug)
#         student_name = f"{student.first_name} {student.last_name}"
#         student.delete()
#         # create_notification(request.user, f"Deleted student: {student_name}")
#         return redirect ('student_list')
#     return HttpResponseForbidden()
#
#
# def generate_qrcode(user_details):
#     """
#         Generate a QR code containing user details.
#
#         Args:
#         user_details (dict): Dictionary with user details.
#         file_name (str): Output file name for the QR code image.
#         """
#     # Convert user details to a string
#     data = f"ID: {user_details['unique_id']}\nFirstName: {user_details['first_name']}\nLastName: {user_details['first_name']}\nCourse: {user_details['course']}\nEmail: {user_details['email']}\nDepartment: {user_details['department']}"
#     qr = qrcode.QRCode(version=1, box_size=10, border=5)
#     qr.add_data(data)
#     qr.make(fit=True)
#     filename = user_details['email']+".png"
#     img = qr.make_image(fill='yellow', back_color='black')
#     qr_code_img = BytesIO()
#
#     img.save(qr_code_img, format='PNG')
#     qr_code_img.seek(0)
#     print(f"QR Code saved")
#
#     return qr_code_img
#
#
# def generate_unique_id():
#     characters = string.ascii_uppercase + string.digits
#     return random.choices(characters, k=11)
#
# valid_ids = ['12345', '235689']
# def scan_qr_code():
#     """
#     Scan a QR code, display user details, and log attendance.
#     """
#     cap = cv2.VideoCapture(0)  # Open webcam
#     detector = cv2.QRCodeDetector()
#     line_position = 0
#     direction = 1  # Moving direction of the line: 1 (right), -1 (left)
#
#     print("Scanning QR code. Show QR code to the camera.")
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to access the camera. Exiting...")
#             break
#
#         height, width, _ = frame.shape
#
#         # Draw a moving line
#         line_position += direction * 10
#         if line_position >= width or line_position <= 0:
#             direction *= -1  # Reverse direction if the line hits the edge
#
#         # Detect and decode QR code
#         data, bbox, _ = detector.detectAndDecode(frame)
#
#         if bbox is not None:
#             # Draw a box around the detected QR code
#             for i in range(len(bbox)):
#                 pt1 = tuple(bbox[i][0].astype(int))
#                 pt2 = tuple(bbox[(i + 1) % len(bbox)][0].astype(int))
#                 cv2.line(frame, pt1, pt2, (255, 0, 0), 2)
#
#             if data:
#                 user_id = data.split("\n")[0].split(": ")[1]  # Extract user ID
#                 if user_id in valid_ids:
#                     print("Valid QR Code Detected!")
#                     print("User Details:")
#                     print(data)
#
#                     # Log attendance
#                     attendance_log = {
#                         "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                         "user_id": user_id
#                     }
#                     print("Attendance logged:", attendance_log)
#
#                     # Change line to green
#                     cv2.line(frame, (line_position, 0), (line_position, height), (0, 255, 0), 2)
#                     break
#                 else:
#                     print("Invalid QR Code!")
#                     # Trigger alarm and change line to red
#                     winsound.Beep(1000, 500)  # 1000 Hz for 500 ms
#                     cv2.line(frame, (line_position, 0), (line_position, height), (0, 0, 255), 2)
#
#         else:
#             # Default moving line
#             cv2.line(frame, (line_position, 0), (line_position, height), (255, 255, 255), 2)
#
#         # Display the camera feed
#         cv2.imshow("QR Code Scanner", frame)
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             print("Exiting scanner.")
#             break
#
#     cap.release()
#     cv2.destroyAllWindows()
