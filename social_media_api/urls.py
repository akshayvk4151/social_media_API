from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from . import views

app_name = 'social_media_api'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', obtain_auth_token, name='login'),
    path('create-post/', views.create_post, name='create-post'),
    path('posts/', views.post_list, name='post-list'),
    path('post/<int:id>/like/', views.like_post, name='like_post'),
    path('post/<int:id>/dislike/', views.dislike_post, name='dislike_post'),
    path('posts/<int:id>/liked-users/',views.post_liked_users, name='post-liked-users') 
]

