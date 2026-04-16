from src.skills.base_skill import BaseSkill
from src.tools import tool_registry


class ExcelSkill(BaseSkill):

    skill_type="excel"

    @property
    def tools(self):
        return [tool_registry.get_tool("excel_analyzer")]

    @property
    def system_prompt(self):
        return "你是Excel数据分析师，读取并分析表格数据"

        # 🔥 结构化多参数规范（完美适配 StructuredTool）

    @property
    def parameters(self):
        return [
            {"name": "file_path", "type": "string", "required": True, "desc": "Excel文件路径"}
        ]