from core.brain.specialists.base_specialist import BaseSpecialist
from src.manager_agent import main_llm


class ChatSpecialist(BaseSpecialist):
    name = "chat"
    description = "日常对话助手"

    def run(self, task: str, session_id: str, context:str = "") -> str:
        prompt = f"上下文： {context} \n用户：{task}\n助手: "
        return main_llm.invoke(prompt).content.strip()