from django.db import models
from user.models import Course

# Create your models here.
class QuestionBank(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    def __str__(self):
        return self.title 
    
class Question(models.Model):
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=50) 
    question = models.TextField()
    options = models.JSONField(null=True, blank=True)
    correct_answers = models.JSONField(null=True, blank=True)
    marks = models.PositiveIntegerField()
    explanation = models.TextField(null=True, blank=True)