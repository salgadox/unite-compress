from django import template

register = template.Library()


@register.simple_tag(name="percent_reduction")
def percent_reduction(original_size, converted_size):
    return 100 * (original_size - converted_size) / original_size
