from adapter import legacy_adapter
from core.brain.specialists.base_specialist import BaseSpecialist


class SearchSpecialist(BaseSpecialist):
    name = "search"
    description = "联网搜索专家"

    def run(self, task: str, session_id: str, context: str ="") -> str:
        skill = legacy_adapter.get_skill("search")
        return skill.run(task, session_id=session_id) if skill else "❌ 搜索技能未加载"