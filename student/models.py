from django.db import models
from django.utils.text import slugify
from django.utils.crypto import get_random_string
# Create your models here.

from django.db import models

# class AccessControl(models.Model):
#     qr_code =  models.ImageField(upload_to='qr_codes/')
#     unique_id = models.CharField(max_length=11, unique=True)
#
#
#     def __str__(self):
#         return self.unique_id
#
# class Student(models.Model):
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     email = models.EmailField(max_length=255, null=True)
#     gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
#     date_of_birth = models.DateField()
#     course = models.CharField(max_length=50)
#     mobile_number = models.CharField(max_length=15)
#     department = models.CharField(max_length=100, null=True)
#     level = models.CharField(max_length=10)
#     image = models.ImageField(upload_to='students/', blank=True)
#     access_control = models.OneToOneField(AccessControl, on_delete=models.CASCADE, null=True)
#     slug = models.SlugField(max_length=255, unique=True, blank=True)
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(f"{self.first_name}-{self.last_name}-{self.email}")
#         super(Student, self).save(*args, **kwargs)
#
#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.email})"