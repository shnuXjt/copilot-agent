from pydantic import BaseModel
from typing import Dict

# MCP协议规范： 提示模板元数据（供模型动态发现，可根据项目需求扩展）
MCP_PROMPTS = {
    "task_parse": {
        "prompt_id": "task_parse",
        "description": "DAG任务拆解提示模板， 用于将用户输入拆解为可执行的子任务",
        "template": "基于上下文{context}, 将用户输入{user_input}拆解为多个子任务，每个子任务包含skill（技能名称）, task（任务描述）, depend_on（依赖任务ID,无依赖填-1）, 返回JSON格式，无需多余描述。",
        "params": ["context", "user_input"] # 模板所需参数
    },
    "reflect_check": {
        "prompt_id": "reflect_check",
        "description": "反思自检提示模板，用于校验任务执行结果的合法性",
        "template": "基于任务{task},技能{skill}, 校验结果{result}是否合法，若不合法，给出具体修改建议，返回校验提示，无需多余描述。",
        "params": ["task", "skill", "result"]
    },
    "stream_output": {
        "prompt_id": "stream_output",
        "description": "流式输出提示模板，用于优化AI回复的打字机效果提示",
        "template": "将结果{result}按自然语气拆分，适配打字机效果，避免过长段落，保留关键信息。",
        "params": ["result"]
    }
}

# MCP协议规范： 提示模板调用参数
class PromptCallParams(BaseModel):
    prompt_id: str # 提示模板ID（唯一标识）
    params: Dict[str, str] # 模板所需参数（键值对）
    session_id: str # 会话ID（关联上下文）

# MCP协议规范： 提示模板响应格式
class PromptResponse(BaseModel):
    code: int = 200
    message: str = "success"
    prompt_id: str # 调用的提示模板ID
    prompt_content: str # 填充参数后的完整提示词
    context_id: str # 上下文ID（关联提示和当前对话）

class MCPromptManager:
    """MCP Prompts原语管理器，遵循协议规范，供Client使用"""
    def get_prompt(self, params: dict) -> dict:
        """MCP协议标准化提示模板调用接口，统一接口名get_prompt"""
        try:
            validated_params = PromptCallParams(**params)
            # 1. 校验提示模板ID是否存在
            if validated_params.prompt_id not in MCP_PROMPTS:
                return PromptResponse(
                    code=404,
                    message=f"提示模板不存在：{validated_params.prompt_id}",
                    prompt_id=validated_params.prompt_id,
                    prompt_content="",
                    context_id=f"prompt_error_{validated_params.session_id}"
                ).model_dump()
            # 2. 获取模板并校验参数完整性
            prompt_info = MCP_PROMPTS[validated_params.prompt_id]
            missing_params = [p for p in prompt_info["params"] if p not in validated_params.params]
            if missing_params:
                return PromptResponse(
                    code=400,
                    message=f"缺少模板所需参数：{','.join(missing_params)}",
                    prompt_id=validated_params.prompt_id,
                    prompt_content="",
                    context_id=f"prompt_error_{validated_params.session_id}"
                ).model_dump()

            # 3. 填充参数， 生成完整提示词
            prompt_content = prompt_info["template"].format(**validated_params)
            # 4. 按MCP协议格式返回
            return PromptResponse(
                prompt_id=validated_params.prompt_id,
                prompt_content=prompt_content,
                context_id=f"prompt_{validated_params.prompt_id}_{validated_params.session_id}"
            ).model_dump()
        except Exception as e:
            return PromptResponse(
                code=500,
                message=f"提示模板调用失败：{str(e)}",
                prompt_id=params.get("prompt_id", ""),
                prompt_content="",
                context_id=f"prompt_error_{params.get('session_id', 'unknown')}"
            ).model_dump()

# 全局单例
mc_prompt_manager = MCPromptManager()