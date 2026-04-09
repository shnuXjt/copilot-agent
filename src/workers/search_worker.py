from src.tools import get_search_tool
from src.workers.base_worker import BaseWorker


def get_search_workder():
    # 仅需：工具 + 专属提示词
    worker = BaseWorker(
        tools=[get_search_tool()],
        system_prompt="你是专业搜索专员，只做联网搜索，返回准确最新信息"
    )
    return worker.get_worker()