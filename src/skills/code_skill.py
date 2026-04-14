from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class CodeSkill(BaseSkill):

    skill_type="code"

    @property
    def tools(self):
        return [tool_registry.get_tool("code_analyze")]

    @property
    def system_prompt(self):
        return "你是代码执行专员，运行Python代码"