from src.tools import calculator
from src.workers.base_worker import BaseWorker


def get_calc_worker():
    worker = BaseWorker(
        tools=[calculator],
        system_prompt="你是计算专员，只做精确数学计算，不编造答案"
    )
    return worker.get_worker()