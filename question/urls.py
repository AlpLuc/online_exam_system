from django.urls import path
from . import views

urlpatterns = [
    path('question_bank_list', views.question_bank_list, name="question_bank_list"),
    path('question_list/<str:encrypted_id>', views.question_list, name="question_list"),
    path('create_question_bank', views.create_question_bank, name="create_question_bank"),
    path('edit_question_bank/<str:encrypted_id>', views.edit_question_bank, name="edit_question_bank"),
    path('create_question', views.create_question, name="create_question"),
    path('view_question/<str:encrypted_id>', views.view_question, name="view_question"),
    path('edit_question/<str:encrypted_id>', views.edit_question, name="edit_question"),
    path('delete_question/<str:encrypted_id>', views.delete_question, name="delete_question"),
    path('delete_question_bank/<str:encrypted_id>', views.delete_question_bank, name="delete_question_bank"),
]