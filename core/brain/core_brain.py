# 大脑： 遵循： 感知 -> 规划 -> 执行 -> 反思 -> 记忆 标准流程
import time

from adapter import legacy_adapter
from core.async_scheduler import AsyncScheduler
from core.brain.plan_agent import PlanAgent
from core.brain.reflect_agent import ReflectAgent
import asyncio

from core.memory.memory_pyramid import memory_system


class CoreBrain:
    def __init__(self):
        self.adapter = legacy_adapter
        self.session_id = None
        self.scheduler = AsyncScheduler()
        self.reflector = ReflectAgent()

    # 设置当前会话
    def set_session(self, session_id):
        self.session_id = session_id

    # 会话： 执行主流程
    def chat(self, user_input: str):
        try:

            #记忆召回
            context = memory_system.get_full_context(self.session_id, user_input)

            # DAG 规划
            dag = PlanAgent().build_dag(user_input)

            # 异步执行DAG
            asyncio.run(self.scheduler.run_dag(dag, self.session_id))

            # 汇总结果
            # final = []
            for node in dag.nodes:

                yield f"\n【任务 {node.task_id+1}】\n"
                time.sleep(0.1)

                ref_result = self.reflector.refine(node.skill, node.task, node.result)
                for c in ref_result:
                    yield  c
                    time.sleep(0.02)

                yield "\n"
                # final.append(f"【任务 {node.task_id + 1}】\n{ref_result}")

            # 记忆
            memory_system.remember(self.session_id, user_input)
            self.adapter.memory.save_user_message(self.session_id, user_input)
            # self.adapter.memory.save_ai_message(self.session_id, "\n\n".join(final))

            # return "\n\n".join(final)
        except Exception as e:
            yield f"系统异常：{str(e)}"


# 全局单例
core_brain = CoreBrain()
