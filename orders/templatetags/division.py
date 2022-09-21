from django import template
register = template.Library()
@register.filter
def division(value, arg):
    return value / arg