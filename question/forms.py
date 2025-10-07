from django import forms
from django.forms import ModelForm
from .models import Course, Question, QuestionBank

class QuestionBankCreationForm(forms.ModelForm):
    course = forms.ModelChoiceField(queryset=Course.objects.all(), empty_label="Select a course")
    title = forms.CharField(label='Title')
    
    class Meta:
        model = QuestionBank
        fields = ['course', 'title']

class QuestionCreationForm(forms.ModelForm):
    question_type_choice = [('', 'Question Type'), ('mcq', 'Multiple Choice Question'), ('essay','Essay'), ('tf','True/False')]
    
    question_bank = forms.ModelChoiceField(queryset=QuestionBank.objects.all().order_by('course'), empty_label="Select Question Bank") #order list by course type
    question_type = forms.ChoiceField(choices=question_type_choice, label='Question Type')  
    question = forms.CharField(label='Question')
    options = forms.JSONField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 50}), label="Option", required=False)
    correct_answers = forms.JSONField(widget=forms.Textarea(attrs={'rows': 3, 'cols': 50}), label="Correct Answer", required=False)
    marks = forms.IntegerField(min_value=1, label="Marks")
    explanation = forms.CharField(label='Explanation', required=False)
    
    class Meta:        
        model = Question
        fields = ['question_bank', 'question_type', 'question', 'options', 'correct_answers', 'marks', 'explanation']
