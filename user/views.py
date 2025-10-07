import os
from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode 
from django.core.mail import EmailMessage

from smtplib import SMTPException
from .models import Programme, Lecturer, Student
from .forms import LecturerRegisForm, StudentRegisForm, UserEditForm, UserForm
from online_exam.decorators import authorized_user, unauthenticated_user
from .tokens import account_activation_token
from datetime import datetime


# Create your views here.
@unauthenticated_user
def loginPage(request):
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            print("Error while loggin in")
            messages.warning(request, ("Incorrect username or password, Try Again"))
            return redirect('user_login')
     
    else:
        return render(request, 'authenticate/login.html', {})

def logoutPage(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')
    else:
        return redirect('home')

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('user_login')
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect('user_login')

def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("authenticate/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    
    try:
        email.send()
        messages.success(request, f'Dear {user}, please head to your email {to_email} to activate your account \
        by clicking the link in the email sent to you. Note: Check your spam folder.')
        return True
    except SMTPException as e:
        messages.warning(request, f'Problem sending activation email to {to_email}. Please check if you typed it correctly and your internet connection. Error: {str(e)}')
        return False
    except Exception as e:
        messages.warning(request, f'An unexpected error occurred while sending the email: {str(e)}')
        return False
    
@unauthenticated_user
def student_reg(request):
    if request.POST:
        user_form = UserForm(request.POST)
        student_form = StudentRegisForm(request.POST)
        
        if user_form.is_valid() and student_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active=False
            
            if activateEmail(request, user, user_form.cleaned_data.get('email')):
                user.save()
                            
                group = Group.objects.get(name='student')
                user.groups.add(group) 
                print("User saved")
                student = student_form.save(commit=False)
                
                register_date = request.POST.get('date')
                cohort = "cohort" + str(datetime.strptime(register_date, '%Y-%m-%d').year)
                
                student.user = user  # Link the User instance
                student.register_date = register_date
                student.cohort = cohort
                student.save()#save form to model
                
                print("Student saved")

            return redirect('user_login')
        else:
            print("Invalid Form, something went wrong")
            print(user_form.errors)
            print(student_form.errors)
    else:
        user_form = UserForm
        student_form = StudentRegisForm
         
   
    return render(request, 'register/student_reg.html', {'user_form' : user_form,'student_form' : student_form})

@unauthenticated_user
def lecturer_reg(request):
    print("in lecturer register")
    if request.POST:
        user_form = UserForm(request.POST)
        lecturer_form = LecturerRegisForm(request.POST)
        
        if user_form.is_valid() and lecturer_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active=False
            
            if activateEmail(request, user, user_form.cleaned_data.get('email')):
                user.save()
               
                group = Group.objects.get(name='lecturer')
                user.groups.add(group)
                
                print("User saved")
                lecturer = lecturer_form.save(commit=False)
                lecturer.user = user  # Link the User instance
                lecturer.save()#save form to model
                
                print("Lecturer saved")
            return redirect('user_login')
        else:
            print("Invalid Form, something went wrong")
            print(user_form.errors)
            print(lecturer_form.errors)
    else:
        user_form = UserForm
        lecturer_form = LecturerRegisForm
         
   
    return render(request, 'register/lecturer_reg.html', {'user_form' : user_form,'lecturer_form' : lecturer_form})

@authorized_user(authorized_groups=['student', 'lecturer'])
def profile(request):
    #check user group type
    try:
        user = request.user
        if user.groups.filter(name='student').exists():
            user_profile = Student.objects.get(user_id=user.id)
        elif user.groups.filter(name='lecturer').exists():
            user_profile = Lecturer.objects.get(user_id=request.user.id)
            
    except User.DoesNotExist:
        raise Http404("User does not exist")
    
    return render(request, 'user/profile.html', {'user_profile': user_profile})

@authorized_user(authorized_groups=['student', 'lecturer'])
def upload_profile_picture(request):
    if request.user.groups.filter(name='student').exists():
        user_profile = Student.objects.get(user_id=request.user.id)
    elif request.user.groups.filter(name='lecturer').exists():
        user_profile = Lecturer.objects.get(user_id=request.user.id)

    if request.method == "POST":
        if 'profile_picture' in request.FILES:
            if user_profile .profile_picture:
                # Get the current profile picture's file path
                current_picture_path = user_profile .profile_picture.path

                # Check if the file exists and delete it
                if os.path.exists(current_picture_path):
                    os.remove(current_picture_path)
            user_profile .profile_picture = request.FILES['profile_picture']
            user_profile .save()

        return redirect('profile')

@authorized_user(authorized_groups=['student', 'lecturer'])
def edit_profile(request):
    #check user group type
    user = User.objects.get(id = request.user.id)
    is_student = user.groups.filter(name='student').exists()
    is_lecturer = user.groups.filter(name='lecturer').exists()
    context = None
        
    try:
        #retrive pk of student or lecturer based on user group type
        if is_student:
            student_profile = Student.objects.get(user_id=user.id)
            student_form = StudentRegisForm(request.POST, instance=student_profile)
        elif is_lecturer:
            lecturer_profile = Lecturer.objects.get(user_id=user.id)
            lecturer_form = LecturerRegisForm(request.POST, instance=lecturer_profile)
            print(lecturer_profile.title)
    except User.DoesNotExist:
        raise Http404("User does not exist")

    if request.POST:
        if is_student:
            student_form = StudentRegisForm(request.POST, instance=student_profile)
            user_form = UserEditForm(request.POST, instance=user)
            if student_form.is_valid() and user_form.is_valid():
                print("valid Form, Updating....")
                user_form.save()
                
                student = student_form.save(commit=False)
                
                register_date = request.POST.get('date')
                cohort = "cohort" + str(datetime.strptime(register_date, '%Y-%m-%d').year)
                
                student.user = user  # Link the User instance
                student.register_date = register_date
                student.cohort = cohort
                student.save()#save form to model
                return redirect('profile')
            else:
                print("Invalid Form, something went wrong")
                return redirect('edit_profile')
        elif is_lecturer:
            lecturer_form = LecturerRegisForm(request.POST, instance=lecturer_profile)
            user_form = UserEditForm(request.POST, instance=user)
            if lecturer_form.is_valid() and user_form.is_valid():
                print("valid Form, Updating....")
                user_form.save()
                lecturer_form.save() #save form to model
                return redirect('profile')
            else:
                print("Invalid Form, something went wrong")
                messages.warning(request, lecturer_form.errors)
                messages.warning(request, user_form.errors)
                return redirect('edit_profile')
    
                
    if is_student:
        student_form = StudentRegisForm(request.POST, instance=student_profile)
        user_form = UserEditForm(request.POST, instance=user)
        context = {
            'user' : user,
            'student_profile': student_profile,
            'student_form': student_form,
            'user_form': user_form,
        }
        
    elif is_lecturer:
        lecturer_form = LecturerRegisForm(request.POST, instance=lecturer_profile)
        user_form = UserEditForm(request.POST, instance=user)
        context = {
            'user' : user,
            'lecturer_profile': lecturer_profile,
            'lecturer_form': lecturer_form,
            'user_form': user_form,
        }
    return render(request, 'user/edit_profile.html', context)
