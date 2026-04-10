from src.skills.base_skill import BaseSkill
from src.tools import get_current_datetime


class DateTimeSkill(BaseSkill):

    def __init__(self):
        super().__init__(skill_type="datetime", tool_func=get_current_datetime)

    @property
    def tools(self):
        return [get_current_datetime]

    @property
    def system_prompt(self):
        return "你是时间查询专员，获取当前日期、时间、星期几"