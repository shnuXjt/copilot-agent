import  os
from dotenv import load_dotenv

load_dotenv()

# LLM 配置
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")

# Agent 配置
VERBOSE = os.getenv("VERBOSE", "False").lower() == "true"