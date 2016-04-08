import os

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.template import Template
from django.utils._os import safe_join


def get_page_or_404(file_name):
    """Return page content as a Django template or raise 404 error.
    :param name: name of the page to display
    """
    try:
        file_path = safe_join(settings.SITE_PAGES_DIRECTORY, file_name)
    except ValueError:
        raise Http404('Page Not Found')
    else:
        if not os.path.exists(file_path):
            raise Http404('Page Not Found')
    with open(file_path, 'r') as f:
        page = Template(f.read())

    return page


def show_page(request, name='index'):
    """Show the requested page if found.
    :param request: requested page
    :param name: name of the page to display, default is index
    """
    file_name = '{}.html'.format(name)
    page = get_page_or_404(file_name)
    context = {
            'name': name,
            'page': page,
    }
    return render(request, 'page.html', context)
