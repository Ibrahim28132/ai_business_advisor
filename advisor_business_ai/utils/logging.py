import logging
from langsmith import Client
from utils.config import config

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Initialize LangSmith client
client = Client(
    api_key=config.LANGCHAIN_API_KEY,
    api_url=config.LANGCHAIN_ENDPOINT
)

def log_to_langsmith(run_id, inputs, outputs, metadata=None):
    try:
        client.create_feedback(
            run_id=run_id,
            key="user_feedback",
            score=1.0,
            comment="Automatic logging from system",
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Failed to log to LangSmith: {e}")