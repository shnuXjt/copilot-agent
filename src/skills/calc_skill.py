from src.skills.base_skill import BaseSkill
from src.tools import calculator

class CalcSkill(BaseSkill):
    @property
    def tools(self):
        return [calculator]

    @property
    def system_prompt(self):
        return "你是计算专员，只做数学计算"