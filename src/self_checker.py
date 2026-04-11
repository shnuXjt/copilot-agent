from venv import logger

from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from src.logger import logger
from src.tools import extract_math_expression
import re


class SelfChecker:
    """
    三级自检引擎： 规则校验 -> LLM智能校验 -> 工具回检
    自动校验结果正确性，失败自动重试
    """
    def __init__(self):
        # 校验用LLM（轻量，低延迟）
        # 这里可以用另一个模型, 更加轻量，更加低延迟的
        self.check_llm = ChatOpenAI(
            model=MODEL_NAME,
            api_key=MODEL_API_KEY,
            base_url=MODEL_BASE_URL,
            temperature=0
        )
        # 最大重试次数
        self.max_retry = 2

    # ============================ 1. 规则校验 ==============================
    def rule_check(self, skill_type: str, task: str, result: str) -> tuple[bool, str]:
        """
        基础规则校验： 根据技能类型做快速校验
        返回：(是否通过， 错误信息)
        """
        try:
            # 计算技能： 检查是否包含数字，无明显错误
            if skill_type == 'calc':
                if any(word in result for word in ["错误", "未知", "未找到"]):
                    return False, "计算结果包含错误标识"
                if not any(c.isdigit() for c in result):
                    return False, "计算结果有无效数字"
            # 时间技能： 检查是否包含年月日
            if skill_type == 'datetime':
                if "年" not in result or "月" not in result or "日" not in result:
                    return False, "时间格式错误"

            # Excel技能: 检查是否包含数据结论
            if skill_type == "excel":
                if len(result) < 20:
                    return False, "数据分析结果过短， 无有效信息"
            return True, "校验通过"
        except:
            return False, "规则校验异常"

    # ============================ 2. LLM 智能体校验（核心，自我审查) ==================================
    def llm_check(self, skill_type: str, task: str, result: str) -> tuple[bool, str]:
        """
        LLM 二次审查： 判断结果是否正确， 是否符合任务要求，是否编造
        只做三件事， 不要质疑客观工具真值
        1. 是否答非所问
        2. 是否明显胡编/无意义
        3. 是否包含错误标识（错误，未知，未找到）
        """
        # 对日期，计算类精准技能，只做轻校验，不挑战真值
        if skill_type in ["datetime", "calc"]:
            if any(word in result for word in ["错误", "未知", "无法"]):
                return False, "结果包含错误标识"
            if len(result.strip()) < 5:
                return False, "结果过短， 无有效信息"
            return True, "校验通过（精准技能豁免深度校验）"
        # 聊天，搜索， Excel： 正常做合理性校验

        prompt = f"""
任务：{task}
AI回答：{result}

只判断2点，输出格式：是/否 | 原因
1. 是否答非所问/完全跑题
2. 是否明显编造内容、无依据
"""
        check_result = self.check_llm.invoke(prompt).content.strip()
        is_pass = check_result.startswith("是")
        return is_pass, check_result

    # ========================= 3. 工具回检（最高精度，用原工具验证） ======================================
    def tool_recheck(self, skill_type: str, task: str, result: str, tool_func) -> tuple[bool, str]:
        """
        工具回检： 直接调用原始Tool重新计算/查询，对比结果
        仅用于 calc/datetime 等精准工具
        """
        # 正则提取：日期（2026年04月11日）+ 星期（六/日...)
        date_pattern = r"(\d{4}年\d{2}月\d{2}日)"
        week_pattern = r"星期([一二三四五六日])"

        if skill_type not in ["calc", "datetime"]:
            return True, "无需工具回检"

        try:
            expr = extract_math_expression(task) if skill_type == "calc" else task
            tool_result = tool_func() if skill_type == "datetime" else tool_func(expr)
            if skill_type == "datetime":
                true_date = re.search(date_pattern, tool_result)
                true_week = re.search(week_pattern, tool_result)
            if true_date if skill_type == "datetime" else tool_result in result:
                return True, f"工具回检通过，真值={tool_result}"
            else:
                return False, f"工具回检结果不匹配！工具真值={tool_result}，LLM返回={result}"
        except Exception as e:
            return False, f"工具回检失败： {str(e)}"

    # ====================== 总校验入口 ================================
    def full_check(self, skill_type: str, task: str, result: str, tool_func=None) -> tuple[bool, str]:
        """三级全量检查"""
        logger.info(f"🔍 开始自检 | 技能：{skill_type}")

        # 1. 规则校验
        pass_rule, msg = self.rule_check(skill_type, task, result)
        if not pass_rule:
            logger.warning(f"规则校验失败： {msg}")
            return False, msg

        # 2. LLM 只能校验
        pass_llm, msg = self.llm_check(skill_type, task, result)
        if not pass_llm:
            logger.warning(f"LLM 校验失败： {msg}")
            return  False, msg

        # 3. 工具回检（精准技能）
        pass_tool, msg = self.tool_recheck(skill_type, task, result, tool_func)
        if not pass_tool:
            logger.warning(f"工具回检失败: {msg}")
            return False, msg

        logger.info("✅ 自检全部通过")
        return True, "自检通过"

# 全局单例（全项目复用)
self_checker = SelfChecker()