from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the arg and the value."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''