from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

class ModelFactory:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_google_model(self, model_name: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self._api_key
        )
    def get_openai_model(self, model_name: str) -> ChatOpenAI:
        return ChatOpenAI(
            model=model_name,
            api_key=self._api_key
        )