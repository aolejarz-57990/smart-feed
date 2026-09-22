from langchain_google_genai import ChatGoogleGenerativeAI

class ModelFactory:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def get_model(self, model_name: str) -> ChatGoogleGenerativeAI:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self._api_key
        )