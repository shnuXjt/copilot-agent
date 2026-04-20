# 记忆金字塔
from adapter import legacy_adapter


class MemoryPyramid:
    """四层记忆体系： 瞬时 -> 短期 -> 长期 -> 实体"""
    def __int__(self):
        self.episodic = {} # 瞬时记忆
        self.short = legacy_adapter.memory # 短期记忆
        self.long_term = None # 向量记忆
        self.entity = {} # 实体记忆

    def get_context(self, session_id: str):
        # 标准上下文组合
        return self.short.get_history(session_id)

# 全局单例
memory_system = MemoryPyramid()