from django import forms

from .models import Exam, Student

class CompletedExamForm(forms.ModelForm):
    exam = forms.ModelChoiceField(Exam, on_delete=forms.CASCADE)
    student = forms.ModelChoiceField(Student, on_delete=forms.CASCADE)
    status = forms.CharField(max_length=50 )
    attempt = forms.IntegerField()
    total_mark = forms.DecimalField()
    time_taken = forms.DurationField()
    answers = forms.JSONField(required=False)
    comment = forms.CharField(required=False)