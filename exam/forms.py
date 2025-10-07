from django import forms
from django.forms import ModelForm

from .models import QuestionBank
from .models import Exam, TrackingSetting

class TrackingSettingForm(forms.ModelForm):
    capture_screen = forms.BooleanField(required=False, label="Capture Screen", widget=forms.CheckboxInput())
    tab_switch = forms.BooleanField(required=False, label="Tab Switch Monitoring", widget=forms.CheckboxInput())
    tab_switch_limit = forms.IntegerField(required=False, min_value=0, label="Tab Switch Limit", widget=forms.NumberInput(attrs={'min': 0}), initial=0)
    browser_activity = forms.BooleanField(required=False, label="Browser Activity Monitoring", widget=forms.CheckboxInput())
    
    class Meta:
        model = TrackingSetting
        fields = ['capture_screen', 'tab_switch', 'tab_switch_limit', 'browser_activity']
    
    # Customizing form fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['capture_screen'].help_text = "Indicates whether screen capture is enabled during the exam."
        self.fields['tab_switch'].help_text = "Indicates whether tab switch monitoring is enabled during the exam."
        self.fields['tab_switch_limit'].help_text = "The maximum number of tab switches allowed during the exam."
        self.fields['browser_activity'].help_text = "Indicates whether browser activity should be monitored during the exam."
        
class ExamForm(forms.ModelForm):
    # Define choices for fields    
    title = forms.CharField(label="Title")
    random_order = forms.BooleanField(required=False, label="Randomize Question Order", initial=False )
    copy_paste_restrict = forms.BooleanField(required=False, label="Restrict Copy/Paste", initial=False)
    total_question = forms.IntegerField(min_value=1, label="Total Questions", widget=forms.NumberInput(attrs={'min': 1}))
    duration = forms.IntegerField(min_value=1, label="Duration (in minutes)", widget=forms.NumberInput(attrs={'min': 1}))
    total_attempt = forms.IntegerField(min_value=1, label="Total Attempts", widget=forms.NumberInput(attrs={'min': 1}))
    start_date_time = forms.DateTimeField(label="Start Date & Time", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_date_time = forms.DateTimeField(label="End Date & Time", widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    question_bank = forms.ModelChoiceField(queryset=QuestionBank.objects.all().order_by('course'), empty_label="Select Question Bank", label="Question Bank")
    
    class Meta:
        model = Exam
        fields = [ 'title','start_date_time', 'end_date_time', 
                   'random_order', 'copy_paste_restrict', 
                   'duration', 'total_attempt', 'question_bank', 'total_question']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['random_order'].help_text = "If enabled, the questions will be displayed in a random order."
        self.fields['copy_paste_restrict'].help_text = "If enabled, copying and pasting will be restricted during the exam."
        self.fields['total_question'].help_text = "Enter the total number of questions in the exam."
        self.fields['duration'].help_text = "Enter the total duration of the exam in minutes."
        self.fields['total_attempt'].help_text = "Enter the total number of attempts allowed for this exam."
        self.fields['start_date_time'].help_text = "The date and time when the exam starts."
        self.fields['end_date_time'].help_text = "The date and time when the exam ends."
