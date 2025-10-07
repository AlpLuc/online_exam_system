from django.contrib import admin
from .models import Exam, TrackingSetting

# Register your models here.

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'lecturer', 'start_date_time', 'end_date_time', 'cohort')  
    search_fields = ('title', 'lecturer__user__first_name', 'lecturer__user__last_name')  
    list_filter = ('start_date_time', 'end_date_time')  
    ordering = ('cohort', 'lecturer', 'title')  
