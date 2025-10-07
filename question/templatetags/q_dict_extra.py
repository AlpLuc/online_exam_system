from django import template
from online_exam.views import decrypt_id

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if decrypt_id(key):
        return decrypt_id(key)
    else:
        print(0)
        return None