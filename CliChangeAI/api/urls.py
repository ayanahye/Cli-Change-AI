from django.urls import path
from .views import chat_completion_view

urlpatterns = [
    path('chat-completion/', chat_completion_view, name='chat_completion'),
]