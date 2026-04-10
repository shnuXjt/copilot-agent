from src.skills.base_skill import BaseSkill
from src.tools import get_excel_reader_tool

class ExcelSkill(BaseSkill):

    def __init__(self):
        super().__init__(skill_type="excel")

    @property
    def tools(self):
        return [get_excel_reader_tool()]

    @property
    def system_prompt(self):
        return "你是Excel数据分析师，读取并分析表格数据"