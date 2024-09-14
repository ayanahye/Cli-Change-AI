from django.http import JsonResponse
import os
from dotenv import load_dotenv
from groq import Groq

# Create your views here.

load_dotenv()

API_KEY = os.getenv('API_KEY')

client = Groq(
    api_key=API_KEY,
)

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
