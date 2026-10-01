from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from src.tools.time import measure_time
from langchain_google_genai.chat_models import GoogleAPIError
from src.tools.logger import get_logger
import feedparser
import requests
import trafilatura
import time

LOGGER = get_logger("ARTICLE")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

@dataclass
class Article:
    title: str
    url: str
    published_date: datetime
    description: str

@dataclass
class FullArticle:
    title: str
    url: str
    published_date: datetime
    description: str
    content: str

class FetchArticleService:
    def __init__(self, rss_url: str):
        self.rss_url = rss_url

    def fetch_articles(self, headers = HEADERS):

        response = requests.get(
            self.rss_url,
            headers=headers)
        
        feed = feedparser.parse(response.content)

        articles = []

        for entry in feed.entries:
            date_str = entry.get("published")
            published_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z") if date_str else None
            description = entry.get("summary", entry.get("description", ""))
            article = Article(
                title=entry.get("title"),
                url=entry.get("link"),
                published_date=published_date,
                description= description   
            )
            articles.append(article)
        return articles 

class ArticleContentScraper:

    def fetch_articles_content(self, articles: list[Article], max_workers=5) -> list[FullArticle]:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            full_articles = list(executor.map(self.fetch_article_content, articles))
        return full_articles

    def fetch_article_content(self, article: Article) -> FullArticle:
        html_content = trafilatura.fetch_url(article.url)
        clean_content = trafilatura.extract(html_content)
        return FullArticle(
            title=article.title,
            url=article.url,
            published_date=article.published_date,
            description=article.description,
            content=clean_content
        )

class ArticleSummary(BaseModel):
    summary: str = Field(description="Write a short summary of the article")

class ArticleSummarizer:
    def __init__(self, llm):
        self.prompt = PromptTemplate.from_template(
            "You're a professional article summarizer and your task it to make a short summary of a given article: " \
            "Title: {title}\n Content: {content} "
        )
        self.llm = llm

        output_structure = self.llm.with_structured_output(ArticleSummary)
        self.chain = self.prompt | output_structure

    @measure_time
    def summarize_articles(self, articles: list[FullArticle]):
        summary_list = []
        for full_article in articles:
            summary = self.summarize_article(full_article)
            if summary is not None:
                summary_list.append(summary)
        return summary_list
    
    def summarize_article(self, article: FullArticle, max_attempts: int = 3, delay: int = 2) -> ArticleSummary:

        for attempt in range(max_attempts):
            try:
                return self.chain.invoke({
                    'title' : article.title,
                    'content' : article.content
                })
            except GoogleAPIError as e:
                if "503" in str(e) and attempt < max_attempts - 1:
                    LOGGER.error(
                        f"503 - overloaded model."
                        f"Try for {delay}s "
                        f"({attempt + 1}/{max_attempts})"
                    )

                    time.sleep(delay)

                else:
                    LOGGER.error(
                        f"Error while trying to generate summary"
                        f"for article '{article.url}': {e}"
                    )

            except Exception as e:
                LOGGER.error(f"Unexpected error while generating article '{article.url}': {str(e)}")
                break   


        



