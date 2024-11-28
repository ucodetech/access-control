from datetime import datetime
from symtable import Class

from django.contrib.messages.context_processors import messages
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
# Create your models here.

from django.db import models
from numpy.ma.extras import unique


class AccessControl(models.Model):
    qr_code =  models.ImageField(upload_to='qr_codes/')
    unique_id = models.CharField(max_length=11, unique=True)


    def __str__(self):
        return self.unique_id

class Student(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    date_of_birth = models.DateField()
    course = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=15, unique=True)
    # department = models.CharField(max_length=100, null=True)
    level = models.CharField(max_length=10)
    image = models.ImageField(upload_to='students/', blank=True)
    access_control = models.OneToOneField(AccessControl, on_delete=models.CASCADE, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.email}")
        super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"



class Area(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='areas/', blank=True)

    def save(self, *args, **kwargs):
        super(Area, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

class StudentArea(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        super(StudentArea, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.area.name}"