"""
URL configuration for online_exam project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static 
from django.conf import settings
from . import views

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    path('', views.home, name="home"),
    path('user/', include('django.contrib.auth.urls')),
    path('user/', include('user.urls')),
    path('question/', include('question.urls')),
    path('exam/', include('exam.urls')),
    path('course/', include('course.urls')),
    path('completed_exam/',include('completed_exam.urls')),
    path('notification/', include('notification.urls')),
]

urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

admin.site.site_title = "Admin Panel"  # The title in the browser tab
admin.site.site_header = "Admin Panel"  # The header displayed in the admin panel
admin.site.index_title = "Admin Panel"  # The title in the admin dashboard