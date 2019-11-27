from django import template

register = template.Library()


@register.filter()
def indent_spaces(value, arg):
    return '\n'.join(' ' * arg + line for line in value.splitlines())
