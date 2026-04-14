from venv import logger

from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from src.logger import logger

# =========================== 自检配置 =================================
CHECK_CONFIG = {
    # 格式：skill_type: 是否开启工具回检
    "calc": True,
    "datetime": True,
    "text_to_image": False,    # 图片生成关闭严格自检
    "text_to_video": False,    # 视频生成关闭严格自检
    "chat": False,
    "search": False,
    "excel": False,
    "code": False
}

# 无需工具回检的技能，默认通过
DEFAULT_PASS_SKILLS = ["chat", "search", "excel", "code"]

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

        # 自检策略注册器（字典存储）
        self._check_strategies = {}
        # 自动注册所有技能的自检策略
        self._register_default_strategies()

    # 策略注册机制
    def _register_default_strategies(self):
        """注册所有内置技能的自检逻辑"""
        self.register_check_strategy("calc", self._check_calc)
        self.register_check_strategy("datetime", self._check_datetime)
        self.register_check_strategy("text_to_image", self._check_text_to_image)
        self.register_check_strategy("text_to_video", self._check_text_to_video)

    def register_check_strategy(self, skill_type: str, check_func):
        """外部注册新技能自检"""
        self._check_strategies[skill_type] = check_func

    # ======================= 🔥 每个技能自检 = 独立函数（无耦合） ==============================
    def _check_calc(self, task: str, llm_result: str) -> tuple[bool, str]:
        """计算器专属自检"""
        from src.tools import extract_math_expression, calculate_math
        expr = extract_math_expression(task)
        true_val = calculate_math(expr)
        if "错误" in true_val:
            return False, f"计算无效：{expr}"
        if true_val in llm_result:
            return True, f"计算结果正确：{true_val}"
        return False, f"计算结果不匹配：真值={true_val}"

    def _check_datetime(self, task: str, llm_result: str) -> tuple[bool, str]:
        """日期时间专属自检（宽松匹配）"""
        import re
        from src.tools import get_current_datetime_raw
        true_str = get_current_datetime_raw()

        date_pattern = r"(\d{4}年\d{2}月\d{2}日)"
        week_pattern = r"星期([一二三四五六日])"

        true_date = re.search(date_pattern, true_str)
        true_week = re.search(week_pattern, true_str)

        if not true_date or not true_week:
            return True, "日期格式无需严格校验"

        true_date = true_date.group(1)
        true_week = true_week.group(1)

        has_date = true_date in llm_result
        has_week = f"星期{true_week}" in llm_result

        if has_date and has_week:
            return True, f"日期校验通过：{true_date} 星期{true_week}"
        return False, f"日期或星期错误：真值={true_date} 星期{true_week}"

    def _check_text_to_image(self, task: str, llm_result: str) -> tuple[bool, str]:
        """文生图自检"""
        if "✅" in llm_result and any(keyword in llm_result for keyword in task.split()[:5]):
            return True, "图片生成校验通过"
        return False, "图片生成失败或信息不匹配"

    def _check_text_to_video(self, task: str, llm_result: str) -> tuple[bool, str]:
        """文生视频自检"""
        if "✅" in llm_result and any(keyword in llm_result for keyword in task.split()[:5]):
            return True, "视频生成校验通过"
        return False, "视频生成失败或信息不匹配"

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
    def tool_recheck(self, skill_type: str, task: str, result: str) -> tuple[bool, str]:
        # 🔥 按配置开关：关闭则直接通过
        if not CHECK_CONFIG.get(skill_type, False):
            return True, "该技能已关闭工具回检"
        """
        工具回检： 直接调用原始Tool重新计算/查询，对比结果
        仅用于 calc/datetime 等精准工具
        """
        try:
            # 查表获取自检函数
            check_func = self._check_strategies.get(skill_type)
            if check_func:
                return check_func(task, result)

            # 无自检策略的技能（如chat/search/excel）直接通过
            return True, "无需工具回检"
        except Exception as e:
            return False, f"回检异常：{str(e)}"

    # ====================== 总校验入口 ================================
    def full_check(self, skill_type: str, task: str, result: str) -> tuple[bool, str]:
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
        pass_tool, msg = self.tool_recheck(skill_type, task, result)
        if not pass_tool:
            logger.warning(f"工具回检失败: {msg}")
            return False, msg

        logger.info("✅ 自检全部通过")
        return True, "自检通过"

# 全局单例（全项目复用)
self_checker = SelfChecker()