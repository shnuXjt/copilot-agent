# src/skills/calc_skill.py（MCP Tools原语适配，改造后完整代码）
from src.tools.calc import calculator
from pydantic import BaseModel
from typing import Optional

# MCP协议规范：定义工具参数（支持基础计算、复杂表达式计算）
class CalcParams(BaseModel):
    session_id: str  # 会话ID（必填）
    expression: str  # 计算表达式（必填，如"1+2*3"、"sqrt(16)+log(10)"）
    precision: Optional[int] = 2  # 计算精度（保留小数位数，默认2位）
    calc_type: Optional[str] = "basic"  # 计算类型，basic=基础计算，advanced=高级计算

# MCP协议规范：定义工具响应
class CalcResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None
    context_id: str
    tool_name: str = "calc_tool"

class CalcSkill:
    """计算技能：MCP Tools原语实现，支持基础算术、高级数学计算"""
    mcp_metadata = {
        "tool_name": "calc_tool",
        "description": "数学计算工具，支持基础算术运算（加减乘除、括号优先级）、高级数学运算（平方根、对数、三角函数等），适用于需要快速计算、数值运算的场景，表达式需符合数学规范",
        "params_schema": CalcParams.model_json_schema(),
        "response_schema": CalcResponse.model_json_schema(),
        "permission": "public",
        "version": "1.0",
        "supported_actions": ["run"],
        "limitation": "表达式需符合数学规范，不支持复杂公式（如微积分），高级计算需确保表达式正确"
    }

    def run(self, params: dict) -> dict:
        """MCP协议标准化调用接口，统一接口名run"""
        try:
            validated_params = CalcParams(**params)
            # 执行计算逻辑，复用原有calc_tool代码
            result = calculator(
                expression=validated_params.expression,
                calc_type=validated_params.calc_type,
                precision=validated_params.precision
            )
            # 封装响应数据
            data = {
                "expression": validated_params.expression,
                "calc_type": validated_params.calc_type,
                "precision": validated_params.precision,
                "result": result
            }
            message = f"计算成功，表达式：{validated_params.expression} = {result}"
            # 按MCP协议返回响应
            return CalcResponse(
                message=message,
                data=data,
                context_id=f"calc_{validated_params.session_id}_{int(time.time())}"
            ).model_dump()
        except Exception as e:
            return CalcResponse(
                code=500,
                message=f"计算工具执行失败：{str(e)}（异常类型：{type(e).__name__}），请检查计算表达式是否正确",
                context_id=f"calc_error_{params.get('session_id', 'unknown')}_{int(time.time())}"
            ).model_dump()

MCP_TOOLS = [CalcSkill()]
