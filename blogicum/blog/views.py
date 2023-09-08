from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
from django.http import Http404

from .forms import CommentForm, PostForm, ProfileChangeForm
from .models import Category, Comment, Post

User = get_user_model()


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
    user = get_object_or_404(User, username=username)
    posts = Post.objects.select_related(
        'author',
        'location',
        'category'
    ).prefetch_related(
        'comments'
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

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.username])


class IndexListView(ListView):
    model = Post
    paginate_by = settings.POSTS_LIMIT
    template_name = 'blog/index.html'
    queryset = Post.published_posts.prefetch_related('comments')


class PostDetailView(DetailView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'
    queryset = Post.objects.select_related('location', 'category', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.select_related('author')
        context['form'] = CommentForm()
        return context

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id']
        )
        if ((post.is_published and
             post.category.is_published and
             post.location.is_published and
             post.pub_date <= timezone.now()) or
           post.author == request.user):
            return super().dispatch(request, *args, **kwargs)
        raise Http404()


class PostBaseMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'


class PostModificationMixin:
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=kwargs['post_id'],
        )
        # redirect if not author
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post.pk)
        return super().dispatch(request, *args, **kwargs)


class PostCreateView(LoginRequiredMixin, PostBaseMixin, CreateView):
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.author])


class PostUpdateView(LoginRequiredMixin, PostBaseMixin, PostModificationMixin,
                     UpdateView):
    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.object.pk])


class PostDeleteView(LoginRequiredMixin, PostBaseMixin, PostModificationMixin,
                     DeleteView):
    def get_success_url(self) -> str:
        return reverse_lazy('blog:profile', args=[self.object.author])


@login_required
def add_comment(request, post_id):
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

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(
            Comment,
            pk=kwargs['comment_id'],
            author=request.user,
            post__pk=kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy('blog:post_detail', args=[self.object.post.pk])


class CommentDeleteView(LoginRequiredMixin, CommentMixin, DeleteView):
    pass


class CommentUpdateView(LoginRequiredMixin, CommentMixin, UpdateView):
    form_class = CommentForm
