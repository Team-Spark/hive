from rest_framework import fields, serializers, status
from djoser.serializers import (
    UserCreateSerializer,
    UserCreatePasswordRetypeSerializer,
)
from .models import Message, Room, User


class UserSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "location",
            "username",
            "password",
        ]


class ResetPasswordSerializer(UserCreatePasswordRetypeSerializer):
    class Meta:
        model = User
        fields = ["password"]


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["room_name", "room_logo_url"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["author", "content", "media_url", "timestamp", "room"]


class FriendsSerializer(serializers.Serializer):
    usernames = serializers.ListField()

    class Meta:
        fields = ["usernames"]
