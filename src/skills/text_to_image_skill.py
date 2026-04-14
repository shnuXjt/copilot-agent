from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class TextToImageSkill(BaseSkill):
    skill_type="text_to_image"

    @property
    def tools(self):
        return [tool_registry.get_tool("text_to_image")]

    @property
    def system_prompt(self):
        return "你是文生图专家，根据用户的文字描述生成高质量图片，返回生成结果"