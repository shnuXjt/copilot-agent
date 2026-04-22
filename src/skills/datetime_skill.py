# src/skills/datetime_skill.py 【极简MCP适配，无冗余，不复杂】
from datetime import datetime
from typing import Optional, Dict

class DatetimeSkill:
    """极简MCP适配：获取当前时间/日期，仅保留协议核心规范"""
    # MCP核心元数据（极简版，够用即可）
    mcp_metadata = {
        "tool_name": "datetime_tool",
        "description": "获取当前系统时间、日期、时间戳，无参数，轻量快速",
        "permission": "public",
        "version": "1.0"
    }

    @property
    def parameters(self):
        return []

    def run(self, params: Optional[Dict] = None) -> Dict:
        """MCP统一接口：极简实现，无复杂参数校验"""
        try:
            # 核心逻辑：1行搞定
            now = datetime.now()
            return {
                # MCP标准响应格式
                "code": 200,
                "message": "success",
                "tool_name": "datetime_tool",
                "context_id": params.get("context_id", f"datetime_{int(now.timestamp())}"),
                # 业务数据
                "data": {
                    "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": now.strftime("%Y-%m-%d"),
                    "time": now.strftime("%H:%M:%S"),
                    "timestamp": int(now.timestamp())
                }
            }
        except Exception as e:
            return {
                "code": 500,
                "message": f"时间获取失败：{str(e)}",
                "tool_name": "datetime_tool",
                "context_id": params.get("context_id", "datetime_error"),
                "data": None
            }

# 注册
MCP_TOOLS = [DatetimeSkill()]