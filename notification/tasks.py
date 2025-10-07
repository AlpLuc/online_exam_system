import os
from django.utils import timezone

from datetime import timedelta
from exam.models import Exam
from celery import Celery, shared_task
from celery.schedules import crontab

from notification.views import send_notification

@shared_task
def examReminderNotification():
    now = timezone.now()
    
    print(now)

    # Calculate the time range for 1 day from now
    next_day = now + timedelta(days=1)
    next_day_end = next_day + timedelta(days=1)

    exams_next_day = Exam.objects.filter(start_date_time__gte=next_day, start_date_time__lt=next_day_end)
    
    if exams_next_day:
            from django.contrib.auth.models import User
            from user.models import Student
            from django.db.models import Q
            
            for exam in exams_next_day:
                course_id = exam.question_bank.course.id 
                
                students = Student.objects.filter( Q(registered_courses__contains=[course_id]))
                
                time = exam.start_date_time.time().strftime('%I:%M %p')
                
                print(students)
                for student in students:
                        user = User.objects.get(id=student.user.id)
                        title = 'Upcoming Exam '+ exam.title 
                        text = "Dear " + student.user.first_name + " " + student.user.last_name + ",\n\nWe hope this message finds you well. This is a reminder that your upcoming exam, "+ exam.title + ", is scheduled to take place on " + str(exam.start_date_time.date()) + " at " + time + ".\n\nPlease ensure that you are prepared and have all the necessary materials ready." + "\n\nShould you have any questions or require assistance, feel free to reach out to your instructor or the support team." + "\n\nBest of luck in your preparations"
                        send_notification(user, title, text, False, 1)
