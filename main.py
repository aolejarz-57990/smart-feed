from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
from model_factory import ModelFactory
import feedparser
import requests

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

model_factory = ModelFactory(API_KEY)
llm = model_factory.get_model("gemini-3.8-flash")

#response = llm.invoke(" Głębsze nakłuwanie skóry występuje w przypadku nano czy mikronakłuwania?")
#print(response.content)

rss_url = "https://www.techrepublic.com/rssfeeds/articles/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
response = requests.get(rss_url, headers=headers)
feed = feedparser.parse(response.content)

for entry in feed.entries:
    print(f"Tytuł: {entry.get('title')}")
    print(f"Link: {entry.get('link')}")
    print(f"Data: {entry.get('published', 'Brak daty')}")
    print(f"Opis: {entry.get('summary', 'Brak opisu')}")
    print("=" * 50)   


print(len(feed.entries))