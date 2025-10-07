from django.db import models

# Create your models here.
class siteInfo(models.Model):
    home_image = models.ImageField(upload_to='home_images/', blank=True, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    introduction = models.TextField()
    contact = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
