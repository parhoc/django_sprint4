from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/create/', views.index, name='create_post'),  # to do
    path('profile/<slug:username>/', views.user_profile, name='profile'),
    path(
        'profile/<slug:username>/edit/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('', views.index, name='index'),
]
