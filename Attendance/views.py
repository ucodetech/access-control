import cv2
import winsound
from cryptography.fernet import Fernet
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models.fields import return_None
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.context_processors import request
from django.urls import reverse
from django.utils.timezone import now

from Attendance.models import Attendance
from superuser.models import Student, AccessControl, StudentArea, Area


# Create your views here.
@login_required
def attendance(request):
    unread_notification = request.user.notification_set.filter(is_read=False)
    attendance_records = Attendance.objects.select_related('student').all()
    context = {
        'unread_notification': unread_notification,
        'attendance_records': attendance_records,
    }
    return render(request, "superuser/attendance/attendance.html", context)


def scan_qr_code(request):
    if request.method == 'POST':
        IsAttendance = request.POST.get('IsAttendance') == 'True'
        IsArea = request.POST.get('IsArea') == 'True'
        CurrentArea = request.POST.get('area')

        cap = cv2.VideoCapture(0)  # Open webcam
        detector = cv2.QRCodeDetector()
        line_position = 0
        direction = 1  # Moving direction of the line: 1 (right), -1 (left)

        print("Scanning QR code. Show QR code to the camera.")
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Failed to access the camera. Exiting...")
                    break

                height, width, _ = frame.shape

                # Draw a moving line
                line_position += direction * 10
                if line_position >= width or line_position <= 0:
                    direction *= -1  # Reverse direction if the line hits the edge

                # Detect and decode QR code
                data, bbox, _ = detector.detectAndDecode(frame)

                if bbox is not None:
                    # Draw a box around the detected QR code
                    for i in range(len(bbox)):
                        pt1 = tuple(bbox[i][0].astype(int))
                        pt2 = tuple(bbox[(i + 1) % len(bbox)][0].astype(int))
                        cv2.line(frame, pt1, pt2, (255, 0, 0), 2)

                    if data:
                        try:
                            user_id = data.split("\n")[0].split(": ")[1]  # Extract user ID
                            email = data.split("\n")[1].split(": ")[1]  # Extract user email
                        except IndexError:
                            print("Invalid QR code format!")
                            break

                        student = Student.objects.filter(email=email).first()
                        valid_ids = AccessControl.objects.all().values_list('unique_id', flat=True)

                        print("student email" + email)
                        if student is None:
                            print("Student not found!")
                            messages.success(request, f"Student not found. Please try again.")
                            return redirect(reverse('dashboard'))

                        if user_id in valid_ids:
                            print("Valid QR Code Detected!")
                            print("User Details:")
                            print(data)

                            if IsAttendance:
                                # Call mark attendance logic
                                mark_attendance(student, status="Present", remarks="Scanned via QR")
                                print("Attendance marked!")
                                messages.success(request, f"You have successfully marked attendance")
                                return redirect(reverse('dashboard'))
                            elif IsArea:
                                checkArea = Area.objects.filter(id=CurrentArea).first()
                                if checkArea is None:
                                    messages.warning(request, "Can not find the requested area!")
                                    return redirect(f"{reverse('areas')}")
                                checkCurrentArea = StudentArea.objects.filter(area=checkArea, student=student).first()
                                if checkCurrentArea is not None:
                                    messages.warning(request, "You have successfully accessed this area!")
                                    return redirect('success',  encrypt_id(checkCurrentArea.id))
                                print("Area access denied!")

                                # Send access denied  email
                                subject = "Illegal Access"
                                message = f"""
                                                 Dear Supervisor,

                                                 Student with the following details is trying to access {checkArea.name}:

                                                 Name: {student.first_name}  {student.last_name}
                                                 Course: {student.course}
                                                 Level: {student.level}

                                                 this is for your notification and action

                                                 Best regards,
                                                 Admin Team
                                                 """
                                from_email = settings.DEFAULT_FROM_EMAIL
                                recipient_list = ["supervisor@gmail.com"]

                                send_mail(subject, message, from_email, recipient_list)

                                messages.success(request, f"You do not have permission to access this area")
                                return redirect(f"{reverse('areas')}")

                            # Change line to green
                            cv2.line(frame, (line_position, 0), (line_position, height), (0, 255, 0), 2)
                            break
                        else:
                            print("Invalid QR Code!")
                            # Trigger alarm and change line to red
                            winsound.Beep(1000, 500)  # 1000 Hz for 500 ms
                            cv2.line(frame, (line_position, 0), (line_position, height), (0, 0, 255), 2)
                else:
                    # Default moving line
                    cv2.line(frame, (line_position, 0), (line_position, height), (255, 255, 255), 2)

                # Display the camera feed
                cv2.imshow("QR Code Scanner", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("Exiting scanner.")
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        # Return success response after loop
        if IsAttendance:
            messages.success(request,f"You have successfully marked attendance")
            return redirect(reverse('dashboard'))
        elif IsArea:
            messages.success(request,f"You have successfully accessed this area")
            return redirect(reverse('dashboard'))
        else:
            messages.success(request,f"Scanning completed but no action was taken. Please try again.")
            return redirect(reverse('dashboard'))
    else:
        # Handle invalid request methods
        messages.success(request,f"Invalid request method. Please try again.")
        return redirect(reverse('dashboard'))


def mark_attendance(Student, status, remarks ):
    attendance, created = Attendance.objects.get_or_create(student=Student, date=now().date(), time=now().time())
    attendance.status = status
    attendance.remarks = remarks
    attendance.save()
    return True


# Use a stored key
FERNET_KEY = b'DlyFivkqp6pnUu706G78N7y3jfep5cFx2YtHC63ewBo='  # Replace with your key
cipher = Fernet(FERNET_KEY)

def encrypt_id(area_id):
    """Encrypt an ID."""
    return cipher.encrypt(str(area_id).encode()).decode()

