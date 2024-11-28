from django.db import models
from django.utils.timezone import now

from superuser.models import Student


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=now)
    time = models.TimeField(default=now)
    status = models.CharField(
        max_length=10,
        choices=[
            ('Present', 'Present'),
            ('Absent', 'Absent'),
            ('Late', 'Late'),
        ],
        default='Present',
    )
    remarks = models.TextField(blank=True, null=True)  # Optional remarks

    def __str__(self):
        return f"{self.student} - {self.date} - {self.time} - {self.status}"
