from django.db import models

# Create your models here.
from django.db import models
from exam.models import Exam
from user.models import Student

class CompletedExam(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name="Identifier linking to the original exam")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="Identifier linking to the student who took the exam")
    graded = models.BooleanField(default=True, verbose_name="Status of the completed exam (e.g., graded=False, ungraded=True)")
    exam_passed = models.BooleanField(default=True, verbose_name="Pass status, Pass or Fail")
    attempt = models.PositiveIntegerField(verbose_name="Attempt number of the completed exam")
    total_mark = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Total marks obtained in the completed exam")
    full_mark = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Total marks of the exam")
    time_taken = models.PositiveIntegerField(verbose_name="Duration of time taken to complete the exam")
    answers = models.JSONField(null=True, blank=True, verbose_name="Marks of each indivisual essay question if exist")
    essay_mark = models.JSONField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True, verbose_name="Comments or feedback on the completed exam")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Completed Exam"
        verbose_name_plural = "Completed Exams"

class ScreenCapture(models.Model):
    completed_exam = models.ForeignKey(CompletedExam, on_delete=models.CASCADE)
    location = models.FileField(max_length=500)
    
class BrowserActivity(models.Model):
    completed_exam = models.ForeignKey(CompletedExam, on_delete=models.CASCADE)
    activity_log = models.JSONField()
