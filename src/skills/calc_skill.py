from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class CalcSkill(BaseSkill):

    skill_type="calc"

    @property
    def tools(self):
        return [tool_registry.get_tool("calculator")]

    @property
    def system_prompt(self):
        return "你是计算专员，只做数学计算"