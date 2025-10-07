import hashlib
import base64
from cryptography.fernet import Fernet
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models import Count, F, Q, OuterRef, Subquery, Value
from django.utils import timezone
from django.utils.timezone import now, localtime

from datetime import timedelta
from website.models import siteInfo
from exam.models import Exam
from user.models import Student, Lecturer, Course
from completed_exam.models import CompletedExam


# Create your views here.
def home(request):
        site_info = siteInfo.objects.first()
        user_profile = None
        info = {}
        started_exams = None    
        upcoming_exams = None
        graded_exams = None
              
        if request.user.is_authenticated:
                user = User.objects.get(id=request.user.id)
                
                if request.user.groups.filter(name='student').exists():
                        user_profile = Student.objects.get(user_id = request.user.id)
    
                        # Ongoing & upcoming Exams
                        completed_attempts = CompletedExam.objects.filter(
                                exam_id=OuterRef('pk'),  # Reference to the current exam in the outer query
                                student_id=user_profile.id  # Use the current student ID
                        ).values('exam_id').annotate(attempt_count=Count('id')).values('attempt_count')


                        current_time = now()
                        if user_profile.registered_courses is not None:
                                started_exams = Exam.objects.annotate(
                                attempt_count=Coalesce(Subquery(completed_attempts), Value(0))    
                                ).filter(
                                question_bank__course__id__in=user_profile.registered_courses,
                                start_date_time__lte=current_time,
                                end_date_time__gte=current_time,
                                cohort = user_profile.cohort
                                ).exclude(
                                attempt_count__gte=F('total_attempt')    
                                )        

                                upcoming_exams = Exam.objects.filter(
                                question_bank__course__id__in=user_profile.registered_courses,
                                start_date_time__gt=current_time,
                                cohort = user_profile.cohort
                                )
                        
                        #Graded Exams
                        three_months_ago = timezone.now() - timedelta(days=90)
                        graded_exams = CompletedExam.objects.filter(student_id = user_profile.id, graded=1, completed_at__gte=three_months_ago).order_by('completed_at')
                                                        
                        for exam in graded_exams:
                                exam.id = encrypt_id(exam.id)
                        
                        info['started_exams'] = started_exams
                        info['upcoming_exams'] = upcoming_exams
                        info['graded_exams'] = graded_exams
                elif request.user.groups.filter(name='lecturer').exists():
                        user_profile = Lecturer.objects.get(user_id = request.user.id)
                        courses = Course.objects.filter(lecturer_id=user_profile.id)
                        non_graded_exam_id = CompletedExam.objects.filter(graded=0, exam__question_bank__course__in=courses).values('exam_id').distinct()
                        non_graded_exams = Exam.objects.filter(id__in=non_graded_exam_id)
                        
                        for exam in non_graded_exams:
                                exam.id = encrypt_id(exam.id)
                        
                        info['non_graded_exams'] = non_graded_exams
                        
        else:
                user = None        
        
        context ={
                'site_info' : site_info,
                'user' : user,
                'user_profile' : user_profile,
                'info' : info,
        }   
        return render(request, 'home.html', context)

def get_cipher():
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key[:32]))

# Encrypt the ID
def encrypt_id(id):
    cipher = get_cipher()
    encrypted_id = cipher.encrypt(str(id).encode())
    return encrypted_id.decode()  # Convert to str format

# Decrypt the ID
def decrypt_id(encrypted_id):
    cipher = get_cipher()
    try:
        decrypted_id = cipher.decrypt(encrypted_id.encode()).decode()  # Convert str to int
        return int(decrypted_id)  # Return original id
    except:
        return None  # Return None if invalid