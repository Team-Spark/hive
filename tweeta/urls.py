from django.urls import path, include
from . import views

urlpatterns = [
    path('chats/', views.chats, name='chats'),
    path('chats/<str:room_name>/', views.room, name='room'),
]