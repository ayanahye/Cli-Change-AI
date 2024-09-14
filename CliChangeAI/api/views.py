from django.http import JsonResponse
import os
from dotenv import load_dotenv
from groq import Groq
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests

# Create your views here.

load_dotenv()

API_KEY = os.getenv('API_KEY')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

client = Groq(
    api_key=API_KEY,
)

@csrf_exempt
def chat_completion_view(request):
    message = "Explain climate change"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            model="llama3-8b-8192",
        )
        response = chat_completion.choices[0].message.content

        return JsonResponse({
            'success': True,
            'response': response,
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
        })

@csrf_exempt
def get_climate_change_news(request):
    url = f"https://api.thenewsapi.com/v1/news/headlines"
    params = {
        "locale": "us",
        "language": "en", 
        "api_token": NEWS_API_KEY,
        "search": "climate+change",
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)
