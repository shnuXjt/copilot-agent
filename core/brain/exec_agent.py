# 执行智能体
from adapter import legacy_adapter


class ExecAgent:
    """执行层： 异步/并行/串行调度"""
    def execute(self, plan: dict, session_id: str) -> str:
        skill_type = plan["skill"]
        task = plan["task"]

        if not skill_type:
            return "😊 你好！我是你的智能助手"

        # 调用适配器
        legacy_adapter.run_skill(skill_type, task, session_id)