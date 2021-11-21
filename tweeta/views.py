from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json
from django.utils.safestring import mark_safe

def chats(request):
    return render(request, 'chats.html')


@login_required
def room(request, room_name):
    return render(request, 'chat.html', {
        'room_name': mark_safe(json.dumps(room_name)) , 
        "username": mark_safe(json.dumps(request.user.username))

    })
