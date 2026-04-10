from src.skills.base_skill import BaseSkill
from src.tools import calculate_math, calculator

class CalcSkill(BaseSkill):

    def __init__(self):
        super().__init__(skill_type="calc", tool_func=calculate_math)

    @property
    def tools(self):
        return [calculator]

    @property
    def system_prompt(self):
        return "你是计算专员，只做数学计算"