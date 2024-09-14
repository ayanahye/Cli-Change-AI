from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_climate_change_news, name='get_climate_change_news'),  
    path('headlines/', views.get_climate_change_news, name='get_climate_change_news'),
    path('chat-completion/', views.chat_completion_view, name='chat_completion_view'),  
]