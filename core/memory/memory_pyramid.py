# 记忆金字塔
from adapter import legacy_adapter
from core.memory.vector_memory import vector_memory


class MemoryPyramid:
    """四层记忆体系： 瞬时 -> 短期 -> 长期 -> 实体"""
    def __init__(self):
        self.episodic = {} # 瞬时记忆
        self.short = legacy_adapter.memory # 短期记忆
        self.long_term = vector_memory # 向量记忆
        self.entity = {} # 实体记忆

    def get_context(self, session_id: str):
        # 标准上下文组合
        return self.short.get_history(session_id)

    def get_full_context(self, session_id: str, query: str):
        """获取上下文， 仅返回有效不报错的历史"""
        short = self.short.get_history_prompt(session_id)
        long_ctx = self.long_term.query(session_id, query)
        return f"长期记忆： {long_ctx}\n 近期对话： {short}"

    def remember(self, session_id: str, text: str):
        self.long_term.add(session_id, text)

# 全局单例
memory_system = MemoryPyramid()