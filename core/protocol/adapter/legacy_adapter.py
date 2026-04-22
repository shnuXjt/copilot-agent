from config_loader import config_loader
# from core.model.memory.vector_memory import MCP_RESOURCES
from src.manager_agent import SKILLS
from src.memory import agent_memory
from src.self_checker import self_checker
from src.skills.search_skill import MCP_TOOLS
from src.tools import tool_registry

# 从配置读取适配器参数
adapter_config = config_loader.protocol_config["adapter"]["legacy"]

class LegacyAdapter:
    """配置化启动，标准化接口"""
    def __init__(self):
        if not adapter_config["enabled"]:
            self.skills = {}
            self.tool_registry = {}
            self.checker = None
            self.memory = None
            return

        self.skills = SKILLS
        self.tool_registry = tool_registry
        self.checker = self_checker
        self.memory = agent_memory

        # 加载MCP工具和资源清单，供转发请求使用
        self.mcp_tools = MCP_TOOLS
        # self.mcp_resources = MCP_RESOURCES
        self.mcp_resources = []

    # 标准化技能调用接口
    def get_skill(self, skill_type: str):
        # 从配置读取启用的技能，过滤未启用的技能
        enabled_skills = config_loader.model_config["skills"]["enabled"]
        if skill_type not in enabled_skills:
            return None
        return self.skills.get(skill_type)

    # 标准化技能执行接口
    def run_skill(self, skill_type: str, task: str, session_id: str):
        skill = self.get_skill(skill_type)
        if not skill:
            return f"❌ 未知技能或技能未启用: {skill_type}"
        return skill.run(task=task, session_id=session_id)

    # MCP协议工具调用转发接口（JSON-RPC 2.0 规范）
    def mcp_call_tool(self, tool_name: str, params: dict) -> dict:
        """MCP Client核心功能： 转发模型的工具调用请求到Tools Server"""
        # 1. 校验工具是否在MCP工具清单中，且已启用
        tool = next((t for t in self.mcp_tools if t.mcp_metadata["tool_name"] == tool_name), None)
        if not tool:
            return {
                "jsonrpc": "2.0",
                "error": {"code": 404, "message": f"工具未找到{tool_name}"},
                "id": params.get("context_id", "unknown")
            }
        # 2. 转发请求到Tools Server， 执行工具（调用工具的run接口）
        response = tool.run(params)
        # 3. 封装为MCP协议JSON-RPC 2.0 响应格式，返回Host
        return {
            "jsonrpc": "2.0",
            "result": response,
            "id": response.get("context_id", "unknown")
        }

    # MCP 协议资源调用转发接口（JSON-RPC 2.0规范）
    def mcp_call_resource(self, resource_uri: str, params: dict, action: str = "get") -> dict:
        """MCP Client 核心功能： 转发模型的资源调用请求到Resource Server"""
        # 1. 校验资源URI是否存在
        resource = next((res for res in self.mcp_resources if res["uri"] == resource_uri), None)
        if not resource:
            return {
                "jsonrpc": "2.0",
                "error": {"code": 404, "message": f"资源未找到：{resource_uri}"},
                "id": params.get("context_id", "unknown")
            }
        # 2. 转发请求到Resources Server，执行对应操作（get/update)
        resource_handler = resource["handler"]
        try:
            if action == "get":
                response = resource_handler.get_resource(params)
            elif action == "update":
                response = resource_handler.update_resource(params)
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": 400, "message": f"不支持的资源操作：{action}"},
                    "id": params.get("context_id", "unknown")
                }
            # 3. 封装为MCP协议JSON-RPC 2.0响应格式
            return {
                "jsonrpc": "2.0",
                "result": response,
                "id": response.get("context_id", "unknown")
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {"code": 500, "message": f"资源操作失败：{str(e)}"},
                "id": params.get("context_id", "unknown")
            }
# 全局单例
legacy_adapter = LegacyAdapter()