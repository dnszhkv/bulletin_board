from django.urls import path
# Импортирую представления
from .views import (IndexView, PostList, PostDetail, PostCreate, PostUpdate, PostDelete, PostCategory, ReplyCreate)


urlpatterns = [
   # Вызываю метод as_view.
   path('', IndexView.as_view(), name='account_info'),
   path('posts/', PostList.as_view(), name='post_list'),
   # pk — первичный ключ поста, который будет выводиться в шаблон
   # int — указывает на то, что принимаются только целочисленные значения
   path('posts/<int:pk>/', PostDetail.as_view(), name='post'),
   path('posts/create/', PostCreate.as_view(), name='create'),
   path('posts/<int:pk>/edit/', PostUpdate.as_view(), name='edit'),
   path('posts/<int:pk>/delete/', PostDelete.as_view(), name='delete'),
   path('posts/category/<int:pk>/', PostCategory.as_view(), name='category'),
   path('posts/<int:pk>/reply/', ReplyCreate.as_view(), name='reply'),
]
