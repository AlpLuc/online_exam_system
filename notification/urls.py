from django.urls import path
from . import views

urlpatterns = [
    path('view_notification', views.view_notification, name='view_notification'),
    path('mark_unread/<str:encrypted_id>', views.mark_unread, name='mark_unread'),
    path('delete_notification/<str:encrypted_id>', views.delete_notification, name='delete_notification'),
]