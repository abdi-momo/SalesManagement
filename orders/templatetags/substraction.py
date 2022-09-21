from django import template
register = template.Library()
@register.filter
def substraction(value, arg):
    return value - arg