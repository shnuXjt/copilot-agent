from langchain_experimental.llms.anthropic_functions import prompt
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from src.memory import agent_memory
from src.skills.calc_skill import CalcSkill
from src.skills.code_skill import CodeSkill
from src.skills.datetime_skill import DateTimeSkill
from src.skills.excel_skill import ExcelSkill
from src.skills.search_skill import SearchSkill
from src.logger import logger
import json
import re

from src.skills.text_to_image_skill import TextToImageSkill
from src.skills.text_to_video_skill import TextToVideoSkill

# 技能池
SKILLS = {
    "search": SearchSkill(),
    "excel": ExcelSkill(),
    "calc": CalcSkill(),
    "code": CodeSkill(),
    "datetime": DateTimeSkill(),
    "text_to_image": TextToImageSkill(),    # 文生图
    "text_to_video": TextToVideoSkill()     # 文生视频
}

SKILL_KEYWORD_MAP = {
    "calc": ["计算", "多少", "加减", "乘除", "等于", "求和", "差值", "天数"],
    "datetime": ["今天", "日期", "时间", "星期", "几号", "几点"],
    "text_to_image": ["画", "生成图", "图片", "插画", "设计", "壁纸"],
    "text_to_video": ["视频", "生成视频", "短片", "动画"],
    "excel": ["excel", "表格", "xlsx", "xls", "销售额", "数据"],
    "search": ["搜索", "查一下", "最新", "新闻", "信息"]
}

def rule_based_route(user_query: str) -> str | None:
    """
    规则路由：关键词硬匹配，LLM 判断错时兜底
    返回：skill_type 或 None
    """
    query = user_query.lower()
    for skill_type, keywords in SKILL_KEYWORD_MAP.items():
        for kw in keywords:
            if kw in query:
                return skill_type
    return None

planner_llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL,
    temperature=0
)
#========================== 核心：LLM自动任务拆解（结构化JSON）=================================
# 升级： 增加 重试 + 校验
def llm_parse_task(user_task: str, retry: int = 1) -> list:
    """
    LLM自动拆解用户任务 → 输出有序子任务列表
    返回：[ {"worker": "search", "task": "xxx"}, ... ]
    """
    system_prompt ="""
    你是专业的AI任务规划师，只输出**纯净JSON**，不添加任何多余文字、解释、markdown。

    可用Skill类型：
    - search：联网搜索实时/最新信息
    - excel：读取、分析Excel文件
    - calc：数学计算、求和、求差、乘法等
    - code：执行Python代码处理复杂逻辑
    - datetime：获取当前日期、时间、星期几
    - text_to_image: 文生图
    - text_to_video：文生视频
    
    拆解规则：
    1. 按执行顺序拆分子任务
    2. 子任务必须依赖前序结果时，要明确写清楚
    3. 不拆分无意义的小任务
    4. 严格输出JSON格式，结构如下：
    {
        "sub_tasks": [
            {"skill": "skill类型", "task": "清晰的子任务描述"},
            ...
        ]
    }
    """
    user_prompt = f"用户任务：{user_task}\n请按规则拆解为有序子任务，只返回JSON"
    # 调用LLM拆解
    response = planner_llm.invoke(f"{system_prompt}\n{user_prompt}")
    raw_content = response.content.strip()

    # 清晰LLM可能带回的'''json标记
    raw_content = re.sub(r"```.+?", "", raw_content).strip()

    # 解析JSON
    try:
        task_json = json.loads(raw_content)
        sub_tasks = task_json.get("sub_tasks", [])
        # 校验过滤无效任务
        return validate_sub_tasks(sub_tasks)
    except Exception as e:
        # 拆解失败自动重试1次
        if retry > 0:
            return llm_parse_task(user_task, retry -1)
        # 重试失败 -> 规则兜底尝试生成1个任务
        fallback_skill = rule_based_route(user_task)
        return [{"skill": fallback_skill, "task": user_task}] if fallback_skill else []

# ======================= 任务调度 + 上下文传递 =================================
def execute_skill(skill_type: str, task: str, context: str = "", session_id: str=None):
    """执行单个Skill， 支持传入谦虚上下文"""
    if skill_type not in SKILLS:
        return f"不支持技能：{skill_type}"
    return SKILLS[skill_type].run(task, context, session_id)


def run_manager_agent(task: str, session_id: str=None) -> str:
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
    # 保存用户问题到记忆
    agent_memory.save_user_message(session_id, task)

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
        result = execute_skill(worker_type, task_desc, task_context, session_id)

        # 保存结果 …& 更新上下文
        all_results.append((f"第（idx)步 【{worker_type}】", task_desc, result))
        task_context = result

    # 汇总结果
    final_summary = llm_summary_result(task, all_results)

    # 保存ai回答到记忆
    agent_memory.save_ai_message(session_id, final_summary)
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

# ================= 保留正常的大模型对话能力， 在对话中需要用到工具的时候才调用skill ========================

# 路由LLM： 只做一件事 -> 判断要不要调用工具，调用哪个
# 主LLM：对话+任务拆解
main_llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL,
    temperature=0
)
# LLM来判断是否调用工具
def should_use_tool(user_query: str, history: str) -> dict:
    """
    LLM 自主判断：
    1. 是否需要调用工具
    2. 需要调用哪个工具
    3. 提取工具执行的真实任务
    """
    prompt = f"""
【历史对话】
{history}

【用户问题】
{user_query}

请判断： 用户是否需要调用以下工具？
    - search：联网搜索、最新信息、新闻、数据
    - calc：数学计算、加减乘除、求和、平均值
    - datetime：当前日期、时间、星期几
    - excel：分析Excel文件、表格数据
    - code：执行Python代码

输出规则：
1. 不需要工具 -> 输出 {{”need_tool": false, "skill": "", "task": ""}}
2. 需要工具 -> 输出 {{“need_tool": true, "skill": "工具名", "task": "纯工具执行任务"}}
只输出JSON： 不要任何其他文字
"""
    res = main_llm.invoke(prompt).content.strip()
    res = re.sub(r"```(json)?", "", res).strip()
    try:
        return json.loads(res)
    except:
        return {"need_tool": False, "skill": "", "task": ""}


# 对话入口
def chat_with_agent(user_input: str, session_id: str=None):
    # 1. 保存用户消息
    agent_memory.save_user_message(session_id, user_input)
    # 2. 获取对话记忆
    history = agent_memory.get_history_prompt(session_id)

    # 3. 分类： 直接聊 / 复杂任务
    task_type = classify_task(user_input, history)

    if task_type == "chat":
        # 简单任务 - 正常大模型对话
        prompt = f"{history}\n用户： {user_input}\n请自然回答"
        final = main_llm.invoke(prompt).content
    else:
        # 复杂任务
        sub_tasks = llm_parse_task(user_input)
        tool_result = run_complex_task(sub_tasks, session_id)
        # LLM整理成自然语言
        final_prompt = f"""
        【历史对话】{history}
        【用户问题】{user_input}
        【工具结果】{tool_result}
        请根据工具结果，自然、简洁地回答用户，不要格式、不要标注。
        """
        final = main_llm.invoke(final_prompt).content


    # 5. 保存AI回答
    agent_memory.save_ai_message(session_id, final)
    return final


# ============= 简单任务和复杂任务需要区分，复杂任务需要拆解 ====================
"""
用户输入
   ↓
1. 简单闲聊 → 直接LLM回答（正常对话）
2. 复杂任务 → LLM拆解多步 → 依次调用Skill → 汇总结果
"""

# 判断: 闲聊/复杂任务
# 升级： 规则优先，LLM辅助
def classify_task(user_query: str, history: str) -> str:
    # 🔥 规则兜底：命中工具关键词 → 直接判定复杂任务
    if rule_based_route(user_query):
        return "complex"

    """判断任务类型： chat(直接聊) / complex(需拆解）"""
    prompt = f"""
历史对话： {history}
用户问题：{user_query}
判断： 只需回答 chat 或 complex
- chat: 日常聊天，问候，无工具需求
- complex： 需要工具，多步计算，查日期 + 计算， 搜索 + 分析等复合任务
"""
    return main_llm.invoke(prompt).content.strip().lower()

# 复杂任务： LLM自动拆解多步, 见函数： llm_parse_task

# 执行多步任务
def run_complex_task(sub_tasks: list, session_id: str) -> str:
    # 无有效任务直接返回空
    if not sub_tasks:
        return "未识别可执行任务"

    context = ""
    for idx, sub in enumerate(sub_tasks):
        skill_name = sub["skill"]
        task = sub["task"]
        if skill_name not in SKILLS:
            continue
        logger.info(f"▶ 执行第{idx+1}步：{skill_name} | {task}")
        try:
            # 带上下文 + 记忆执行skill
            res = SKILLS[skill_name].run(task=task, context=context, session_id=session_id)
            context = f"第{idx+1}步结果： {res}"
        except Exception as e:
            context = f"第{idx+1}步执行失败：{str(e)}"
    return context


# ============================================================
# 子任务拆解校验
def validate_sub_tasks(sub_tasks: list) -> list:
    """
    【新增】校验拆解结果：
    1. 移除skill不存在的任务
    2. 空任务自动过滤
    3. 保证至少有有效任务
    """
    valid = []
    for st in sub_tasks:
        skill = st.get("skill")
        task = st.get("task")
        if skill in SKILLS and task and len(task.strip()) > 1:
            valid.append(st)
    return valid
