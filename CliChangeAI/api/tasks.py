import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import shared_task
from django.conf import settings
from .models import Subscriber
from .views import fetch_weekly_articles

@shared_task
def send_daily_summary():
    try:
        subscribers = Subscriber.objects.filter(subscribed=True)
        articles = fetch_weekly_articles()  
        
        if not articles:
            return

        message_content = f"Summarize the following articles {articles} in 2-3 sentences for the whole summary. Use plaintext English and simplify where necessary but do not skip important / relevant information to climate change."
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": message_content,
            }],
            model="llama3-8b-8192",
        )
        summary = chat_completion.choices[0].message.content

        subject = "Daily Climate News Summary"
        
        fromaddr = settings.EMAIL_HOST_USER  
        password = settings.EMAIL_HOST_PASSWORD  

        for subscriber in subscribers:
            toaddrs = subscriber.email
            
            msg = MIMEMultipart()
            msg['From'] = fromaddr
            msg['To'] = toaddrs
            msg['Subject'] = subject
            
            body = f"Hello,\n\nHere is your daily climate news summary:\n\n{summary}\n\n" \
                   "If you wish to unsubscribe, please click the following link: " \
                   f"http://yourdomain.com/unsubscribe?email={subscriber.email}\n\n" \
                   "Best regards,\nCli-Change AI Team"
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.ehlo()
                server.starttls()
                server.login('clichangeai', password)
                server.sendmail(fromaddr, toaddrs, msg.as_string())
    except Exception as e:
        print(f"Error sending summary: {e}")
