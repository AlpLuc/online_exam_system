from django.urls import path
from . import views

urlpatterns = [
    path('exam_list', views.exam_list, name="exam_list"),
    path('create_exam', views.create_exam, name="create_exam"),
    path('edit_exam/<str:encrypted_id>/', views.edit_exam, name="edit_exam"),
    path('view_exam/<str:encrypted_id>/', views.view_exam, name="view_exam"),
    path('get_questions/<int:question_bank_id>/', views.get_questions, name="get_questions"),
    path('delete_exam/<str:encrypted_id>/', views.delete_exam, name="delete_exam"),
    path('change_exam_status/<str:encrypted_id>/', views.change_exam_status, name="change_exam_status"),
    path('view_exam', views.student_view_exam, name="student_view_exam"),
    path('exam_agreement/<str:encrypted_id>/', views.exam_agreement, name="exam_agreement"),
    path('examination/<str:encrypted_id>/', views.examination, name="examination"),
    path('save_timer/', views.save_timer, name='save_timer'),
    path('session_save_selected_answer/', views.session_save_selected_answer, name='session_save_selected_answer'),
    path('update_tab_switch_counter/', views.update_tab_switch_counter, name='update_tab_switch_counter'),
    path('upload_screen_chunk/<int:exam_id>', views.upload_screen_chunk, name='upload_screen_chunk'),
    path('log_browser_activity/', views.log_browser_activity, name='log_browser_activity'),
    path('save_flagged_questions/', views.save_flagged_questions, name='save_flagged_questions'),
    path('end_exam/', views.end_exam, name='end_exam'),
    path('exam_ended/<str:encrypted_id>', views.exam_ended, name='exam_ended'),
]