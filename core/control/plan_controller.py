from core.protocol.adapter.legacy_adapter import legacy_adapter
from config_loader import config_loader
from core.model.task.models import TaskDAG, TaskNode
from core.orchestrator.param_extractor import extract_params_from_nautral
from core.protocol.mcp_prompts import mc_prompt_manager
from src.manager_agent import llm_parse_task


# 从配置中读取规划参数
plan_config = config_loader.control_config["plan"]

class PlanController:
    """规划控制器： 配置化驱动任务拆解， 不依赖具体Model实现"""
    def build_tag(self, user_input: str, context: str = "") -> TaskDAG:
        """构建DAG任务，根据配置决定是否使用上下文"""
        # 配置化启用上下文辅助拆解
        if plan_config["enable_context"]:
            from core.control.core_controller import core_controller
            # MCP协议能力发现： 获取Host中的能力清单，供模型拆解任务使用
            mcp_capabilities = core_controller.mcp_capabilities if core_controller else {}
            # 调用MCP Prompts Server ,获取任务拆解提示模板
            prompt_params = {
                "prompt_id": "task_parse",
                "params": {"context": context, "user_input": user_input},
                "session_id": core_controller.session_id if core_controller else "unknown"
            }
            prompt_response = mc_prompt_manager.get_prompt(prompt_params)
            # 处理协议响应，获取提示内容
            if prompt_response["code"] != 200:
                # 协议异常，使用默认提示
                prompt_content = f"将用户输入{user_input}拆解为多个子任务，每个子任务包含skill、task、depend_on，返回JSON格式。"
            else:
                prompt_content = prompt_response["prompt_content"]
            # 模型结合MCP能力清单，拆解任务
            sub_tasks = llm_parse_task(user_input,
                                       context=context,
                                       prompt=prompt_content,
                                       capabilities=mcp_capabilities)
        else:
            sub_tasks = llm_parse_task(user_input)

        # 配置化限制最大子任务数
        sub_tasks = sub_tasks[:plan_config["max_sub_tasks"]]
        nodes = []

        for idx, t in enumerate(sub_tasks):
            skill = t.get("skill", "")
            task_content = t.get("task", "")
            dep = t.get("depend_on", -1)
            depend_on = [dep] if isinstance(dep, int) and dep >=0 else []

            # 提取参数
            skill_obj = legacy_adapter.get_skill(skill) if skill else None
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

# 全局单例
plan_controller = PlanController()