from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import User

# Create your models here.
class Faculty(models.Model):
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name 
    
class Programme(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name 

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    cohort = models.CharField(max_length=50)
    register_date = models.DateField()
    phone_num = PhoneNumberField()
    registered_courses = models.JSONField(null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}".title()
    
class Lecturer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=True)
    phone_num = PhoneNumberField()
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    def __str__(self):
        return f"{self.title} {self.user.first_name} {self.user.last_name}".title()

class Course(models.Model):
    programme = models.ForeignKey(Programme, on_delete=models.CASCADE)
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    code = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, unique=True)
    def __str__(self):
        return self.name