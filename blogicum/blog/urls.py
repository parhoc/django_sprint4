from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path(
        'post/<int:post_id>/comment/<int:comment_id>/',
        views.IndexListView.as_view(),
        name='edit_comment'
    ),  # to do
    path(
        'post/<int:post_id>/comment/',
        views.IndexListView.as_view(),
        name='add_comment'
    ),  # to do
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'profile/<slug:username>/',
        views.user_profile,
        name='profile'
    ),
    path(
        'profile/<slug:username>/edit/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        '',
        views.IndexListView.as_view(),
        name='index'
    ),
]
