from src.manager_agent import SKILLS
from src.memory import agent_memory
from src.tools import tool_registry
from src.self_checker import self_checker


# 适配器
class LegacyAdapter:
    def __init__(self):
        # 直接复用现有所有技能/工具/自检/记忆
        self.skills = SKILLS
        self.tool_registry = tool_registry
        self.checker = self_checker
        self.memory = agent_memory

    # 获取技能
    def get_sill(self, skill_type: str):
        return self.skills.get(skill_type)

    # 执行技能
    def run_skill(self, skill_type: str, task: str, session_id: str):
        skill = self.get_sill(skill_type)
        if not skill:
            return f"❌ 未知技能: {skill_type}"
        return skill.run(task=task, session_id=session_id)

# 全局单例
legacy_adapter = LegacyAdapter()