# 规划智能体
from adapter import legacy_adapter
from core.orchestrator.models import TaskDAG, TaskNode
from core.orchestrator.param_extractor import extract_params_from_nautral
from src.manager_agent import llm_parse_task


class PlanAgent:
    """规划曾： DAG任务编排"""

    def build_dag(self, user_input: str) -> TaskDAG:
        # 任务拆解
        sub_tasks = llm_parse_task(user_input)

        # 转为DAG节点
        nodes = []
        for idx, t in enumerate(sub_tasks):
            skill = t["skill"]
            task_content = t["task"]

            dep = t.get("depend_on", -1)

            depend_on = []
            if isinstance(dep, int) and dep >= 0:
                depend_on = [dep]


            # 自动提取参数
            skill_obj = legacy_adapter.get_skill(skill)
            params = extract_params_from_nautral(task_content, skill_obj.parameters) if skill_obj else {}

            node = TaskNode(
                task_id = idx,
                skill = skill,
                task = task_content,
                depend_on = depend_on,
                params = params
            )
            nodes.append(node)
        return TaskDAG(nodes=nodes)

    def generate(self, skill_type: str, task: str) -> dict:
        # 生成标准执行计划
        return {
            "skill": skill_type,
            "task": task,
            "depend_on": -1,
            "type": "single"
        }