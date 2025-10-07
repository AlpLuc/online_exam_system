from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.timezone import now
from django.core.paginator import Paginator

from .models import Notification
from online_exam.views import encrypt_id, decrypt_id

# Create your views here.
def send_notification(user, title, message, status=False, user_type=None):
    from .models import Notification  # Import the Notification model
    Notification.objects.create(
        user=user,
        user_type=user_type,
        title=title,
        message=message,
        status=status,
        timestamp=now()
    )


def view_notification(request):
    notifications = Notification.objects.filter(user_id = request.user.id). order_by("-timestamp")
    
    for noti in notifications:
        noti.id = encrypt_id(noti.id)
    
    noti_id = request.GET.get('noti')  # Get the 'noti' query parameter
    if noti_id:
        noti_id = decrypt_id(noti_id)
        selected_notification = notifications.get(id = noti_id)  # Fetch the notification by ID
        # Mark as read if needed
        if not selected_notification.status:
            selected_notification.status = True
            selected_notification.save()
        selected_notification.id = encrypt_id(selected_notification.id)
    else:
        selected_notification = None 
        
    paginator = Paginator(notifications, 10)  # Show 10 exams per page
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)  # Get current page
    
    context = {
        'notifications' : notifications,
        'selected_notification' : selected_notification,
        'page_number' : page_number,
    }   
    return render(request, 'notification/view_notification.html', context)

def mark_unread(request, encrypted_id):
    id = decrypt_id(encrypted_id)
    notification = get_object_or_404(Notification, id=id)
    
    notification.status = False  # False = unread
    notification.save()

    # Redirect back to the view where the notification details are shown
    return redirect('view_notification')
    
def delete_notification(request, encrypted_id):
    id = decrypt_id(encrypted_id)
    notification = get_object_or_404(Notification, id=id)
    
    notification.status = False  # False = unread
    notification.delete()
    return redirect('view_notification')