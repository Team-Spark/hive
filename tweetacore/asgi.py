"""
ASGI config for tweetacore project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import tweeta.routing as route

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tweetacore.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "https": get_asgi_application(),
    "websocket":AuthMiddlewareStack(
        URLRouter(
            route.websocket_urlpatterns
        )
    )
})

