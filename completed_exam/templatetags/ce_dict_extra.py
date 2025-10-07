from django import template
from online_exam.views import decrypt_id

register = template.Library()

@register.filter
def seconds_to_minutes(value):
    try:
        total_seconds = int(value)
        hours = total_seconds // 3600  # Calculate hours
        minutes = (total_seconds % 3600) // 60  # Calculate minutes
        seconds = total_seconds % 60  # Calculate remaining seconds
        return f"{hours}hr {minutes}m {seconds}s"
    except (ValueError, TypeError):
        return "Invalid Input"
    
@register.filter
def decode(encoded_id):
    return decrypt_id(encoded_id)
    
@register.filter
def id_exist_in(encoded_id, list):
    id = decrypt_id(encoded_id)
    for item in list:
        print(id)
        print(decode(item.id))
        if id == decode(item.id):
            print("Found id" + str(id))
            return True
    return False