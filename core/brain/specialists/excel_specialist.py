from adapter import legacy_adapter
from core.brain.specialists.base_specialist import BaseSpecialist


class ExcelSpecialist(BaseSpecialist):
    name = "excel"
    discription = "Excel 数据分析专家"

    def run(self, task: str, session_id: str, context: str="") -> str:
        skill = legacy_adapter.get_skill("excel")
        return skill.run(task, session_id=session_id) if skill else "❌ Excel 技能未加载"

    