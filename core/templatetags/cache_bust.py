import os
from django import template
from django.contrib.staticfiles import finders

register = template.Library()

@register.simple_tag
def static_version(path):
    """Returns the static file's last-modified time, for use as a cache-busting query string."""
    found = finders.find(path)
    if found:
        return int(os.path.getmtime(found))
    return '0'
