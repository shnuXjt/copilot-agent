from src.skills.base_skill import BaseSkill
from src.tools import get_text_to_video_tool

class TextToVideoSkill(BaseSkill):
    def __init__(self):
        super().__init__(skill_type="text_to_video")

    @property
    def tools(self):
        return [get_text_to_video_tool()]

    @property
    def system_prompt(self):
        return "你是文生视频专家，根据用户的文字描述生成高清视频，返回生成结果"