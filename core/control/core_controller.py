import time

from core.protocol.adapter.legacy_adapter import legacy_adapter
from config_loader import config_loader
from core.control.reflect_controller import reflect_controller
from core.model.memory.memory_pyramid import memory_system
from core.control.plan_controller import plan_controller
from core.control.scheduler_controller import scheduler_controller
from core.protocol.mcp_prompts import mc_prompt_manager, MCP_PROMPTS

# 从配置读取核心控制参数
core_config = config_loader.control_config["core"]

class CoreController:
    """核心控制器： 统筹全流程，配置化驱动，不依赖具体实现"""
    def __init__(self):
        self.adapter = legacy_adapter
        self.session_id = None
        # 配置化流式输出延迟
        self.stream_delay = core_config["stream_delay"]
        self.task_delay = core_config["task_delay"]
        # MCP 协议握手初始化，启动时与CLient， Server建立连接
        self._mcp_handshake()

    def set_session(self, session_id: str):
        self.session_id = session_id
        # 会话切换时，同步MCP上下文ID前缀
        self.context_prefix = f"session_{session_id}"

    def _mcp_handshake(self):
        """MCP协议握手： 交换协议版本，能力清单，确保通信兼容"""
        # 1. 通过Client获取所以Server的能力清单（Tools,Resources,Prompts)
        mcp_capabilities = {
            "protocol_version": "1.0",  # 遵循MCP协议1.0版本
            "tools": [tool.mcp_metadata for tool in self.adapter.mcp_tools],  # Tools能力清单
            "resources": [res["uri"] for res in self.adapter.mcp_resources],  # Resources能力清单
            "prompts": list(MCP_PROMPTS.keys())  # Prompts能力清单
        }
        # 2. Host记录能力清单，供模型查询使用
        self.mcp_capabilities = mcp_capabilities

        # 3. 握手成功日志
        print(f"✅ MCP协议握手成功，已发现能力：{mcp_capabilities}")

    def chat_stream(self, user_input):
        """流式输出主流程，完全遵循配置"""
        try:
            # 1. 记忆召回（配置化启用/禁用）
            # context = memory_system.get_full_context(self.session_id, user_input)
            context = ""

            # 2. DAG 规划
            dag = plan_controller.build_tag(user_input, context=context)

            # 3. 任务调度
            scheduler_controller.run_dag(dag, self.session_id)

            # 4. 流式输出
            full_reply = ""
            for node in dag.nodes:
                yield f"\n【任务 {node.task_id + 1}】\n"
                time.sleep(self.task_delay)

                # 调用MCP Prompts Server，获取反思提示模板
                reflect_params = {
                    "prompt_id": "reflect_check",
                    "params": {"task": node.task, "skill": node.skill, "result": node.result},
                    "session_id": self.session_id
                }
                reflect_prompt = mc_prompt_manager.get_prompt(reflect_params)
                if reflect_prompt["code"] == 200:
                    # 使用MCP提示模板进行反思优化
                    refined_result = reflect_controller.refine(
                        node.skill, node.task, node.result, context=context, prompt=reflect_prompt["prompt_content"]
                    )
                else:
                    # 协议异常，使用原有逻辑
                    refined_result = reflect_controller.refine(
                        node.skill, node.task, node.result, context=context
                    )

                # 流式输出拆分（调用MCP流式输出提示）
                stream_params = {
                    "prompt_id": "stream_output",
                    "params": {"result": refined_result},
                    "session_id": self.session_id
                }
                stream_prompt = mc_prompt_manager.get_prompt(stream_params)
                if stream_prompt["code"] == 200:
                    refined_result = stream_prompt["prompt_content"].format(result=refined_result)
                for c in refined_result:
                    yield  c
                    time.sleep(self.stream_delay)
                yield  "\n"
                full_reply += refined_result + "\n"

            # 5. 上下文更新（通过MCP CLient调用Resources Server更新长期记忆）
            self._mcp_update_context(user_input, full_reply)

            # 6. 记忆存储
            # memory_system.remember(self.session_id, user_input)
            if memory_system.short_memory:
                self.adapter.memory.save_user_message(self.session_id, user_input)
                self.adapter.memory.save_ai_message(self.session_id, full_reply)

        except Exception as e:
            yield f"系统异常： {str(e)}"

    def _mcp_update_context(self, user_input: str, full_reply: str):
        """MCP协议上下文更新， 调用Resrouces server更新长期记忆"""
        resource_update_params = {
            "session_id": self.session_id,
            "text": f"用户输入：{user_input}\nAI回复：{full_reply}",
            "context_id": f"{self.context_prefix}_update_{int(time.time())}"  # 全局唯一上下文ID
        }

        # 通过MCP Clinet转发氢气，更新向量记忆资源
        self.adapter.mcp_call_resource(
            resource_uri="vector_memory://long_term_context",
            params=resource_update_params,
            action="update"
        )

# 全局单例
core_controller = CoreController()