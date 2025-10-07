from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Notification(models.Model):
    USER_TYPE_CHOICES = [
        (1, "Student"),
        (2, "Lecturer"),
        (3, "Admin"),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES) 
    title = models.CharField(max_length=255)    
    message = models.TextField()
    status = models.BooleanField()  # read or unread
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
