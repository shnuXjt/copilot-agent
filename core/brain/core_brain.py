# 大脑： 遵循： 感知 -> 规划 -> 执行 -> 反思 -> 记忆 标准流程
from adapter import legacy_adapter
from core.brain.exec_agent import ExecAgent
from core.brain.percept_agent import PerceptAgent
from core.brain.plan_agent import PlanAgent
from core.brain.reflect_agent import ReflectAgent


class CoreBrain:
    def __init__(self):
        self.adapter = legacy_adapter
        self.session_id = None

    # 设置当前会话
    def set_session(self, session_id):
        self.session_id = session_id

    # 会话： 执行主流程
    def chat(self, user_input: str):
        # 1. 感知： 理解用户输入（意图 + 实体)
        intent, skill_type, task = PerceptAgent().parse(user_input)

        # 2. 规划： 生成执行任务（DAG骨架)
        plan = PlanAgent().generate(skill_type, task)

        # 3. 执行：调度技能/工具
        raw_result = ExecAgent().execute(plan, self.session_id)

        # 4. 反思：校验 + 纠错
        final_result = ReflectAgent().refine(skill_type, task, raw_result)

        # 5. 记忆
        self.adapter.momery.add_message(self.session_id, "user", user_input)
        self.adapter.memory.add_message(self.session_id, "assistant", final_result)

        return final_result


# 全局单例
core_brain = CoreBrain()
