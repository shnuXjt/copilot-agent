from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class SearchSkill(BaseSkill):

    skill_type="search"

    @property
    def tools(self):
        return [tool_registry.get_tool("duckduckgo_search")]

    @property
    def system_prompt(self):
        return "你是专业搜索专员，只做联网搜索"