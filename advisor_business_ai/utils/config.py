import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

    # Model Configurations
    MODEL_NAME = "gpt-4.1-nano"
    TEMPERATURE = 0.3

    # LangSmith Configuration
    LANGCHAIN_TRACING_V2 = "true"
    LANGCHAIN_PROJECT = "StartSmart-Business-Advisor"
    LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"

    # File Paths
    OUTPUT_DIR = "outputs"
    TEMPLATES_DIR = "templates"


config = Config()