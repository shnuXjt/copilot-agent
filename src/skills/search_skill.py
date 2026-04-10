from src.skills.base_skill import BaseSkill
from src.tools import get_search_tool

class SearchSkill(BaseSkill):
    @property
    def tools(self):
        return [get_search_tool()]

    @property
    def system_prompt(self):
        return "你是专业搜索专员，只做联网搜索"