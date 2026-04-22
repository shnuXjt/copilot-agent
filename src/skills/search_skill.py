# src/skills/search_skill.py（MCP Tools原语适配，改造后完整代码）
from src.tools.search import duckduckgo_search
from pydantic import BaseModel
from typing import Optional
import time

# MCP协议规范：定义工具参数（标准化格式，必填参数标注清晰，可选参数设默认值）
class SearchParams(BaseModel):
    query: str  # 搜索关键词（必填，MCP协议要求：核心参数必须明确）
    session_id: str  # 会话ID（关联上下文，必填，用于关联当前调用与会话上下文）
    timeout: Optional[int] = 10  # 超时时间（协议可选参数，默认10秒）
    search_type: Optional[str] = "web"  # 搜索类型（可选，web/学术/新闻，默认web）

# MCP协议规范：定义工具响应（标准化格式，统一状态码、上下文ID）
class SearchResponse(BaseModel):
    code: int = 200  # 协议状态码（200成功，400参数错误，500执行失败，遵循MCP规范）
    message: str = "success"  # 状态描述，异常时返回错误信息
    data: Optional[dict] = None  # 搜索结果数据（核心返回内容，按实际场景封装）
    context_id: str  # 上下文ID（关联本次响应与MCP全流程交互，格式：模块_会话ID_时间戳）
    tool_name: str = "search_tool"  # 工具名称，与mcp_metadata中一致，便于模型识别

class SearchSkill:
    """搜索技能：MCP Tools原语实现，遵循MCP协议规范，负责联网获取实时数据"""
    # MCP协议：工具元数据（供模型动态发现，必须包含以下字段，可扩展）
    mcp_metadata = {
        "tool_name": "search_tool",  # 工具唯一标识，不可重复
        "description": "联网搜索工具，支持web/学术/新闻三种搜索类型，获取最新网络信息，适用于需要实时数据、外部信息的场景（如查询实时事件、最新数据、行业动态等）",
        "params_schema": SearchParams.model_json_schema(),  # 标准化参数schema，供模型校验参数
        "response_schema": SearchResponse.model_json_schema(),  # 标准化响应schema，供模型解析结果
        "permission": "public",  # 权限等级（MCP安全规范，public=所有会话可调用，private=仅指定会话可调用）
        "version": "1.0",  # 工具版本，便于后续升级迭代
        "supported_actions": ["run"]  # 支持的接口，MCP规范统一为run
    }

    @property
    def parameters(self):
        return [
            {"name": "query", "type": "string", "required": True, "description": "搜索关键词"},
            {"name": "session_id", "type": "string", "required": True, "description": "会话ID"},
            {"name": "timeout", "type": "int", "required": False, "description": "超时时间"},
            {"name": "search_type", "type": "string", "required": False, "description": "搜索类型"}
        ]

    def run(self, params: dict) -> dict:
        """MCP协议标准化调用接口，统一接口名run，所有技能必须实现此接口"""
        try:
            # 1. 协议参数校验（遵循MCP规范，防止非法请求、参数缺失，提升接口安全性）
            validated_params = SearchParams(**params)
            # 2. 执行搜索逻辑（复用原有search工具代码，不修改原有业务逻辑，仅做协议适配）
            # 按搜索类型执行对应逻辑，复用原有工具能力
            if validated_params.search_type == "web":
                search_result = duckduckgo_search(validated_params.query, timeout=validated_params.timeout)
            elif validated_params.search_type == "academic":
                search_result = duckduckgo_search(validated_params.query, search_type="academic", timeout=validated_params.timeout)
            elif validated_params.search_type == "news":
                search_result = duckduckgo_search(validated_params.query, search_type="news", timeout=validated_params.timeout)
            else:
                return SearchResponse(
                    code=400,
                    message=f"不支持的搜索类型：{validated_params.search_type}，仅支持web/academic/news",
                    context_id=f"search_error_{validated_params.session_id}_{int(time.time())}"
                ).model_dump()
            # 3. 按MCP协议格式返回响应，关联上下文ID（确保全局唯一，便于上下文追溯）
            return SearchResponse(
                data={
                    "search_result": search_result,  # 搜索结果（原有格式不变，封装到data字段）
                    "query": validated_params.query,  # 回显查询关键词，便于模型关联
                    "search_type": validated_params.search_type,  # 回显搜索类型
                    "timeout": validated_params.timeout  # 回显超时时间
                },
                context_id=f"search_{validated_params.session_id}_{int(time.time())}"
            ).model_dump()
        except Exception as e:
            # 协议异常响应格式（标准化错误提示，便于模型识别异常、排查问题）
            return SearchResponse(
                code=500,
                message=f"搜索工具执行失败：{str(e)}（异常类型：{type(e).__name__}）",
                context_id=f"search_error_{params.get('session_id', 'unknown')}_{int(time.time())}"
            ).model_dump()

# 注册到MCP工具清单（供Client层发现、调用，所有技能需统一注册）
MCP_TOOLS = [SearchSkill()]
