# core/protocol/specialist/search_specialist.py
from .base_specialist import BaseSpecialist
from core.protocol.adapter.legacy_adapter import legacy_adapter

class SearchSpecialist(BaseSpecialist):
    """搜索专家：标准化接口实现"""
    name = "search_specialist"
    description = "联网搜索专家，负责获取最新网络信息"

    def run(self, task: str, session_id: str, context: str = "") -> str:
        skill = legacy_adapter.get_skill("search")
        return skill.run(task, session_id=session_id) if skill else "❌ 搜索技能未加载"
