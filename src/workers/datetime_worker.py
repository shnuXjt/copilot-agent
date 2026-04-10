from src.tools import get_datetime_tool
from src.workers.base_worker import BaseWorker


def get_datetime_worker():
    worker = BaseWorker(
        tools=[get_datetime_tool()],
        system_prompt="你是时间查询专员，只负责查询当前日期、时间、星期几"
    )
    return worker.get_worker()