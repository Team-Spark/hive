from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
import json
from django.utils.safestring import mark_safe
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema


from .serializers import (
    FriendsSerializer,
    MessageSerializer,
    ResetPasswordSerializer,
    RoomSerializer,
    UserSerializer,
)
from .models import Message, User, Room

from rest_framework import serializers, status, permissions
from django.utils.encoding import force_text, force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .token import account_activation_token
from django.template.loader import render_to_string


# def chats(request):
#     return render(request, "chats.html")


# @login_required
# def room(request, room_name):
#     return render(
#         request,
#         "chat.html",
#         {
#             "room_name": mark_safe(json.dumps(room_name)),
#             "username": mark_safe(json.dumps(request.user.username)),
#         },
#     )


class RoomSet(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = RoomSerializer
    model = Room

    def post(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        instance = Room.objects.create(
            created_by=user,
            room_name=data["room_name"],
            room_logo_url=data["room_logo_url"],
        )
        instance.save()
        instance.members.add(user)
        return Response(
            {"message": "Room Created Successfully"}, status=status.HTTP_201_CREATED
        )

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.pk)
        user_rooms = Room.objects.filter(members=user)
        serializer = RoomSerializer(user_rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RoomCreate(ViewSet):
    permission_classes = (IsAuthenticated,)

    def create_private_rooms(self, request):
        serializer = FriendsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        my_sweet_response = {}
        for friend in serializer.data:
            try:
                user = get_object_or_404(User, pk=request.user.pk)
                friend = get_object_or_404(User, username=friend)
                instance = Room.objects.create(
                    created_by=user,
                    room_name=f"{user.username} " + f"{friend.username}",
                    room_logo_url=f"{friend.image_url}",
                )
                instance.is_private = True
                instance.save()
                instance.members.add(user, friend)
                my_sweet_response[friend] = "Added Successfully"
            except Exception as e:
                my_sweet_response[friend] = f"{e}"
        return Response({"message": my_sweet_response}, status=status.HTTP_200_OK)


class MessageSet(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MessageSerializer

    def get(self, request, room_name):
        room = get_object_or_404(Room, room_name=room_name)
        messages = Message.objects.filter(room=room)
        serializer = self.serializer_class(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateUser(CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, format="json"):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            if user:
                token = Token.objects.create(user=user)
                json = serializer.data
                json["token"] = token

                current_site = get_current_site(request)
                subject = "Please Activate Your Account"
                message = render_to_string(
                    "activation_request.html",
                    {
                        "user": user,
                        "domain": current_site.domain,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": account_activation_token.make_token(user),
                    },
                )
                user.email_user(subject, message)
                return Response(
                    {"message": "User created Succesfully, Check email to confirm"},
                    status=status.HTTP_201_CREATED,
                )

        return Response(
            {"message": f"{serializer.errors}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "data": {
                        "token": token.key,
                        "user": {
                            "user_id": user.pk,
                            "email": user.email,
                            "full_name": f"{user.first_name} {user.last_name}",
                        },
                    },
                    "message": "login successful",
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.signup_confirmation = True
        user.save()
        return Response(
            {"message": "activation successfull"}, status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"message": "activation failed"}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["GET"])
def resend_activation_email(request, email):
    try:
        user = User.objects.get(email=email)
        if user.is_active != True:
            current_site = get_current_site(request)
            subject = "Please Activate Your Account"
            message = render_to_string(
                "activation_request.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            user.email_user(subject, message)
            return Response(
                {"message": "Activation Email Sent"}, status=status.HTTP_201_CREATED
            )
        return Response(
            {"message": "user is already active"}, status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response({"message": f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def send_resetpassword_email(request, email):
    user = User.objects.get(email=email)
    if user.is_active == True:
        current_site = get_current_site(request)
        subject = "Please Reset your password"
        message = render_to_string(
            "reset_password_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(subject, message)
        return Response(
            {"message": "Reset Password Email Sent"}, status=status.HTTP_201_CREATED
        )
    return Response(
        {"message": "user is not active"}, status=status.HTTP_400_BAD_REQUEST
    )


class ResetPassword(APIView):
    serializer_class = ResetPasswordSerializer

    def put(self, request, uidb64, token):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                user.set_password(request.data.get("password"))
                user.save()
                return Response(
                    {"message": "Password Reset Successfull"}, status=status.HTTP_200_OK
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {"message": "Password Reset Failed"}, status=status.HTTP_400_BAD_REQUEST
            )
