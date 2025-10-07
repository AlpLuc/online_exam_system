from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Faculty, Lecturer, Programme, Student
from phonenumber_field.formfields import PhoneNumberField

class UserForm(UserCreationForm):
    usable_password = None
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email']
        
class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class StudentRegisForm(forms.ModelForm):
    programme = forms.ModelChoiceField(queryset=Programme.objects.all(), empty_label="Select a programme")
    phone_num = PhoneNumberField()
    
    class Meta:
        model = Student
        fields = ['programme','phone_num']
        
class LecturerRegisForm(forms.ModelForm):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.all(), empty_label="Select a Faculty")
    title = forms.CharField(required=False)
    phone_num = PhoneNumberField()
    
    class Meta:
        model = Lecturer
        fields = ['faculty','title','phone_num']