from django.shortcuts import redirect, render

from online_exam.decorators import authorized_user
from user.models import Course, Student

# Create your views here.
@authorized_user(authorized_groups=['student'])
def course_list(request):
    student = Student.objects.get(user_id=request.user.id)
    
    #check if registered_courses is NULL, if NULL make it a list
    if student.registered_courses is None:
        student.registered_courses = []  
    registered_course_list = Course.objects.filter(id__in=student.registered_courses)
    
    context = {
        'student' : student,
        'registered_course_list' : registered_course_list,
    }
    return render(request, 'course/course_list.html', context)

@authorized_user(authorized_groups=['student'])
def register_course(request):
    student = Student.objects.get(user_id=request.user.id)
    #check if registered_courses is NULL, if NULL make it a list
    if student.registered_courses is None:
        student.registered_courses = []
    
    course_list = Course.objects.filter(programme_id=student.programme.id).exclude(id__in=student.registered_courses)
    
    context = {
        'student' : student,
        'course_list' : course_list,
    }
    return render(request, 'course/register_course.html', context)

@authorized_user(authorized_groups=['student'])
def register(request, id):
    student = Student.objects.get(user_id=request.user.id)
    #check if registered_courses is NULL, if NULL make it a list
    if student.registered_courses is None:
        student.registered_courses = []  
    
    #append course into registered_courses    
    student.registered_courses.append(id)
    student.save()
    return redirect('register_course')

@authorized_user(authorized_groups=['student'])
def remove_course(request, id):
    student = Student.objects.get(user_id=request.user.id)
    #remove id if exist
    if id in student.registered_courses:
        student.registered_courses.remove(id)
        student.save()
    
    return redirect('course_list')
    
    