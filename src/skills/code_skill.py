from src.skills.base_skill import BaseSkill
from src.tools import get_python_analyze_tool

class CodeSkill(BaseSkill):

    skill_type="code"

    @property
    def tools(self):
        return [get_python_analyze_tool()]

    @property
    def system_prompt(self):
        return "你是代码执行专员，运行Python代码"