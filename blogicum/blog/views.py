from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm, ProfileChangeForm
from .models import Category, Comment, Post

IS_PUBLISHED_TRUE = (Q(pub_date__lte=timezone.now())
                     & Q(is_published=True)
                     & Q(category__is_published=True)
                     & Q(location__is_published=True))

User = get_user_model()


class CategoryDetailView(DetailView):
    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            is_published=True,
            slug=self.kwargs[self.slug_url_kwarg]
        )
        return obj

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.select_related(
            'location',
            'author',
        ).prefetch_related(
            'comments'
        ).filter(
            IS_PUBLISHED_TRUE
        )
        paginator = Paginator(posts, settings.POSTS_LIMIT)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['page_obj'] = page_obj
        return context


class UserMixin:
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'


class UserDetailView(UserMixin, DetailView):
    context_object_name = 'profile'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        posts = self.object.posts.select_related(
            'location',
            'category'
        ).prefetch_related(
            'comments'
        ).filter(
            IS_PUBLISHED_TRUE
            | Q(author__username=self.request.user.username)
        )
        paginator = Paginator(posts, settings.POSTS_LIMIT)
        page = self.request.GET.get('page')
        page_obj = paginator.get_page(page)
        context['page_obj'] = page_obj
        return context


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UserMixin,
                     UpdateView):
    """
    User update class view for profile change page.

    Use blog/user.html template. Available only to profile owner.
    """

    form_class = ProfileChangeForm
    template_name = 'blog/user.html'

    def test_func(self):
        return self.request.user.username == self.kwargs['username']

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.username])


class IndexListView(ListView):
    """
    Posts list class view for index page.

    Use blog/index.html template. Return all posts with `is_published` is true
    for `Post`, `Location`, `Category` and `pub_date` <= now.
    """

    paginate_by = settings.POSTS_LIMIT
    template_name = 'blog/index.html'
    queryset = Post.published_posts.prefetch_related('comments')


class PostDetailView(DetailView):
    """
    Class view for post detail page.

    If post has true for `Post`, `Location`, `Category` and `pub_date` <= now,
    than everyone can see post. Otherwise only the author has access to the
    post.
    """

    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    queryset = Post.objects.select_related('location', 'category', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs[self.pk_url_kwarg]
        obj = get_object_or_404(
            queryset,
            IS_PUBLISHED_TRUE
            | Q(author__username=self.request.user.username),
            pk=pk
        )
        return obj


class PostBaseMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostModificationMixin(UserPassesTestMixin):
    """
    Add redirect for not post authors.
    """

    pk_url_kwarg = 'post_id'

    def test_func(self) -> bool:
        obj = self.get_object()
        return self.request.user == obj.author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect(
                'blog:post_detail',
                post_id=self.kwargs[self.pk_url_kwarg]
            )
        return super().handle_no_permission()


class PostCreateView(LoginRequiredMixin, PostBaseMixin, CreateView):
    """
    Post creation class view.

    Available only to logged in users.
    """

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.author])


class PostUpdateView(LoginRequiredMixin, PostBaseMixin, PostModificationMixin,
                     UpdateView):
    """
    Update class view for post edit page.

    Only post author has access to it. Redirect other users to posts detail
    page.
    """

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, PostBaseMixin, PostModificationMixin,
                     DeleteView):
    """
    Delete class view for post delete page.

    Only post author has access to it. Redirect other users to posts detail
    page.
    """

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.author])


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponseRedirect:
    """
    Comment creation view function.

    Available only to logged in users.

    Parameters
    ----------
    request : HttpRequest
        Http request.
    post_id : str
        Post pk.

    Returns
    -------
    HttpResponseRedirect
        Redirect response to post detail page.
    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


class CommentMixin:
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        obj = get_object_or_404(
            queryset,
            pk=self.kwargs['comment_id'],
            author=self.request.user,
            post__pk=self.kwargs['post_id']
        )
        return obj

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.object.post.pk])


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    """
    Delete class view for comment delete page.

    Only comment author has access to it.
    """

    pass


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    """
    Update class view for comment edit page.

    Only comment author has access to it.
    """
    form_class = CommentForm
