from collections import deque

from core.protocol.adapter.legacy_adapter import legacy_adapter
from config_loader import config_loader
from typing import Dict
import asyncio

from core.model.task.models import TaskNode, TaskDAG

# 从配置读取调度参数
scheduler_config = config_loader.control_config["scheduler"]

class SchedulerController:
    """调度控制器： 配置化驱动异步/同步调度"""
    def __init__(self):
        self.results: Dict[int, str] = {}
        self.enable_async = scheduler_config["enable_async"]

    async def run_node(self, node: TaskNode, session_id: str):
        """执行单个任务节点，适配配置化超时"""
        skill = legacy_adapter.get_skill(node.skill)
        if not skill:
            node.result = f"❌ 技能不存在：{node.skill}"
            self.results[node.task_id] = node.result
            return

        try:
            # 配置化任务超时控制
            async with asyncio.timeout(node.timeout):
                res = skill.run(node.task, session_id=session_id)
                node.result = res
                self.results[node.task_id] = res
        except asyncio.TimeoutError:
            node.result = f"❌ 任务超时（超过{node.timeout}秒）"
            self.results[node.task_id]=node.result
        except Exception as e:
            node.result = f"❌ 任务执行失败：{str(e)}"
            self.results[node.task_id] = node.result

    async def run_dag_async(self, dag: TaskDAG, session_id: str):
        """异步调度DAG，适配配置化并行数量"""

        nodes = {n.task_id: n for n in dag.nodes}
        in_degree = {nid: 0 for nid in nodes}
        adj = {nid: [] for nid in nodes}

        for node in nodes.values():
            for dep_id in  node.depend_on:
                if dep_id in nodes:
                    adj[dep_id].append(node.task_id)
                    in_degree[node.task_id] += 1

        q = deque()
        for nid in in_degree:
            if in_degree[nid] == 0:
                q.append(nid)

        while q:
            # 配置化最大滨兴数量
            batch_size = min(len(q), dag.max_parallel)
            batch = []
            for _ in range(batch_size):
                nid = q.popleft()
                batch.append(self.run_node(nodes[nid], session_id=session_id))
            await asyncio.gather(*batch)

            for executed_nid in [nid for nid in in_degree if in_degree == 0]:
                for neighbor in adj[executed_nid]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        q.append(neighbor)
        return self.results

    def run_dag(self, dag: TaskDAG, session_id: str):
        """统一调度入口，根据配置决定异步/同步"""
        if self.enable_async:
            return asyncio.run(self.run_dag_async(dag, session_id))
        else:
            # 同步调度
            for node in dag.nodes:
                self.run_node_sync(node, session_id)
            return self.results

    def run_node_sync(self, node: TaskNode, session_id: str):
        """同步执行任务节点"""
        skill = legacy_adapter.get_skill(node.skill)
        if not skill:
            node.result = f"❌ 技能不存在：{node.skill}"
            self.results[node.task_id] = node.result
            return

        try:
            res = skill.run(node.task, session_id=session_id)
            node.result = res
            self.results[node.task_id] = res
        except Exception as e:
            node.result = f"❌ 任务执行失败：{str(e)}"
            self.results[node.task_id] = node.result


# 全局单例
scheduler_controller = SchedulerController()
