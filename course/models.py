from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.

class Course(models.Model):
    course_name = models.CharField(max_length=255, unique=True)
    short_code = models.CharField(max_length=500)


    def save(
        self,
        *args,
        **kwargs,
    ):
        super(Course, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.course_name} ({self.short_code})"