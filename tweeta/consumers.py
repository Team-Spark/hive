import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import Message, Room, User


class ChatConsumer(WebsocketConsumer):
    def fetch_messages(self, data):
        instance = Message()
        messages = instance.last_messages()
        content = {"command": "messages", "messages": self.messages_to_json(messages)}
        self.send_message(content)

    def new_message(self, data):
        author = data["from"]
        room_name = data["room_name"]
        media_url = data["media_url"]
        author_user = get_object_or_404(User, username=author)
        room = get_object_or_404(Room, room_name=room_name)
        message = Message.objects.create(
            author=author_user, content=data["message"], room=room, media_url=media_url
        )

        content = {"command": "new_message", "message": self.message_to_json(message)}

        return self.send_chat_message(content)

    commands = {
        "fetch_messages": fetch_messages,
        "new_message": new_message,
    }

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            if message.room.room_name == self.room_name:
                result.append(self.message_to_json(message))
        return result[:10]

    def message_to_json(self, message):
        return {
            "author": message.author.username,
            "content": message.content,
            "media_url": message.media_url,
            "timestamp": str(message.timestamp),
        }

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data["command"]](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
