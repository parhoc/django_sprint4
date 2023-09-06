from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.core.paginator import Paginator

from .models import Category, Post

User = get_user_model()


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


def user_profile(request, username):
    template_name = 'blog/profile.html'
    user = User.objects.get(username=username)
    posts = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).filter(
        author=user,
        is_published=True,
        pub_date__lte=timezone.now()
    )
    paginator = Paginator(posts, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)
