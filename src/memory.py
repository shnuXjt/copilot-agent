# 记忆管理器
from langchain_openai import ChatOpenAI

from src.config import MODEL_NAME, MODEL_API_KEY, MODEL_BASE_URL
from src.db import create_session, add_message, get_session_history
from src.logger import logger


SUMMARY_THRESHOLD = 6 # 超过6条历史，触发摘要
RECENT_KEEP = 3 # 永远保留最新3条
SUMMARY_LLM = ChatOpenAI(
    model=MODEL_NAME,
    api_key=MODEL_API_KEY,
    base_url=MODEL_BASE_URL,
    temperature=0,
    max_tokens=300
)
# 摘要缓存（避免重复生成）
_summary_cache = {}


class AgentMemory:
    """全局记忆管理器： 会话管理 + 历史存储 + 上下文构建(只能摘要)"""
    def __init__(self):
        # 默认会话（自动创建）
        self.default_session = create_session()

    def save_user_message(self, session_id: str, content: str):
        add_message(session_id, 'user', content)
        # 新增消息清空对应缓存
        _summary_cache.pop(session_id, None)

    def save_ai_message(self, session_id: str, content: str):
        add_message(session_id, 'ai', content)
        _summary_cache.pop(session_id, None)

    # ===================== 对话摘要生成 =============================
    def _generate_summary(self, session_id: str, history: list) -> str:
        """生成历史对话摘要， 压缩关键信息"""
        if not history:
            return "无历史对话"

        # 缓存命中，直接返回
        if session_id in _summary_cache:
            return _summary_cache[session_id]

        # 构建摘要prompt
        hist_text = "\n".join(f"{r}: {c}" for r, c in history)
        prompt = f"""
请把以下对话压缩成一段简洁的关键信息摘要，只保留核心事实：
- 用户的名字、偏好、关键要求
- 已完成的任务、工具执行结果
- 重要上下文信息
不要冗余描述，尽量短。

对话历史：
{hist_text}

摘要：
"""
        try:
            summary = SUMMARY_LLM.invoke(prompt).content.strip()
            _summary_cache[session_id] = summary
            logger.info(f"✅ 生成对话摘要：{summary[:50]}...")
            return summary
        except Exception as e:
            logger.warning(f"摘要生成失败: {e}")
            return "历史对话较长，已自动压缩"

    def get_history_prompt(self, session_id: str = None, limit: int = 10) -> str:
        """
        升级：
        1. 短对话 → 直接返回全部
        2. 长对话 → 摘要 + 最新3条
        彻底解决Token爆炸+失忆问题
        """
        if not session_id:
            session_id = self.default_session
        # 获取全量历史
        full_history = get_session_history(session_id, limit=20)

        if not full_history:
            return "无历史对话"

        hist_len = len(full_history)
        # 短对话，直接返回
        if hist_len <= SUMMARY_THRESHOLD:
            prompt = "【历史对话】\n"
            for role, content in full_history:
                prompt += f"- {role}: {content}\n"
            return prompt

        # 长对话： 旧消息摘要 + 保留最新3条
        old_history = full_history[:-RECENT_KEEP]
        recent_history = full_history[-RECENT_KEEP:]

        summary = self._generate_summary(session_id, old_history)
        prompt = f"【历史摘要】： {summary}\n【最近对话】\n"
        for role, content in recent_history:
            prompt += f"- {role}: {content}\n"\

        return prompt

# 全局单例
agent_memory = AgentMemory()