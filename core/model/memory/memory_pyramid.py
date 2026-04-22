from core.protocol.adapter.legacy_adapter import legacy_adapter
from config_loader import config_loader

# 从配置读取记忆开关
memory_config = config_loader.model_config["memory"]

class MemoryPyramid:
    """记忆金字塔： 配置化启用/禁用短期/长期记忆"""
    def __init__(self):
        # 配置化启用短期记忆
        self.short_memory = legacy_adapter.memory if memory_config["short_memory"]["enabled"] else None
        # 配置化启用长期记忆
        # self.long_memory = vector_memory if memory_config["long_memory"]["enabled"] else None
        self.long_memory = None

    def get_full_context(self, session_id: str, query: str = ""):
        """获取完整上下文，根据配置决定是否启用长期/短期记忆"""
        short_ctx = self.short_memory.get_history_prompt(session_id) if self.short_memory else ""
        long_ctx = self.long_memory.query(session_id, query) if self.long_memory else ""
        return f"【长期记忆】\n{long_ctx}\n\n【近期对话】\n{short_ctx}"

    def remember(self, session_id: str, text: str):
        """存储记忆，根据配置决定是否写入长期记忆"""
        if self.long_memory:
            self.long_memory.add(session_id, text)

memory_system = MemoryPyramid()