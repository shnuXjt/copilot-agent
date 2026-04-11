# 记忆管理器
from src.db import create_session, add_message, get_session_history


class AgentMemory:
    """全局记忆管理器： 会话管理 + 历史存储 + 上下文构建"""
    def __init__(self):
        # 默认会话（自动创建）
        self.default_session = create_session()

    def save_user_message(self, session_id: str, content: str):
        add_message(session_id, 'user', content)

    def save_ai_message(self, session_id: str, content: str):
        add_message(session_id, 'ai', content)

    def get_history_prompt(self, session_id: str = None, limit: int = 10) -> str:
        """
        把历史对话转换成LLM能看懂的提示词
        自动注入到任务中，实现记忆功能
        """
        if not session_id:
            session_id = self.default_session

        history = get_session_history(session_id, limit)

        if not history:
            return "无历史对话"
        prompt = "【历史对话】：\n"
        for role, content in history:
            prompt += f"- {role}: {content}\n"
        return prompt

# 全局单例
agent_memory = AgentMemory()