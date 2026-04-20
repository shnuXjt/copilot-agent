# 感知智能体
from src.manager_agent import rule_based_route


class PerceptAgent:
    """感知层： 意图识别 + 技能路由"""
    def parse(self, user_input: str) -> tuple[str, str, str]:
        # 意图： chat/ tool
        # 技能路由： 复用你现有规则路由
        skill_type = rule_based_route(user_input)
        intent = "tool" if skill_type else "chat"
        return intent, skill_type, user_input