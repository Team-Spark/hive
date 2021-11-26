from django.urls import path, include
from . import views

urlpatterns = [
    # path('chats/', views.chats, name='chats'),
    # path('chats/<str:room_name>/', views.room, name='room'),
    path("auth/registration", views.CreateUser.as_view(), name="user_create"),
    path("auth/login", views.CustomAuthToken.as_view(), name="login"),
    path(
        "auth/confirm_email/<str:uidb64>/<str:token>/", views.activate, name="activate"
    ),
    path(
        "auth/reset_password/<str:uidb64>/<str:token>/",
        views.ResetPassword.as_view(),
        name="reset_password",
    ),
    path(
        "auth/forgot_password/<str:email>/",
        views.send_resetpassword_email,
        name="reset",
    ),
    path(
        "auth/resend_email_verification/<str:email>/",
        views.resend_activation_email,
        name="resend",
    ),
    path("user/rooms", views.RoomSet.as_view(), name="rooms"),
    path(
        "user/rooms/<str:room_name>/messages",
        views.MessageSet.as_view(),
        name="messages",
    ),
    path(
        "user/join-room/<str:uidb64>/",
        views.RoomCreate.as_view({"post": "add_with_link"}),
        name="join-room",
    ),
    path(
        "user/add_users/",
        views.RoomCreate.as_view({"post": "create_private_rooms"}),
        name="join-room",
    ),
]
