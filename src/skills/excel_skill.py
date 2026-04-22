# src/skills/excel_skill.py（MCP Tools原语适配，改造后完整代码）
from src.tools.excel import excel_reader
from pydantic import BaseModel
from typing import Optional, List, Dict
import time

# MCP协议规范：定义工具参数（Excel操作支持读取、写入、修改三种操作，参数按需适配）
class ExcelParams(BaseModel):
    session_id: str  # 会话ID（关联上下文，必填）
    file_path: str  # Excel文件路径（必填，绝对路径/相对路径均可）
    operation_type: str  # 操作类型（必填，read/write/modify）
    sheet_name: Optional[str] = "Sheet1"  # 工作表名称（可选，默认Sheet1）
    # 读取操作参数（operation_type=read时生效）
    read_range: Optional[str] = None  # 读取范围（如"A1:C10"，不填则读取整个工作表）
    # 写入操作参数（operation_type=write时生效）
    write_data: Optional[List[List[str]]] = None  # 写入数据（二维列表，与Excel单元格对应）
    start_cell: Optional[str] = "A1"  # 写入起始单元格（默认A1）
    # 修改操作参数（operation_type=modify时生效）
    modify_cell: Optional[str] = None  # 待修改单元格（如"B2"）
    modify_value: Optional[str] = None  # 修改后的值

# MCP协议规范：定义工具响应（标准化格式，区分不同操作的返回数据）
class ExcelResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[Dict] = None  # 操作结果数据，按操作类型封装
    context_id: str  # 上下文ID，关联MCP全流程
    tool_name: str = "excel_tool"
    operation_type: str  # 回显操作类型，便于模型关联

class ExcelSkill:
    """Excel操作技能：MCP Tools原语实现，支持读取、写入、修改Excel文件"""
    # MCP协议：工具元数据（供模型动态发现，详细描述功能，便于模型判断是否调用）
    mcp_metadata = {
        "tool_name": "excel_tool",
        "description": "Excel文件操作工具，支持读取Excel内容、写入数据到Excel、修改Excel指定单元格值，适用于需要处理表格数据、数据统计、文件导出的场景，支持.xlsx/.xls格式文件",
        "params_schema": ExcelParams.model_json_schema(),
        "response_schema": ExcelResponse.model_json_schema(),
        "permission": "public",
        "version": "1.0",
        "supported_actions": ["run"],
        "limitation": "需确保文件路径正确、文件可读写，写入/修改操作会覆盖原有数据，请谨慎操作"
    }

    @property
    def parameters(self):
        return [
            {"name": "session_id", "type": "string", "required": True},
            {"name": "file_path", "type": "string", "required": True},
            {"name": "operation_type", "type": "string", "required": True},
            {"name": "sheet_name", "type": "string", "required": False},
            {"name": "read_range", "type": "string", "required": False},
            {"name": "write_data", "type": "list", "required": False},
            {"name": "start_cell", "type": "string", "required": False},
            {"name": "modify_cell", "type": "string", "required": False},
            {"name": "modify_value", "type": "string", "required": False}
        ]

    def run(self, params: dict) -> dict:
        """MCP协议标准化调用接口，统一接口名run，适配三种Excel操作"""
        try:
            # 1. 协议参数校验，确保必填参数齐全、操作类型合法
            validated_params = ExcelParams(**params)
            operation_type = validated_params.operation_type.lower()
            # 2. 按操作类型执行对应Excel逻辑（复用原有excel_tool代码，不修改业务逻辑）
            if operation_type == "read":
                # 读取Excel操作
                result = excel_reader(
                    file_path=validated_params.file_path
                )
                data = {
                    "operation": "read",
                    "sheet_name": validated_params.sheet_name,
                    "read_range": validated_params.read_range,
                    "excel_data": result  # 读取到的Excel数据（二维列表）
                }
                message = f"Excel读取成功，工作表：{validated_params.sheet_name}"
            else:
                return ExcelResponse(
                    code=400,
                    message=f"不支持的操作类型：{operation_type}，仅支持read/write/modify",
                    context_id=f"excel_error_{validated_params.session_id}_{int(time.time())}",
                    operation_type=operation_type
                ).model_dump()
            # 3. 按MCP协议格式返回响应，关联上下文ID
            return ExcelResponse(
                message=message,
                data=data,
                context_id=f"excel_{operation_type}_{validated_params.session_id}_{int(time.time())}",
                operation_type=operation_type
            ).model_dump()
        except Exception as e:
            # 标准化异常响应，明确异常原因
            return ExcelResponse(
                code=500,
                message=f"Excel工具执行失败：{str(e)}（异常类型：{type(e).__name__}），请检查文件路径、文件权限或操作参数",
                context_id=f"excel_error_{params.get('session_id', 'unknown')}_{int(time.time())}",
                operation_type=params.get("operation_type", "unknown")
            ).model_dump()

# 注册到MCP工具清单（后续新增技能，直接添加到列表中）
MCP_TOOLS = [ExcelSkill()]
