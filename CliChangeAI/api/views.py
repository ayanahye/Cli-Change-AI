from django.http import JsonResponse
import os
from dotenv import load_dotenv
from groq import Groq
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
from datetime import datetime, timedelta
import json

# Create your views here.

load_dotenv()

API_KEY = os.getenv('API_KEY')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

client = Groq(
    api_key=API_KEY,
)

@csrf_exempt
def chat_completion_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            articles = data.get("articles", [])

            if not articles:
                return JsonResponse({'success': False, 'error': 'No articles provided.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in request body.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    message = f"Summarize the following articles {articles} in 2-3 sentences for the whole summary. Use plaintext English and simplify where necessary but do not skip important / relevant information to climate change. Do not include irrelvant notes just output the summary"
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
def get_week_summaries(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            articles = data.get("articles", [])
            print(articles)

            if not articles:
                return JsonResponse({'success': False, 'error': 'No articles provided.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON in request body.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    message = f"Summarize the following articles {articles} in 2-3 sentences for the whole summary. Use plaintext English and simplify where necessary but do not skip important / relevant information to climate change. Do not include irrelvant notes just output the summary"
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
        print(response)

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
    today = datetime.today().strftime('%Y-%m-%d')

    url = f"https://api.thenewsapi.com/v1/news/top"
    params = {
        "language": "en", 
        "api_token": NEWS_API_KEY,
        "search": "climate change | weather",
        "published_on": today,
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        json_res = json.dumps(data)
        print(json_res)
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)

@csrf_exempt
def get_week_news(request):
    today = datetime.today()

    results = []

    for i in range(5):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')

        url = f"https://api.thenewsapi.com/v1/news/top"
        params = {
            "language": "en", 
            "api_token": NEWS_API_KEY,
            "search": "climate change | weather",
            "published_on": date
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            for article in articles:
                results.append({
                'title': article['title'],
                'description': article['description'],
                'url': article['url']
                })
        else:
            return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)
    json_data = json.dumps(results)
    print(json_data)
    return JsonResponse({"success": True, "summaries": results})
