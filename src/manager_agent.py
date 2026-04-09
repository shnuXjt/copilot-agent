from src.workers.calc_worker import get_calc_worker
from src.workers.code_worker import get_code_worker
from src.workers.excel_worker import get_excel_worker
from src.workers.search_worker import get_search_workder
from src.logger import logger

workers = {
    "search": get_search_workder(),
    "excel": get_excel_worker(),
    "calc": get_calc_worker(),
    "code": get_code_worker()
}

def dispatch_task(worker_type: str, task: str) -> str:
    '''调度器： 分配任务给对应worker'''
    if worker_type not in workers:
        return f"不支持的任务类型： {worker_type}"
    logger.info(f"📤 分配任务至 {worker_type} Worker：{task}")
    result = workers[worker_type].invoke({"input": task})
    return result["output"]

def run_manager_agent(task: str) -> str:
    """
    Manager核心逻辑：
    1. 分析任务
    2. 拆分成子任务
    3. 调度对应Worker执行
    4. 汇总结果
    :param task:
    :return:
    """
    logger.info(f"📋 Manager 接收任务：{task}")
    # ========================== 简易调度规则 ================================
    results = []
    task_lower = task.lower()

    # 1. 需要搜搜
    if any(key in task_lower for key in ["搜索", "最新", "趋势", "新闻", "2026"]):
        res = dispatch_task("search", task)
        results.append(("搜索结果", res))

    # 2. 需要Excel
    if any(key in task_lower for key in ["excel", "表格", "分析", "xlsx", "data/"]):
        res = dispatch_task("excel", task)
        results.append(("Excel分析结果", res))

    # 3. 需要计算
    if any(key in task_lower for key in ["计算", "总和", "平均", "差值", "乘以"]):
        res = dispatch_task("calc", task)
        results.append(("计算结果", res))

    # 4. 需要代码
    if any(key in task_lower for key in ["代码", "python", "编程", "生成"]):
        res = dispatch_task("code", task)
        results.append(("代码执行结果", res))

    # ===================== 汇总输出 =====================
    if not results:
        return "⚠️ 未识别到可执行任务"

    final = "📌 多智能体协作完成\n\n"
    for title, content in results:
        final += f"【{title}】\n{content}\n\n"
    return final