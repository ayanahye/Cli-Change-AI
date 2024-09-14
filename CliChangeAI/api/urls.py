from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_climate_change_news, name='get_climate_change_news'),  
    path('headlines/', views.get_climate_change_news, name='get_climate_change_news'),
    path('chat-completion/', views.chat_completion_view, name='chat_completion_view'),  
    path('get_week_news/', views.get_week_news, name='get_week_news'),
    path('chat-completion-week/', views.get_week_summaries, name='get_week_summaries'),
]