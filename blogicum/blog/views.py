from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views.generic import UpdateView, ListView, DetailView

from .models import Category, Post
from .forms import ProfileChangeForm

User = get_user_model()


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
    paginator = Paginator(posts, settings.POSTS_LIMIT)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def user_profile(request, username):
    template_name = 'blog/profile.html'
    user = User.objects.get(username=username)
    posts = Post.published_posts.select_related(
        'author',
        'location',
        'category'
    ).filter(
        author=user
    )
    paginator = Paginator(posts, settings.POSTS_LIMIT)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'profile': user,
        'page_obj': page_obj,
    }
    return render(request, template_name, context)


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = ProfileChangeForm
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            User,
            pk=request.user.pk,
            username=kwargs['username']
        )
        return super().dispatch(request, *args, **kwargs)


class IndexListView(ListView):
    model = Post
    paginate_by = settings.POSTS_LIMIT
    template_name = 'blog/index.html'
    queryset = Post.published_posts.all()


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    queryset = Post.published_posts
    template_name = 'blog/detail.html'
