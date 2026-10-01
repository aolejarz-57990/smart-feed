from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
import os
import json
from src.model_factory import ModelFactory
from src.article import ArticleContentScraper, ArticleSummarizer, ArticleSummary, FetchArticleService



load_dotenv()

API_KEY = os.getenv("API_KEY")

model_factory = ModelFactory(API_KEY)
llm = model_factory.get_google_model("gemini-3.8-flash")

rss_url = "https://www.techrepublic.com/rssfeeds/articles/"

def save_summaries_to_json(summaries :list[ArticleSummary], path: str):
    summary_dict_list = []
    for summary in summaries:
        summary_dict = summary.model_dump()
        summary_dict_list.append(summary_dict)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary_dict_list, f, ensure_ascii=False, indent=4)

    

fetch_article_service = FetchArticleService(rss_url)
articles = fetch_article_service.fetch_articles()
content_scraper = ArticleContentScraper()
full_articles = content_scraper.fetch_articles_content(articles)
article_summarizer = ArticleSummarizer(llm)
summarized_articles = article_summarizer.summarize_articles(full_articles)
save_summaries_to_json(summarized_articles, "output.json")
