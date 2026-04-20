# 异步执行器
import asyncio
from typing import Dict

from adapter import legacy_adapter
from core.orchestrator.models import TaskNode, TaskDAG


class AsyncScheduler:
    """异步DAG调度引擎： 并行执行无依赖任务"""

    def __init__(self):
        self.results: Dict[int, str] = {}

    async def run_node(self, node: TaskNode, session_id: str):
        """执行单个任务节点"""
        skill = legacy_adapter.get_skill(node.skill)

        if not skill:
            node.result = f"❌ 技能不存在: {node.skill}"
            self.results[node.task_id] = node.result
            return

        try:
            # 结构化参数调用(兼容dict/str自动判断）
            if node.params:
                res = skill.run(node.task, session_id=session_id)
            else:
                res = skill.run(node.task, session_id=session_id)

            node.result = res
            self.results[node.task_id]=node.result
        except Exception as e:
            node.result = f"❌ 执行失败: {str(e)}"
            self.results[node.task_id] = node.result

    async def run_dag(self, dag: TaskDAG, session_id: str):
        """拓扑调度"""
        tasks = []
        for node in dag.nodes:
            tasks.append(self.run_node(node, session_id))
        await asyncio.gather(*tasks)
        return self.results