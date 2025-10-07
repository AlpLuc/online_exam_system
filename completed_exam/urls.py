from django.urls import path
from . import views

urlpatterns = [
    path('lecture_view_completed_exam', views.lecture_view_completed_exam, name="lecture_view_completed_exam"),
    path('grade_completed_exam/<str:encrypted_id>/', views.grade_completed_exam, name='grade_completed_exam'),
    path('view_exam_report/<str:encrypted_id>/', views.view_exam_report, name='view_exam_report'),
    path('student_view_completed_exam', views.student_view_completed_exam, name="student_view_completed_exam"),
    path('student_view_completed_exam_detail/<str:encrypted_id>/', views.student_view_completed_exam_detail, name="student_view_completed_exam_detail"),
    path('view_exam_log/<str:encrypted_id>/', views.view_exam_log, name="view_exam_log"),
]