from django.utils.timezone import now
from django.db import models

from user.models import Lecturer
from question.models import QuestionBank

# Create your models here. 
class Exam(models.Model):
    title = models.CharField(max_length=255, default="Exam")
    lecturer = models.ForeignKey(Lecturer, on_delete=models.CASCADE)
    question_bank = models.ForeignKey(QuestionBank, on_delete=models.CASCADE)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    exam_status = models.BooleanField(default=True)
    random_order = models.BooleanField()
    copy_paste_restrict = models.BooleanField()
    total_question = models.IntegerField()
    duration = models.IntegerField()
    total_attempt = models.IntegerField()
    question_list = models.JSONField(null=True, blank=True)
    cohort = models.CharField(max_length=50)
    
class TrackingSetting(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    # Capture Screen setting (BOOLEAN)
    capture_screen = models.BooleanField(
        default=False,
        verbose_name="Capture Screen",
        help_text="Indicates if screen capture is enabled"
    )

    # Tab Switch setting (BOOLEAN)
    tab_switch = models.BooleanField(
        default=False,
        verbose_name="Tab Switch",
        help_text="Indicates if tab switch monitoring is enabled"
    )

    # Tab Switch Limit (INT)
    tab_switch_limit = models.IntegerField(
        default=0,
        verbose_name="Tab Switch Limit",
        help_text="Maximum allowable tab switches during the exam"
    )

    # Browser Activity setting (BOOLEAN)
    browser_activity = models.BooleanField(
        default=False,
        verbose_name="Browser Activity",
        help_text="Indicates if browser activity monitoring is enabled"
    )

    def __str__(self):
        return f"Exam Settings ({self.id})"
        