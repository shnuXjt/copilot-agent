# 异步执行器
import asyncio
from typing import Dict

from adapter import legacy_adapter
from core.orchestrator.models import TaskNode, TaskDAG
from collections import deque

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
            res = skill.run(node.task, session_id=session_id)
            node.result = res
            self.results[node.task_id]=node.result
        except Exception as e:
            node.result = f"❌ 执行失败: {str(e)}"
            self.results[node.task_id] = node.result

    async def run_dag(self, dag: TaskDAG, session_id: str):
        """拓扑调度: 按依赖顺序执行"""
        nodes = {n.task_id: n for n in dag.nodes}
        in_degree = {nid: 0 for nid in nodes}
        adj = {nid: [] for nid in nodes}

        for node in nodes.values():
            for dep_id in node.depend_on:
                if dep_id in nodes:
                    adj[dep_id].append(node.task_id)
                    in_degree[node.task_id] += 1

        q = deque()
        for nid in in_degree:
            if in_degree[nid] == 0:
                q.append(nid)


        while q:
            batch = []
            for _ in range(len(q)):
                nid = q.popleft()
                batch.append(self.run_node(nodes[nid], session_id))
            await asyncio.gather(*batch)

            for executed_nid in [n.task_id for n in [nodes[nid] for nid in in_degree if in_degree[nid] == 0]]:
                for neighbor in adj[executed_nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        q.append(neighbor)

        return self.results

        tasks = []