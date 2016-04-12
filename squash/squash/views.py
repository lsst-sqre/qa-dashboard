from django.http import Http404
from django.http import HttpResponse
from django.template import loader


def show_page(request, name="index"):
    """Return page content as a Django template or raise 404 error.
    :param name: name of the html page to display
    """
    file_name = '{}.html'.format(name)

    try:
        page = loader.get_template(file_name)
    except:
        raise Http404('Page Not Found')

    context = {
            'name': name,
            'page': page,
    }

    return HttpResponse(page.render(context, request))
