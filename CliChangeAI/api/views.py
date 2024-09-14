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
from .models import Subscriber
from django.core.mail import EmailMessage
from django.http import JsonResponse
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from datetime import datetime, timedelta
from .models import Subscriber
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

load_dotenv()

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('SMTP_USERNAME') 
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

API_KEY = os.getenv('API_KEY')

NEWS_API_KEY = os.getenv('NEWS_API_KEY')

client = Groq(
    api_key=API_KEY,
)

@csrf_exempt
def subscribe_to_newsletter(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")

            if email:
                subscriber, created = Subscriber.objects.get_or_create(email=email)
                if created:
                    subject = "Welcome to Daily Climate News"
                    message = "Thank you for subscribing to our daily climate news summary. You'll receive daily updates in your inbox."

                    msg = MIMEMultipart()
                    msg['From'] = SMTP_USERNAME
                    msg['To'] = email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(message, 'plain'))

                    try:
                        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                            server.starttls()
                            server.login(SMTP_USERNAME, SMTP_PASSWORD)
                            server.sendmail(SMTP_USERNAME, email, msg.as_string())
                        return JsonResponse({'success': True, 'message': 'Subscription successful! Daily emails will be sent to you.'})
                    except Exception as e:
                        return JsonResponse({'success': False, 'message': f'Failed to send email: {str(e)}'})
                else:
                    return JsonResponse({'success': False, 'message': 'Email already subscribed.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid email.'})
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'})


def unsubscribe_from_newsletter(request):
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        if email:
            try:
                subscriber = Subscriber.objects.get(email=email)
                subscriber.subscribed = False
                subscriber.save()
                return JsonResponse({'success': True, 'message': 'Unsubscribed successfully.'})
            except Subscriber.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Email not found.'})
        return JsonResponse({'success': False, 'message': 'Invalid email.'})

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

def fetch_weekly_articles():
    today = datetime.today()

    results = []

    for i in range(5):
        date = (today - timedelta(days=i)).strftime('%Y-%m-%d')

        url = f"https://api.thenewsapi.com/v1/news/top"
        params = {
            "language": "en", 
            "api_token": NEWS_API_KEY,
            "search": "climate change | weather",
            "published_on": date,
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            for article in articles:
                results.append({
                    'title': article['title'],
                    'description': article['description'],
                    'url': article['url'],
                    'date': date,
                })
        else:
            raise Exception("Unable to fetch data from news API")
    
    return results

@csrf_exempt
def get_week_summaries(request):
    if request.method == "POST":
        try:
            articles = fetch_weekly_articles()  # Use the helper function
            if not articles:
                return JsonResponse({'success': False, 'error': 'No articles found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    message = f"Summarize the following articles {articles} in 2-3 sentences for the whole summary. Use plaintext English and simplify where necessary but do not skip important / relevant information to climate change. Do not include irrelevant notes just output the summary."
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
            "published_on": date,
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            articles = data.get('data', [])
            for article in articles:
                results.append({
                'title': article['title'],
                'description': article['description'],
                'url': article['url'],
                'date': date,
                })
        else:
            return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)
    json_data = json.dumps(results)
    print(json_data)
    return JsonResponse({"success": True, "summaries": results})
