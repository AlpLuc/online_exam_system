from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('user_login', views.loginPage, name="user_login"),
    path('student_reg', views.student_reg, name="student_reg"),
    path('lecturer_reg', views.lecturer_reg, name="lecturer_reg"),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('user_logout', views.logoutPage, name="user_logout"),
    path('profile', views.profile, name="profile"),
    path('upload_profile_picture', views.upload_profile_picture, name="upload_profile_picture"),
    path('edit_profile', views.edit_profile, name="edit_profile"),
    path('password_reset', auth_views.PasswordResetView.as_view(template_name="authenticate/password_reset.html"), name="password_reset"),
    path('password_reset_done', auth_views.PasswordResetDoneView.as_view(template_name="authenticate/password_reset_done.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name="authenticate/password_reset_confirm.html"), name="password_reset_confirm"),
    path('password_reset_complete', auth_views.PasswordResetCompleteView.as_view(template_name="authenticate/password_reset_complete.html"), name="password_reset_complete"),
]
