from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class TextToVideoSkill(BaseSkill):
    skill_type="text_to_video"

    @property
    def tools(self):
        return [tool_registry.get_tool("text_to_video")]

    @property
    def system_prompt(self):
        return "你是文生视频专家，根据用户的文字描述生成高清视频，返回生成结果"

    @property
    def parameters(self):
        return [{"name": "prompt", "type": "string", "required": True, "desc": "视频提示词"}]