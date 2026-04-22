from core.protocol.adapter.legacy_adapter import legacy_adapter
from config_loader import config_loader
from src.self_checker import self_checker
# 从配置读取反思参数
reflect_config = config_loader.control_config["reflect"]

class ReflectController:
    """反思控制器： 配置化驱动反思和重试"""
    def __init__(self):
        self.enable_retry = reflect_config["enable_retry"]
        self.max_retry = reflect_config["max_retry"]

    def refine(self, skill: str, task: str, result: str, context: str = "", prompt: str = ""):
        """
        反思优化任务执行结果，适配MCP协议
        :param skill: 技能名称（如search_tool、excel_tool）
        :param task: 任务描述（用户拆解后的子任务）
        :param result: 技能执行后的原始结果
        :param context: 会话上下文（复用原有参数）
        :param prompt: MCP Prompts原语提供的反思提示模板（新增参数，适配MCP协议）
        :return: 反思优化后的结果
        """
        # 1. 若MCP提示模板调用失败（prompt为空），使用原有默认反思逻辑
        if not prompt or reflect_config["enable_default_reflect"]:
            default_prompt = f"基于会话上下文：{context}，技能：{skill}，任务：{task}，校验执行结果：{result}是否合法、完整，若不合法或不完整，给出具体修改建议，优化结果，无需多余描述，保持结果简洁准确。"
            refined_result = self_checker.check(
                task=task,
                skill=skill,
                result=result,
                prompt=default_prompt
            )
        else:
            # 2. 若有MCP提示模板，使用标准化提示进行反思（新增逻辑，适配MCP协议）
            refined_result = self_checker.check(
                task=task,
                skill=skill,
                result=result,
                prompt=prompt  # 传入MCP Prompts原语返回的标准化提示
            )

        # 3. 配置化控制反思结果长度（复用原有逻辑）
        max_length = reflect_config["max_refine_length"]
        if len(refined_result) > max_length:
            refined_result = refined_result[:max_length] + "..."

        return refined_result

# 全局单例
reflect_controller = ReflectController()