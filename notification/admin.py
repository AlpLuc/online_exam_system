from django.contrib import admin
from .models import Notification

# Register your models here.
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'timestamp')  
    search_fields = ('title', 'user__first_name', 'user__last_name', 'timestamp')
    list_filter = ('timestamp',)    
    ordering = ('timestamp', 'title') 