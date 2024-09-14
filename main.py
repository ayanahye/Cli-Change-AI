import os
from dotenv import load_dotenv

load_dotenv()

from groq import Groq

API_KEY = os.getenv('API_KEY')

client = Groq(
    api_key=API_KEY,
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain climate change",
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)

#masongu2019

# Climate Change news 
# llm summarize 
# sign up for a newsletter or get access to it on the website itself

# https://newsapi.org/