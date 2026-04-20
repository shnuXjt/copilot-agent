# 智能参数提取
import re
import json

from src.manager_agent import main_llm


def extract_params_from_nautral(task_text: str, param_schema: list) -> dict:
    """
    从自然语言李提取技能需要的参数
    """
    if not param_schema:
        return {}

    schema_desc = "\n".join([
        f" - {p['name']}: {p.get('desc', '')} ({p['type']})"
        for p in param_schema
    ])

    prompt = f"""
你是参数提取专家， 只输出干净JSON
任务描述： {task_text}
需要提取的参数：
{schema_desc}

输出JSON格式： {{"{param_schema[0]['name']}"： "..."}}
"""

    try:
        resp = main_llm.invoke(prompt).content.strip()
        resp = re.sub(r"```(json)?|```", "", resp).strip()
        return json.loads(resp)
    except Exception:
        return {}