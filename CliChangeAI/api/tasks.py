import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from django.conf import settings
from .models import Subscriber
from .views import fetch_weekly_articles
from groq import Groq
import os

API_KEY = os.getenv('API_KEY')
client = Groq(api_key=API_KEY)

@shared_task
def send_daily_summary():
    try:
        subscribers = Subscriber.objects.filter(subscribed=True)
        articles = fetch_weekly_articles() 
        
        if not articles:
            return  
        message_content = "\n".join([f"- {article['title']}: {article['url']}" for article in articles])
    
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Summarize the following articles in 2-3 sentences: {message_content}",
            }],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content

        subject = "Daily Climate News Summary"
        
        for subscriber in subscribers:
            toaddrs = subscriber.email
            
            msg = MIMEMultipart()
            msg['From'] = settings.EMAIL_HOST_USER
            msg['To'] = toaddrs
            msg['Subject'] = subject
            
            article_links = "\n".join([f"{article['title']}: {article['url']}" for article in articles])
            body = f"Hello,\n\nHere is your daily climate news summary:\n\n{summary}\n\n" \
                   "You can find the articles here:\n" \
                   f"{article_links}\n\n" \
                   "If you wish to unsubscribe, please click the following link: " \
                   f"http://yourdomain.com/unsubscribe?email={subscriber.email}\n\n" \
                   "Best regards,\nCli-Change AI Team"
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.send_message(msg)

    except Exception as e:
        print(f"Error sending summary: {e}")