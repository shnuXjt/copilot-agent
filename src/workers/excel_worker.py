from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL, VERBOSE
from src.tools import get_excel_reader_tool
from src.workers.base_worker import BaseWorker


def get_excel_worker():
    worker = BaseWorker(
        tools=[get_excel_reader_tool()],
        system_prompt="你是Excel专员，只读取分析Excel，输出专业数据结论"
    )
    return worker.get_worker()