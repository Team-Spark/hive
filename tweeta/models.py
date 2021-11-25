from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models.deletion import CASCADE
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=timezone.now, editable=False)
    modified = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    first_name = models.CharField(max_length=50, verbose_name=None)
    last_name = models.CharField(max_length=50, verbose_name=None)
    phone = PhoneNumberField(null=True, blank=True, unique=True, verbose_name=None)
    email = models.EmailField(max_length=254, unique=True, verbose_name=None)
    location = models.CharField(max_length=300, verbose_name=None)
    username = models.CharField(max_length=100, unique=True)
    image_url = models.CharField(max_length=700, default="")
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "username"]


class Room(BaseModel):
    room_name = models.CharField(max_length=30, unique=True)
    created_by = models.ForeignKey(
        User, related_name="room_creator", on_delete=models.CASCADE
    )
    room_logo_url = models.CharField(max_length=700, default="")
    is_private = models.BooleanField(default=False)
    members = models.ManyToManyField(User, related_name="room_members", blank=True)

    def clean(self):
        if self.name:
            self.name = self.name.replace(" ", "-")

    def __str__(self):
        return self.name


class Message(BaseModel):
    room = models.ForeignKey(Room, related_name="message", on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name="author_messages", on_delete=CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    media_url = models.CharField(max_length=700)

    def __str__(self):
        return self.content

    def last_messages(self):
        return reversed(Message.objects.order_by("-timestamp"))

    @property
    def get_author_username(self):
        return self.author.username
