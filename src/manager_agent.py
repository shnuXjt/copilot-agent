from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from src.skills.calc_skill import CalcSkill
from src.skills.code_skill import CodeSkill
from src.skills.datetime_skill import DateTimeSkill
from src.skills.excel_skill import ExcelSkill
from src.skills.search_skill import SearchSkill
from src.logger import logger
import json
import re

# 技能池
SKILLS = {
    "search": SearchSkill(),
    "excel": ExcelSkill(),
    "calc": CalcSkill(),
    "code": CodeSkill(),
    "datetime": DateTimeSkill()
}

planner_llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL,
    temperature=0
)
#========================== 核心：LLM自动任务拆解（结构化JSON）=================================

def llm_parse_task(user_task: str) -> list:
    """
    LLM自动拆解用户任务 → 输出有序子任务列表
    返回：[ {"worker": "search", "task": "xxx"}, ... ]
    """
    system_prompt ="""
    你是专业的AI任务规划师，只输出**纯净JSON**，不添加任何多余文字、解释、markdown。

    可用Worker类型（只能选以下4种）：
    - search：联网搜索实时/最新信息
    - excel：读取、分析Excel文件
    - calc：数学计算、求和、求差、乘法等
    - code：执行Python代码处理复杂逻辑
    - datetime：获取当前日期、时间、星期几
    
    拆解规则：
    1. 按执行顺序拆分子任务
    2. 子任务必须依赖前序结果时，要明确写清楚
    3. 不拆分无意义的小任务
    4. 严格输出JSON格式，结构如下：
    {
        "sub_tasks": [
            {"worker": "worker类型", "task": "清晰的子任务描述"},
            ...
        ]
    }
    """
    user_prompt = f"用户任务：{user_task}\n请按规则拆解为有序子任务，只返回JSON"
    # 调用LLM拆解
    response = planner_llm.invoke(f"{system_prompt}\n{user_prompt}")
    raw_content = response.content.strip()

    # 清晰LLM可能带回的'''json标记
    raw_content = re.sub(r'''(json)?''', "", raw_content).strip()

    # 解析JSON
    try:
        task_json = json.loads(raw_content)
        return task_json.get("sub_tasks", [])
    except Exception as e:
        logger.error(f"任务拆解JSON解析失败：{e}，原始内容：{raw_content}")
        return []

# ======================= 任务调度 + 上下文传递 =================================
def execute_worker(worker_type: str, task: str, context: str = ""):
    """执行单个worker， 支持传入前序上下文"""
    if worker_type not in workers:
        return f"❌ 不支持的Worker类型：{worker_type}"
    # 拼接上下文（让后续任务知道前面的结果
    full_task = task
    if context:
        full_task = f"前置任务结果： {context}\n当前任务： {task}"

    logger.info(f"📤 分配任务 → {worker_type}：{full_task}")
    result = workers[worker_type].invoke({"input": full_task})
    return result["output"]

def execute_skill(skill_type: str, task: str, context: str = ""):
    """执行单个Skill， 支持传入谦虚上下文"""
    if skill_type not in SKILLS:
        return f"不支持技能：{skill_type}"
    return SKILLS[skill_type].run(task, context)


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

    # 任务拆解
    sub_tasks = llm_parse_task(task)
    if not sub_tasks:
        return "❌ LLM无法拆解该任务，请换一种描述方式"
    logger.info(f"✅ 任务拆解完成，共 {len(sub_tasks)} 个子任务")

    # 按顺序执行，保存上下文
    task_context = ""
    all_results = []

    for idx, sub in enumerate(sub_tasks, 1) :
        worker_type = sub["worker"]
        task_desc = sub["task"]

        logger.info(f"\n===== 执行第 {idx} 个子任务 | Worker：{worker_type} =====")

        # 执行并携带上下文
        result = execute_skill(worker_type, task_desc, task_context)

        # 保存结果 …& 更新上下文
        all_results.append((f"第（idx)步 【{worker_type}】", task_desc, result))
        task_context = result

    # 汇总结果
    final_summary = llm_summary_result(task, all_results)
    return final_summary

# ========================== LLM最终结果汇总 ====================================
def llm_summary_result(user_task: str, results: list) -> str:

    """LLM把多步执行结果整理成专业，通顺的最总回答"""
    result_text = "\n".join([f"{title}: {content}" for title, _, content in results])
    prompt = f"""
用户原始任务：{user_task}

多智能体执行结果：
{result_text}

请你整合所有结果，给出一份清晰、专业、简洁的最终答案，不要冗余格式。
"""
    summary = planner_llm.invoke(prompt).content
    return f"📌 多Agent协作最终答案\n\n{summary}"