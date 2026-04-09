from src.tools import get_python_analyze_tool
from src.workers.base_worker import BaseWorker


def get_code_worker():
    worker = BaseWorker(
        tools=[get_python_analyze_tool()],
        system_prompt="你是代码专员，只执行Python代码，输出运行结果"
    )
    return worker.get_worker()