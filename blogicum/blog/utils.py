from django.conf import settings
from django.core.paginator import Paginator


def get_page_obj(model, page):
    paginator = Paginator(model, settings.POSTS_LIMIT)
    page_obj = paginator.get_page(page)
    return page_obj
