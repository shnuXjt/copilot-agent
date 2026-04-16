from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class DateTimeSkill(BaseSkill):

    skill_type="datetime"

    @property
    def tools(self):
        return [tool_registry.get_tool("get_current_datetime")]

    @property
    def system_prompt(self):
        return "你是时间查询专员，获取当前日期、时间、星期几"

    @property
    def parameters(self):
        return []