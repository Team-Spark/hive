from django.urls import path, include
from . import views

urlpatterns = [
    # path('chats/', views.chats, name='chats'),
    # path('chats/<str:room_name>/', views.room, name='room'),
    path("users/", views.CreateUser.as_view(), name="user_create"),
    path("users/login", views.CustomAuthToken.as_view(), name="login"),
    path(
        "users/confirm_email/<str:uidb64>/<str:token>/", views.activate, name="activate"
    ),
    path(
        "users/reset_password/<str:uidb64>/<str:token>/",
        views.ResetPassword.as_view(),
        name="reset_password",
    ),
    path(
        "users/reset_password/<str:email>/",
        views.send_resetpassword_email,
        name="reset",
    ),
    path(
        "users/resend_email_verification/<str:email>/",
        views.resend_activation_email,
        name="resend",
    ),
    path("user/rooms", views.RoomSet.as_view(), name="rooms"),
    path(
        "user/rooms/<str:room_name>/messages",
        views.MessageSet.as_view(),
        name="messages",
    ),
]
