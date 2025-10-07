from django.urls import path
from . import views


urlpatterns = [
    path('course_list', views.course_list, name="course_list"),
    path('register_course', views.register_course, name="register_course"),
    path('register/<int:id>', views.register, name="register"),
    path('remove_course/<int:id>', views.remove_course, name="remove_course"),
]