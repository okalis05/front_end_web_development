from django import template

register = template.Library()

@register.filter
def money(value):
    try:
        return f"${value:,.2f}"
    except Exception:
        return "$0.00"
