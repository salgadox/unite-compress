from django import template

register = template.Library()


@register.simple_tag(name="percent_reduction")
def percent_reduction(original_size, converted_size):
    percent_reduction = 100 * (original_size - converted_size) / original_size
    return f"{percent_reduction:.2f}"
