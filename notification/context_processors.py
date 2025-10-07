from .models import Notification  # Adjust according to your model
from user.models import Student, Lecturer
from website.models import siteInfo

def unread_notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, status=False).count()
        if request.user.groups.filter(name='student').exists():
            user_profile = Student.objects.get(user_id = request.user.id)
        elif request.user.groups.filter(name='lecturer').exists():
            user_profile = Lecturer.objects.get(user_id = request.user.id)
        else: 
            user_profile = None    
    
        site_info = siteInfo.objects.first()
           
    else:
        unread_count = 0
        user_profile = None
        site_info = None
    return {'unread_count': unread_count, 'user_profile': user_profile, 'site_info' : site_info,}
