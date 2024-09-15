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
from .models import Article, ArticleLike
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

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
    if request.method != "POST":
        return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'})

    try:
        data = json.loads(request.body)
        email = data.get("email")

        if not email:
            return JsonResponse({'success': False, 'message': 'Invalid email.'})

        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if created:
            subscriber.subscribed = True
            subscriber.save()
            message = "Thank you for subscribing to our daily climate news summary. You'll receive daily updates in your inbox."
        else:
            if not subscriber.subscribed:
                subscriber.subscribed = True
                subscriber.save()
                message = "You have been successfully re-subscribed to our daily climate news summary."
            else:
                return JsonResponse({'success': False, 'message': 'Email already subscribed.'})

        articles = fetch_weekly_articles()[:3] 
        
        if articles:
            message_content = "Summary:\n\n"
            for article in articles:
                message_content += f"- {article['title']}: {article['url']}\n"  # Add the link to the article

            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": message_content}],
                model="llama3-8b-8192",
            )
            summary = chat_completion.choices[0].message.content
        else:
            summary = "No articles available today. We'll keep you updated with the latest climate news soon!"

        subject = "Welcome to Daily Climate News"
        body = f"""
Dear Subscriber,

{message}

Here's a brief summary of today's climate news to get you started:

{summary}

You'll receive daily updates like this in your inbox. We hope you find them informative and engaging.

If you wish to unsubscribe at any time, please visit our website and use the unsubscribe option.

Best regards,
Cli-Change AI Team
        """

        msg = MIMEMultipart()
        msg['From'] = settings.EMAIL_HOST_USER
        msg['To'] = email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.send_message(msg)

        return JsonResponse({'success': True, 'message': 'Subscription successful! A welcome email with today\'s summary has been sent to you.'})

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'})
    except smtplib.SMTPException as e:
        return JsonResponse({'success': False, 'message': f'Failed to send email: {str(e)}'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

@csrf_exempt
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
    return JsonResponse({'success': False, 'message': 'Only POST requests are allowed.'})

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
            articles = fetch_weekly_articles()  
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
        print(data)
        articles_data = data.get('data', [])

        articles_response = []


        ip_address = request.META.get('REMOTE_ADDR')
        
        for article_data in articles_data:
            article, created = Article.objects.update_or_create(
                uuid=article_data['uuid'],
                defaults={
                'title': article_data['title'],
                'description': article_data['description'],
                'url': article_data['url'],
                'image_url': article_data['image_url'],
                'published_at': datetime.strptime(article_data['published_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
                }
            )
            
            liked = ArticleLike.objects.filter(article=article, ip_address=ip_address).exists()
            
            articles_response.append({
            'uuid': article.uuid,
            'title': article.title or "No title available",
            'description': article.description or "No description available",
            'url': article.url or "#",
            'image_url': article.image_url or "path/to/default/image.jpg",
            'published_at': article.published_at.isoformat(),
            'likes': article.likes_count,
            'liked': liked
        })

        print(articles_response)
        return JsonResponse({"data": articles_response})
    else:
        return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)

def create_or_update_article(article_data):
    article, created = Article.objects.get_or_create(
        uuid=article_data['uuid'],
        defaults={
            'title': article_data['title'],
            'description': article_data['description'],
            'url': article_data['url'],
            'image_url': article_data.get('image_url', ''),
            'published_at': datetime.strptime(article_data['published_at'], "%Y-%m-%dT%H:%M:%S.%fZ"),
        }
    )
    if not created:
        article.title = article_data['title']
        article.description = article_data['description']
        article.url = article_data['url']
        article.image_url = article_data.get('image_url', '')
        article.published_at = datetime.strptime(article_data['published_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
        article.save()
    return article

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
            for article_data in articles:
                article = create_or_update_article(article_data)
                results.append({
                    'uuid': article.uuid,
                    'title': article.title,
                    'description': article.description,
                    'url': article.url,
                    'date': article.published_at.strftime('%Y-%m-%d'),
                    'likes': article.likes,
                    'liked': ArticleLike.objects.filter(article=article, ip_address=request.META.get('REMOTE_ADDR')).exists()
                })
        else:
            return JsonResponse({"error": "Unable to fetch data"}, status=response.status_code)
    json_data = json.dumps(results)
    print(json_data)
    return JsonResponse({"success": True, "summaries": results})

@csrf_exempt
def like_article(request):
    if request.method == "POST":
        data = json.loads(request.body)
        article_uuid = data.get("uuid")
        ip_address = request.META.get('REMOTE_ADDR')

        try:
            article = Article.objects.get(uuid=article_uuid)
            like, created = ArticleLike.objects.get_or_create(article=article, ip_address=ip_address)

            if created:
                article.likes_count += 1
                liked = True
            else:
                article.likes_count = max(0, article.likes_count - 1)  
                like.delete()
                liked = False

            article.save()

            print(f"Article {article_uuid} liked: {liked}, total likes: {article.likes_count}")

            return JsonResponse({
                "success": True, 
                "likes": article.likes_count,
                "liked": liked,
                "uuid": article_uuid
            })
        except Article.DoesNotExist:
            return JsonResponse({"success": False, "message": "Article not found"})

    return JsonResponse({"success": False, "message": "Invalid request method"})