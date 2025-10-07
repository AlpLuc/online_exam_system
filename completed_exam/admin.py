from django.contrib import admin
from .models import CompletedExam

# Register your models here.
@admin.register(CompletedExam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('exam__title', 'student', 'exam__question_bank__course', 'exam__question_bank__course__lecturer', 'completed_at')  
    search_fields = ('exam__title', 'exam__question_bank__course__lecturer__user__first_name', 'exam__question_bank__course__lecturer__user__last_name')  
    list_filter = ('completed_at', 'exam__question_bank__course')  
    ordering = ('exam__title', 'completed_at')  
