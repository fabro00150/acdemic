from django import template

register = template.Library()

@register.filter
def get_index(value, index):
    try:
        return value[index]
    except IndexError:
        return None
