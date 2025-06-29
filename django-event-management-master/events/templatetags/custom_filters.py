from django import template
register = template.Library()

@register.filter
def get_attendance(attendance_dict, key):
    return attendance_dict.get(key, None)
