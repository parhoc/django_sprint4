from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Category, Post


def index(request: HttpRequest) -> HttpResponse:
    """
    Render start page with data from `posts`. Use blog/index.html template.

    Parameters
    ----------
    request : HttpRequest
        Http request.

    Returns
    -------
    HttpResponse
        Response with rendered page.
    """
    template = 'blog/index.html'
    posts = Post.published_posts.all()[:settings.INDEX_POSTS_LIMIT]
    context = {
        'post_list': posts,
    }
    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """
    Render page with selected post detail. Use blog/detail.html template.

    Parameters
    ----------
    request : HttpRequest
        Http request.
    post_id : int
        Post id.

    Returns
    -------
    HttpResponse
        Response with rendered page.
    """
    template = 'blog/detail.html'
    post = get_object_or_404(
        Post.published_posts,
        pk=post_id
    )
    context = {
        'post': post,
    }
    return render(request, template, context)


def category_posts(request: HttpRequest, category_slug: str) -> HttpResponse:
    """
    Render page with posts wich have `category_slug` category.

    Use blog/category.html template.

    Parameters
    ----------
    request : HttpRequest
        Http request.
    category_slug : str
        Category name.

    Returns
    -------
    HttpResponse
        Response with rendered page.
    """
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    posts = category.posts.select_related(
        'location',
        'category',
        'author'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )
    context = {
        'category': category,
        'post_list': posts,
    }
    return render(request, template, context)
