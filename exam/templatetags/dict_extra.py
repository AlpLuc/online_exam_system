from django import template

register = template.Library()

@register.filter
def get_key_list(dictionary, key):
    if dictionary and key:
        return dictionary.get(str(key), [])
    return []

@register.filter
def get_key(dictionary, key):
    if dictionary and key:
        return dictionary.get(str(key), None)  # Return None if key doesn't exist
    return None